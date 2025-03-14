"""
System Detection and Information Module

This module provides functions for detecting and gathering information about the system,
including CPU, GPU, memory, and operating system details.
"""

import platform
import os
import subprocess
import json
from typing import Dict, Any, List, Tuple, Optional

# Try to import hardware detection libraries
# These are optional and the module will work without them
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. System detection will be limited.")

try:
    import cpuinfo
    CPUINFO_AVAILABLE = True
except ImportError:
    CPUINFO_AVAILABLE = False
    print("Warning: py-cpuinfo not available. CPU detection will be limited.")

try:
    import GPUtil
    GPU_DETECTION_AVAILABLE = True
except ImportError:
    GPU_DETECTION_AVAILABLE = False
    print("Warning: GPUtil not available. GPU detection will be limited.")

# Overall hardware detection availability
HW_DETECTION_AVAILABLE = PSUTIL_AVAILABLE and CPUINFO_AVAILABLE

# Check if we're on ARM architecture
IS_ARM = platform.machine().lower() in ["aarch64", "armv7l", "arm64"]

# Define platform types
PLATFORM_TYPES = ["auto", "dgx", "jetson", "apple", "nvidia", "amd", "intel", "arm"]
CPU_TYPES = ["auto", "amd", "arm", "intel", "apple"]
GPU_TYPES = ["auto", "nvidia", "amd", "apple", "cpu"]

def detect_os() -> str:
    """
    Detect the operating system.
    
    Returns:
        str: The detected operating system (Linux, Windows, Mac, Other)
    """
    system = platform.system()
    if system == "Linux":
        try:
            with open("/etc/os-release") as f:
                os_release = f.read()
            if "Arch Linux" in os_release:
                return "Arch"
            elif "Pop!_OS" in os_release:
                return "PopOS"
            elif "Debian" in os_release:
                return "Debian"
            elif "Ubuntu" in os_release:
                return "Ubuntu"
            elif "Fedora" in os_release:
                return "Fedora"
            else:
                return "Linux"
        except:
            return "Linux"
    elif system == "Darwin":
        return "Mac"
    elif system == "Windows":
        return "Windows"
    else:
        return "Other"

def detect_cpu_type() -> str:
    """
    Detect the CPU type.
    
    Returns:
        str: The detected CPU type (amd, arm, intel, apple)
    """
    system = platform.system()
    machine = platform.machine().lower()
    
    # Check for Apple Silicon
    if system == "Darwin" and machine == "arm64":
        return "apple"
    
    # Check for ARM
    if machine in ["aarch64", "armv7l", "arm64"]:
        return "arm"
    
    # Check for AMD or Intel
    if HW_DETECTION_AVAILABLE:
        try:
            info = cpuinfo.get_cpu_info()
            vendor = info.get("vendor_id_raw", "").lower()
            if "amd" in vendor:
                return "amd"
            elif "intel" in vendor:
                return "intel"
        except:
            pass
    
    # Alternative check for AMD/Intel
    if system == "Linux":
        try:
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo_content = f.read().lower()
                if "amd" in cpuinfo_content:
                    return "amd"
                elif "intel" in cpuinfo_content:
                    return "intel"
        except:
            pass
    elif system == "Windows":
        try:
            processor = platform.processor().lower()
            if "amd" in processor:
                return "amd"
            elif "intel" in processor:
                return "intel"
        except:
            pass
    
    # Default to intel for x86_64
    if machine == "x86_64":
        return "intel"
    
    return "unknown"

