# PGP Signing Guide for ProjectStrataML

**Complete guide for using GPG/PGP for artifact signing as defined in TFC-0008**

---

## 🔐 Overview

ProjectStrataML uses **OpenPGP/GPG signatures** to ensure artifact integrity and authenticity. This guide covers setting up GPG, signing artifacts, and verifying signatures within the framework.

### Why Use PGP Signing?
- **Integrity**: Guarantees artifacts haven't been tampered with
- **Authenticity**: Confirms creator identity
- **Reproducibility**: Ensures consistent artifact verification
- **Compliance**: Meets TFC-0008 signing requirements

---

## 🛠️ Step 1: GPG Installation and Setup

### 1.1 Install GPG on Debian
```bash
# Install GnuPG (includes gpg, gpg-agent, etc.)
sudo apt-get update
sudo apt-get install -y gnupg gnupg2 gnupg-agent

# Verify installation
gpg --version
```

### 1.2 Generate GPG Key Pair
```bash
# Generate new GPG key (RSA 4096 bit, 1 year validity)
gpg --full-generate-key

# Recommended key settings:
# Key type: RSA and RSA
# Key size: 4096 bits
# Valid for: 1y (or longer for production)
# Real name: Your Full Name
# Email: your.email@example.com
# Comment: ProjectStrataML Artifact Signing
```

### 1.3 Alternative: Generate Key with Parameters
```bash
# Generate with explicit parameters
gpg --batch --gen-key << EOF
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Expire-Date: 1y
Name-Real: Your Full Name
Name-Email: your.email@example.com
Name-Comment: ProjectStrataML Signing
EOF
```

### 1.4 List and Verify Keys
```bash
# List private keys
gpg --list-secret-keys

# List public keys  
gpg --list-public-keys

# Show key details (replace KEY_ID)
gpg --show-key --with-fingerprint KEY_ID
```

---

## 🔑 Step 2: Key Management

### 2.1 Export and Backup Keys
```bash
# Export public key (for sharing)
gpg --armor --export your.email@example.com > public-key.asc

# Export private key (KEEP SECRET)
gpg --armor --export-secret-keys your.email@example.com > private-key.asc

# Backup to secure location
cp public-key.asc ~/.ssh/backup/
cp private-key.asc ~/.ssh/backup/
chmod 600 ~/.ssh/backup/private-key.asc
```

### 2.2 Configure Git to Use GPG
```bash
# Configure Git to use your GPG key
git config --global user.signingkey $(gpg --list-secret-keys --keyid-format LONG | grep sec | awk '{print $2}' | tail -1)
git config --global commit.gpgsign true
git config --global tag.gpgsign true

# Verify Git GPG configuration
git config --list | grep gpg
```

### 2.3 Set Up GPG Agent (Optional but Recommended)
```bash
# Start GPG agent
gpg-agent --daemon --write-env-file "$HOME/.gpg-agent-info"

# Add to ~/.bashrc for persistence
echo 'export GPG_TTY=$(tty)' >> ~/.bashrc
echo 'if [ -f "$HOME/.gpg-agent-info" ]; then source "$HOME/.gpg-agent-info"; export GPG_AGENT_INFO' >> ~/.bashrc

# Restart shell or source configuration
source ~/.bashrc
```

---

## 📝 Step 3: Signing Workflow for ProjectStrataML

### 3.1 Sign Dataset Artifacts
```bash
# Navigate to dataset directory
cd datasets/your-dataset/v1

# Generate checksums
find . -type f ! -name "CHECKSUMS.txt" ! -name "SIGNATURE.asc" -exec sha256sum {} \; > CHECKSUMS.txt

# Sign the directory (creates SIGNATURE.asc)
gpg --armor --detach-sign --output SIGNATURE.asc CHECKSUMS.txt

# Verify signature
gpg --verify SIGNATURE.asc CHECKSUMS.txt

# Commit to Git
git add CHECKSUMS.txt SIGNATURE.asc
git commit -S -m "dataset(your-dataset): add PGP signature and checksums

tfc-version: TFC-0004
dataset-version: your-dataset:v1
artifact-signed: true
```

### 3.2 Sign Model Artifacts
```bash
# Navigate to model directory
cd models/your-model/v1

# Generate checksums for all model files
find . -type f ! -name "metadata.yaml" ! -name "card.md" ! -name "metrics.yaml" ! -name "CHECKSUMS.txt" ! -name "SIGNATURE.asc" -exec sha256sum {} \; > CHECKSUMS.txt

# Sign the checksums file
gpg --armor --detach-sign --output SIGNATURE.asc CHECKSUMS.txt

# Verify the signature
gpg --verify SIGNATURE.asc CHECKSUMS.txt

# Update metadata.yaml to include signing info
cat >> metadata.yaml << EOF

signing:
  algorithm: "sha256"
  signature_file: "SIGNATURE.asc"
  signed_by: "your.email@example.com"
  signed_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  key_fingerprint: "$(gpg --list-secret-keys --keyid-format LONG | grep sec | awk '{print $2}' | tail -1)"
EOF

# Commit with signature
git add CHECKSUMS.txt SIGNATURE.asc metadata.yaml
git commit -S -m "model(your-model): add PGP signature and signing metadata

tfc-version: TFC-0005
model-version: your-model:v1
artifact-signed: true
key-fingerprint: $(gpg --list-secret-keys --keyid-format LONG | grep sec | awk '{print $2}' | tail -1)
```

