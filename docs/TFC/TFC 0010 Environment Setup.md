# TFC-0010: Environment Setup and Dependency Management

**Status:** Draft
**Author:** James Henry (james.phenry@gmail.com)
**Created:** 2025-12-23

---

## 1. Summary

This document defines the **standard environment setup and dependency management contract** for ML projects adopting TFC-0001 through TFC-0009. It specifies Python virtual environment requirements, dependency management using `requirements.txt`, Linux system requirements, and GPU support guidelines to ensure reproducible development environments across all ProjectStrataML projects.

The contract is designed to be **strict**, **Linux-focused**, and **framework-agnostic** while maintaining compatibility with existing TFC artifact management.

---

## 2. Motivation

ML projects frequently suffer from inconsistent development environments:

* Python version mismatches across developers and CI
* Dependency conflicts between ML frameworks
* Missing system dependencies causing silent failures
* GPU support inconsistencies between development and production
* Reproducibility failures due to environment drift

This TFC establishes a **rigid environment contract** that:
* Guarantees Python version consistency
* Provides standardized dependency management
* Ensures all required system dependencies are present
* Enables optional GPU support with clear guidelines
* Allows strict validation through automated tools

---

## 3. Goals

* Define a standard Python virtual environment setup using `venv`
* Specify dependency management using `requirements.txt` files
* Establish Linux system requirements and dependencies
* Provide optional GPU support with clear installation guidelines
* Enable strict environment validation through TFC-0006 doctor tool
* Ensure reproducibility across development machines and CI

---

## 4. Non-Goals

* Supporting Windows or macOS (Linux only)
* Providing container-based environments (Docker, etc.)
* Replacing system package managers (apt, yum, etc.)
* Mandating specific ML framework versions beyond minimums
* Providing automated environment installation scripts

---

## 5. Virtual Environment Contract

### 5.1 Virtual Environment Requirements

All development MUST use Python virtual environments:

* **Tool**: `venv` (built-in Python module only)
* **Python Version**: 3.11 or higher (strict requirement)
* **Directory Name**: `.venv/` or `venv/` (recommended: `.venv/`)
* **Activation**: Standard venv activation scripts

### 5.2 Virtual Environment Structure

```
project-root/
├── .venv/                    # Virtual environment directory
│   ├── bin/
│   ├── include/
│   ├── lib/
│   └── pyvenv.cfg
├── requirements.txt          # Core dependencies
├── requirements-dev.txt      # Development dependencies
├── requirements-gpu.txt       # Optional GPU dependencies
└── tools/setup.py           # Environment validation tool
```

### 5.3 Virtual Environment Validation Rules

The following MUST be enforced:

* **ERROR**: Not using a virtual environment
* **ERROR**: Virtual environment Python version < 3.11
* **ERROR**: Virtual environment not activated during development
* **WARNING**: Virtual environment in project root (must be `.venv/` or `venv/`)

### 5.4 Activation Scripts

Standard activation MUST be used:

```bash
# For bash/zsh
source .venv/bin/activate

# For fish
source .venv/bin/activate.fish

# For csh/tcsh
source .venv/bin/activate.csh
```

---

## 6. Dependency Management Schema

### 6.1 Requirements Files Structure

Three requirements files are MANDATORY:

* `requirements.txt` - Core ML and framework dependencies
* `requirements-dev.txt` - Development and testing dependencies
* `requirements-gpu.txt` - Optional GPU-enabled dependencies

### 6.2 `requirements.txt` Schema (Core Dependencies)

Purpose: Essential ML dependencies for all ProjectStrataML projects.

```
# Core ML framework dependencies
torch>=2.0.0,<3.0.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0

# Data processing and validation
pyyaml>=6.0
tqdm>=4.65.0
jsonschema>=4.17.0

# ProjectStrataML framework dependencies
click>=8.1.0
rich>=13.0.0

# System interaction
requests>=2.31.0
```

### 6.3 `requirements-dev.txt` Schema (Development Dependencies)

Purpose: Development tools, testing, and code quality.

```
# Testing framework
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0

# Code formatting and linting
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
isort>=5.12.0

# Pre-commit hooks
pre-commit>=3.0.0

# Documentation
mkdocs>=1.5.0
mkdocs-material>=9.0.0
```

### 6.4 `requirements-gpu.txt` Schema (Optional GPU Dependencies)

Purpose: GPU-accelerated versions of core dependencies.

```
# GPU-enabled PyTorch (CUDA 11.8)
torch>=2.0.0 --index-url https://download.pytorch.org/whl/cu118
torchvision>=0.15.0 --index-url https://download.pytorch.org/whl/cu118
torchaudio>=2.0.0 --index-url https://download.pytorch.org/whl/cu118

# GPU-accelerated data processing
cupy-cuda11x>=12.0.0
```

### 6.5 Dependency Validation Rules

