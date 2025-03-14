#!/bin/bash

# Singularity Launcher
# Launch script for the Singularity Launcher application

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set version
VERSION="0.1.0"
echo "Starting Singularity Launcher v${VERSION}..."

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
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install required packages."
        exit 1
    fi
fi

# Create data directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/data"

# Check for container engine
if command -v podman &> /dev/null; then
    CONTAINER_ENGINE="podman"
    echo "Using Podman as container engine"
    
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

# Create config.ini if it doesn't exist
if [ ! -f "$SCRIPT_DIR/cfg/config.ini" ]; then
    echo "Creating config.ini from sample..."
    cp "$SCRIPT_DIR/cfg/config.sample.ini" "$SCRIPT_DIR/cfg/config.ini"
    
    # Update container engine in config
    if [ "$CONTAINER_ENGINE" != "none" ]; then
        sed -i "s/container_engine = .*/container_engine = $CONTAINER_ENGINE/" "$SCRIPT_DIR/cfg/config.ini"
    fi
fi

# Launch the application
echo "Launching Singularity Launcher..."
$PYTHON_CMD -m streamlit run main.py "$@"
