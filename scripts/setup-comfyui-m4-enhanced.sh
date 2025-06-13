#!/bin/bash

# Enhanced ComfyUI Apple Silicon Setup Script with M4 Support
# This script sets up the optimal environment for running ComfyUI on Apple Silicon with Podman
# Now includes automatic M4 detection and optimization

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_m4() {
    echo -e "${PURPLE}[M4]${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS (Apple Silicon). Detected OS: $OSTYPE"
    exit 1
fi

# Check if running on Apple Silicon
ARCH=$(uname -m)
if [[ "$ARCH" != "arm64" ]]; then
    print_error "This script requires Apple Silicon (ARM64). Detected architecture: $ARCH"
    exit 1
fi

print_status "Setting up ComfyUI for Apple Silicon with M4 optimizations..."

# Check for Podman installation
if ! command -v podman &> /dev/null; then
    print_error "Podman is not installed. Please install Podman first:"
    echo "  brew install podman"
    exit 1
fi

# Check for podman-compose
if ! command -v podman-compose &> /dev/null; then
    print_warning "podman-compose not found. Installing..."
    pip3 install podman-compose
fi

# Initialize Podman machine if not already done
if ! podman machine list | grep -q "Currently running"; then
    print_status "Initializing Podman machine with optimized settings..."
    
    # Get system memory for optimal Podman machine configuration
    TOTAL_MEMORY=$(sysctl -n hw.memsize)
    TOTAL_MEMORY_GB=$((TOTAL_MEMORY / 1024 / 1024 / 1024))
    
    # Calculate optimal Podman machine memory (50% of system memory, min 8GB, max 32GB)
    PODMAN_MEMORY=$((TOTAL_MEMORY_GB / 2))
    if [[ $PODMAN_MEMORY -lt 8 ]]; then
        PODMAN_MEMORY=8
    elif [[ $PODMAN_MEMORY -gt 32 ]]; then
        PODMAN_MEMORY=32
    fi
    
    # Calculate optimal CPU allocation (75% of total cores, min 4, max 16)
    TOTAL_CORES=$(sysctl -n hw.ncpu)
    PODMAN_CPUS=$((TOTAL_CORES * 3 / 4))
    if [[ $PODMAN_CPUS -lt 4 ]]; then
        PODMAN_CPUS=4
    elif [[ $PODMAN_CPUS -gt 16 ]]; then
        PODMAN_CPUS=16
    fi
    
    print_status "Configuring Podman machine: ${PODMAN_CPUS} CPUs, ${PODMAN_MEMORY}GB RAM"
    podman machine init --cpus $PODMAN_CPUS --memory $((PODMAN_MEMORY * 1024)) --disk-size 100
    podman machine start
fi

# Detect Apple Silicon variant using the detection script
print_status "Detecting Apple Silicon variant..."

# Create temporary detection script if not available
if [[ ! -f "./detect-apple-silicon.sh" ]]; then
    print_status "Creating Apple Silicon detection script..."
    cat > "./detect-apple-silicon.sh" << 'EOF'
#!/bin/bash
# Simplified detection for setup script
cpu_brand=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "Unknown")
performance_cores=$(sysctl -n hw.perflevel0.physicalcpu 2>/dev/null || echo "0")
efficiency_cores=$(sysctl -n hw.perflevel1.physicalcpu 2>/dev/null || echo "0")

if [[ "$cpu_brand" == *"M4"* ]]; then
    if [[ $performance_cores -ge 14 && $efficiency_cores -ge 20 ]]; then
        echo "M4_MAX"
    elif [[ $performance_cores -ge 12 && $efficiency_cores -ge 16 ]]; then
        echo "M4_PRO"
    elif [[ $performance_cores -ge 4 && $efficiency_cores -ge 6 ]]; then
        echo "M4_BASE"
    else
        echo "M4_UNKNOWN"
    fi
elif [[ "$cpu_brand" == *"M3"* ]]; then
    if [[ $performance_cores -ge 12 ]]; then
        echo "M3_MAX"
    elif [[ $performance_cores -ge 8 ]]; then
        echo "M3_PRO"
    else
        echo "M3_BASE"
    fi
