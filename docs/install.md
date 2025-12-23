# ProjectStrataML Installation Guide

**Complete setup for forking ProjectStrataML on bare metal Debian**

---

## 📋 Prerequisites

### System Requirements
- **OS**: Debian 11+ (Bullseye) or Debian 12+ (Bookworm)
- **CPU**: 2+ cores minimum, 4+ cores recommended
- **RAM**: 8GB minimum, 16GB+ recommended
- **Storage**: 50GB free minimum, 100GB+ recommended
- **GPU**: Optional, NVIDIA with 8GB+ VRAM and CUDA 11.8+ support

### Hardware Check
```bash
# Check CPU cores
nproc

# Check RAM
free -h

# Check disk space
df -h

# Check GPU (optional)
nvidia-smi  # If NVIDIA GPU present
```

---

## 🔄 Step 1: Fork Repository

### 1.1 Fork on Git Platform
1. Navigate to your Git platform (GitHub, GitLab, etc.)
2. Fork the original ProjectStrataML repository
3. Copy your fork's clone URL

### 1.2 Clone Your Fork
```bash
# Replace with your fork URL
git clone https://github.com/yourusername/ProjectStrataML.git
cd ProjectStrataML

# Add upstream remote (optional but recommended)
git remote add upstream https://github.com/original/ProjectStrataML.git
```

### 1.3 Verify Repository
```bash
# Check repository structure
ls -la

# Verify TFC documents
ls -la docs/TFC/

# Check for required files
ls -la requirements*.txt environments/ tools/
```

---

## 🐧 Step 2: System Dependencies

### 2.1 Update System Packages
```bash
# Update package lists
sudo apt-get update

# Upgrade existing packages
sudo apt-get upgrade -y
```

### 2.2 Install Required System Packages
```bash
# Install core dependencies
sudo apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    git-lfs \
    curl \
    wget \
    build-essential \
    ca-certificates
```

### 2.3 Verify Installations
```bash
# Check Git version (should be >= 2.30)
git --version

# Check Python version (should be >= 3.11)
python3 --version

# Check pip
pip3 --version

# Verify Git LFS
git lfs version
```

### 2.4 Configure Git LFS
```bash
# Initialize Git LFS
git lfs install

# Verify LFS hooks
git lfs env
```

---

## 🐍 Step 3: Python Virtual Environment

### 3.1 Create Virtual Environment
```bash
# Create .venv directory
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Verify activation (should show (.venv) in prompt)
which python
python --version
```

### 3.2 Upgrade Pip in Virtual Environment
```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Verify new pip version
pip --version
```

### 3.3 Set Environment Variables (Optional)
```bash
# Add to ~/.bashrc for persistence
echo 'export PYTHONPATH="${PYTHONPATH}:$(pwd)"' >> ~/.bashrc
echo 'export PATH="$(pwd)/.venv/bin:$PATH"' >> ~/.bashrc

# Reload shell configuration
source ~/.bashrc
```

---

## 📦 Step 4: Install Python Dependencies

### 4.1 Install Core Dependencies
```bash
# Install core ML and framework dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 4.2 Verify Core Installation
```bash
# Test critical imports
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
python -c "import pandas; print(f'Pandas: {pandas.__version__}')"
python -c "import yaml; print('YAML: OK')"
python -c "import click; print('Click: OK')"
python -c "from rich.console import Console; print('Rich: OK')"
```

### 4.3 Install GPU Dependencies (Optional)
```bash
# Check if NVIDIA GPU is available
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected, installing GPU dependencies..."
    pip install -r requirements-gpu.txt
    
    # Verify GPU support
    python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
    if python -c "import torch; torch.cuda.is_available()"; then
        echo "✅ GPU support configured successfully"
    else
        echo "⚠️  GPU packages installed but CUDA not available"
    fi
else
    echo "ℹ️  No NVIDIA GPU detected, skipping GPU dependencies"
fi
```

---

## 🎯 Step 5: Environment Validation

### 5.1 Run Environment Validation
```bash
# Validate basic environment
python tools/setup.py --validate

# Validate with GPU support (if installed)
python tools/setup.py --validate-gpu

# Verify requirements file hashes
python tools/setup.py --verify-hashes
```

### 5.2 Expected Validation Output
```
🔍 ProjectStrataML Environment Validation

✅ Python version: 3.11.6
✅ Virtual environment: /path/to/.venv
✅ Git: git version 2.40.0
✅ Git LFS: git-lfs version 3.4.0
✅ Package installed: torch
✅ Package installed: numpy
... (more packages)

🎉 Environment validation passed!
```

### 5.3 Troubleshooting Validation Issues
```bash
# If Python version error
echo "Install Python 3.11+ first:"
echo "sudo apt-get install python3.11 python3.11-venv"

# If virtual environment error
echo "Activate virtual environment:"
echo "source .venv/bin/activate"

# If missing packages
echo "Install requirements:"
echo "pip install -r requirements.txt"
```

---

## 🛠️ Step 6: Development Tools Setup

### 6.1 Set Up Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

### 6.2 Configure Development Environment
```bash
# Set up code formatting (optional)
echo 'export BLACK_LINE_LENGTH=88' >> ~/.bashrc
echo 'export ISORT_PROFILE=black' >> ~/.bashrc

# Set environment variables for ProjectStrataML
echo 'export STRATAML_ENV=development' >> ~/.bashrc
echo 'export STRATAML_CONFIG_PATH=$(pwd)/environments' >> ~/.bashrc

# Reload configuration
source ~/.bashrc
```

### 6.3 Test Development Tools
```bash
# Test code formatting
black --version
isort --version
flake8 --version
mypy --version

