"""Tests for tools/doctor.py"""

import sys
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.doctor import RepositoryDoctor


class TestRepositoryDoctor:
    """Test the RepositoryDoctor class"""

    def test_init_default(self):
        """Test default initialization"""
        doctor = RepositoryDoctor()
        assert doctor.strict is False
        assert doctor.json_output is False
        assert doctor.warnings == []
        assert doctor.errors == []

    def test_init_with_options(self):
        """Test initialization with options"""
        doctor = RepositoryDoctor(strict=True, json_output=True)
        assert doctor.strict is True
        assert doctor.json_output is True

    def test_validate_required_directory_success(self):
        """Test successful directory validation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doctor = RepositoryDoctor()
            tmpdir_path = Path(tmpdir) / "test_dir"
            tmpdir_path.mkdir()

            result = doctor._validate_required_directory(tmpdir_path, "Test Directory")
            assert result is True
            assert len(doctor.errors) == 0

    def test_validate_required_directory_missing(self):
        """Test validation of missing directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doctor = RepositoryDoctor()
            missing_path = Path(tmpdir) / "missing_dir"

            result = doctor._validate_required_directory(
                missing_path, "Missing Directory"
            )
            assert result is False
            assert len(doctor.errors) == 1
            assert "Required directory missing" in doctor.errors[0]

    def test_validate_required_directory_not_directory(self):
        """Test validation when path exists but is not directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doctor = RepositoryDoctor()
            file_path = Path(tmpdir) / "not_a_dir.txt"
            file_path.write_text("test content")

            result = doctor._validate_required_directory(file_path, "Not a Directory")
            assert result is False
            assert len(doctor.errors) == 1
            assert "not a directory" in doctor.errors[0]

    @patch("subprocess.run")
    def test_validate_git_lfs_success(self, mock_run):
        """Test successful Git LFS validation"""
        # Mock git lfs version command
        mock_run.return_value = MagicMock(stdout="git-lfs/2.13.0", returncode=0)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock .gitattributes with LFS rules
            gitattributes_path = Path(tmpdir) / ".gitattributes"
            gitattributes_path.write_text("*.pth filter=lfs diff=lfs merge=lfs -text")

            doctor = RepositoryDoctor()
            doctor.project_root = Path(tmpdir)

            result = doctor.validate_git_lfs_setup()
            assert result is True

    @patch("subprocess.run")
    def test_validate_git_lfs_not_installed(self, mock_run):
        """Test Git LFS validation when not installed"""
        mock_run.side_effect = FileNotFoundError("git lfs not found")

        doctor = RepositoryDoctor()
        result = doctor.validate_git_lfs_setup()
        assert result is False
        assert len(doctor.errors) == 1
        assert "Git LFS is not installed" in doctor.errors[0]

    def test_exit_with_code_success(self):
        """Test exit code for successful validation"""
        doctor = RepositoryDoctor()
        result = doctor.exit_with_code(True)
        assert result == 0

    def test_exit_with_code_warnings_only(self):
        """Test exit code for warnings only"""
        doctor = RepositoryDoctor(strict=False)
        doctor.warnings.append("Test warning")
        result = doctor.exit_with_code(False)
        assert result == 1

    def test_exit_with_code_errors(self):
        """Test exit code for errors"""
        doctor = RepositoryDoctor(strict=False)
        doctor.errors.append("Test error")
        result = doctor.exit_with_code(False)
        assert result == 2

    def test_exit_with_code_warnings_strict(self):
        """Test exit code when strict mode treats warnings as errors"""
        doctor = RepositoryDoctor(strict=True)
        doctor.warnings.append("Test warning")
        result = doctor.exit_with_code(False)
        assert result == 2

    def test_format_output_json(self):
        """Test JSON output format"""
        doctor = RepositoryDoctor(json_output=True)
        doctor.errors.append("Test error")
        doctor.warnings.append("Test warning")
        doctor.validation_results = {"tfc_0001": True}

        output = doctor.format_output(False)
        parsed = json.loads(output)

        assert parsed["success"] is False
        assert parsed["errors"] == ["Test error"]
        assert parsed["warnings"] == ["Test warning"]
        assert parsed["validation_results"]["tfc_0001"] is True

    def test_validate_tfc_0002_schemas_missing_template(self):
        """Test TFC-0002 validation with missing template"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doctor = RepositoryDoctor()
            doctor.project_root = Path(tmpdir)

            # Create configs directory but no templates
            configs_path = Path(tmpdir) / "configs" / "datasets"
            configs_path.mkdir(parents=True)

            result = doctor.validate_tfc_0002_schemas()
            assert result is False
            assert "Missing configuration template" in doctor.errors[0]

    def test_validate_tfc_0002_schemas_invalid_yaml(self):
        """Test TFC-0002 validation with invalid YAML"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doctor = RepositoryDoctor()
            doctor.project_root = Path(tmpdir)

            # Create configs directory with invalid YAML
            configs_path = Path(tmpdir) / "configs" / "datasets"
            configs_path.mkdir(parents=True)

            template_path = configs_path / "base.yaml"
            template_path.write_text("invalid: yaml: content: [")

            result = doctor.validate_tfc_0002_schemas()
            assert result is False
            assert any("Invalid YAML" in error for error in doctor.errors)

    def test_validate_all_tfc_specific(self):
        """Test validating a specific TFC"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doctor = RepositoryDoctor()
            doctor.project_root = Path(tmpdir)

            # Mock successful TFC-0001 validation and ensure it sets result
            def mock_validate_tfc_0001():
                doctor.validation_results["tfc_0001"] = True
                return True

            with patch.object(
                doctor, "validate_tfc_0001_layout", side_effect=mock_validate_tfc_0001
            ):
                result = doctor.validate_all_tfc(target_tfc=1)
                assert result is True
                assert doctor.validation_results["tfc_0001"] is True

    def test_validate_all_tfc_unknown(self):
        """Test validating unknown TFC number"""
        doctor = RepositoryDoctor()
        result = doctor.validate_all_tfc(target_tfc=999)
        assert result is False
        assert "Unknown TFC number" in doctor.errors[0]
