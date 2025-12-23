"""Tests for tools/index.py"""

import sys
import pytest
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.index import WorkspaceIndexer


class TestWorkspaceIndexer:
    """Test WorkspaceIndexer class"""

    def test_init_default(self):
        """Test default initialization"""
        indexer = WorkspaceIndexer()
        assert indexer.project_root.exists()
        assert isinstance(indexer.index, dict)
        assert "datasets" in indexer.index
        assert "runs" in indexer.index
        assert "models" in indexer.index
        assert "lineage" in indexer.index
        assert "metadata" in indexer.index

    def test_init_custom_project_root(self):
        """Test initialization with custom project root"""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_root = Path(tmpdir)
            indexer = WorkspaceIndexer(project_root=custom_root)
            assert indexer.project_root == custom_root

    def test_load_yaml_file_success(self):
        """Test successful YAML file loading"""
        with tempfile.TemporaryDirectory() as tmpdir:
            indexer = WorkspaceIndexer()

            test_file = Path(tmpdir) / "test.yaml"
            test_content = {"name": "test", "version": "v1"}
            test_file.write_text(yaml.dump(test_content))

            result = indexer._load_yaml_file(test_file)
            assert result == test_content

    def test_load_yaml_file_missing(self):
        """Test loading missing YAML file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            indexer = WorkspaceIndexer()
            missing_file = Path(tmpdir) / "missing.yaml"

            result = indexer._load_yaml_file(missing_file)
            assert result == {}

    def test_load_yaml_file_invalid(self):
        """Test loading invalid YAML file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            indexer = WorkspaceIndexer()

            test_file = Path(tmpdir) / "invalid.yaml"
            test_file.write_text("invalid: yaml: content: [")

            result = indexer._load_yaml_file(test_file)
            assert result == {}

    def test_load_json_file_success(self):
        """Test successful JSON file loading"""
        with tempfile.TemporaryDirectory() as tmpdir:
            indexer = WorkspaceIndexer()

            test_file = Path(tmpdir) / "test.json"
            test_content = {"name": "test", "metrics": {"accuracy": 0.9}}
            test_file.write_text(json.dumps(test_content))

            result = indexer._load_json_file(test_file)
            assert result == test_content

    def test_load_json_file_missing(self):
        """Test loading missing JSON file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            indexer = WorkspaceIndexer()
            missing_file = Path(tmpdir) / "missing.json"

            result = indexer._load_json_file(missing_file)
            assert result == {}

    def test_index_datasets_empty(self):
        """Test indexing when no datasets directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            indexer = WorkspaceIndexer(project_root=Path(tmpdir))
            indexer.index_datasets()

            assert indexer.index["datasets"] == {}

    def test_index_datasets_with_metadata(self):
        """Test indexing datasets with metadata"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory structure
            datasets_dir = Path(tmpdir) / "datasets"
            dataset_dir = datasets_dir / "test_dataset" / "v1"
            dataset_dir.mkdir(parents=True)

            # Create metadata
            metadata = {
                "name": "test_dataset",
                "version": "v1",
                "description": "Test dataset for indexing",
                "source": {"type": "synthetic", "uri": "test://data"},
                "license": "MIT",
                "hash": {"algorithm": "sha256", "value": "abc123"},
            }
            metadata_file = dataset_dir / "metadata.yaml"
            metadata_file.write_text(yaml.dump(metadata))

            # Create split directories
            for split in ["train", "val", "test"]:
                split_dir = dataset_dir / split
                split_dir.mkdir()
                # Add sample files
                (split_dir / f"sample_{split}1.txt").write_text("sample data")
                (split_dir / f"sample_{split}2.txt").write_text("sample data")

            indexer = WorkspaceIndexer(project_root=Path(tmpdir))
            indexer.index_datasets()

            assert "test_dataset" in indexer.index["datasets"]
            assert "v1" in indexer.index["datasets"]["test_dataset"]

            dataset_info = indexer.index["datasets"]["test_dataset"]["v1"]
            assert dataset_info["metadata"] == metadata
            assert dataset_info["sample_counts"]["train"] == 2
            assert dataset_info["sample_counts"]["val"] == 2
            assert dataset_info["sample_counts"]["test"] == 2

    def test_index_runs_empty(self):
        """Test indexing when no runs directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            indexer = WorkspaceIndexer(project_root=Path(tmpdir))
            indexer.index_runs()

            assert indexer.index["runs"] == {}

    def test_index_runs_with_artifacts(self):
        """Test indexing runs with artifacts"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create run directory
            run_dir = Path(tmpdir) / "runs" / "run-2023-12-01-001"
            run_dir.mkdir(parents=True)

            # Create run artifacts
            config = {
                "run_id": "run-2023-12-01-001",
                "experiment": "test_experiment",
                "model": "test_model",
                "dataset": "test_dataset",
            }
            config_file = run_dir / "config.yaml"
            config_file.write_text(yaml.dump(config))

            metrics = {
                "summary": {"accuracy": 0.95, "loss": 0.1},
                "history": [{"step": 1, "value": 0.8}, {"step": 2, "value": 0.9}],
            }
            metrics_file = run_dir / "metrics.json"
            metrics_file.write_text(json.dumps(metrics))

            system = {
                "os": "Linux",
                "python": "3.11.0",
                "frameworks": {"torch": "2.0.0"},
            }
            system_file = run_dir / "system.json"
            system_file.write_text(json.dumps(system))

            log_file = run_dir / "log.txt"
            log_file.write_text("Training log content...")

            indexer = WorkspaceIndexer(project_root=Path(tmpdir))
            indexer.index_runs()

            assert "run-2023-12-01-001" in indexer.index["runs"]

            run_info = indexer.index["runs"]["run-2023-12-01-001"]
            assert run_info["config"] == config
            assert run_info["metrics"] == metrics
            assert run_info["system"] == system
            assert "Training log" in run_info["log_preview"]

    def test_index_models_empty(self):
        """Test indexing when no models directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            indexer = WorkspaceIndexer(project_root=Path(tmpdir))
            indexer.index_models()

            assert indexer.index["models"] == {}

    def test_index_models_with_artifacts(self):
        """Test indexing models with artifacts"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create model directory
            model_dir = Path(tmpdir) / "models" / "test_model" / "v1"
            model_dir.mkdir(parents=True)

            # Create model artifacts
            metadata = {
                "name": "test_model",
                "version": "v1",
                "run_id": "run-2023-12-01-001",
                "dataset": {"name": "test_dataset", "version": "v1"},
                "code": {"repo": "test_repo", "commit": "abc123"},
                "framework": "pytorch",
            }
            metadata_file = model_dir / "metadata.yaml"
            metadata_file.write_text(yaml.dump(metadata))

            metrics = {
                "primary_metric": {"name": "accuracy", "value": 0.95},
                "secondary_metrics": {"precision": 0.93, "recall": 0.92},
            }
            metrics_file = model_dir / "metrics.yaml"
            metrics_file.write_text(yaml.dump(metrics))

            card_file = model_dir / "card.md"
            card_file.write_text(
                "# Test Model Card\n\nThis is a test model with good performance."
            )

            model_file = model_dir / "model.pth"
            model_file.write_text("fake model data")

            indexer = WorkspaceIndexer(project_root=Path(tmpdir))
            indexer.index_models()

            assert "test_model" in indexer.index["models"]
            assert "v1" in indexer.index["models"]["test_model"]

            model_info = indexer.index["models"]["test_model"]["v1"]
            assert model_info["metadata"] == metadata
            assert model_info["metrics"] == metrics
            assert "Test Model Card" in model_info["card_preview"]
            assert len(model_info["model_files"]) == 1
            assert model_info["model_files"][0]["name"] == "model.pth"

    def test_build_lineage(self):
        """Test lineage building"""
        with tempfile.TemporaryDirectory() as tmpdir:
            indexer = WorkspaceIndexer(project_root=Path(tmpdir))

            # Set up mock indexed data
            indexer.index["runs"] = {
                "run-2023-12-01-001": {
                    "config": {
                        "experiment": "test_exp",
                        "model": "test_model",
                        "dataset": "test_dataset",
                    }
                }
            }

            indexer.index["models"] = {
                "test_model": {
                    "v1": {
                        "metadata": {
                            "run_id": "run-2023-12-01-001",
                            "dataset": {"name": "test_dataset"},
                        }
                    }
                }
            }

            indexer.index["datasets"] = {
                "test_dataset": {
                    "v1": {
                        "metadata": {
                            "source": {"type": "synthetic", "uri": "test://data"}
                        }
                    }
                }
            }

            indexer.build_lineage()

            lineage = indexer.index["lineage"]
            assert "run-2023-12-01-001" in lineage
            assert lineage["run-2023-12-01-001"]["type"] == "run"
            assert lineage["run-2023-12-01-001"]["model"] == "test_model"

            assert "test_model/v1" in lineage
            assert lineage["test_model/v1"]["type"] == "model"
            assert lineage["test_model/v1"]["run_id"] == "run-2023-12-01-001"

            assert "test_dataset/v1" in lineage
            assert lineage["test_dataset/v1"]["type"] == "dataset"

    def test_get_summary_stats(self):
        """Test summary statistics calculation"""
        indexer = WorkspaceIndexer()

        # Set up mock data
        indexer.index = {
            "datasets": {"dataset1": {"v1": {}, "v2": {}}, "dataset2": {"v1": {}}},
            "runs": {"run-001": {}, "run-002": {}, "run-003": {}},
            "models": {"model1": {"v1": {}}, "model2": {"v1": {}, "v2": {}}},
        }

        stats = indexer.get_summary_stats()

        assert stats["datasets"] == 2
        assert stats["dataset_versions"] == 3
        assert stats["runs"] == 3
        assert stats["models"] == 2
        assert stats["model_versions"] == 3

    def test_index_all_integration(self):
        """Test full indexing integration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal directory structure
            root = Path(tmpdir)
            (root / "datasets").mkdir()
            (root / "runs").mkdir()
            (root / "models").mkdir()

            indexer = WorkspaceIndexer(project_root=root)
            result = indexer.index_all()

            assert isinstance(result, dict)
            assert "datasets" in result
            assert "runs" in result
            assert "models" in result
            assert "lineage" in result
            assert "metadata" in result