The following MUST be enforced:

* **ERROR**: Missing core dependencies from `requirements.txt`
* **ERROR**: Package version conflicts
* **ERROR**: Development dependencies missing in development mode
* **WARNING**: GPU available but GPU packages not installed
* **WARNING**: Package versions above maximum specified ranges

---

## 7. System Requirements Specification

### 7.1 Operating System Support

Only Linux distributions are supported:

* **Ubuntu 20.04 LTS and later**
* **RHEL 8 and later**
* **CentOS Stream 8 and later**
* **Debian 11 and later**
* **Fedora 36 and later**

Windows and macOS are explicitly **NOT SUPPORTED**.

### 7.2 Hardware Requirements

#### Minimum Hardware
* **RAM**: 8GB
* **Storage**: 50GB free disk space
* **CPU**: 2+ cores (x86-64 architecture)

#### Recommended Hardware
* **RAM**: 16GB
* **Storage**: 100GB free disk space (SSD recommended)
* **CPU**: 4+ cores

#### GPU Support (Optional)
* **GPU Memory**: 8GB+ (NVIDIA recommended)
* **CUDA Support**: CUDA 11.8 or later
* **Compute Capability**: 6.0+

### 7.3 System Dependencies

#### Required System Packages
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y git python3 python3-pip python3-venv git-lfs

# RHEL/CentOS/Fedora
sudo dnf install -y git python3 python3-pip git-lfs
```

#### Optional GPU System Packages
```bash
# Ubuntu/Debian
sudo apt-get install -y nvidia-driver-525 cuda-toolkit-11-8

# RHEL/CentOS/Fedora
sudo dnf install -y nvidia-driver-cuda cuda-toolkit
```

### 7.4 System Validation Rules

The following MUST be enforced:

* **ERROR**: Unsupported operating system
* **ERROR**: Python version < 3.11
* **ERROR**: git not installed or < 2.30
* **ERROR**: git-lfs not installed or < 3.0
* **WARNING**: System below minimum hardware requirements
* **WARNING**: GPU detected but CUDA not installed

---

## 8. Environment Validation Rules

### 8.1 Doctor Tool Enhancement (TFC-0006)

The repository doctor MUST be enhanced with environment validation:

```python
def validate_environment(self) -> ValidationResult:
    """Validate environment meets TFC-0010 requirements"""
    
    # Check Python version
    if sys.version_info < (3, 11):
        return ValidationError("Python 3.11+ required")
    
    # Check virtual environment
    if not in_virtual_env():
        return ValidationError("Virtual environment required")
    
    # Check system dependencies
    if not check_git_version():
        return ValidationError("Git 2.30+ required")
    
    if not check_git_lfs():
        return ValidationError("Git LFS 3.0+ required")
    
    # Check Python packages
    missing_packages = check_requirements("requirements.txt")
    if missing_packages:
        return ValidationError(f"Missing packages: {missing_packages}")
    
    return ValidationSuccess()
```

### 8.2 Validation Categories

#### Errors (MUST Fail)
* Not using a virtual environment
* Python version < 3.11
* Missing core dependencies from `requirements.txt`
* git or git-lfs not installed
* Unsupported operating system

#### Warnings (SHOULD NOT Fail)
* System below recommended hardware
* GPU available but CUDA packages not installed
* Development dependencies missing in non-CI environments
* Package versions approaching maximum limits

---

## 9. Tooling Integration

### 9.1 Environment Validation Tool (`tools/setup.py`)

Mandatory validation tool for environment compliance:

```python
#!/usr/bin/env python3
"""ProjectStrataML Environment Validation Tool"""

import sys
import subprocess
from pathlib import Path

def validate_python_version():
    """Validate Python 3.11+ requirement"""
    return sys.version_info >= (3, 11)

def validate_virtual_env():
    """Validate virtual environment usage"""
    return hasattr(sys, 'real_prefix') or hasattr(sys, 'base_prefix')

def validate_requirements(requirements_file):
    """Validate all requirements are installed"""
    # Implementation details...
    pass

def validate_system_dependencies():
    """Validate git and git-lfs availability"""
    pass

def main():
    """Main validation entry point"""
    if not all([
        validate_python_version(),
        validate_virtual_env(),
        validate_requirements("requirements.txt"),
        validate_system_dependencies()
    ]):
        sys.exit(2)  # TFC-0006 error code
    
    print("✅ Environment validation passed")

if __name__ == "__main__":
    main()
```

### 9.2 Integration with Existing Tools

#### TFC-0006 Doctor Integration
Environment validation MUST be part of doctor checks:

```bash
# Full repository validation includes environment
python tools/doctor.py --strict

