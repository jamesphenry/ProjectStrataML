#!/usr/bin/env python3
"""ProjectStrataML CLI Tool

This is the main CLI entry point for ProjectStrataML. It wraps core tools
and provides user-friendly access to doctor validation, workspace indexing,
and other functionality.

Usage:
    strataml doctor                    # Run repository validation
    strataml index                     # Index workspace artifacts
    strataml list datasets|runs|models # List artifacts
    strataml serve                     # Start dashboard server
"""

import sys
import json
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

console = Console()

# Import core tools
sys.path.insert(0, str(Path(__file__).parent))
from doctor import RepositoryDoctor
from index import WorkspaceIndexer


@click.group()
@click.version_option(version="0.1.0", prog_name="strataml")
def main():
    """ProjectStrataML - Local-First ML Framework

    A Git-native ML framework for reproducible experiments, dataset versioning,
    and model registry management.
    """
    pass


@main.command()
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
    import subprocess
    import sys

    project_root = Path(__file__).parent.parent

    # Call the init script
    init_script = project_root / "tools" / "init.py"
    cmd = [sys.executable, str(init_script)]

    if keep_examples:
        cmd.append("--keep-examples")
    if keep_docs:
        cmd.append("--keep-docs")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            console.print(
                f"❌ Initialization failed: {result.stderr}", style="bold red"
            )
            sys.exit(1)
    except Exception as e:
        console.print(f"❌ Failed to run initialization: {e}", style="bold red")
        sys.exit(1)


@main.command()
@click.option("--keep-examples", is_flag=True, help="Keep example data and runs")
@click.option("--keep-docs", is_flag=True, help="Keep documentation examples")
@click.confirmation_option(
    prompt="This will remove all datasets, models, runs, and data. Are you sure?"
)
def init_workspace(keep_examples: bool, keep_docs: bool):
    """Initialize clean workspace

    Resets the repository to a clean state ready for new projects.
    Removes example data, runs, and generated artifacts while preserving
    configuration and documentation.
    """
    import subprocess
    import sys

    project_root = Path(__file__).parent.parent

    # Call init script
    init_script = project_root / "tools" / "init.py"
    cmd = [sys.executable, str(init_script)]

    if keep_examples:
        cmd.append("--keep-examples")
    if keep_docs:
        cmd.append("--keep-docs")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            console.print(
                f"❌ Initialization failed: {result.stderr}", style="bold red"
            )
            sys.exit(1)
    except Exception as e:
        console.print(f"❌ Failed to run initialization: {e}", style="bold red")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Failed to run initialization: {e}", style="bold red")
        sys.exit(1)


@main.command()
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
def status(format: str):
    """Show workspace status summary

    Display a quick summary of the current workspace state including
    number of datasets, runs, models, and recent activity.
    """
    indexer = WorkspaceIndexer()
    indexer.index_all()

    stats = indexer.get_summary_stats()

    if format == "json":
        print(json.dumps(stats, indent=2))
    else:
        # Summary table
        table = Table(title="Workspace Status")
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="green")

        table.add_row("Datasets", str(stats["datasets"]))
        table.add_row("Dataset Versions", str(stats["dataset_versions"]))
        table.add_row("Runs", str(stats["runs"]))
        table.add_row("Models", str(stats["models"]))
        table.add_row("Model Versions", str(stats["model_versions"]))

        console.print(table)

        # Recent activity
        runs = indexer.index["runs"]
        if runs:
            console.print("\n🕐 Recent Runs:", style="bold")
            recent_runs = sorted(runs.items(), reverse=True)[:5]

            for run_id, run_data in recent_runs:
                config = run_data.get("config", {})
                experiment = config.get("experiment", "Unknown")
                console.print(f"  • {run_id} - {experiment}")


if __name__ == "__main__":
    main()