elif [[ "$cpu_brand" == *"M2"* ]]; then
    if [[ $performance_cores -ge 8 && $efficiency_cores -ge 16 ]]; then
        echo "M2_ULTRA"
    elif [[ $performance_cores -ge 8 ]]; then
        echo "M2_MAX"
    elif [[ $performance_cores -ge 6 ]]; then
        echo "M2_PRO"
    else
        echo "M2_BASE"
    fi
elif [[ "$cpu_brand" == *"M1"* ]]; then
    if [[ $performance_cores -ge 8 && $efficiency_cores -ge 16 ]]; then
        echo "M1_ULTRA"
    elif [[ $performance_cores -ge 8 ]]; then
        echo "M1_MAX"
    elif [[ $performance_cores -ge 6 ]]; then
        echo "M1_PRO"
    else
        echo "M1_BASE"
    fi
else
    echo "UNKNOWN"
fi
EOF
    chmod +x "./detect-apple-silicon.sh"
fi

# Detect the variant
APPLE_SILICON_VARIANT=$(./detect-apple-silicon.sh)
print_success "Detected Apple Silicon variant: $APPLE_SILICON_VARIANT"

# Set up environment variables based on detected variant
print_status "Configuring environment variables for $APPLE_SILICON_VARIANT..."

# Get system memory
TOTAL_MEMORY=$(sysctl -n hw.memsize)
TOTAL_MEMORY_GB=$((TOTAL_MEMORY / 1024 / 1024 / 1024))

