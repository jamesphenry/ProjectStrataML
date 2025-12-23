#!/usr/bin/env python3
"""ProjectStrataML Repository Initialization Tool

This tool cleans up a forked repository to make it ready for new projects.
It removes example data, runs, and generated artifacts while preserving
configuration and documentation.

Usage:
    python tools/init.py                    # Clean everything
    python tools/init.py --keep-examples   # Keep example data
"""

import sys
import shutil
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command()
@click.option("--keep-examples", is_flag=True, help="Keep example data and runs")
@click.option("--keep-docs", is_flag=True, help="Keep documentation examples")
@click.confirmation_option(
    prompt="This will remove all datasets, models, runs, and data. Are you sure?"
)
def init(keep_examples: bool, keep_docs: bool):
    """Initialize clean workspace

    Resets the repository to a clean state ready for new projects.
    Removes example data, runs, and generated artifacts while preserving
    configuration and documentation.
    """
    project_root = Path(__file__).parent.parent
    removed_items = []

    console.print(Panel.fit("🧹 Repository Initialization", style="bold blue"))

    # Remove example directories
    if not keep_examples:
        dirs_to_clean = ["data", "datasets", "models", "runs"]
        for dir_name in dirs_to_clean:
            dir_path = project_root / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                removed_items.append(dir_name)
                console.print(f"  Removed directory: {dir_name}", style="yellow")

    # Remove example runs if keeping examples
    if keep_examples:
        runs_dir = project_root / "runs"
        if runs_dir.exists():
            # Keep only example runs, remove generated ones
            for item in runs_dir.iterdir():
                if item.is_dir() and not item.name.startswith("run-"):
                    shutil.rmtree(item)
                    removed_items.append(f"runs/{item.name}")

    # Remove Python cache and build artifacts
    patterns_to_remove = [
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
    ]

    for pattern in patterns_to_remove:
        for path in project_root.glob(pattern):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                removed_items.append(str(path.relative_to(project_root)))
                console.print(f"  Removed cache/build: {path.name}", style="yellow")
            except Exception:
                pass  # Some files might be locked

    # Remove generated model files from root
    model_extensions = ["*.pkl", "*.pth", "*.pt", "*.h5", "*.hdf5"]
    for ext in model_extensions:
        for path in project_root.glob(ext):
            if path.is_file():
                path.unlink()
                removed_items.append(path.name)
                console.print(f"  Removed model file: {path.name}", style="yellow")

    # Re-create essential directories with README files
    essential_dirs = ["datasets", "models", "runs", "data"]
    for dir_name in essential_dirs:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)

        readme_content = (
            f"# {dir_name.title()}\n\nThis directory is ready for your {dir_name}.\n"
        )
        readme_file = dir_path / "README.md"
        if not readme_file.exists():
            readme_file.write_text(readme_content)
            console.print(f"  Created directory: {dir_name}/", style="green")

    # Show results
    console.print(f"\n✅ Repository initialized successfully!", style="bold green")
    console.print(f"Removed {len(removed_items)} items.", style="blue")
    console.print(
        "Your workspace is now clean and ready for new projects.", style="blue"
    )

    if keep_examples:
        console.print("Example files preserved as requested.", style="yellow")


if __name__ == "__main__":
    init()
