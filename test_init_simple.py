#!/usr/bin/env python3
"""Simple test to show init functionality works"""

import subprocess
import sys
from pathlib import Path


def test_init_functionality():
    """Test that init tool can be called and works"""
    project_root = Path(__file__).parent.parent
    init_script = project_root / "tools" / "init.py"

    print("🧪 Testing strataml init functionality...")

    # Test 1: Help works
    print("1. Testing help command:")
    result = subprocess.run(
        [sys.executable, str(init_script), "--help"], capture_output=True, text=True
    )
    if result.returncode == 0 and "Initialize clean workspace" in result.stdout:
        print("✅ Help command works")
    else:
        print("❌ Help command failed")
        return False

    # Test 2: Dry run with --keep-examples
    print("2. Testing with --keep-examples flag:")
    # Create a test directory structure
    test_data_dir = project_root / "test_data_temp"
    test_data_dir.mkdir(exist_ok=True)
    (test_data_dir / "example.txt").write_text("test")

    # Temporarily rename test_data to data for init to clean up
    data_dir = project_root / "data"
    if data_dir.exists():
        data_dir.rename(project_root / "data_backup")

    test_data_dir.rename(project_root / "data")

    result = subprocess.run(
        [sys.executable, str(init_script), "--keep-examples", "--yes"],
        capture_output=True,
        text=True,
        input="y\n",
    )

    if result.returncode == 0 and "Successfully" in result.stdout:
        print("✅ Init with keep-examples works")
    else:
        print(f"❌ Init failed: {result.stderr}")
        return False

    # Test 3: Verify essential directories were recreated
    print("3. Verifying essential directories:")
    essential_dirs = ["datasets", "models", "runs"]
    for dir_name in essential_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists() and (dir_path / "README.md").exists():
            print(f"✅ {dir_name}/ directory recreated")
        else:
            print(f"❌ {dir_name}/ directory missing or incomplete")
            return False

    # Cleanup test files
    for dir_name in essential_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            import shutil

            shutil.rmtree(dir_path)

    # Restore original data if it existed
    backup_dir = project_root / "data_backup"
    if backup_dir.exists():
        backup_dir.rename(project_root / "data")

    print("✅ All init functionality tests passed!")
    return True


if __name__ == "__main__":
    success = test_init_functionality()
    sys.exit(0 if success else 1)