# Format sample code
echo 'def test():pass' > test.py
black test.py
isort test.py
rm test.py
```

---

## 🎮 Step 7: First Run (Optional)

### 7.1 Create Test Configuration
```bash
# Create a simple test experiment
mkdir -p experiments
cat > experiments/test-setup.yaml << EOF
name: "test-setup"
description: "Test installation and environment setup"

dataset:
  name: "test-dataset"
  version: "v1"

model:
  name: "test-model"
  architecture: "simple"

training:
  epochs: 1
  batch_size: 32
  learning_rate: 0.001
EOF
```

### 7.2 Test Framework Functionality
```bash
# Test validation tools (if implemented)
if [ -f "tools/doctor.py" ]; then
    python tools/doctor.py --strict
else
    echo "ℹ️  Doctor tool not yet implemented"
fi

# Test environment validation one more time
python tools/setup.py --validate
```

---

## 🔧 Step 8: GPU Setup (Optional)

### 8.1 Install NVIDIA Drivers (Debian)
```bash
# Add NVIDIA repository
wget https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update

# Install NVIDIA driver
sudo apt-get install -y nvidia-driver-535

# Reboot system
sudo reboot
```

### 8.2 Install CUDA Toolkit
```bash
# Install CUDA toolkit
sudo apt-get install -y cuda-toolkit-12-2

# Set up environment variables
echo 'export PATH=/usr/local/cuda-12.2/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc

# Reload configuration
source ~/.bashrc

# Verify CUDA installation
nvcc --version
```

### 8.3 Verify GPU Integration
```bash
# Check NVIDIA driver
nvidia-smi

# Test PyTorch CUDA integration
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
    print(f'GPU name: {torch.cuda.get_device_name(0)}')
"
```

---

## 🎯 Step 9: Final Validation

### 9.1 Complete System Check
```bash
# Create comprehensive validation script
cat > validate-install.sh << 'EOF'
#!/bin/bash

echo "🔍 ProjectStrataML Installation Validation"
echo "=========================================="

# Check repository
if [ -d "docs/TFC" ] && [ -f "requirements.txt" ]; then
    echo "✅ Repository structure OK"
else
    echo "❌ Repository structure issue"
    exit 1
fi

# Check virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "❌ Virtual environment not active"
    exit 1
fi

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2)
if [[ $(echo "$python_version >= 3.11" | bc -l) -eq 1 ]]; then
    echo "✅ Python version: $python_version"
else
    echo "❌ Python version too old: $python_version"
    exit 1
fi

# Check dependencies
if python -c "import torch,yaml,click" 2>/dev/null; then
    echo "✅ Core dependencies installed"
else
    echo "❌ Core dependencies missing"
    exit 1
fi

# Check tools
if [ -f "tools/setup.py" ]; then
    if python tools/setup.py --validate >/dev/null 2>&1; then
        echo "✅ Environment validation passes"
    else
        echo "❌ Environment validation fails"
        python tools/setup.py --validate
        exit 1
    fi
else
    echo "❌ Tools missing"
    exit 1
fi

echo "=========================================="
echo "🎉 Installation validation successful!"
echo "You're ready to use ProjectStrataML!"
EOF

# Make script executable and run
chmod +x validate-install.sh
./validate-install.sh
```

### 9.2 Expected Final Output
```
🔍 ProjectStrataML Installation Validation
==========================================
✅ Repository structure OK
✅ Virtual environment active: /path/to/.venv
✅ Python version: 3.11.6
✅ Core dependencies installed
✅ Environment validation passes
==========================================
🎉 Installation validation successful!
You're ready to use ProjectStrataML!
```

---

## 🔄 Step 10: Ongoing Maintenance

### 10.1 Keeping Dependencies Updated
```bash
# Update requirements
pip install --upgrade -r requirements.txt
pip install --upgrade -r requirements-dev.txt

# Check for security updates
pip audit

# Update virtual environment if needed
python -m venv --upgrade .venv
```

### 10.2 Syncing with Upstream
```bash
# If you added upstream remote
git fetch upstream
git merge upstream/main

# Resolve any conflicts and push to your fork
git push origin main
```

### 10.3 Regular Validation
```bash
# Run environment validation before development
python tools/setup.py --validate

# Run doctor for full repository validation (when implemented)
python tools/doctor.py --strict

# Run pre-commit checks
pre-commit run --all-files
```

---

## 🆘 Troubleshooting

### Common Issues and Solutions

#### Python Version Issues
```bash
# Issue: Python version < 3.11
# Solution: Install Python 3.11+
sudo apt-get install python3.11 python3.11-venv python3.11-dev

# Rebuild virtual environment
rm -rf .venv
python3.11 -m venv .venv
```

#### Git LFS Issues
```bash
# Issue: Git LFS not working
# Solution: Reinitialize Git LFS
git lfs uninstall
git lfs install
git lfs pull
```

#### Permission Issues
```bash
# Issue: Permission denied
# Solution: Fix ownership of project directory
sudo chown -R $USER:$USER /path/to/ProjectStrataML
```

#### Memory Issues
```bash
# Issue: Out of memory during installation
# Solution: Create swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## ✅ Installation Complete!

Your ProjectStrataML development environment is now ready for:

- 🧪 **Experiment Development**: Create and run ML experiments
- 📊 **Dataset Management**: Version and track datasets
- 🤖 **Model Development**: Train and version models
- 📋 **Validation**: Ensure repository compliance
- 🎯 **Reproducibility**: Maintain reproducible ML workflows

### Next Steps
1. Read the **TFC documents** in `docs/TFC/` to understand the framework
2. Create your first **experiment** in `experiments/`
3. Start developing with **confidence** in your validated environment

---

**Welcome to ProjectStrataML!** 🚀

*For ongoing support and documentation, see the README.md and TFC documents in docs/TFC/.*