# Environment-only validation
python tools/setup.py --validate
```

#### TFC-0003 Run Integration
Run execution MUST capture environment state:

```json
{
  "environment": {
    "python": "3.11.6",
    "virtual_env": ".venv",
    "requirements_hash": "sha256:...",
    "gpu_available": true,
    "cuda_version": "11.8"
  }
}
```

---

## 10. Setup and Installation Procedures

### 10.1 Initial Environment Setup

One-time setup for new developers:

```bash
# 1. Clone repository
git clone <repository-url>
cd <repository-name>

# 2. Install system dependencies
sudo apt-get update
sudo apt-get install -y git python3 python3-pip python3-venv git-lfs

# 3. Initialize Git LFS
git lfs install

# 4. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 5. Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 6. Validate environment
python tools/setup.py --validate
```

### 10.2 GPU Setup (Optional)

For GPU-enabled development:

```bash
# 1. Install system GPU dependencies
sudo apt-get install -y nvidia-driver-525 cuda-toolkit-11-8

# 2. Install GPU Python packages
pip install -r requirements-gpu.txt

# 3. Validate GPU setup
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### 10.3 Ongoing Development

Daily development workflow:

```bash
# Activate environment
source .venv/bin/activate

# Validate before starting work
python tools/setup.py --validate

# Run doctor for full validation
python tools/doctor.py --strict
```

---

## 11. Environment Metadata Capture

### 11.1 Enhanced System Schema (TFC-0002 Extension)

The `system.json` schema MUST be enhanced with environment metadata:

```json
{
  "os": "Linux 6.6",
  "python": "3.11.6",
  "environment": {
    "virtual_env": {
      "active": true,
      "path": "/path/to/.venv",
      "python_path": "/path/to/.venv/bin/python"
    },
    "requirements": {
      "core_hash": "sha256:abc123...",
      "dev_hash": "sha256:def456...",
      "gpu_installed": false
    },
    "system_packages": {
      "git": "2.40.0",
      "git_lfs": "3.4.0"
    }
  },
  "gpu": {
    "available": true,
    "driver_version": "525.60.13",
    "cuda_version": "11.8",
    "memory_gb": 8
  },
  "hardware": {
    "cpu": "AMD EPYC 7302",
    "gpus": ["RTX 3090"],
    "ram_gb": 128
  }
}
```

### 11.2 Requirements Hash Calculation

For reproducibility, requirements files MUST have SHA256 hashes:

```python
def calculate_requirements_hash(requirements_file):
    """Calculate SHA256 hash of requirements file"""
    import hashlib
    with open(requirements_file, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()
```

---

## 12. Future Compatibility

This environment contract is designed to be compatible with:

* **MLflow environments** - Similar dependency management approach
* **Conda environments** - Possible future migration path
* **Docker containers** - Can be built from requirements files
* **CI/CD systems** - Standard Linux package management
* **Cloud ML platforms** - Compatible dependency specifications

---

## 13. Open Questions

* Automatic requirements hash updates on package changes
* Integration with external package security scanning
* Support for alternative CUDA versions
* Environment drift detection and notification
* Automated dependency updates and testing

---

## 14. Appendix

### 14.1 Complete File Structure

```
project-root/
├── .gitignore                  # Updated with venv exclusions
├── requirements.txt            # Core dependencies
├── requirements-dev.txt        # Development dependencies
├── requirements-gpu.txt        # Optional GPU dependencies
├── environments/
│   └── system.yaml           # System requirements spec
├── tools/
│   ├── setup.py              # Environment validation tool
│   ├── doctor.py             # Enhanced with env validation
│   └── run.py                # Captures environment metadata
└── docs/TFC/
    └── TFC 0010 Environment Setup.md
```

### 14.2 Git Ignore Updates

The following MUST be added to `.gitignore`:

```
# Virtual environments
.venv/
venv/
ENV/
env/

# Environment files
.env
.python-version

# Package cache
__pycache__/
*.pyc
```

### 14.3 Integration Matrix

| TFC | Integration Point | Enhancement Required |
|-----|-------------------|---------------------|
| TFC-0001 | Repository layout | Add environment files |
| TFC-0002 | System schema | Add environment metadata |
| TFC-0003 | Run execution | Capture environment state |
| TFC-0005 | Model registry | Include environment metadata |
| TFC-0006 | Doctor tool | Add environment validation |
| TFC-0009 | Development workflow | Environment validation required |

### 14.4 Validation Command Reference

```bash
# Environment-only validation
python tools/setup.py --validate

# Full repository validation (includes environment)
python tools/doctor.py --strict

# GPU-specific validation (optional)
python tools/setup.py --validate-gpu

# Requirements hash verification
python tools/setup.py --verify-hashes
```

---

This TFC establishes a **rigid, reproducible, and Linux-focused** environment management system that ensures **consistent development environments** across all ProjectStrataML projects while maintaining strict validation and comprehensive integration with the existing framework.

An environment that passes TFC-0010 validation is considered **fully compliant** and ready for **production ML development** within the ProjectStrataML ecosystem.