"""Tests for tools/init.py"""

import sys
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import shutil


class TestInitTool:
    """Test init tool functionality"""

    def setup_method(self):
        """Set up test environment"""
        # Import init module
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "init", Path(__file__).parent.parent / "tools" / "init.py"
        )
        self.init_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.init_module)

    def test_init_help(self):
        """Test that help shows correct options"""
        with patch("sys.argv", ["init.py", "--help"]):
            with pytest.raises(SystemExit):
                self.init_module.init()

    @patch("shutil.rmtree")
    @patch("shutil.Path.mkdir")
    @patch("shutil.Path.exists")
    @patch("shutil.Path.iterdir")
    @patch("shutil.Path.unlink")
    def test_init_remove_directories(
        self, mock_unlink, mock_iterdir, mock_exists, mock_mkdir, mock_rmtree
    ):
        """Test directory removal functionality"""
        # Mock existing directories
        mock_exists.return_value = True

        # Mock items in runs directory (keep example runs)
        def mock_iterdir_func():
            class MockItem:
                def __init__(self, name):
                    self.name = name

                def is_dir(self):
                    return True

            return [MockItem("run-example-001")]

        mock_iterdir.side_effect = mock_iterdir_func

        # Mock click confirmation
        with patch("click.confirmation_option", return_value=lambda f: f):
            # Test init function
            with patch("click.command", return_value=lambda f: f):
                with patch("rich.console.Console.print"):
                    self.init_module.init(keep_examples=False, keep_docs=False)

        # Verify rmtree was called for main directories
        expected_calls = ["data", "datasets", "models", "runs"]
        for call in mock_rmtree.call_args_list:
            path = call[0][0]
            if isinstance(path, Path) and path.name in expected_calls:
                expected_calls.remove(path.name)

        assert len(expected_calls) == 0, (
            f"Expected directories not removed: {expected_calls}"
        )

    @patch("shutil.rmtree")
    @patch("shutil.Path.mkdir")
    @patch("shutil.Path.exists")
    def test_init_recreate_directories(self, mock_exists, mock_mkdir, mock_rmtree):
        """Test directory recreation"""

        # Mock directories don't exist for recreation phase
        def mock_exists_func(path):
            if path.name in ["datasets", "models", "runs", "data"]:
                return False
            return True

        mock_exists.side_effect = mock_exists_func

        # Mock click confirmation
        with patch("click.confirmation_option", return_value=lambda f: f):
            with patch("click.command", return_value=lambda f: f):
                with patch("rich.console.Console.print"):
                    self.init_module.init(keep_examples=False, keep_docs=False)

        # Verify mkdir was called for essential directories
        essential_dirs = ["datasets", "models", "runs", "data"]
        mkdir_calls = [call[0][0].name for call in mock_mkdir.call_args_list]

        for dir_name in essential_dirs:
            assert dir_name in mkdir_calls, f"Directory {dir_name} not recreated"

    @patch("shutil.rmtree")
    @patch("shutil.Path.unlink")
    @patch("shutil.Path.glob")
    def test_init_remove_cache_files(self, mock_glob, mock_unlink, mock_rmtree):
        """Test cache file removal"""

        # Mock cache files
        def mock_glob_func(pattern):
            class MockPath:
                def __init__(self, name):
                    self.name = name

                    def is_file(self):
                        return True

                    def is_dir(self):
                        return False

                if pattern == "**/__pycache__":
                    return [MockPath("__pycache__")]
                elif pattern == ".pytest_cache":
                    return [MockPath(".pytest_cache")]
                return []

        mock_glob.side_effect = mock_glob_func

        # Mock click confirmation
        with patch("click.confirmation_option", return_value=lambda f: f):
            with patch("click.command", return_value=lambda f: f):
                with patch("rich.console.Console.print"):
                    self.init_module.init(keep_examples=False, keep_docs=False)

        # Verify unlink was called for cache files
        assert mock_unlink.called, "Cache files not removed"

    @patch("shutil.rmtree")
    @patch("shutil.Path.mkdir")
    @patch("shutil.Path.exists")
    def test_init_keep_examples(self, mock_exists, mock_mkdir, mock_rmtree):
        """Test keeping examples flag"""
        # Mock all directories exist
        mock_exists.return_value = True

        # Mock click confirmation with keep_examples=True
        with patch("click.confirmation_option", return_value=lambda f: f):
            with patch("click.command", return_value=lambda f: f):
                with patch("rich.console.Console.print"):
                    self.init_module.init(keep_examples=True, keep_docs=False)

        # Verify rmtree was NOT called for main directories
        rmtree_calls = [
            call[0][0].name for call in mock_rmtree.call_args_list if len(call[0]) > 0
        ]
        main_dirs = ["data", "datasets", "models", "runs"]

        for dir_name in main_dirs:
            assert dir_name not in rmtree_calls, (
                f"Directory {dir_name} should be kept but was removed"
            )

    def test_init_error_handling(self):
        """Test error handling during init"""
        # Mock an exception during directory removal
        with patch("shutil.rmtree", side_effect=Exception("Permission denied")):
            with patch("click.confirmation_option", return_value=lambda f: f):
                with patch("click.command", return_value=lambda f: f):
                    with patch("rich.console.Console.print"):
                        with pytest.raises(Exception):
                            self.init_module.init(keep_examples=False, keep_docs=False)

    def test_init_readme_creation(self):
        """Test README file creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test directory structure
            datasets_dir = Path(tmpdir) / "datasets"
            datasets_dir.mkdir()

            # Mock project root and essential directories
            with patch("Path.__new__", return_value=Path(tmpdir)):
                with patch("shutil.Path.exists", return_value=False):
                    with patch("click.confirmation_option", return_value=lambda f: f):
                        with patch("click.command", return_value=lambda f: f):
                            with patch("rich.console.Console.print"):
                                self.init_module.init(
                                    keep_examples=False, keep_docs=False
                                )

            # Check README was created
            readme_file = datasets_dir / "README.md"
            assert readme_file.exists(), "README.md not created in datasets directory"

            # Check README content
            content = readme_file.read_text()
            assert "Datasets" in content, "README content incorrect"
