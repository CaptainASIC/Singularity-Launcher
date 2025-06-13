#!/bin/bash

# Enhanced Apple Silicon Detection Script with M4 Support
# Detects specific Apple Silicon variants and provides optimized settings

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

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

# Function to detect specific Apple Silicon variant
detect_apple_silicon_variant() {
    local cpu_brand=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "Unknown")
    local cpu_cores=$(sysctl -n hw.ncpu 2>/dev/null || echo "0")
    local performance_cores=$(sysctl -n hw.perflevel0.physicalcpu 2>/dev/null || echo "0")
    local efficiency_cores=$(sysctl -n hw.perflevel1.physicalcpu 2>/dev/null || echo "0")
    
    print_status "Detected CPU: $cpu_brand"
    print_status "Total cores: $cpu_cores (P-cores: $performance_cores, E-cores: $efficiency_cores)"
    
    # M4 Detection (2024 variants)
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
    # M3 Detection (2023 variants)
    elif [[ "$cpu_brand" == *"M3"* ]]; then
        if [[ $performance_cores -ge 12 && $efficiency_cores -ge 16 ]]; then
            echo "M3_MAX"
        elif [[ $performance_cores -ge 8 && $efficiency_cores -ge 4 ]]; then
            echo "M3_PRO"
        elif [[ $performance_cores -ge 4 && $efficiency_cores -ge 4 ]]; then
            echo "M3_BASE"
        else
            echo "M3_UNKNOWN"
        fi
    # M2 Detection (2022 variants)
    elif [[ "$cpu_brand" == *"M2"* ]]; then
        if [[ $performance_cores -ge 8 && $efficiency_cores -ge 16 ]]; then
            echo "M2_ULTRA"
        elif [[ $performance_cores -ge 8 && $efficiency_cores -ge 8 ]]; then
            echo "M2_MAX"
        elif [[ $performance_cores -ge 6 && $efficiency_cores -ge 4 ]]; then
            echo "M2_PRO"
        elif [[ $performance_cores -ge 4 && $efficiency_cores -ge 4 ]]; then
            echo "M2_BASE"
        else
            echo "M2_UNKNOWN"
        fi
    # M1 Detection (2020-2021 variants)
    elif [[ "$cpu_brand" == *"M1"* ]]; then
        if [[ $performance_cores -ge 8 && $efficiency_cores -ge 16 ]]; then
            echo "M1_ULTRA"
        elif [[ $performance_cores -ge 8 && $efficiency_cores -ge 8 ]]; then
            echo "M1_MAX"
        elif [[ $performance_cores -ge 6 && $efficiency_cores -ge 2 ]]; then
            echo "M1_PRO"
        elif [[ $performance_cores -ge 4 && $efficiency_cores -ge 4 ]]; then
            echo "M1_BASE"
        else
            echo "M1_UNKNOWN"
        fi
    else
        echo "UNKNOWN_APPLE_SILICON"
    fi
}