# Configure settings based on detected variant
case "$APPLE_SILICON_VARIANT" in
    "M4_MAX")
        print_m4 "Configuring for M4 Max - Ultra High Performance"
        MEMORY_LIMIT="32G"
        CPU_LIMIT="0.85"
        PERFORMANCE_PROFILE="ultra"
        TORCH_COMPILE_MODE="max-autotune"
        COMFYUI_HIGHVRAM="1"
        COMFYUI_NORMALVRAM="1"
        COMFYUI_LOWVRAM="0"
        ;;
    "M4_PRO")
        print_m4 "Configuring for M4 Pro - High Performance"
        MEMORY_LIMIT="24G"
        CPU_LIMIT="0.80"
        PERFORMANCE_PROFILE="high"
        TORCH_COMPILE_MODE="default"
        COMFYUI_HIGHVRAM="0"
        COMFYUI_NORMALVRAM="1"
        COMFYUI_LOWVRAM="0"
        ;;
    "M4_BASE")
        print_m4 "Configuring for M4 Base - Optimized Performance"
        MEMORY_LIMIT="16G"
        CPU_LIMIT="0.75"
        PERFORMANCE_PROFILE="optimized"
        TORCH_COMPILE_MODE="default"
        COMFYUI_HIGHVRAM="0"
        COMFYUI_NORMALVRAM="1"
        COMFYUI_LOWVRAM="0"
        ;;
    "M3_MAX")
        MEMORY_LIMIT="24G"
        CPU_LIMIT="0.80"
        PERFORMANCE_PROFILE="high"
        TORCH_COMPILE_MODE="default"
        COMFYUI_HIGHVRAM="0"
        COMFYUI_NORMALVRAM="1"
        COMFYUI_LOWVRAM="0"
        ;;
    "M3_PRO")
        MEMORY_LIMIT="18G"
        CPU_LIMIT="0.75"
        PERFORMANCE_PROFILE="balanced"
        TORCH_COMPILE_MODE="default"
        COMFYUI_HIGHVRAM="0"
        COMFYUI_NORMALVRAM="1"
        COMFYUI_LOWVRAM="0"
        ;;
    "M3_BASE")
        MEMORY_LIMIT="12G"
        CPU_LIMIT="0.70"
        PERFORMANCE_PROFILE="balanced"
        TORCH_COMPILE_MODE="default"
        COMFYUI_HIGHVRAM="0"
        COMFYUI_NORMALVRAM="0"
        COMFYUI_LOWVRAM="1"
        ;;
    "M2_ULTRA")
        MEMORY_LIMIT="32G"
        CPU_LIMIT="0.85"
        PERFORMANCE_PROFILE="ultra"
        TORCH_COMPILE_MODE="default"
        COMFYUI_HIGHVRAM="1"
        COMFYUI_NORMALVRAM="1"
        COMFYUI_LOWVRAM="0"
        ;;
    "M2_MAX")
        MEMORY_LIMIT="24G"
        CPU_LIMIT="0.80"
        PERFORMANCE_PROFILE="high"
        TORCH_COMPILE_MODE="default"
        COMFYUI_HIGHVRAM="0"
        COMFYUI_NORMALVRAM="1"
        COMFYUI_LOWVRAM="0"
        ;;
    "M2_PRO")
        MEMORY_LIMIT="16G"
        CPU_LIMIT="0.75"
        PERFORMANCE_PROFILE="balanced"
        TORCH_COMPILE_MODE="default"
        COMFYUI_HIGHVRAM="0"
        COMFYUI_NORMALVRAM="1"
        COMFYUI_LOWVRAM="0"
        ;;
    "M2_BASE")
        MEMORY_LIMIT="12G"
        CPU_LIMIT="0.70"
        PERFORMANCE_PROFILE="balanced"
        TORCH_COMPILE_MODE="default"
        COMFYUI_HIGHVRAM="0"
        COMFYUI_NORMALVRAM="0"
        COMFYUI_LOWVRAM="1"
        ;;
    "M1_ULTRA")
        MEMORY_LIMIT="24G"
        CPU_LIMIT="0.80"
        PERFORMANCE_PROFILE="high"
        TORCH_COMPILE_MODE="default"
        COMFYUI_HIGHVRAM="0"
        COMFYUI_NORMALVRAM="1"
        COMFYUI_LOWVRAM="0"
        ;;
    "M1_MAX")
        MEMORY_LIMIT="18G"
        CPU_LIMIT="0.75"
        PERFORMANCE_PROFILE="balanced"
        TORCH_COMPILE_MODE="default"
        COMFYUI_HIGHVRAM="0"
        COMFYUI_NORMALVRAM="1"
        COMFYUI_LOWVRAM="0"
        ;;
    "M1_PRO")
        MEMORY_LIMIT="12G"
        CPU_LIMIT="0.70"
        PERFORMANCE_PROFILE="balanced"
        TORCH_COMPILE_MODE="default"
        COMFYUI_HIGHVRAM="0"
        COMFYUI_NORMALVRAM="0"
        COMFYUI_LOWVRAM="1"
        ;;
    "M1_BASE")
        MEMORY_LIMIT="8G"
        CPU_LIMIT="0.65"
        PERFORMANCE_PROFILE="conservative"
        TORCH_COMPILE_MODE="default"
        COMFYUI_HIGHVRAM="0"
        COMFYUI_NORMALVRAM="0"
        COMFYUI_LOWVRAM="1"
        ;;
    *)
        print_warning "Unknown Apple Silicon variant, using conservative settings"
        MEMORY_LIMIT="8G"
        CPU_LIMIT="0.60"
        PERFORMANCE_PROFILE="conservative"
        TORCH_COMPILE_MODE="default"
        COMFYUI_HIGHVRAM="0"
        COMFYUI_NORMALVRAM="0"
        COMFYUI_LOWVRAM="1"
        ;;
esac

# Adjust memory limit based on available system memory
if [[ $TOTAL_MEMORY_GB -lt 16 && "$MEMORY_LIMIT" == "16G" ]]; then
    MEMORY_LIMIT="12G"
    print_warning "Adjusted memory limit to 12G due to system memory constraints"
elif [[ $TOTAL_MEMORY_GB -lt 24 && "$MEMORY_LIMIT" == "24G" ]]; then
    MEMORY_LIMIT="18G"
    print_warning "Adjusted memory limit to 18G due to system memory constraints"
elif [[ $TOTAL_MEMORY_GB -lt 32 && "$MEMORY_LIMIT" == "32G" ]]; then
    MEMORY_LIMIT="24G"
    print_warning "Adjusted memory limit to 24G due to system memory constraints"
fi

# Set up Singularity Drive
SINGULARITY_DRIVE="${HOME}/Singularity"
if [[ ! -d "$SINGULARITY_DRIVE" ]]; then
    print_status "Creating Singularity Drive directory: $SINGULARITY_DRIVE"
    mkdir -p "$SINGULARITY_DRIVE"
