"""
Singularity Launcher v2.5 - Enhanced UI & Optimized Scripts
A Streamlit UI for deploying Lab and AI Environments with support for various CPU and GPU architectures.
Now featuring comprehensive Apple Silicon M4 optimizations and improved user interface.
Author: Captain ASIC
Version: 2.5.0
License: MIT
"""
__version__ = "2.5.0"
__author__ = "Captain ASIC"
__license__ = "MIT"
__description__ = "Singularity Launcher v2.5 - Enhanced UI & Optimized Scripts: Streamlit UI for deploying Lab and AI Environments"

# Version history
VERSION_HISTORY = {
    "2.5.0": {
        "release_date": "2025-06-14",
        "features": [
            "Enhanced UI with improved responsiveness and visual hierarchy",
            "Robust initialization sequence with proper error handling",
            "Improved session state management",
            "Error boundaries around UI components",
            "Debugging mode for troubleshooting",
            "Improved accessibility with ARIA attributes",
            "Enhanced loading states and indicators",
            "Comprehensive error messaging with actionable guidance"
        ],
        "improvements": [
            "Refactored state management for better reliability",
            "Modularized UI components for improved maintainability",
            "Implemented proper async operations for container management",
            "Added strategic caching for performance-intensive operations",
            "Enhanced in-code documentation and type hints",
            "Updated README with clearer setup instructions"
        ]
    },
    "2.0.0": {
        "release_date": "2024-12-13",
        "features": [
            "Apple Silicon M4 support (M4 Base, M4 Pro, M4 Max)",
            "Enhanced Apple Silicon variant detection (M1-M4)",
            "M4-specific optimizations with advanced MPS support",
            "Dynamic resource allocation based on Apple Silicon variant",
            "Thermal management and power efficiency controls",
            "Performance profiles: Ultra, High, Optimized, Balanced, Conservative",
            "M4-optimized compose files for all services",
            "Comprehensive M4 performance benchmarks",
            "Enhanced system detection with Apple Silicon optimizations",
            "Backwards compatibility with M1, M2, and M3 variants"
        ],
        "improvements": [
            "Significant performance improvements on M4 systems",
            "Better memory management for Apple Silicon",
            "Enhanced thermal throttling capabilities",
            "Improved container resource allocation",
            "Advanced PyTorch MPS optimizations"
        ]
    },
    "1.0.0": {
        "release_date": "2024-06-01",
        "features": [
            "Initial release",
            "Basic Apple Silicon support",
            "NVIDIA GPU optimizations",
            "AMD GPU support",
            "Multi-platform container deployment"
        ]
    }
}

# M4 specific constants
M4_VARIANTS = ["M4_BASE", "M4_PRO", "M4_MAX"]
M4_OPTIMIZATIONS = {
    "M4_MAX": {
        "memory_limit": "32G",
        "cpu_limit": "0.85",
        "performance_profile": "ultra",
        "torch_compile_mode": "max-autotune"
    },
    "M4_PRO": {
        "memory_limit": "24G", 
        "cpu_limit": "0.80",
        "performance_profile": "high",
        "torch_compile_mode": "default"
    },
    "M4_BASE": {
        "memory_limit": "16G",
        "cpu_limit": "0.75", 
        "performance_profile": "optimized",
        "torch_compile_mode": "default"
    }
}

# Apple Silicon support matrix
APPLE_SILICON_SUPPORT = {
    "M1": ["M1_BASE", "M1_PRO", "M1_MAX", "M1_ULTRA"],
    "M2": ["M2_BASE", "M2_PRO", "M2_MAX", "M2_ULTRA"],
    "M3": ["M3_BASE", "M3_PRO", "M3_MAX"],
    "M4": ["M4_BASE", "M4_PRO", "M4_MAX"]
}

def get_version_info():
    """Get comprehensive version information."""
    return {
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "description": __description__,
        "m4_support": True,
        "apple_silicon_variants": sum(len(variants) for variants in APPLE_SILICON_SUPPORT.values()),
        "latest_features": VERSION_HISTORY["2.5.0"]["features"]
    }
