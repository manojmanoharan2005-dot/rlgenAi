#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "=========================================="
echo "=== RTLGen AI - Render Build Script ==="
echo "=========================================="

# 1. Install Icarus Verilog system package on Debian/Ubuntu Linux
if command -v apt-get &> /dev/null; then
    echo "[Build] Installing system dependency: iverilog..."
    apt-get update && apt-get install -y --no-install-recommends iverilog build-essential || true
else
    echo "[Build] Note: apt-get not available in current container/user context."
fi

# 2. Upgrade pip & Install Python Dependencies
echo "[Build] Installing Python dependencies..."
if [ -f "backend/requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r backend/requirements.txt
elif [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# 3. Executable Discovery Verification
echo "=========================================="
echo "=== Verifying Executable Discovery ==="
echo "=========================================="

echo "[Check] iverilog location:"
which iverilog || echo "iverilog not found via which"

echo "[Check] vvp location:"
which vvp || echo "vvp not found via which"

if command -v iverilog &> /dev/null; then
    echo "[Check] iverilog version:"
    iverilog -V | head -n 2
fi

echo "=========================================="
echo "=== Render Build Completed Successfully ==="
echo "=========================================="
