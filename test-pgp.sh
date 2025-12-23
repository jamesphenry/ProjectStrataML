#!/bin/bash
# Quick test script for PGP signing commands

echo "🔐 Testing PGP Installation and Basic Commands"
echo "==============================================="

# Test GPG installation
if command -v gpg &> /dev/null; then
    echo "✅ GPG is installed: $(gpg --version | head -1)"
else
    echo "❌ GPG is not installed"
    echo "Install with: sudo apt-get install gnupg gnupg2"
    exit 1
fi

# Check for existing keys
echo "🔑 Checking for existing GPG keys..."
if gpg --list-secret-keys 2>/dev/null | grep -q "sec"; then
    echo "✅ Found existing GPG keys"
    gpg --list-secret-keys --keyid-format SHORT | grep "sec"
else
    echo "ℹ️  No GPG keys found"
    echo "Generate with: gpg --full-generate-key"
fi

# Test GPG configuration
echo "⚙️  Checking GPG configuration..."
if [ -d "$HOME/.gnupg" ]; then
    echo "✅ GPG directory exists: $HOME/.gnupg"
else
    echo "ℹ️  GPG directory will be created when needed"
fi

echo "==============================================="
echo "✅ PGP environment is ready for ProjectStrataML signing!"
echo ""
echo "Next steps:"
echo "1. Generate GPG key if needed"
echo "2. Follow docs/pgp-signing.md for complete guide"