### 3.3 Sign Run Artifacts
```bash
# Navigate to run directory
cd runs/run-2025-12-23-001

# Generate checksums for artifacts
if [ -d "artifacts" ]; then
    find artifacts -type f -exec sha256sum {} \; > artifacts/CHECKSUMS.txt
    gpg --armor --detach-sign --output artifacts/SIGNATURE.asc artifacts/CHECKSUMS.txt
    
    # Verify
    gpg --verify artifacts/SIGNATURE.asc artifacts/CHECKSUMS.txt
fi

# Sign the entire run directory by signing config.yaml
gpg --armor --detach-sign --output SIGNATURE.asc config.yaml

# Commit signed run
git add artifacts/CHECKSUMS.txt artifacts/SIGNATURE.asc SIGNATURE.asc config.yaml
git commit -S -m "run(run-2025-12-23-001): add PGP signatures for artifacts and configuration

tfc-version: TFC-0002
run-id: run-2025-12-23-001
artifact-signed: true
```

---

## ✅ Step 4: Verification Workflow

### 4.1 Verify Dataset Signatures
```bash
# Navigate to dataset directory
cd datasets/your-dataset/v1

# Verify signature exists
if [ -f "SIGNATURE.asc" ] && [ -f "CHECKSUMS.txt" ]; then
    echo "🔍 Verifying dataset signatures..."
    
    # Verify checksums signature
    if gpg --verify SIGNATURE.asc CHECKSUMS.txt 2>/dev/null; then
        echo "✅ Signature valid"
        
        # Verify checksums match files
        sha256sum -c CHECKSUMS.txt
        if [ $? -eq 0 ]; then
            echo "✅ All checksums valid"
        else
            echo "❌ Checksum verification failed"
            exit 1
        fi
    else
        echo "❌ Invalid signature"
        exit 1
    fi
else
    echo "⚠️  No signature found"
fi
```

### 4.2 Verify Model Signatures
```bash
# Navigate to model directory
cd models/your-model/v1

# Verify model signature
if [ -f "SIGNATURE.asc" ]; then
    echo "🔍 Verifying model signature..."
    
    if gpg --verify SIGNATURE.asc CHECKSUMS.txt 2>/dev/null; then
        echo "✅ Model signature valid"
        
        # Check metadata.yaml for signing info
        if grep -q "signing:" metadata.yaml; then
            echo "✅ Signing metadata found in metadata.yaml"
            grep -A 5 "signing:" metadata.yaml
        else
            echo "⚠️  Signing metadata missing from metadata.yaml"
        fi
        
        # Verify checksums
        sha256sum -c CHECKSUMS.txt
    else
        echo "❌ Invalid model signature"
        exit 1
    fi
fi
```

### 4.3 Batch Verification Script
```bash
# Create verification script
cat > verify-signatures.sh << 'EOF'
#!/bin/bash

echo "🔍 ProjectStrataML Signature Verification"
echo "====================================="

# Function to verify directory
verify_directory() {
    local dir=$1
    local type=$2
    
    if [ -d "$dir" ]; then
        echo "📁 Verifying $type: $dir"
        
        for version_dir in "$dir"/*/; do
            if [ -d "$version_dir" ] && [ -f "$version_dir/SIGNATURE.asc" ]; then
                echo "  🔍 Checking $(basename "$version_dir")"
                
                if gpg --verify "$version_dir/SIGNATURE.asc" "$version_dir/CHECKSUMS.txt" 2>/dev/null; then
                    echo "    ✅ Signature valid"
                    
                    if sha256sum -c "$version_dir/CHECKSUMS.txt" >/dev/null 2>&1; then
                        echo "    ✅ Checksums valid"
                    else
                        echo "    ❌ Checksums invalid"
                    fi
                else
                    echo "    ❌ Signature invalid"
                fi
            else
                echo "  ⚠️  No signature found"
            fi
        done
    fi
}

# Verify all artifact types
verify_directory "datasets" "Datasets"
verify_directory "models" "Models"
verify_directory "runs" "Runs"

echo "====================================="
echo "🎯 Verification complete"
EOF

chmod +x verify-signatures.sh
./verify-signatures.sh
```

---

## 🔐 Step 5: Advanced GPG Configuration

### 5.1 Multiple Key Management
```bash
# Create separate keys for different purposes
gpg --generate-key  # Development key
gpg --generate-key  # Production key
gpg --generate-key  # Testing key

# List all keys
gpg --list-secret-keys --keyid-format LONG

# Set default signing key
git config --global user.signingkey YOUR_PRODUCTION_KEY_ID
```