fi

# Create ComfyUI directories
print_status "Creating ComfyUI directories..."
mkdir -p "$SINGULARITY_DRIVE/comfyui"/{models,custom_nodes,output,input,user,temp,config}

# Set proper permissions
chmod -R 755 "$SINGULARITY_DRIVE/comfyui"

# Create environment file with M4 optimizations
ENV_FILE="$SINGULARITY_DRIVE/.env"
print_status "Creating environment file with M4 optimizations: $ENV_FILE"

cat > "$ENV_FILE" << EOF
# ComfyUI Apple Silicon Configuration with M4 Support
SINGULARITY_DRIVE=$SINGULARITY_DRIVE
COMFYUI_MEMORY_LIMIT=$MEMORY_LIMIT
COMFYUI_CPU_LIMIT=$CPU_LIMIT
COMFYUI_MEMORY_RESERVATION=2G
COMFYUI_CPU_RESERVATION=0.1
UID=$(id -u)
GID=$(id -g)

# Apple Silicon Variant Detection
APPLE_SILICON_VARIANT=$APPLE_SILICON_VARIANT
PERFORMANCE_PROFILE=$PERFORMANCE_PROFILE

# M4-Specific Optimizations
TORCH_COMPILE_MODE=$TORCH_COMPILE_MODE
COMFYUI_HIGHVRAM=$COMFYUI_HIGHVRAM
COMFYUI_NORMALVRAM=$COMFYUI_NORMALVRAM
COMFYUI_LOWVRAM=$COMFYUI_LOWVRAM
COMFYUI_DONT_UPCAST_ATTENTION=0
COMFYUI_USE_SPLIT_CROSS_ATTENTION=0

# Power Management
COMFYUI_POWER_EFFICIENT=0

# System Information
TOTAL_MEMORY_GB=$TOTAL_MEMORY_GB
DETECTED_ARCH=$ARCH
SETUP_DATE=$(date)
SETUP_VERSION=2.0-M4
EOF

print_success "Environment file created with optimal settings:"
print_status "  Apple Silicon Variant: $APPLE_SILICON_VARIANT"
print_status "  Memory Limit: $MEMORY_LIMIT"
print_status "  CPU Limit: $CPU_LIMIT"
print_status "  Performance Profile: $PERFORMANCE_PROFILE"
if [[ "$APPLE_SILICON_VARIANT" == M4_* ]]; then
    print_m4 "  M4 Optimizations: Enabled"
    print_m4 "  Torch Compile Mode: $TORCH_COMPILE_MODE"
fi

# Download models (optional)
read -p "Do you want to download basic ComfyUI models? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Downloading basic models..."
    
    # Create models subdirectories
    mkdir -p "$SINGULARITY_DRIVE/comfyui/models"/{checkpoints,vae,clip,unet,controlnet,loras}
    
    print_status "Note: You'll need to manually download models from HuggingFace or other sources"
    print_status "Place them in: $SINGULARITY_DRIVE/comfyui/models/"
    
    if [[ "$APPLE_SILICON_VARIANT" == M4_* ]]; then
        print_m4 "M4 systems can handle larger models efficiently. Consider downloading SDXL models."
    fi
fi

# Create enhanced launch script with M4 support
LAUNCH_SCRIPT="$SINGULARITY_DRIVE/launch-comfyui-m4.sh"
print_status "Creating M4-optimized launch script: $LAUNCH_SCRIPT"

cat > "$LAUNCH_SCRIPT" << 'EOF'
#!/bin/bash

# ComfyUI M4-Optimized Launch Script for Apple Silicon

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_m4() {
    echo -e "${PURPLE}[M4]${NC} $1"
}

# Load environment variables
if [[ -f "$(dirname "$0")/.env" ]]; then
    source "$(dirname "$0")/.env"
    print_status "Loaded environment from .env"
    print_status "Apple Silicon Variant: ${APPLE_SILICON_VARIANT}"
    print_status "Performance Profile: ${PERFORMANCE_PROFILE}"
    
    if [[ "$APPLE_SILICON_VARIANT" == M4_* ]]; then
        print_m4 "M4 optimizations enabled"
        print_m4 "Torch Compile Mode: ${TORCH_COMPILE_MODE}"
    fi
