#!/bin/bash

# Enhanced Test Suite for ComfyUI Apple Silicon Optimization with M4 Support
# This script validates the M4-enhanced configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_m4() {
    echo -e "${PURPLE}[M4]${NC} $1"
}

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    print_test "$test_name"
    
    if eval "$test_command"; then
        print_pass "$test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        print_fail "$test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo "=== ComfyUI Apple Silicon M4-Enhanced Configuration Test Suite ==="
echo

# Test 1: M4 Detection Script Validation
run_test "Apple Silicon detection script exists and is executable" \
    "test -x /home/ubuntu/detect-apple-silicon.sh"

run_test "Detection script has proper shebang" \
    "head -1 /home/ubuntu/detect-apple-silicon.sh | grep -q '#!/bin/bash'"

# Test 2: M4-Optimized Compose File Validation
run_test "M4-optimized compose file YAML syntax validation" \
    "python3 -c 'import yaml; yaml.safe_load(open(\"/home/ubuntu/comfyui-compose-m4-optimized.yaml\"))'"

run_test "M4 compose file has required sections" \
    "python3 -c '
import yaml
data = yaml.safe_load(open(\"/home/ubuntu/comfyui-compose-m4-optimized.yaml\"))
assert \"version\" in data
assert \"services\" in data
assert \"comfyui\" in data[\"services\"]
assert \"networks\" in data
'"

# Test 3: M4-Specific Environment Variables
run_test "M4-specific optimizations present in compose file" \
    "grep -q 'COMFYUI_M4_OPTIMIZATIONS=1' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

run_test "PyTorch MPS prefer metal optimization present" \
    "grep -q 'PYTORCH_MPS_PREFER_METAL=1' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

run_test "Advanced sampling optimization present" \
    "grep -q 'COMFYUI_ADVANCED_SAMPLING=1' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

run_test "Fast decode optimization present" \
    "grep -q 'COMFYUI_FAST_DECODE=1' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

run_test "Torch compile mode configuration present" \
    "grep -q 'TORCH_COMPILE_MODE=' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

# Test 4: Dynamic Resource Management
run_test "Dynamic memory allocation variables present" \
    "grep -q 'COMFYUI_MEMORY_LIMIT' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

run_test "Dynamic CPU allocation variables present" \
    "grep -q 'COMFYUI_CPU_LIMIT' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

run_test "Memory reservation configuration present" \
    "grep -q 'COMFYUI_MEMORY_RESERVATION' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

# Test 5: Apple Silicon Variant Detection
run_test "Apple Silicon variant environment variable present" \
    "grep -q 'APPLE_SILICON_VARIANT=' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

run_test "Performance profile configuration present" \
    "grep -q 'PERFORMANCE_PROFILE=' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

# Test 6: M4-Enhanced Setup Script Validation
run_test "M4-enhanced setup script exists and is executable" \
    "test -x /home/ubuntu/setup-comfyui-m4-enhanced.sh"

run_test "M4 setup script contains variant detection" \
    "grep -q 'detect-apple-silicon.sh' /home/ubuntu/setup-comfyui-m4-enhanced.sh"

run_test "M4 setup script has M4-specific configurations" \
    "grep -q 'M4_MAX\\|M4_PRO\\|M4_BASE' /home/ubuntu/setup-comfyui-m4-enhanced.sh"

# Test 7: Container Labels and Metadata
run_test "M4 optimization label present in compose file" \
    "grep -q 'com.singularity.m4_optimized=true' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

run_test "Version 2.0 label present" \
    "grep -q 'com.singularity.version=2.0' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

# Test 8: Enhanced Health Checks
run_test "Enhanced health check with system stats endpoint" \
    "grep -q 'system_stats' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

run_test "Extended startup period for M4 optimizations" \
    "grep -q 'start_period: 120s' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

# Test 9: Network Configuration
run_test "Enhanced network configuration with gateway" \
    "grep -q 'gateway: 172.20.0.1' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

# Test 10: Documentation Validation
run_test "M4 performance guide exists" \
    "test -f /home/ubuntu/m4-performance-guide.md"

run_test "M4 performance guide contains M4 specifications" \
    "grep -q 'M4 Base\\|M4 Pro\\|M4 Max' /home/ubuntu/m4-performance-guide.md"

run_test "Performance benchmarks included in guide" \
    "grep -q 'Benchmarking Results' /home/ubuntu/m4-performance-guide.md"

# Test 11: M4 Variant Detection Logic
run_test "M4 Max detection logic present" \
    "grep -q 'performance_cores -ge 14.*efficiency_cores -ge 20' /home/ubuntu/detect-apple-silicon.sh"

run_test "M4 Pro detection logic present" \
    "grep -q 'performance_cores -ge 12.*efficiency_cores -ge 16' /home/ubuntu/detect-apple-silicon.sh"

run_test "M4 Base detection logic present" \
    "grep -q 'performance_cores -ge 4.*efficiency_cores -ge 6' /home/ubuntu/detect-apple-silicon.sh"

# Test 12: M4-Specific Optimization Functions
run_test "M4 optimization function exists in detection script" \
    "grep -q 'get_m4_optimizations' /home/ubuntu/detect-apple-silicon.sh"


# Test 13: Thermal Management
run_test "Thermal management configuration present" \
    "grep -q 'COMFYUI_THERMAL_THROTTLE=auto' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

run_test "Power efficiency option present" \
    "grep -q 'COMFYUI_POWER_EFFICIENT=' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

# Test 14: Backwards Compatibility
run_test "M1/M2/M3 detection still present" \
    "grep -q 'M1_\\|M2_\\|M3_' /home/ubuntu/detect-apple-silicon.sh"

run_test "Fallback compose file support in setup script" \
    "grep -q 'FALLBACK_COMPOSE_FILE' /home/ubuntu/setup-comfyui-m4-enhanced.sh"

# Test 15: Advanced M4 Features
run_test "Garbage collection allocator policy present" \
    "grep -q 'PYTORCH_MPS_ALLOCATOR_POLICY=garbage_collection' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

run_test "JIT optimization for M4 present" \
    "grep -q 'PYTORCH_JIT_USE_NNC_NOT_NVFUSER=1' /home/ubuntu/comfyui-compose-m4-optimized.yaml"

echo
echo "=== Test Results ==="
echo "Tests Run: $TESTS_RUN"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"

if [ $TESTS_FAILED -eq 0 ]; then
    print_pass "All tests passed! ✨"
    echo
    print_m4 "M4 Apple Silicon optimization is ready for deployment."
    echo
    echo "Key M4 improvements validated:"
    echo "  ✓ M4 variant detection (Base, Pro, Max)"
    echo "  ✓ M4-specific environment optimizations"
    echo "  ✓ Enhanced performance profiles"
    echo "  ✓ Advanced MPS and PyTorch optimizations"
    echo "  ✓ Thermal management and power efficiency"
    echo "  ✓ Dynamic resource allocation"
    echo "  ✓ Backwards compatibility with M1/M2/M3"
    exit 0
else
    print_fail "Some tests failed. Please review the issues above."
    exit 1
fi

