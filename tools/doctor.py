#!/usr/bin/env python3
"""ProjectStrataML Repository Doctor Tool

This tool validates comprehensive TFC compliance across all Technical Framework Contracts.
It validates repository layout, dataset metadata, run and model artifacts, and lineage.

Usage:
    python tools/doctor.py                    # Basic validation
    python tools/doctor.py --strict          # Strict mode (fail on warnings)
    python tools/doctor.py --json            # JSON output
    python tools/doctor.py --tfc <number>     # Validate specific TFC
"""

import sys
import json
import subprocess
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime

import yaml
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

console = Console()


class ValidationError(Exception):
    """Raised when repository validation fails"""

    pass


class RepositoryDoctor:
    """Validates repository against all TFC specifications"""

    def __init__(self, strict: bool = False, json_output: bool = False):
        self.project_root = Path(__file__).parent.parent
        self.strict = strict
        self.json_output = json_output
        self.warnings = []
        self.errors = []
        self.validation_results = {}

    def _validate_required_directory(self, path: Path, name: str) -> bool:
        """Validate a required directory exists"""
        if not path.exists():
            self.errors.append(f"Required directory missing: {name} ({path})")
            return False
        elif not path.is_dir():
            self.errors.append(
                f"Required path exists but is not a directory: {name} ({path})"
            )
            return False
        else:
            return True

    def validate_tfc_0001_layout(self) -> bool:
        """Validate TFC-0001 Standard ML Project layout"""
        success = True

        required_directories = [
            ("configs", "Configuration templates"),
            ("data", "Raw data storage"),
            ("datasets", "Versioned datasets"),
            ("docs", "Documentation"),
            ("environments", "Environment configuration"),
            ("experiments", "Experiment definitions"),
            ("models", "Model registry"),
            ("runs", "Execution records"),
            ("scripts", "Utility scripts"),
            ("src", "Source code"),
            ("spaces", "Interactive demos"),
            ("tools", "Project tooling"),
        ]

        for dir_name, description in required_directories:
            dir_path = self.project_root / dir_name
            if not self._validate_required_directory(dir_path, description):
                success = False

        # Validate required files
        required_files = [
            ("README.md", "Project documentation"),
            (".gitignore", "Git ignore rules"),
            (".gitattributes", "Git LFS configuration"),
            (".lfsconfig", "Git LFS settings"),
            ("requirements.txt", "Core dependencies"),
            ("requirements-dev.txt", "Development dependencies"),
            ("requirements-gpu.txt", "GPU dependencies"),
            ("environments/system.yaml", "System configuration"),
        ]

        for file_name, description in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                self.errors.append(
                    f"Required file missing: {description} ({file_path})"
                )
                success = False

        self.validation_results["tfc_0001"] = success
        return success

    def validate_tfc_0002_schemas(self) -> bool:
        """Validate TFC-0002 Standard Schemas compliance"""
        success = True

        # Check configuration templates exist and follow schema
        config_templates = [
            "configs/datasets/base.yaml",
            "configs/models/base.yaml",
            "configs/training/base.yaml",
            "configs/sweeps/base.yaml",
        ]

        for template in config_templates:
            template_path = self.project_root / template
            if not template_path.exists():
                self.errors.append(f"Missing configuration template: {template}")
                success = False
            else:
                try:
                    with open(template_path, "r") as f:
                        content = yaml.safe_load(f)
                        # Basic structure validation
                        if not isinstance(content, dict):
                            self.errors.append(f"Invalid YAML structure in {template}")
                            success = False
                except yaml.YAMLError as e:
                    self.errors.append(f"Invalid YAML in {template}: {e}")
                    success = False

        self.validation_results["tfc_0002"] = success
        return success

    def _validate_dataset_version(self, dataset_path: Path) -> bool:
        """Validate a single dataset version"""
        success = True

        # Check required subdirectories
        for split in ["train", "val", "test"]:
            split_path = dataset_path / split
            if not split_path.exists():
                self.warnings.append(
                    f"Dataset {dataset_path.name} missing {split} split"
                )

        # Check metadata.yaml
        metadata_path = dataset_path / "metadata.yaml"
        if not metadata_path.exists():
            self.errors.append(f"Dataset {dataset_path.name} missing metadata.yaml")
            success = False
        else:
            try:
                with open(metadata_path, "r") as f:
                    metadata = yaml.safe_load(f)

                # Validate required fields
                required_fields = [
                    "name",
                    "version",
                    "created_at",
                    "description",
                    "source",
                    "hash",
                ]
                for field in required_fields:
                    if field not in metadata:
                        self.errors.append(
                            f"Dataset {dataset_path.name} metadata missing field: {field}"
                        )
                        success = False

                # Validate version format
                if not metadata.get("version", "").startswith("v"):
                    self.errors.append(
                        f"Dataset {dataset_path.name} has invalid version format: {metadata.get('version')}"
                    )
                    success = False

            except yaml.YAMLError as e:
                self.errors.append(
                    f"Invalid YAML in dataset metadata {dataset_path}: {e}"
                )
                success = False

        return success

    def validate_tfc_0004_datasets(self) -> bool:
        """Validate TFC-0004 Dataset Metadata compliance"""
        success = True
        datasets_path = self.project_root / "datasets"

        if not datasets_path.exists():
            return True  # No datasets to validate

        # Find all dataset versions
        for dataset_dir in datasets_path.iterdir():
            if dataset_dir.is_dir() and dataset_dir.name != "README.md":
                for version_dir in dataset_dir.iterdir():
                    if version_dir.is_dir():
                        if not self._validate_dataset_version(version_dir):
                            success = False

        self.validation_results["tfc_0004"] = success
        return success

    def _validate_model_version(self, model_path: Path) -> bool:
        """Validate a single model version"""
        success = True

        # Check required files
        required_files = {
            "metadata.yaml": "Model metadata",
            "metrics.yaml": "Model metrics",
            "card.md": "Model card",
        }

        for file_name, description in required_files.items():
            file_path = model_path / file_name
            if not file_path.exists():
                self.warnings.append(
                    f"Model {model_path.name} missing {description} ({file_name})"
                )

        # Check for model artifact (any file that could be a model)
        model_files = [
            f
            for f in model_path.iterdir()
            if f.is_file()
            and f.suffix
            in [".pth", ".pt", ".pkl", ".onnx", ".pb", ".h5", ".keras", ".ckpt"]
        ]

        if not model_files:
            self.warnings.append(
                f"Model {model_path.name} has no recognizable model artifact"
            )

        # Validate metadata.yaml if it exists
        metadata_path = model_path / "metadata.yaml"
        if metadata_path.exists():
            try:
                with open(metadata_path, "r") as f:
                    metadata = yaml.safe_load(f)

                # Validate required fields
                required_fields = [
                    "name",
                    "version",
                    "created_at",
                    "run_id",
                    "dataset",
                    "code",
                    "framework",
                ]
                for field in required_fields:
                    if field not in metadata:
                        self.errors.append(
                            f"Model {model_path.name} metadata missing field: {field}"
                        )
                        success = False

                # Validate version format
                if not metadata.get("version", "").startswith("v"):
                    self.errors.append(
                        f"Model {model_path.name} has invalid version format: {metadata.get('version')}"
                    )
                    success = False

            except yaml.YAMLError as e:
                self.errors.append(f"Invalid YAML in model metadata {model_path}: {e}")
                success = False

        return success

    def validate_tfc_0005_models(self) -> bool:
        """Validate TFC-0005 Model Registry compliance"""
        success = True
        models_path = self.project_root / "models"

        if not models_path.exists():
            return True  # No models to validate

        # Find all model versions
        for model_dir in models_path.iterdir():
            if model_dir.is_dir() and model_dir.name != "README.md":
                for version_dir in model_dir.iterdir():
                    if version_dir.is_dir():
                        if not self._validate_model_version(version_dir):
                            success = False

        self.validation_results["tfc_0005"] = success
        return success

    def _validate_run_directory(self, run_path: Path) -> bool:
        """Validate a single run directory"""
        success = True

        # Check required files
        required_files = {
            "config.yaml": "Run configuration",
            "metrics.json": "Run metrics",
            "system.json": "System metadata",
            "log.txt": "Run log",
        }

        for file_name, description in required_files.items():
            file_path = run_path / file_name
            if not file_path.exists():
                self.errors.append(
                    f"Run {run_path.name} missing {description} ({file_name})"
                )
                success = False

        # Validate config.yaml
        config_path = run_path / "config.yaml"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)

                # Validate required fields
                required_fields = ["run_id", "experiment", "model", "dataset"]
                for field in required_fields:
                    if field not in config:
                        self.errors.append(
                            f"Run {run_path.name} config missing field: {field}"
                        )
                        success = False

            except yaml.YAMLError as e:
                self.errors.append(f"Invalid YAML in run config {run_path}: {e}")
                success = False

        # Validate metrics.json
        metrics_path = run_path / "metrics.json"
        if metrics_path.exists():
            try:
                with open(metrics_path, "r") as f:
                    metrics = json.load(f)

                if not isinstance(metrics, dict):
                    self.errors.append(
                        f"Run {run_path.name} metrics.json is not a valid JSON object"
                    )
                    success = False

            except json.JSONDecodeError as e:
                self.errors.append(f"Invalid JSON in run metrics {run_path}: {e}")
                success = False

        return success

    def validate_tfc_0003_runs(self) -> bool:
        """Validate TFC-0003 Standard Run compliance"""
        success = True
        runs_path = self.project_root / "runs"

        if not runs_path.exists():
            return True  # No runs to validate

        # Find all run directories
        for run_dir in runs_path.iterdir():
            if run_dir.is_dir() and run_dir.name.startswith("run-"):
                if not self._validate_run_directory(run_dir):
                    success = False

        self.validation_results["tfc_0003"] = success
        return success

    def validate_git_lfs_setup(self) -> bool:
        """Validate Git LFS configuration and usage"""
        success = True

        # Check if git-lfs is installed
        try:
            result = subprocess.run(
                ["git", "lfs", "version"], capture_output=True, text=True, check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.errors.append("Git LFS is not installed or not configured")
            success = False
            return success

        # Check if .gitattributes exists and has LFS rules
        gitattributes_path = self.project_root / ".gitattributes"
        if gitattributes_path.exists():
            with open(gitattributes_path, "r") as f:
                content = f.read()
                if "filter=lfs" not in content:
                    self.warnings.append("No LFS filters found in .gitattributes")
        else:
            self.errors.append("Missing .gitattributes file for LFS configuration")
            success = False

        # Check for potentially large files that should be tracked with LFS
        large_extensions = [
            ".pth",
            ".pt",
            ".pkl",
            ".h5",
            ".hdf5",
            ".onnx",
            ".pb",
            ".png",
            ".jpg",
            ".jpeg",
            ".csv",
            ".parquet",
        ]

        for ext in large_extensions:
            files = list(self.project_root.rglob(f"*{ext}"))
            for file_path in files:
                if file_path.stat().st_size > 1024 * 1024:  # > 1MB
                    # Check if file is tracked by LFS
                    try:
                        result = subprocess.run(
                            [
                                "git",
                                "lfs",
                                "ls-files",
                                str(file_path.relative_to(self.project_root)),
                            ],
                            capture_output=True,
                            text=True,
                        )
                        if not result.stdout.strip():
                            self.warnings.append(
                                f"Large file not tracked by LFS: {file_path.relative_to(self.project_root)}"
                            )
                    except subprocess.CalledProcessError:
                        pass  # File might not be tracked yet

        return success

    def validate_all_tfc(self, target_tfc: Optional[int] = None) -> bool:
        """Run all TFC validations"""
        success = True

        if target_tfc:
            validations = {
                1: self.validate_tfc_0001_layout,
                2: self.validate_tfc_0002_schemas,
                3: self.validate_tfc_0003_runs,
                4: self.validate_tfc_0004_datasets,
                5: self.validate_tfc_0005_models,
            }

            if target_tfc in validations:
                success &= validations[target_tfc]()
            else:
                self.errors.append(f"Unknown TFC number: {target_tfc}")
                success = False
        else:
            # Run all validations
            success &= self.validate_tfc_0001_layout()
            success &= self.validate_tfc_0002_schemas()
            success &= self.validate_tfc_0003_runs()
            success &= self.validate_tfc_0004_datasets()
            success &= self.validate_tfc_0005_models()
            success &= self.validate_git_lfs_setup()

        return success

    def format_output(self, success: bool) -> str:
        """Format validation output"""
        if self.json_output:
            return json.dumps(
                {
                    "success": success,
                    "errors": self.errors,
                    "warnings": self.warnings,
                    "validation_results": self.validation_results,
                },
                indent=2,
            )

        # Rich console output
        output = []

        # Summary panel
        if success and not self.warnings:
            title = "✅ Repository Validation: PASSED"
            style = "bold green"
        elif success and self.warnings:
            title = "⚠️ Repository Validation: PASSED WITH WARNINGS"
            style = "bold yellow"
        else:
            title = "❌ Repository Validation: FAILED"
            style = "bold red"

        console.print(Panel.fit(title, style=style))

        # TFC results table
        table = Table(title="TFC Validation Results")
        table.add_column("TFC", style="cyan")
        table.add_column("Status", style="")
        table.add_column("Description", style="white")

        tfc_names = {
            "tfc_0001": "TFC-0001: Standard ML Project",
            "tfc_0002": "TFC-0002: Standard Schemas",
            "tfc_0003": "TFC-0003: Standard Run",
            "tfc_0004": "TFC-0004: Dataset Metadata",
            "tfc_0005": "TFC-0005: Model Registry",
        }

        for tfc_key, passed in self.validation_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            status_style = "green" if passed else "red"
            table.add_row(
                tfc_names.get(tfc_key, tfc_key),
                f"[{status_style}]{status}[/{status_style}]",
                "",
            )

        console.print(table)

        # Errors
        if self.errors:
            console.print("\n❌ Errors:")
            for error in self.errors:
                console.print(f"   • {error}", style="red")

        # Warnings
        if self.warnings:
            console.print("\n⚠️ Warnings:")
            for warning in self.warnings:
                console.print(f"   • {warning}", style="yellow")

        return ""

    def exit_with_code(self, success: bool) -> int:
        """Return appropriate exit code"""
        if success:
            return 0
        elif self.warnings and not self.strict:
            return 1  # Warnings only
        else:
            return 2  # Errors


@click.command()
@click.option("--strict", is_flag=True, help="Treat warnings as errors")
@click.option("--json", "json_output", is_flag=True, help="JSON output format")
@click.option("--tfc", type=int, help="Validate specific TFC number (1-5)")
def main(strict: bool, json_output: bool, tfc: Optional[int]):
    """Validate ProjectStrataML repository TFC compliance"""

    doctor = RepositoryDoctor(strict=strict, json_output=json_output)
    success = doctor.validate_all_tfc(target_tfc=tfc)

    output = doctor.format_output(success)
    if json_output:
        print(output)

    sys.exit(doctor.exit_with_code(success))


if __name__ == "__main__":
    main()
