#!/usr/bin/env python3
"""ProjectStrataML Experiment Runner

This tool provides standardized experiment execution following TFC-0003.
It creates run directories, captures metadata, logs metrics, and handles
experiment lifecycle management.

Usage:
    python tools/run.py --experiment experiments/train_model.py
    python tools/run.py --config configs/training/config.yaml
    python tools/run.py --run-id custom-run-123 --dataset cifar10/v1
"""

import sys
import os
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

import yaml
import click
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, TaskID

console = Console()


class ExperimentRunner:
    """Handles standardized experiment execution"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.run_id = None
        self.run_dir = None
        self.config = {}
        self.metrics_history = []
        self.start_time = None

    def _generate_run_id(self, custom_id: Optional[str] = None) -> str:
        """Generate unique run ID with timestamp"""
        if custom_id:
            return custom_id

        timestamp = datetime.now().strftime("%Y-%m-%d")
        # Simple counter - in production this would check existing runs
        counter = 1
        while True:
            candidate = f"run-{timestamp}-{counter:03d}"
            if not (self.project_root / "runs" / candidate).exists():
                return candidate
            counter += 1

    def _capture_system_info(self) -> Dict[str, Any]:
        """Capture system information"""
        import platform
        import subprocess

        ram_gb = 0
        if psutil:
            ram_gb = round(psutil.virtual_memory().total / (1024**3), 1)

        info = {
            "os": platform.system() + " " + platform.release(),
            "python": platform.python_version(),
            "frameworks": {},
            "hardware": {"cpu": platform.processor(), "ram_gb": ram_gb},
        }

        # Detect ML frameworks
        try:
            import torch

            info["frameworks"]["pytorch"] = torch.__version__
            if torch.cuda.is_available():
                info["hardware"]["gpus"] = [
                    torch.cuda.get_device_name(i)
                    for i in range(torch.cuda.device_count())
                ]
        except ImportError:
            pass

        try:
            import tensorflow as tf

            info["frameworks"]["tensorflow"] = tf.__version__
        except ImportError:
            pass

        try:
            import sklearn

            info["frameworks"]["sklearn"] = sklearn.__version__
        except ImportError:
            pass

        return info

    def _get_git_info(self) -> Dict[str, str]:
        """Get current git repository information"""
        try:
            import subprocess

            # Get current commit
            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            )
            commit = commit_result.stdout.strip()

            # Get remote URL
            remote_result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
            )
            repo_url = (
                remote_result.stdout.strip() if remote_result.returncode == 0 else ""
            )

            return {"repo": repo_url, "commit": commit}
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {"repo": "", "commit": ""}

    def _create_run_directory(self) -> None:
        """Create run directory with standard structure"""
        self.run_dir = self.project_root / "runs" / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)

        # Create artifacts subdirectory
        (self.run_dir / "artifacts").mkdir(exist_ok=True)

    def _write_config(self) -> None:
        """Write run configuration to config.yaml"""
        config_file = self.run_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def _write_system_info(self) -> None:
        """Write system information to system.json"""
        system_info = self._capture_system_info()
        system_file = self.run_dir / "system.json"
        with open(system_file, "w") as f:
            json.dump(system_info, f, indent=2)

    def _write_metrics(self, summary: Optional[Dict[str, Any]] = None) -> None:
        """Write metrics to metrics.json"""
        metrics_data = {"summary": summary or {}, "history": self.metrics_history}

        metrics_file = self.run_dir / "metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics_data, f, indent=2)

    def _log_message(self, message: str) -> None:
        """Log message to run log"""
        if self.run_dir:
            log_file = self.run_dir / "log.txt"
            timestamp = datetime.now().isoformat()
            with open(log_file, "a") as f:
                f.write(f"[{timestamp}] {message}\n")

        # Also output to console
        console.print(message)

    def _load_experiment_file(self, experiment_path: Path) -> None:
        """Load experiment configuration from Python file"""
        try:
            # Import experiment module
            spec = importlib.util.spec_from_file_location("experiment", experiment_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get configuration from experiment
            if hasattr(module, "get_config"):
                self.config = module.get_config()
            elif hasattr(module, "CONFIG"):
                self.config = module.CONFIG
            else:
                raise ValueError(
                    "Experiment must have get_config() function or CONFIG variable"
                )

            self.config["experiment"] = str(
                experiment_path.relative_to(self.project_root)
            )

        except Exception as e:
            raise ValueError(f"Failed to load experiment {experiment_path}: {e}")

    def _load_config_file(self, config_path: Path) -> None:
        """Load configuration from YAML file"""
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
            self.config["experiment"] = str(config_path.relative_to(self.project_root))
        except Exception as e:
            raise ValueError(f"Failed to load config {config_path}: {e}")

    def _validate_config(self) -> None:
        """Validate required configuration fields"""
        required_fields = ["model", "dataset"]
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Required field missing from config: {field}")

        # Ensure experiment field exists for TFC-0003 compliance
        if "experiment" not in self.config:
            self.config["experiment"] = (
                f"placeholder-{self.config.get('dataset', 'unknown')}"
            )

    def _log_metric(self, step: int, metrics: Dict[str, float]) -> None:
        """Log a metric step"""
        entry = {"step": step, "timestamp": datetime.now().isoformat(), **metrics}
        self.metrics_history.append(entry)

        # Update metrics file periodically
        if step % 10 == 0:  # Every 10 steps
            self._write_metrics()

    def run_experiment(self, experiment_config: Dict[str, Any]) -> int:
        """Execute the experiment"""
        self.config.update(experiment_config)
        self._validate_config()

        # Set up run directory and files
        self.run_id = self._generate_run_id(experiment_config.get("run_id"))
        self._create_run_directory()

        # Add metadata to config
        self.config["run_id"] = self.run_id
        self.config["started_at"] = datetime.now().isoformat()
        self.config["code"] = self._get_git_info()
        if "seed" not in self.config:
            self.config["seed"] = 42

        # Write initial files
        self._write_config()
        self._write_system_info()
        self._write_metrics()

        console.print(
            Panel.fit(f"🚀 Starting Experiment: {self.run_id}", style="bold green")
        )
        self._log_message(f"Starting experiment {self.run_id}")
        self._log_message(f"Configuration: {json.dumps(self.config, indent=2)}")

        self.start_time = time.time()

        try:
            # Execute experiment logic
            result = self._execute_experiment_logic()

            # Calculate runtime
            runtime = time.time() - self.start_time
            self.config["completed_at"] = datetime.now().isoformat()
            self.config["runtime_seconds"] = round(runtime, 2)

            # Write final metrics
            final_metrics = result.get("metrics", {})
            self._write_metrics(final_metrics)

            # Update config with results
            self.config["status"] = "completed"
            self.config["result"] = result.get("status", "success")
            self._write_config()

            console.print(
                f"✅ Experiment {self.run_id} completed successfully!",
                style="bold green",
            )
            self._log_message(f"Experiment completed with result: {result}")

            return 0

        except Exception as e:
            # Handle experiment failure
            runtime = time.time() - self.start_time
            self.config["completed_at"] = datetime.now().isoformat()
            self.config["runtime_seconds"] = round(runtime, 2)
            self.config["status"] = "failed"
            self.config["error"] = str(e)

            self._write_config()

            console.print(f"❌ Experiment {self.run_id} failed: {e}", style="bold red")
            self._log_message(f"Experiment failed with error: {e}")

            return 1

    def _execute_experiment_logic(self) -> Dict[str, Any]:
        """Execute the actual experiment logic"""
        # This is a placeholder for the actual experiment execution
        # In a real implementation, this would:
        # 1. Load the dataset
        # 2. Initialize the model
        # 3. Run training loop
        # 4. Log metrics during training
        # 5. Save model artifacts
        # 6. Return results

        experiment_type = self.config.get("experiment_type", "placeholder")

        if experiment_type == "placeholder":
            return self._run_placeholder_experiment()
        else:
            # Try to execute actual experiment
            return self._run_custom_experiment()

    def _run_placeholder_experiment(self) -> Dict[str, Any]:
        """Run a placeholder experiment for testing"""
        console.print("🔄 Running placeholder experiment...")

        # Simulate training steps
        for step in range(50):
            # Simulate some training progress
            time.sleep(0.1)  # Simulate work

            # Log dummy metrics
            metrics = {
                "loss": 1.0 - (step * 0.018),  # Decreasing loss
                "accuracy": min(0.5 + (step * 0.008), 0.95),  # Increasing accuracy
            }
            self._log_metric(step, metrics)

            if step % 10 == 0:
                console.print(
                    f"Step {step}: Loss={metrics['loss']:.3f}, Acc={metrics['accuracy']:.3f}"
                )

        # Save a dummy model artifact
        model_file = self.run_dir / "artifacts" / "dummy_model.pkl"
        with open(model_file, "w") as f:
            f.write("# Dummy model artifact\n")

        return {
            "status": "success",
            "metrics": {
                "final_loss": 0.1,
                "final_accuracy": 0.90,
                "best_accuracy": 0.92,
            },
        }

    def _run_custom_experiment(self) -> Dict[str, Any]:
        """Run a custom experiment from loaded module"""
        experiment_path = self.project_root / self.config["experiment"]

        try:
            spec = importlib.util.spec_from_file_location("experiment", experiment_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Call experiment's run function
            if hasattr(module, "run_experiment"):
                return module.run_experiment(self.config, self._log_metric)
            else:
                raise ValueError(
                    "Experiment module must have run_experiment() function"
                )

        except Exception as e:
            raise RuntimeError(f"Failed to execute experiment: {e}")


# Add psutil import for system info
try:
    import psutil
except ImportError:
    console.print(
        "⚠️ psutil not installed, system info may be incomplete", style="yellow"
    )
    psutil = None


# Add importlib for dynamic module loading
import importlib.util


@click.command()
@click.option(
    "--experiment", "-e", type=click.Path(exists=True), help="Experiment Python file"
)
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Configuration YAML file"
)
@click.option("--run-id", help="Custom run ID")
@click.option("--dataset", help="Dataset name/version (e.g., cifar10/v1)")
@click.option("--model", help="Model name")
@click.option("--seed", type=int, default=42, help="Random seed")
@click.option(
    "--experiment-type",
    default="placeholder",
    help="Experiment type (placeholder or custom)",
)
def main(
    experiment: Optional[str],
    config: Optional[str],
    run_id: Optional[str],
    dataset: Optional[str],
    model: Optional[str],
    seed: int,
    experiment_type: str,
):
    """Run a ProjectStrataML experiment

    Executes experiments following TFC-0003 standard. Creates run directory,
    captures metadata, logs metrics, and manages experiment lifecycle.

    Examples:
        python tools/run.py --experiment experiments/train_cnn.py
        python tools/run.py --config configs/training/cifar10.yaml
        python tools/run.py --dataset cifar10/v1 --model resnet50 --seed 123
    """

    runner = ExperimentRunner()

    # Build configuration from command line options
    config = {}

    if experiment:
        runner._load_experiment_file(Path(experiment))
        config = runner.config
    elif config:
        runner._load_config_file(Path(config))
        config = runner.config
    else:
        # Build config from command line options
        config = {
            "experiment_type": experiment_type,
            "dataset": dataset or "unknown",
            "model": model or "unknown",
            "seed": seed,
            "training": {"epochs": 10, "batch_size": 32, "learning_rate": 0.001},
        }

    # Override with command line options
    if run_id:
        config["run_id"] = run_id
    if dataset:
        config["dataset"] = dataset
    if model:
        config["model"] = model
    if seed != 42:
        config["seed"] = seed

    # Run the experiment
    exit_code = runner.run_experiment(config)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
