#!/bin/bash

# Singularity Launcher v2.0 - M4 Enhanced
# Launch script for the Singularity Launcher application with Apple Silicon M4 optimizations

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set version
VERSION="2.0.0"
echo "Starting Singularity Launcher v${VERSION} - M4 Enhanced..."

# Detect Apple Silicon and set optimizations
if [[ "$(uname -m)" == "arm64" ]] && [[ "$(uname -s)" == "Darwin" ]]; then
    echo "Apple Silicon detected - enabling M4 optimizations..."
    
    # Detect Apple Silicon variant
    CPU_BRAND=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "Unknown")
    if [[ "$CPU_BRAND" == *"M4"* ]]; then
        echo "M4 Apple Silicon detected - applying M4-specific optimizations"
        export APPLE_SILICON_VARIANT="M4"
        export PYTORCH_MPS_PREFER_METAL=1
        export PYTORCH_MPS_ALLOCATOR_POLICY=garbage_collection
    elif [[ "$CPU_BRAND" == *"M3"* ]]; then
        echo "M3 Apple Silicon detected"
        export APPLE_SILICON_VARIANT="M3"
    elif [[ "$CPU_BRAND" == *"M2"* ]]; then
        echo "M2 Apple Silicon detected"
        export APPLE_SILICON_VARIANT="M2"
    elif [[ "$CPU_BRAND" == *"M1"* ]]; then
        echo "M1 Apple Silicon detected"
        export APPLE_SILICON_VARIANT="M1"
    fi
    
    # Set MPS optimizations for all Apple Silicon
    export PYTORCH_ENABLE_MPS_FALLBACK=1
    export MPS_AVAILABLE=1
    export ACCELERATE_USE_MPS=1
fi

# Check for Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check for required Python packages
echo "Checking dependencies..."
$PYTHON_CMD -c "import streamlit" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    # Try to install required packages, but continue even if some fail
    $PYTHON_CMD -m pip install -r requirements.txt || echo "Warning: Some packages may not have installed correctly. Continuing anyway..."
    
    # Check if streamlit was installed
    $PYTHON_CMD -c "import streamlit" &> /dev/null
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install streamlit, which is required."
        echo "Please install it manually with: $PYTHON_CMD -m pip install streamlit"
        exit 1
    fi
fi

# Create data directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/data"

# Check for container engine (prefer Podman for Apple Silicon)
if command -v podman &> /dev/null; then
    CONTAINER_ENGINE="podman"
    echo "Using Podman as container engine (recommended for Apple Silicon)"
    
    # Create the singularity_net network if it doesn't exist
    if ! podman network ls | grep -q "singularity_net"; then
        echo "Creating singularity_net network..."
        podman network create singularity_net
    fi
elif command -v docker &> /dev/null; then
    CONTAINER_ENGINE="docker"
    echo "Using Docker as container engine"
    
    # Create the singularity_net network if it doesn't exist
    if ! docker network ls | grep -q "singularity_net"; then
        echo "Creating singularity_net network..."
        docker network create singularity_net
    fi
else
    CONTAINER_ENGINE="none"
    echo "Warning: No container engine found. Container functionality will be limited."
fi

# Export container engine for use by the application
export CONTAINER_ENGINE="$CONTAINER_ENGINE"

# Create config.ini if it doesn't exist
if [ ! -f "$SCRIPT_DIR/cfg/config.ini" ]; then
    echo "Creating config.ini from sample..."
    cp "$SCRIPT_DIR/cfg/config.sample.ini" "$SCRIPT_DIR/cfg/config.ini"
    
    # Update container engine in config
    if [ "$CONTAINER_ENGINE" != "none" ]; then
        sed -i "s/container_engine = .*/container_engine = $CONTAINER_ENGINE/" "$SCRIPT_DIR/cfg/config.ini"
    fi
fi

# Install the package in development mode
echo "Installing Singularity Launcher in development mode..."
cd "$SCRIPT_DIR"
$PYTHON_CMD -m pip install -e . || echo "Warning: Could not install package in development mode. Continuing anyway..."

# Launch the application
echo "Launching Singularity Launcher v${VERSION}..."

# Set PYTHONPATH to include the current directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run the application
cd "$SCRIPT_DIR"
$PYTHON_CMD -m streamlit run main.py "$@"