# Function to get optimized settings based on variant
get_optimized_settings() {
    local variant="$1"
    local total_memory_gb="$2"
    
    case "$variant" in
        "M4_MAX")
            print_m4 "Detected M4 Max - Ultra High Performance Configuration"
            echo "MEMORY_LIMIT=32G"
            echo "CPU_LIMIT=0.85"
            echo "PERFORMANCE_PROFILE=ultra"
            echo "RECOMMENDED_MEMORY=64"
            ;;
        "M4_PRO")
            print_m4 "Detected M4 Pro - High Performance Configuration"
            echo "MEMORY_LIMIT=24G"
            echo "CPU_LIMIT=0.80"
            echo "PERFORMANCE_PROFILE=high"
            echo "RECOMMENDED_MEMORY=32"
            ;;
        "M4_BASE")
            print_m4 "Detected M4 Base - Optimized Performance Configuration"
            echo "MEMORY_LIMIT=16G"
            echo "CPU_LIMIT=0.75"
            echo "PERFORMANCE_PROFILE=optimized"
            echo "RECOMMENDED_MEMORY=24"
            ;;
        "M3_MAX")
            echo "MEMORY_LIMIT=24G"
            echo "CPU_LIMIT=0.80"
            echo "PERFORMANCE_PROFILE=high"
            echo "RECOMMENDED_MEMORY=32"
            ;;
        "M3_PRO")
            echo "MEMORY_LIMIT=18G"
            echo "CPU_LIMIT=0.75"
            echo "PERFORMANCE_PROFILE=balanced"
            echo "RECOMMENDED_MEMORY=24"
            ;;
        "M3_BASE")
            echo "MEMORY_LIMIT=12G"
            echo "CPU_LIMIT=0.70"
            echo "PERFORMANCE_PROFILE=balanced"
            echo "RECOMMENDED_MEMORY=16"
            ;;
        "M2_ULTRA")
            echo "MEMORY_LIMIT=32G"
            echo "CPU_LIMIT=0.85"
            echo "PERFORMANCE_PROFILE=ultra"
            echo "RECOMMENDED_MEMORY=64"
            ;;
        "M2_MAX")
            echo "MEMORY_LIMIT=24G"
            echo "CPU_LIMIT=0.80"
            echo "PERFORMANCE_PROFILE=high"
            echo "RECOMMENDED_MEMORY=32"
            ;;
        "M2_PRO")
            echo "MEMORY_LIMIT=16G"
            echo "CPU_LIMIT=0.75"
            echo "PERFORMANCE_PROFILE=balanced"
            echo "RECOMMENDED_MEMORY=24"
            ;;
        "M2_BASE")
            echo "MEMORY_LIMIT=12G"
            echo "CPU_LIMIT=0.70"
            echo "PERFORMANCE_PROFILE=balanced"
            echo "RECOMMENDED_MEMORY=16"
            ;;
        "M1_ULTRA")
            echo "MEMORY_LIMIT=24G"
            echo "CPU_LIMIT=0.80"
            echo "PERFORMANCE_PROFILE=high"
            echo "RECOMMENDED_MEMORY=32"
            ;;
        "M1_MAX")
            echo "MEMORY_LIMIT=18G"
            echo "CPU_LIMIT=0.75"
            echo "PERFORMANCE_PROFILE=balanced"
            echo "RECOMMENDED_MEMORY=24"
            ;;
        "M1_PRO")
            echo "MEMORY_LIMIT=12G"
            echo "CPU_LIMIT=0.70"
            echo "PERFORMANCE_PROFILE=balanced"
            echo "RECOMMENDED_MEMORY=16"
            ;;
        "M1_BASE")
            echo "MEMORY_LIMIT=8G"
            echo "CPU_LIMIT=0.65"
            echo "PERFORMANCE_PROFILE=conservative"
            echo "RECOMMENDED_MEMORY=16"
            ;;
        *)
            print_warning "Unknown Apple Silicon variant, using conservative settings"
            echo "MEMORY_LIMIT=8G"
            echo "CPU_LIMIT=0.60"
            echo "PERFORMANCE_PROFILE=conservative"
            echo "RECOMMENDED_MEMORY=16"
            ;;
    esac
}

# Function to get M4-specific optimizations
get_m4_optimizations() {
    local variant="$1"
    
    if [[ "$variant" == M4_* ]]; then
        cat << 'EOF'
# M4-Specific Environment Variables
- PYTORCH_MPS_PREFER_METAL=1
- PYTORCH_MPS_ALLOCATOR_POLICY=garbage_collection
- COMFYUI_M4_OPTIMIZATIONS=1
- COMFYUI_ADVANCED_SAMPLING=1
- COMFYUI_FAST_DECODE=1
- TORCH_COMPILE_MODE=max-autotune
- PYTORCH_JIT_USE_NNC_NOT_NVFUSER=1
EOF
    fi
}

# Main execution
if [[ "$1" == "--detect-only" ]]; then
    # Just detect and return variant
    detect_apple_silicon_variant
    exit 0
fi

print_status "Apple Silicon Variant Detection and Optimization"
echo

# Get system information
TOTAL_MEMORY=$(sysctl -n hw.memsize)
TOTAL_MEMORY_GB=$((TOTAL_MEMORY / 1024 / 1024 / 1024))

print_status "System Memory: ${TOTAL_MEMORY_GB}GB"

# Detect variant
VARIANT=$(detect_apple_silicon_variant)
print_success "Detected variant: $VARIANT"

# Get optimized settings
SETTINGS=$(get_optimized_settings "$VARIANT" "$TOTAL_MEMORY_GB")

echo
print_status "Recommended Settings:"
echo "$SETTINGS" | while read line; do
    if [[ -n "$line" ]]; then
        key=$(echo "$line" | cut -d'=' -f1)
        value=$(echo "$line" | cut -d'=' -f2)
        printf "  %-20s: %s\n" "$key" "$value"
    fi
done

# Check if M4 and show additional optimizations
if [[ "$VARIANT" == M4_* ]]; then
    echo
    print_m4 "M4-Specific Optimizations Available:"
    get_m4_optimizations "$VARIANT"
fi

# Memory recommendation check
RECOMMENDED_MEMORY=$(echo "$SETTINGS" | grep "RECOMMENDED_MEMORY" | cut -d'=' -f2)
if [[ $TOTAL_MEMORY_GB -lt $RECOMMENDED_MEMORY ]]; then
    echo
    print_warning "Your system has ${TOTAL_MEMORY_GB}GB RAM, but ${RECOMMENDED_MEMORY}GB is recommended for optimal performance with $VARIANT"
    print_warning "Consider reducing memory limits or upgrading system memory"
fi

echo
print_success "Detection complete. Use these settings in your ComfyUI configuration."

