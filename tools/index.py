#!/usr/bin/env python3
"""ProjectStrataML Workspace Indexer

This tool scans datasets/, runs/, and models/ directories to build an in-memory
index with lineage references. It exports to JSON for dashboards or CLI tools.

Usage:
    python tools/index.py                           # Index and print summary
    python tools/index.py --json                   # Export JSON
    python tools/index.py --output index.json       # Save to file
    python tools/index.py --datasets               # Index only datasets
    python tools/index.py --models                  # Index only models
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

import yaml
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

console = Console()


class WorkspaceIndexer:
    """Indexes workspace artifacts and builds lineage relationships"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.index = {
            "datasets": {},
            "runs": {},
            "models": {},
            "lineage": {},
            "metadata": {
                "indexed_at": datetime.now().isoformat(),
                "project_root": str(self.project_root),
            },
        }

    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Safely load YAML file"""
        try:
            if file_path.exists():
                with open(file_path, "r") as f:
                    return yaml.safe_load(f) or {}
            return {}
        except yaml.YAMLError:
            return {}

    def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Safely load JSON file"""
        try:
            if file_path.exists():
                with open(file_path, "r") as f:
                    return json.load(f)
            return {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def index_datasets(self) -> None:
        """Index all datasets in datasets/ directory"""
        datasets_path = self.project_root / "datasets"
        if not datasets_path.exists():
            return

        for dataset_name in datasets_path.iterdir():
            if dataset_name.is_dir() and dataset_name.name != "README.md":
                self.index["datasets"][dataset_name.name] = {}

                for version_dir in dataset_name.iterdir():
                    if version_dir.is_dir() and version_dir.name.startswith("v"):
                        # Load dataset metadata
                        metadata_file = version_dir / "metadata.yaml"
                        metadata = self._load_yaml_file(metadata_file)

                        # Count samples in splits if directories exist
                        sample_counts = {}
                        for split in ["train", "val", "test"]:
                            split_path = version_dir / split
                            if split_path.exists():
                                # Count files (simplified sample count)
                                sample_counts[split] = len(list(split_path.iterdir()))

                        self.index["datasets"][dataset_name.name][version_dir.name] = {
                            "metadata": metadata,
                            "sample_counts": sample_counts,
                            "path": str(version_dir.relative_to(self.project_root)),
                        }

    def index_runs(self) -> None:
        """Index all runs in runs/ directory"""
        runs_path = self.project_root / "runs"
        if not runs_path.exists():
            return

        for run_dir in runs_path.iterdir():
            if run_dir.is_dir() and run_dir.name.startswith("run-"):
                # Load run artifacts
                config = self._load_yaml_file(run_dir / "config.yaml")
                metrics = self._load_json_file(run_dir / "metrics.json")
                system = self._load_json_file(run_dir / "system.json")

                # Read log file if exists
                log_content = ""
                log_file = run_dir / "log.txt"
                if log_file.exists():
                    try:
                        with open(log_file, "r") as f:
                            log_content = f.read()[:500]  # First 500 chars
                    except Exception:
                        pass

                self.index["runs"][run_dir.name] = {
                    "config": config,
                    "metrics": metrics,
                    "system": system,
                    "log_preview": log_content,
                    "path": str(run_dir.relative_to(self.project_root)),
                }

    def index_models(self) -> None:
        """Index all models in models/ directory"""
        models_path = self.project_root / "models"
        if not models_path.exists():
            return

        for model_name in models_path.iterdir():
            if model_name.is_dir() and model_name.name != "README.md":
                self.index["models"][model_name.name] = {}

                for version_dir in model_name.iterdir():
                    if version_dir.is_dir() and version_dir.name.startswith("v"):
                        # Load model artifacts
                        metadata = self._load_yaml_file(version_dir / "metadata.yaml")
                        metrics = self._load_yaml_file(version_dir / "metrics.yaml")
                        card_content = ""

                        card_file = version_dir / "card.md"
                        if card_file.exists():
                            try:
                                with open(card_file, "r") as f:
                                    card_content = f.read()[:1000]  # First 1000 chars
                            except Exception:
                                pass

                        # Find model files
                        model_files = []
                        for file_path in version_dir.iterdir():
                            if file_path.is_file() and file_path.suffix in [
                                ".pth",
                                ".pt",
                                ".pkl",
                                ".onnx",
                                ".pb",
                                ".h5",
                                ".keras",
                                ".ckpt",
                            ]:
                                model_files.append(
                                    {
                                        "name": file_path.name,
                                        "size": file_path.stat().st_size,
                                        "path": str(
                                            file_path.relative_to(self.project_root)
                                        ),
                                    }
                                )

                        self.index["models"][model_name.name][version_dir.name] = {
                            "metadata": metadata,
                            "metrics": metrics,
                            "card_preview": card_content,
                            "model_files": model_files,
                            "path": str(version_dir.relative_to(self.project_root)),
                        }

    def build_lineage(self) -> None:
        """Build lineage relationships between artifacts"""
        lineage = {}

        # Build run -> dataset/model relationships
        for run_id, run_data in self.index["runs"].items():
            config = run_data.get("config", {})
            lineage[run_id] = {
                "type": "run",
                "dataset": f"{config.get('dataset', '')}",
                "model": f"{config.get('model', '')}",
                "experiment": config.get("experiment", ""),
            }

        # Build model -> run relationships
        for model_name, versions in self.index["models"].items():
            for version, model_data in versions.items():
                model_id = f"{model_name}/{version}"
                metadata = model_data.get("metadata", {})
                run_id = metadata.get("run_id", "")

                if run_id:
                    lineage[model_id] = {
                        "type": "model",
                        "run_id": run_id,
                        "dataset": metadata.get("dataset", {}).get("name", ""),
                    }

        # Build dataset relationships
        for dataset_name, versions in self.index["datasets"].items():
            for version, dataset_data in versions.items():
                dataset_id = f"{dataset_name}/{version}"
                metadata = dataset_data.get("metadata", {})

                lineage[dataset_id] = {
                    "type": "dataset",
                    "derived_from": metadata.get("derived_from", {}),
                    "source": metadata.get("source", {}),
                }

        self.index["lineage"] = lineage

    def index_all(self) -> Dict[str, Any]:
        """Index all workspace artifacts"""
        self.index_datasets()
        self.index_runs()
        self.index_models()
        self.build_lineage()
        return self.index

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics of indexed artifacts"""
        stats = {
            "datasets": 0,
            "dataset_versions": 0,
            "runs": 0,
            "models": 0,
            "model_versions": 0,
        }

        # Count datasets and versions
        for dataset_name, versions in self.index["datasets"].items():
            stats["datasets"] += 1
            stats["dataset_versions"] += len(versions)

        # Count runs
        stats["runs"] += len(self.index["runs"])

        # Count models and versions
        for model_name, versions in self.index["models"].items():
            stats["models"] += 1
            stats["model_versions"] += len(versions)

        return stats

    def format_table_output(self) -> None:
        """Format index output as Rich tables"""
        stats = self.get_summary_stats()

        console.print(
            Panel.fit("📊 ProjectStrataML Workspace Index", style="bold blue")
        )

        # Summary table
        summary_table = Table(title="Summary Statistics")
        summary_table.add_column("Category", style="cyan")
        summary_table.add_column("Count", style="green")

        summary_table.add_row("Datasets", str(stats["datasets"]))
        summary_table.add_row("Dataset Versions", str(stats["dataset_versions"]))
        summary_table.add_row("Runs", str(stats["runs"]))
        summary_table.add_row("Models", str(stats["models"]))
        summary_table.add_row("Model Versions", str(stats["model_versions"]))

        console.print(summary_table)

        # Datasets table
        if self.index["datasets"]:
            datasets_table = Table(title="Datasets")
            datasets_table.add_column("Dataset", style="cyan")
            datasets_table.add_column("Versions", style="green")
            datasets_table.add_column("Latest", style="yellow")
            datasets_table.add_column("Description", style="white")

            for dataset_name, versions in self.index["datasets"].items():
                latest_version = max(versions.keys()) if versions else "N/A"
                description = ""
                if latest_version != "N/A":
                    description = (
                        versions[latest_version]
                        .get("metadata", {})
                        .get("description", "")[:50]
                    )

                datasets_table.add_row(
                    dataset_name, str(len(versions)), latest_version, description
                )

            console.print(datasets_table)

        # Recent runs table
        if self.index["runs"]:
            runs_table = Table(title="Recent Runs")
            runs_table.add_column("Run ID", style="cyan")
            runs_table.add_column("Experiment", style="green")
            runs_table.add_column("Model", style="yellow")
            runs_table.add_column("Dataset", style="white")

            # Sort by run ID (which includes timestamp)
            sorted_runs = sorted(self.index["runs"].items(), reverse=True)[:10]

            for run_id, run_data in sorted_runs:
                config = run_data.get("config", {})
                runs_table.add_row(
                    run_id[:20] + "...",
                    config.get("experiment", "")[:15],
                    config.get("model", "")[:15],
                    config.get("dataset", "")[:15],
                )

            console.print(runs_table)

        # Models table
        if self.index["models"]:
            models_table = Table(title="Models")
            models_table.add_column("Model", style="cyan")
            models_table.add_column("Versions", style="green")
            models_table.add_column("Latest", style="yellow")
            models_table.add_column("Framework", style="white")

            for model_name, versions in self.index["models"].items():
                latest_version = max(versions.keys()) if versions else "N/A"
                framework = ""
                if latest_version != "N/A":
                    framework = (
                        versions[latest_version]
                        .get("metadata", {})
                        .get("framework", "")
                    )

                models_table.add_row(
                    model_name, str(len(versions)), latest_version, framework
                )

            console.print(models_table)


@click.command()
@click.option("--json", "json_output", is_flag=True, help="Output JSON format")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--datasets", is_flag=True, help="Index only datasets")
@click.option("--models", is_flag=True, help="Index only models")
@click.option("--runs", is_flag=True, help="Index only runs")
def main(
    json_output: bool, output: Optional[str], datasets: bool, models: bool, runs: bool
):
    """Index ProjectStrataML workspace artifacts"""

    indexer = WorkspaceIndexer()

    # Index based on options
    if datasets:
        indexer.index_datasets()
    elif models:
        indexer.index_models()
    elif runs:
        indexer.index_runs()
    else:
        indexer.index_all()

    # Output results
    if json_output or output:
        output_data = indexer.index
        json_str = json.dumps(output_data, indent=2)

        if output:
            with open(output, "w") as f:
                f.write(json_str)
            console.print(f"✅ Index saved to {output}", style="bold green")
        else:
            print(json_str)
    else:
        indexer.format_table_output()


if __name__ == "__main__":
    main()