else
    echo "Warning: .env file not found"
fi

# Check if Podman is running
if ! podman machine list | grep -q "Currently running"; then
    print_status "Starting Podman machine..."
    podman machine start
fi

# Launch ComfyUI with M4 optimizations
print_status "Launching ComfyUI with optimizations for ${APPLE_SILICON_VARIANT}..."
print_status "Memory Limit: ${COMFYUI_MEMORY_LIMIT:-16G}"
print_status "CPU Limit: ${COMFYUI_CPU_LIMIT:-0.75}"

# Use the M4-optimized compose file if available, otherwise fall back to Podman compose
COMPOSE_FILE="$(dirname "$0")/comfyui-compose-m4-optimized.yaml"
FALLBACK_COMPOSE_FILE="$(dirname "$0")/comfyui-compose-podman.yaml"

if [[ -f "$COMPOSE_FILE" ]]; then
    print_m4 "Using M4-optimized compose file"
    podman-compose -f "$COMPOSE_FILE" up -d
elif [[ -f "$FALLBACK_COMPOSE_FILE" ]]; then
    print_status "Using standard Podman compose file"
    podman-compose -f "$FALLBACK_COMPOSE_FILE" up -d
else
    echo "Error: No compose file found"
    echo "Expected: $COMPOSE_FILE or $FALLBACK_COMPOSE_FILE"
    exit 1
fi

print_success "ComfyUI started successfully!"
print_status "Access it at: http://localhost:8188"

if [[ "$APPLE_SILICON_VARIANT" == M4_* ]]; then
    print_m4 "M4 Performance Tips:"
    print_m4 "- Use SDXL models for best performance"
    print_m4 "- Enable advanced sampling for better quality"
    print_m4 "- Monitor thermal performance in Activity Monitor"
fi
EOF

chmod +x "$LAUNCH_SCRIPT"

# Create stop script
STOP_SCRIPT="$SINGULARITY_DRIVE/stop-comfyui.sh"
cat > "$STOP_SCRIPT" << 'EOF'
#!/bin/bash

# ComfyUI Stop Script

COMPOSE_FILE="$(dirname "$0")/comfyui-compose-m4-optimized.yaml"
FALLBACK_COMPOSE_FILE="$(dirname "$0")/comfyui-compose-podman.yaml"

if [[ -f "$COMPOSE_FILE" ]]; then
    echo "Stopping ComfyUI (M4-optimized)..."
    podman-compose -f "$COMPOSE_FILE" down
elif [[ -f "$FALLBACK_COMPOSE_FILE" ]]; then
    echo "Stopping ComfyUI (standard)..."
    podman-compose -f "$FALLBACK_COMPOSE_FILE" down
else
    echo "Error: No compose file found"
    exit 1
fi

echo "ComfyUI stopped successfully!"
EOF

chmod +x "$STOP_SCRIPT"

print_success "Setup completed successfully!"
print_status ""
print_status "Next steps:"
print_status "1. Copy the M4-optimized compose file to: $SINGULARITY_DRIVE/comfyui-compose-m4-optimized.yaml"
print_status "2. Run: $LAUNCH_SCRIPT"
print_status "3. Access ComfyUI at: http://localhost:8188"
print_status ""
print_status "Scripts created:"
print_status "  Launch: $LAUNCH_SCRIPT"
print_status "  Stop: $STOP_SCRIPT"
print_status "  Environment: $ENV_FILE"

if [[ "$APPLE_SILICON_VARIANT" == M4_* ]]; then
    echo ""
    print_m4 "M4-Specific Features Enabled:"
    print_m4 "  ✓ Advanced MPS optimizations"
    print_m4 "  ✓ Torch compilation: $TORCH_COMPILE_MODE"
    print_m4 "  ✓ Enhanced memory management"
    print_m4 "  ✓ Thermal optimization"
fi

# Clean up temporary detection script if we created it
if [[ -f "./detect-apple-silicon.sh" && ! -f "../detect-apple-silicon.sh" ]]; then
    rm "./detect-apple-silicon.sh"
fi

