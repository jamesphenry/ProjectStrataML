#!/usr/bin/env python3
"""ProjectStrataML Environment Validation Tool

This tool validates that the current environment meets TFC-0010 requirements.
It checks Python version, virtual environment usage, system dependencies,
and package installation status.

Usage:
    python tools/setup.py --validate          # Validate all requirements
    python tools/setup.py --validate-gpu      # Validate GPU setup (optional)
    python tools/setup.py --verify-hashes     # Verify requirements hashes
"""

import sys
import subprocess
import importlib.util
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import yaml
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class ValidationError(Exception):
    """Raised when environment validation fails"""

    pass


class ValidationWarning(Exception):
    """Raised when environment validation finds warnings"""

    pass


class EnvironmentValidator:
    """Validates environment against TFC-0010 requirements"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.system_config = self._load_system_config()
        self.warnings = []
        self.errors = []

    def _load_system_config(self) -> Dict:
        """Load system configuration from environments/system.yaml"""
        config_path = self.project_root / "environments" / "system.yaml"
        if not config_path.exists():
            raise ValidationError(f"System config not found: {config_path}")

        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def validate_python_version(self) -> bool:
        """Validate Python 3.11+ requirement"""
        required_version = self.system_config["validation_rules"]["python_version"][
            "minimum"
        ]
        min_major, min_minor = map(int, required_version.split("."))

        current_version = f"{sys.version_info.major}.{sys.version_info.minor}"

        if sys.version_info < (min_major, min_minor):
            self.errors.append(
                f"Python {required_version}+ required, found {current_version}"
            )
            return False

        console.print(f"✅ Python version: {current_version}")
        return True

    def validate_virtual_environment(self) -> bool:
        """Validate virtual environment usage"""
        # Check if running in virtual environment
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            venv_path = sys.prefix
            allowed_paths = self.system_config["validation_rules"][
                "virtual_environment"
            ]["allowed_paths"]

            venv_name = Path(venv_path).name
            if venv_name not in allowed_paths:
                self.warnings.append(
                    f"Virtual environment name '{venv_name}' not recommended. Use: {', '.join(allowed_paths)}"
                )

            console.print(f"✅ Virtual environment: {venv_path}")
            return True
        else:
            self.errors.append("Virtual environment is required")
            return False

    def validate_system_dependencies(self) -> bool:
        """Validate system dependencies (git, git-lfs)"""
        success = True

        # Check git
        try:
            git_version = subprocess.run(
                ["git", "--version"], capture_output=True, text=True, check=True
            ).stdout.strip()
            console.print(f"✅ Git: {git_version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.errors.append("Git is not installed or not in PATH")
            success = False

        # Check git-lfs
        try:
            git_lfs_version = subprocess.run(
                ["git", "lfs", "version"], capture_output=True, text=True, check=True
            ).stdout.strip()
            console.print(f"✅ Git LFS: {git_lfs_version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.errors.append("Git LFS is not installed or not configured")
            success = False

        return success

    def _parse_requirements(self, requirements_file: Path) -> List[str]:
        """Parse requirements file and return package names"""
        packages = []
        if not requirements_file.exists():
            return packages

        with open(requirements_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Extract package name (remove version specifiers)
                    package_name = (
                        line.split(">=")[0]
                        .split("==")[0]
                        .split("<=")[0]
                        .split("<")[0]
                        .split(">")[0]
                    )
                    package_name = package_name.split("--index-url")[0].strip()
                    if package_name:
                        packages.append(package_name)

        return packages

    def validate_requirements(self, requirements_file: str) -> bool:
        """Validate that all requirements are installed"""
        req_path = self.project_root / requirements_file
        if not req_path.exists():
            self.warnings.append(f"Requirements file not found: {requirements_file}")
            return True

        packages = self._parse_requirements(req_path)
        missing_packages = []

        for package in packages:
            try:
                importlib.util.find_spec(package.replace("-", "_"))
                console.print(f"✅ Package installed: {package}")
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            self.errors.append(f"Missing packages: {', '.join(missing_packages)}")
            return False

        return True

    def validate_gpu_support(self) -> bool:
        """Validate GPU support (optional)"""
        try:
            import torch

            if torch.cuda.is_available():
                cuda_version = torch.version.cuda
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0)

                console.print(f"✅ GPU Support: {gpu_count} GPU(s)")
                console.print(f"   CUDA Version: {cuda_version}")
                console.print(f"   GPU 0: {gpu_name}")

                # Check if GPU requirements are installed
                gpu_req_path = self.project_root / "requirements-gpu.txt"
                if gpu_req_path.exists():
                    gpu_packages = self._parse_requirements(gpu_req_path)
                    missing_gpu_packages = []

                    for package in gpu_packages:
                        if package == "cupy-cuda11x":
                            try:
                                import cupy

                                console.print(f"✅ GPU Package: cupy")
                            except ImportError:
                                missing_gpu_packages.append(package)
                        else:
                            # For torch packages, check CUDA version
                            pass

                    if missing_gpu_packages:
                        self.warnings.append(
                            f"GPU detected but missing GPU packages: {', '.join(missing_gpu_packages)}"
                        )

                return True
            else:
                console.print("ℹ️  GPU not available (CPU-only mode)")
                return True
        except ImportError:
            console.print("ℹ️  PyTorch not installed, cannot validate GPU support")
            return True

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        if not file_path.exists():
            return ""

        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def verify_hashes(self) -> bool:
        """Verify requirements file hashes"""
        success = True

        requirements_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "requirements-gpu.txt",
        ]

        table = Table(title="Requirements File Hashes")
        table.add_column("File", style="cyan")
        table.add_column("SHA256 Hash", style="green")

        for req_file in requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                file_hash = self.calculate_file_hash(req_path)
                table.add_row(req_file, file_hash)
            else:
                table.add_row(req_file, "[red]File not found[/red]")

        console.print(table)
        return success

    def validate_all(self, validate_gpu: bool = False) -> bool:
        """Run all validation checks"""
        console.print(
            Panel.fit("🔍 ProjectStrataML Environment Validation", style="bold blue")
        )

        success = True

        # Core validations
        success &= self.validate_python_version()
        success &= self.validate_virtual_environment()
        success &= self.validate_system_dependencies()
        success &= self.validate_requirements("requirements.txt")
        success &= self.validate_requirements("requirements-dev.txt")

        # Optional GPU validation
        if validate_gpu:
            self.validate_gpu_support()

        # Print warnings
        if self.warnings:
            console.print("\n⚠️  Warnings:")
            for warning in self.warnings:
                console.print(f"   • {warning}", style="yellow")

        # Print errors
        if self.errors:
            console.print("\n❌ Errors:")
            for error in self.errors:
                console.print(f"   • {error}", style="red")

        return success and len(self.errors) == 0


@click.command()
@click.option("--validate-gpu", is_flag=True, help="Validate GPU support")
@click.option("--verify-hashes", is_flag=True, help="Verify requirements file hashes")
def main(validate_gpu: bool, verify_hashes: bool):
    """Validate ProjectStrataML environment"""
    validator = EnvironmentValidator()

    if verify_hashes:
        validator.verify_hashes()
        return

    success = validator.validate_all(validate_gpu=validate_gpu)

    if success:
        console.print("\n🎉 Environment validation passed!", style="bold green")
        sys.exit(0)
    else:
        console.print("\n💥 Environment validation failed!", style="bold red")
        console.print(
            "Please fix the errors above before proceeding.", style="bold red"
        )
        sys.exit(2)  # TFC-0006 error code


if __name__ == "__main__":
    main()