def detect_gpu_type() -> str:
    """
    Detect the GPU type.
    
    Returns:
        str: The detected GPU type (nvidia, amd, apple, cpu)
    """
    system = platform.system()
    
    # Check for Apple Silicon
    if system == "Darwin" and platform.machine().lower() == "arm64":
        return "apple"
    
    # Check for NVIDIA GPU
    if GPU_DETECTION_AVAILABLE and not IS_ARM:
        try:
            nvidia_gpus = GPUtil.getGPUs()
            if nvidia_gpus:
                return "nvidia"
        except:
            pass
    
    # Check for NVIDIA GPU using nvidia-smi
    try:
        result = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if result.returncode == 0:
            return "nvidia"
    except:
        pass
    
    # Check for AMD GPU
    if system == "Linux":
        try:
            # Check for AMD GPU with ROCm
            if os.path.exists("/opt/rocm") or subprocess.run(["rocminfo"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False).returncode == 0:
                return "amd"
        except:
            pass
        
        # Check for AMD GPU in lspci
        try:
            result = subprocess.run(["lspci"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if "amd" in result.stdout.lower() and "vga" in result.stdout.lower():
                return "amd"
        except:
            pass
    elif system == "Windows":
        try:
            # Check for AMD GPU in Windows
            result = subprocess.run(["wmic", "path", "win32_VideoController", "get", "name"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if "amd" in result.stdout.lower() or "radeon" in result.stdout.lower():
                return "amd"
        except:
            pass
    
    # Default to CPU
    return "cpu"

def detect_platform() -> str:
    """
    Detect the hardware platform.
    
    Returns:
        str: The detected platform (dgx, jetson, apple, nvidia, amd, intel, arm)
    """
    system = platform.system()
    machine = platform.machine().lower()
    
    # Check for NVIDIA DGX
    if os.path.exists("/etc/dgx-release") or (os.path.exists("/proc/cpuinfo") and "NVIDIA DGX" in open("/proc/cpuinfo").read()):
        return "dgx"
    
    # Check for NVIDIA Jetson
    if os.path.exists("/etc/nv_tegra_release"):
        return "jetson"
    
    # Check for Apple Silicon
    if system == "Darwin" and machine == "arm64":
        return "apple"
    
    # Check for NVIDIA GPU
    gpu_type = detect_gpu_type()
    if gpu_type == "nvidia":
        return "nvidia"
    
    # Check for AMD GPU
    if gpu_type == "amd":
        return "amd"
    
    # Check for CPU type
    cpu_type = detect_cpu_type()
    if cpu_type in ["amd", "intel", "arm"]:
        return cpu_type
    
    # Default to the machine architecture
    if machine == "x86_64":
        return "intel"
    elif machine in ["aarch64", "armv7l", "arm64"]:
        return "arm"
    
    return "unknown"

def detect_jetson_model() -> str:
    """
    Detect the specific Jetson model.
    
    Returns:
        str: The detected Jetson model (orin_nano_4gb, orin_nano_8gb, orin_nx_8gb, orin_nx_16gb, agx_32gb, agx_64gb, unknown)
    """
    if not os.path.exists("/etc/nv_tegra_release"):
        return "unknown"
    
    # Check for Jetson model in device tree
    if os.path.exists("/proc/device-tree/model"):
        try:
            with open("/proc/device-tree/model", "r") as f:
                model = f.read().lower()
                
                # Detect Orin models
                if "orin" in model:
                    # Detect Orin Nano
                    if "nano" in model:
                        # Check memory
                        mem = get_system_memory()
                        if mem <= 4:
                            return "orin_nano_4gb"
                        else:
                            return "orin_nano_8gb"
                    
                    # Detect Orin NX
                    if "nx" in model:
                        # Check memory
                        mem = get_system_memory()
                        if mem <= 8:
                            return "orin_nx_8gb"
                        else:
                            return "orin_nx_16gb"
                    
                    # Detect AGX Orin
                    if "agx" in model:
                        # Check memory
                        mem = get_system_memory()
                        if mem <= 32:
                            return "agx_32gb"
                        else:
                            return "agx_64gb"
                
                # Default to unknown Jetson
                return "unknown_jetson"
        except:
            pass
    
    # Default to unknown
    return "unknown"

def get_system_memory() -> int:
    """
    Get the system memory in GB.
    
    Returns:
        int: The system memory in GB
    """
    if HW_DETECTION_AVAILABLE:
        try:
            mem = psutil.virtual_memory()
            return round(mem.total / (1024**3))
        except:
            pass
    
    # Try to get memory from OS-specific commands
    system = platform.system()
    if system == "Linux":
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemTotal" in line:
                        # Extract the memory value in KB and convert to GB
                        mem_kb = int(line.split()[1])
                        return round(mem_kb / (1024**2))
        except:
            pass
    elif system == "Windows":
        try:
            result = subprocess.run(["wmic", "computersystem", "get", "totalphysicalmemory"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if result.returncode == 0:
                # Extract the memory value in bytes and convert to GB
                mem_bytes = int(result.stdout.strip().split("\n")[1])
                return round(mem_bytes / (1024**3))
        except:
            pass
    elif system == "Darwin":
        try:
            result = subprocess.run(["sysctl", "-n", "hw.memsize"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if result.returncode == 0:
                # Extract the memory value in bytes and convert to GB
                mem_bytes = int(result.stdout.strip())
                return round(mem_bytes / (1024**3))
        except:
            pass
    
    # Default to 8GB
    return 8

def get_cpu_info() -> Dict[str, Any]:
    """
    Get detailed CPU information.
    
    Returns:
        Dict[str, Any]: CPU information including brand, cores, and architecture
    """
    if HW_DETECTION_AVAILABLE:
        try:
            info = cpuinfo.get_cpu_info()
            return {
                "brand": info.get("brand_raw", "Unknown CPU"),
                "cores": info.get("count", 4),
                "arch": info.get("arch", platform.machine()),
                "type": detect_cpu_type()
            }
        except:
            pass
    
    # Get basic CPU info from platform
    return {
        "brand": platform.processor() or "Unknown CPU",
        "cores": os.cpu_count() or 4,
        "arch": platform.machine(),
        "type": detect_cpu_type()
    }

def get_gpu_info() -> Dict[str, Any]:
    """
    Get detailed GPU information.
    
    Returns:
        Dict[str, Any]: GPU information including name, memory, and type
    """
    gpu_type = detect_gpu_type()
    
    if gpu_type == "nvidia" and GPU_DETECTION_AVAILABLE:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                return {
                    "name": gpus[0].name,
                    "memory": round(gpus[0].memoryTotal / 1024),  # Convert to GB
                    "type": "nvidia"
                }
        except:
            pass
        
        # Try nvidia-smi
        try:
            result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if result.returncode == 0:
                parts = result.stdout.strip().split(",")
                if len(parts) >= 2:
                    return {
                        "name": parts[0].strip(),
                        "memory": round(float(parts[1].strip()) / 1024),  # Convert to GB
                        "type": "nvidia"
                    }
        except:
            pass
    
    elif gpu_type == "amd":
        # Try to get AMD GPU info
        if platform.system() == "Linux":
            try:
                result = subprocess.run(["lspci", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
                if result.returncode == 0:
                    for line in result.stdout.split("\n"):
                        if "VGA" in line and ("AMD" in line or "ATI" in line):
                            return {
                                "name": line.split(":")[-1].strip(),
                                "memory": 0,  # Cannot determine memory easily
                                "type": "amd"
                            }
            except:
                pass
        elif platform.system() == "Windows":
            try:
                result = subprocess.run(["wmic", "path", "win32_VideoController", "get", "name,AdapterRAM"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")[1:]
                    for line in lines:
                        if "amd" in line.lower() or "radeon" in line.lower():
                            parts = line.split()
                            if len(parts) >= 2:
                                try:
                                    memory = round(int(parts[-1]) / (1024**3))  # Convert to GB
                                    return {
                                        "name": " ".join(parts[:-1]),
                                        "memory": memory,
                                        "type": "amd"
                                    }
                                except:
                                    return {
                                        "name": line.strip(),
                                        "memory": 0,
                                        "type": "amd"
                                    }
            except:
                pass
    
    elif gpu_type == "apple":
        return {
            "name": "Apple Silicon GPU",
            "memory": 0,  # Shared with system memory
            "type": "apple"
        }
    
    # Default GPU info
    return {
        "name": "CPU (No dedicated GPU)",
        "memory": 0,
        "type": "cpu"
    }

def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information.
    
    Returns:
        Dict[str, Any]: System information including OS, CPU, GPU, memory, and platform details
    """
    return {
        "os": {
            "name": detect_os(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version()
        },
        "cpu": get_cpu_info(),
        "gpu": get_gpu_info(),
        "memory": {
            "total": get_system_memory(),
            "unit": "GB"
        },
        "platform": detect_platform(),
        "jetson_model": detect_jetson_model() if detect_platform() == "jetson" else None
    }

def detect_container_engine() -> str:
    """
    Detect the available container engine.
    
    Returns:
        str: The detected container engine (podman, docker, none)
    """
    # Check for Podman
    try:
        result = subprocess.run(["podman", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if result.returncode == 0:
            return "podman"
    except:
        pass
    
    # Check for Docker
    try:
        result = subprocess.run(["docker", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if result.returncode == 0:
            return "docker"
    except:
        pass
    
    # No container engine found
    return "none"

def get_container_engine_info() -> Dict[str, Any]:
    """
    Get information about the available container engine.
    
    Returns:
        Dict[str, Any]: Container engine information including name and version
    """
    engine = detect_container_engine()
    
    if engine == "podman":
        try:
            result = subprocess.run(["podman", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if result.returncode == 0:
                return {
                    "name": "podman",
                    "version": result.stdout.strip(),
                    "available": True
                }
        except:
            pass
    
    elif engine == "docker":
        try:
            result = subprocess.run(["docker", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if result.returncode == 0:
                return {
                    "name": "docker",
                    "version": result.stdout.strip(),
                    "available": True
                }
        except:
            pass
    
    # No container engine found
    return {
        "name": "none",
        "version": "",
        "available": False
    }

if __name__ == "__main__":
    # Print system information when run directly
    system_info = get_system_info()
    print(json.dumps(system_info, indent=2))
    
    # Print container engine information
    container_info = get_container_engine_info()
    print("\nContainer Engine:")
    print(json.dumps(container_info, indent=2))
