"""Tests for tools/strataml.py"""

import sys
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from click.testing import CliRunner


class TestStratamlCLI:
    """Test strataml CLI commands"""

    def setup_method(self):
        """Set up test runner"""
        # Import the main CLI function
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "strataml", Path(__file__).parent.parent / "tools" / "strataml.py"
        )
        strataml_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(strataml_module)

        self.runner = CliRunner()
        self.strataml = strataml_module.main

    @patch("tools.strataml.RepositoryDoctor")
    def test_doctor_command_success(self, mock_doctor_class):
        """Test doctor command with successful validation"""
        # Mock doctor instance
        mock_doctor = MagicMock()
        mock_doctor_class.return_value = mock_doctor
        mock_doctor.validate_all_tfc.return_value = True
        mock_doctor.errors = []
        mock_doctor.warnings = []
        mock_doctor.validation_results = {"tfc_0001": True}
        mock_doctor.exit_with_code.return_value = 0

        result = self.runner.invoke(self.strataml, ["doctor"])

        assert result.exit_code == 0
        mock_doctor.validate_all_tfc.assert_called_once()
        mock_doctor.format_output.assert_called_once()

    @patch("tools.strataml.RepositoryDoctor")
    def test_doctor_command_strict(self, mock_doctor_class):
        """Test doctor command with strict flag"""
        mock_doctor = MagicMock()
        mock_doctor_class.return_value = mock_doctor
        mock_doctor.validate_all_tfc.return_value = True
        mock_doctor.errors = []
        mock_doctor.warnings = []
        mock_doctor.validation_results = {"tfc_0001": True}
        mock_doctor.exit_with_code.return_value = 0

        result = self.runner.invoke(self.strataml, ["doctor", "--strict"])

        assert result.exit_code == 0
        mock_doctor_class.assert_called_once_with(strict=True, json_output=False)

    @patch("tools.strataml.RepositoryDoctor")
    def test_doctor_command_json(self, mock_doctor_class):
        """Test doctor command with JSON output"""
        mock_doctor = MagicMock()
        mock_doctor_class.return_value = mock_doctor
        mock_doctor.validate_all_tfc.return_value = False
        mock_doctor.errors = ["Test error"]
        mock_doctor.warnings = []
        mock_doctor.validation_results = {"tfc_0001": False}
        mock_doctor.exit_with_code.return_value = 2

        result = self.runner.invoke(self.strataml, ["doctor", "--json"])

        # Should output JSON
        output_data = json.loads(result.output)
        assert "success" in output_data
        assert "errors" in output_data
        assert "warnings" in output_data
        assert "validation_results" in output_data

    @patch("tools.strataml.RepositoryDoctor")
    def test_doctor_command_specific_tfc(self, mock_doctor_class):
        """Test doctor command with specific TFC"""
        mock_doctor = MagicMock()
        mock_doctor_class.return_value = mock_doctor
        mock_doctor.validate_all_tfc.return_value = True
        mock_doctor.errors = []
        mock_doctor.warnings = []
        mock_doctor.validation_results = {"tfc_0001": True}
        mock_doctor.exit_with_code.return_value = 0

        result = self.runner.invoke(self.strataml, ["doctor", "--tfc", "1"])

        assert result.exit_code == 0
        mock_doctor.validate_all_tfc.assert_called_once_with(target_tfc=1)

    @patch("tools.strataml.WorkspaceIndexer")
    def test_index_command(self, mock_indexer_class):
        """Test index command"""
        mock_indexer = MagicMock()
        mock_indexer_class.return_value = mock_indexer
        mock_indexer.index = {"datasets": {}, "runs": {}, "models": {}}

        result = self.runner.invoke(self.strataml, ["index"])

        assert result.exit_code == 0
        mock_indexer.index_all.assert_called_once()
        mock_indexer.format_table_output.assert_called_once()

    @patch("tools.strataml.WorkspaceIndexer")
    def test_index_command_datasets_only(self, mock_indexer_class):
        """Test index command with datasets flag"""
        mock_indexer = MagicMock()
        mock_indexer_class.return_value = mock_indexer

        result = self.runner.invoke(self.strataml, ["index", "--datasets"])

        assert result.exit_code == 0
        mock_indexer.index_datasets.assert_called_once()
        mock_indexer.index_models.assert_not_called()
        mock_indexer.index_runs.assert_not_called()

    @patch("tools.strataml.WorkspaceIndexer")
    def test_list_command_datasets(self, mock_indexer_class):
        """Test list command for datasets"""
        mock_indexer = MagicMock()
        mock_indexer_class.return_value = mock_indexer
        mock_indexer.index = {"datasets": {"test_dataset": {"v1": {}}}}

        result = self.runner.invoke(self.strataml, ["list", "datasets"])

        assert result.exit_code == 0
        mock_indexer.index_datasets.assert_called_once()

    @patch("tools.strataml.WorkspaceIndexer")
    def test_list_command_runs(self, mock_indexer_class):
        """Test list command for runs"""
        mock_indexer = MagicMock()
        mock_indexer_class.return_value = mock_indexer
        mock_indexer.index = {"runs": {"run-001": {}}}

        result = self.runner.invoke(self.strataml, ["list", "runs"])

        assert result.exit_code == 0
        mock_indexer.index_runs.assert_called_once()

    @patch("tools.strataml.WorkspaceIndexer")
    def test_list_command_models(self, mock_indexer_class):
        """Test list command for models"""
        mock_indexer = MagicMock()
        mock_indexer_class.return_value = mock_indexer
        mock_indexer.index = {"models": {"test_model": {"v1": {}}}}

        result = self.runner.invoke(self.strataml, ["list", "models"])

        assert result.exit_code == 0
        mock_indexer.index_models.assert_called_once()

    @patch("tools.strataml.WorkspaceIndexer")
    def test_status_command(self, mock_indexer_class):
        """Test status command"""
        mock_indexer = MagicMock()
        mock_indexer_class.return_value = mock_indexer
        mock_indexer.get_summary_stats.return_value = {
            "datasets": 2,
            "runs": 5,
            "models": 3,
            "dataset_versions": 4,
            "model_versions": 6,
        }

        result = self.runner.invoke(self.strataml, ["status"])

        assert result.exit_code == 0
        mock_indexer.index_all.assert_called_once()
        mock_indexer.get_summary_stats.assert_called_once()

    @patch("tools.strataml.WorkspaceIndexer")
    def test_status_command_json(self, mock_indexer_class):
        """Test status command with JSON output"""
        mock_indexer = MagicMock()
        mock_indexer_class.return_value = mock_indexer
        mock_indexer.get_summary_stats.return_value = {
            "datasets": 2,
            "runs": 5,
            "models": 3,
        }

        result = self.runner.invoke(self.strataml, ["status", "--format", "json"])

        assert result.exit_code == 0
        output_data = json.loads(result.output)
        assert output_data["datasets"] == 2
        assert output_data["runs"] == 5
        assert output_data["models"] == 3

    def test_version_command(self):
        """Test version command"""
        result = self.runner.invoke(self.strataml, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    @patch(
        "tools.strataml.import", side_effect=ImportError("No module named 'fastapi'")
    )
    def test_serve_command_missing_deps(self, mock_import):
        """Test serve command when FastAPI is not installed"""
        result = self.runner.invoke(self.strataml, ["serve"])
        assert result.exit_code == 1
        assert "FastAPI not installed" in result.output
