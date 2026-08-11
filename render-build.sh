#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "=========================================="
echo "=== RTLGen AI - Render Build Script ==="
echo "=========================================="

# 1. Install or compile Icarus Verilog on Linux
LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"
export PATH="$LOCAL_BIN:$PATH"

if command -v apt-get &> /dev/null; then
    echo "[Build] Trying system package installation via apt-get..."
    apt-get update && apt-get install -y --no-install-recommends iverilog build-essential || true
fi

if ! command -v iverilog &> /dev/null; then
    echo "[Build] iverilog not found via apt-get. Compiling Icarus Verilog from source..."
    
    IV_VERSION="12_0"
    IV_DIR="verilog-v12_0"
    IV_TAR="v12_0.tar.gz"
    
    # Install dependencies if apt available, else rely on build tools provided by Render native environment
    if [ ! -f "$LOCAL_BIN/iverilog" ]; then
        BUILD_DIR="/tmp/iverilog-build"
        rm -rf "$BUILD_DIR"
        mkdir -p "$BUILD_DIR"
        cd "$BUILD_DIR"
        
        echo "[Build] Downloading Icarus Verilog source (v12_0)..."
        curl -sSL "https://github.com/steveicarus/iverilog/archive/refs/tags/${IV_TAR}" -o "${IV_TAR}"
        tar -xzf "${IV_TAR}"
        cd "${IV_DIR}"
        
        echo "[Build] Configuring and compiling Icarus Verilog..."
        autoconf || sh autoconf.sh || true
        ./configure --prefix="$HOME/.local"
        make -j$(nproc 2>/dev/null || echo 2)
        make install
        
        cd "$RENDER_PROJECT_ROOT" 2>/dev/null || cd /opt/render/project/src 2>/dev/null || cd -
    fi
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

echo "[Check] PATH variable: $PATH"
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