### 5.2 Key Trust Management
```bash
# Import someone else's public key
gpg --import public-key.asc

# Verify imported key
gpg --show-key --with-fingerprint KEY_ID

# Sign their key (establishes trust)
gpg --sign-key KEY_ID

# Set trust level (interactive)
gpg --edit-key KEY_ID
# gpg> trust
# gpg> 5 (ultimate trust)
# gpg> save
# gpg> quit
```

### 5.3 Key Revocation Certificate
```bash
# Generate revocation certificate (DO THIS BEFORE LOSE KEY!)
gpg --output revoke.asc --gen-revoke your.email@example.com

# Store revocation certificate securely
cp revoke.asc ~/.ssh/backup/revoke.asc
chmod 600 ~/.ssh/backup/revoke.asc
```

---

## 🛡️ Step 6: Security Best Practices

### 6.1 Key Security
```bash
# Protect your private key
chmod 600 ~/.gnupg/private-keys-v1.d/*.key
chmod 700 ~/.gnupg/

# Use strong passphrases
gpg --change-passphrase your.email@example.com

# Never share private key via unsecured channels
```

### 6.2 Backup Strategy
```bash
# Create encrypted backup of GPG directory
tar -czf - ~/.gnupg | gpg --cipher-algo AES256 --compress-algo 1 --symmetric --output gpg-backup.tar.gz.gpg

# Store backup in multiple secure locations
# 1. Encrypted cloud storage
# 2. Offline storage (USB drive)
# 3. Trusted colleague's custody
```

### 6.3 CI/CD Integration
```bash
# For automated signing in CI (use with caution)
export GPG_PRIVATE_KEY=$(cat ~/.ssh/backup/private-key.asc | base64 -w 0)
export GPG_PASSPHRASE="your_passphrase"

# Import key in CI
echo "$GPG_PRIVATE_KEY" | base64 -d | gpg --import --batch --yes

# Configure Git for CI
git config --global user.signingkey $GPG_KEY_ID
git config --global commit.gpgsign true
```

---

## 🔧 Step 7: Integration with ProjectStrataML Tools

### 7.1 Enhanced Verification Tool
```bash
# Add to tools/setup.py signature verification
def verify_signatures(self) -> bool:
    """Verify PGP signatures in repository"""
    success = True
    
    # Check datasets
    for dataset_path in Path("datasets").glob("*/v*"):
        signature_file = dataset_path / "SIGNATURE.asc"
        checksums_file = dataset_path / "CHECKSUMS.txt"
        
        if signature_file.exists() and checksums_file.exists():
            # Run GPG verification
            result = subprocess.run(
                ["gpg", "--verify", str(signature_file), str(checksums_file)],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                console.print(f"✅ {dataset_path.name}: Signature valid")
            else:
                console.print(f"❌ {dataset_path.name}: Invalid signature")
                success = False
    
    return success
```

### 7.2 Git Hooks for Automatic Signing
```bash
# Create pre-commit hook for automatic signing
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# Check if any datasets or models were modified
if git diff --cached --name-only | grep -E "^(datasets|models)/"; then
    echo "🔐 Dataset or model changes detected"
    echo "Please ensure signatures are up to date before committing:"
    echo "1. Run: ./verify-signatures.sh"
    echo "2. Update signatures if needed"
    echo "3. Stage signature files"
    exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

---

## 🆘 Troubleshooting

### Common GPG Issues

#### "No public key" Error
```bash
# Import the required public key
gpg --import public-key.asc

# Or fetch from keyserver
gpg --keyserver keys.openpgp.org --recv-key KEY_ID
```

#### "Bad passphrase" Error
```bash
# Check GPG agent is running
gpg-agent --daemon

# Reset passphrase
gpg --change-passphrase your.email@example.com
```

#### "Cannot lock" Error
```bash
# Kill existing GPG agent
pkill gpg-agent

# Start fresh agent
gpg-agent --daemon --write-env-file "$HOME/.gpg-agent-info"
```

#### Signature Verification Failures
```bash
# Check for line ending issues
dos2unix SIGNATURE.asc CHECKSUMS.txt

# Re-verify after conversion
gpg --verify SIGNATURE.asc CHECKSUMS.txt
```

### Key Recovery

#### Lost Private Key
```bash
# Use revocation certificate if available
gpg --import revoke.asc

# Notify collaborators of key compromise
# Generate new key and redistribute public key
```

#### Forgotten Passphrase
```bash
# No recovery possible for forgotten passphrase
# Must generate new key pair
# Revoke old key with revocation certificate
```

---

## ✅ Summary

With PGP signing configured, ProjectStrataML provides:

- **🔐 Artifact Integrity**: Cryptographic guarantees against tampering
- **👤 Identity Verification**: Confirmation of artifact creators
- **🔄 Reproducibility**: Consistent verification across environments
- **🛡️ Security**: Protection against unauthorized modifications
- **📋 Compliance**: Full TFC-0008 signing contract compliance

### Next Steps
1. **Generate your GPG key** following Step 1
2. **Sign your artifacts** using Step 3 workflows
3. **Verify signatures** before using artifacts
4. **Integrate with CI/CD** for automated verification
5. **Follow security best practices** for key management

**Your ProjectStrataML artifacts are now cryptographically secure!** 🛡️✨