"""
Performance monitoring module for Singularity Launcher.
Provides functionality for monitoring system performance metrics.
"""
import os
import time
import threading
import platform
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available, some performance metrics will be limited")

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False
    logger.warning("GPUtil not available, GPU metrics will be limited")

try:
    import py_cpuinfo
    CPUINFO_AVAILABLE = True
except ImportError:
    CPUINFO_AVAILABLE = False
    logger.warning("py-cpuinfo not available, CPU info will be limited")

class PerformanceMonitor:
    """
    Monitor system performance metrics.
    """
    def __init__(self):
        """Initialize the performance monitor."""
        # CPU metrics
        self.cpu_usage = 0.0
        self.cpu_temp = 0.0
        self.cpu_type = "Unknown"
        
        # Memory metrics
        self.memory_usage = 0.0
        self.memory_total = 0
        
        # GPU metrics
        self.gpu_usage = 0.0
        self.gpu_temp = 0.0
        self.gpu_memory_usage = 0.0
        self.gpu_memory_total = 0
        self.gpu_type = "Unknown"
        
        # Disk metrics
        self.disk_usage = 0.0
        self.disk_total = 0
        self.disk_used = 0
        
        # Monitoring state
        self.running = False
        self.update_thread = None
        self.update_interval = 2  # seconds
        self.update_callbacks = []
        
        # Initialize CPU info
        self._initialize_cpu_info()
        
        # Initialize GPU info
        self._initialize_gpu_info()
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
    
    def _initialize_cpu_info(self):
        """Initialize CPU information."""
        if CPUINFO_AVAILABLE:
            try:
                info = py_cpuinfo.get_cpu_info()
                self.cpu_type = info.get('brand_raw', "Unknown")
            except:
                pass
        else:
            # Try to get CPU info from /proc/cpuinfo on Linux
            if platform.system() == "Linux":
                try:
                    with open("/proc/cpuinfo", "r") as f:
                        for line in f:
                            if line.startswith("model name"):
                                self.cpu_type = line.split(":")[1].strip()
                                break
                except:
                    pass
            # Try to get CPU info on macOS
            elif platform.system() == "Darwin":
                try:
                    import subprocess
                    result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE, 
                                          text=True, 
                                          check=False)
                    if result.returncode == 0:
                        self.cpu_type = result.stdout.strip()
                except:
                    pass
    
    def _initialize_gpu_info(self):
        """Initialize GPU information."""
        if GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    self.gpu_type = gpus[0].name
                    self.gpu_memory_total = gpus[0].memoryTotal
            except:
                pass
        else:
            # Try to get NVIDIA GPU info on Linux
            if platform.system() == "Linux":
                try:
                    import subprocess
                    result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE, 
                                          text=True, 
                                          check=False)
                    if result.returncode == 0:
                        parts = result.stdout.strip().split(',')
                        if len(parts) >= 2:
                            self.gpu_type = parts[0].strip()
                            self.gpu_memory_total = int(parts[1].strip().split()[0])
                except:
                    pass
            
            # Check for Apple Silicon GPU
            if platform.system() == "Darwin" and platform.processor() == "arm":
                self.gpu_type = "Apple Silicon"
                # We can't easily get the GPU memory on Apple Silicon
                self.gpu_memory_total = 0
    
    def start(self):
        """Start the performance monitoring thread."""
        if self.running:
            return
        
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        logger.info("Performance monitoring started")
    
    def stop(self):
        """Stop the performance monitoring thread."""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
            self.update_thread = None
        logger.info("Performance monitoring stopped")
    
    def _update_loop(self):
        """Update performance metrics periodically."""
        while self.running:
            try:
                self._update_metrics()
                
                # Notify callbacks
                metrics = self.get_metrics()
                for callback in self.update_callbacks:
                    try:
                        callback(metrics)
                    except Exception as e:
                        logger.error(f"Error in performance update callback: {e}")
                
            except Exception as e:
                logger.error(f"Error updating performance metrics: {e}")
            
            # Sleep for the update interval
            time.sleep(self.update_interval)
    
    def _update_metrics(self):
        """Update all performance metrics."""
        self._update_cpu_metrics()
        self._update_memory_metrics()
        self._update_gpu_metrics()
        self._update_disk_metrics()
    
    def _update_cpu_metrics(self):
        """Update CPU usage and temperature metrics."""
        if PSUTIL_AVAILABLE:
            try:
                self.cpu_usage = psutil.cpu_percent(interval=0.1)
            except:
                self.cpu_usage = self._estimate_cpu_usage()
        else:
            self.cpu_usage = self._estimate_cpu_usage()
        
        # Try to get CPU temperature on Linux
        if platform.system() == "Linux":
            try:
                # Try to read from thermal zone
                for i in range(10):  # Check up to 10 thermal zones
                    path = f"/sys/class/thermal/thermal_zone{i}/temp"
                    if os.path.exists(path):
                        with open(path, "r") as f:
                            temp = float(f.read().strip()) / 1000  # Convert from millidegrees to degrees
                            if temp > 0 and temp < 150:  # Sanity check
                                self.cpu_temp = temp
                                break
            except:
                pass
    
    def _update_memory_metrics(self):
        """Update memory usage metrics."""
        if PSUTIL_AVAILABLE:
            try:
                memory = psutil.virtual_memory()
                self.memory_usage = memory.percent
                self.memory_total = round(memory.total / (1024**3))  # Convert to GB
            except:
                pass
        else:
            # Try to get memory info from /proc/meminfo on Linux
            if platform.system() == "Linux":
                try:
                    with open("/proc/meminfo", "r") as f:
                        mem_total = 0
                        mem_free = 0
                        mem_available = 0
                        
                        for line in f:
                            if line.startswith("MemTotal:"):
                                mem_total = int(line.split()[1]) * 1024  # Convert from KB to bytes
                            elif line.startswith("MemFree:"):
                                mem_free = int(line.split()[1]) * 1024  # Convert from KB to bytes
                            elif line.startswith("MemAvailable:"):
                                mem_available = int(line.split()[1]) * 1024  # Convert from KB to bytes
                        
                        if mem_total > 0:
                            self.memory_total = round(mem_total / (1024**3))  # Convert to GB
                            if mem_available > 0:
                                self.memory_usage = 100.0 * (1.0 - mem_available / mem_total)
                            elif mem_free > 0:
                                self.memory_usage = 100.0 * (1.0 - mem_free / mem_total)
                except:
                    pass
    
    def _update_gpu_metrics(self):
        """Update GPU usage and temperature metrics."""
        if GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    self.gpu_usage = gpus[0].load * 100
                    self.gpu_temp = gpus[0].temperature
                    self.gpu_memory_usage = gpus[0].memoryUtil * 100
            except:
                pass
        else:
            # Try to get NVIDIA GPU info on Linux
            if platform.system() == "Linux" and self.gpu_type != "Unknown" and "NVIDIA" in self.gpu_type:
                try:
                    import subprocess
                    result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,temperature.gpu,memory.used', '--format=csv,noheader'], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE, 
                                          text=True, 
                                          check=False)
                    if result.returncode == 0:
                        parts = result.stdout.strip().split(',')
                        if len(parts) >= 3:
                            self.gpu_usage = float(parts[0].strip().split()[0])
                            self.gpu_temp = float(parts[1].strip())
                            gpu_memory_used = int(parts[2].strip().split()[0])
                            if self.gpu_memory_total > 0:
                                self.gpu_memory_usage = 100.0 * gpu_memory_used / self.gpu_memory_total
                except:
                    pass
            
            # Try to get GPU temperature from sysfs on Linux
            if platform.system() == "Linux" and self.gpu_temp == 0:
                try:
                    # AMD GPU temperature
                    if os.path.exists("/sys/class/drm/card0/device/hwmon/hwmon0/temp1_input"):
                        with open("/sys/class/drm/card0/device/hwmon/hwmon0/temp1_input", "r") as f:
                            self.gpu_temp = float(f.read().strip()) / 1000  # Convert from millidegrees to degrees
                except:
                    pass
    
    def _update_disk_metrics(self):
        """Update disk usage metrics."""
        if PSUTIL_AVAILABLE:
            try:
                # Get disk usage for the root directory
                disk = psutil.disk_usage("/")
                self.disk_usage = disk.percent
                self.disk_total = round(disk.total / (1024**3))  # Convert to GB
                self.disk_used = round(disk.used / (1024**3))  # Convert to GB
            except:
                pass
    
    def _estimate_cpu_usage(self) -> float:
        """
        Estimate CPU usage without psutil.
        
        Returns:
            float: Estimated CPU usage percentage
        """
        # This is a very crude estimation and not accurate
        # It's only used as a fallback when psutil is not available
        if platform.system() == "Linux":
            try:
                with open("/proc/stat", "r") as f:
                    cpu_line = f.readline().strip()
                    cpu_values = [float(x) for x in cpu_line.split()[1:]]
                    idle = cpu_values[3]
                    total = sum(cpu_values)
                    return 100.0 * (1.0 - idle / total)
            except:
                return 0.0
        
        return 0.0
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all performance metrics.
        
        Returns:
            Dict[str, Any]: Dictionary containing all performance metrics
        """
        return {
            "cpu": {
                "usage": self.cpu_usage,
                "temperature": self.cpu_temp,
                "type": self.cpu_type
            },
            "memory": {
                "usage": self.memory_usage,
                "total": self.memory_total,
                "unit": "GB"
            },
            "gpu": {
                "usage": self.gpu_usage,
                "temperature": self.gpu_temp,
                "memory_usage": self.gpu_memory_usage,
                "memory_total": self.gpu_memory_total,
                "type": self.gpu_type
            },
            "disk": {
                "usage": self.disk_usage,
                "total": self.disk_total,
                "used": self.disk_used,
                "unit": "GB"
            }
        }
    
    def add_update_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Add a callback function to be called when metrics are updated.
        
        Args:
            callback (Callable[[Dict[str, Any]], None]): The callback function
        """
        self.update_callbacks.append(callback)
    
    def remove_update_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Remove a callback function.
        
        Args:
            callback (Callable[[Dict[str, Any]], None]): The callback function to remove
        """
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)

# Singleton instance for global use
monitor = PerformanceMonitor()

def start_monitoring():
    """Start the global performance monitor."""
    monitor.start()

def stop_monitoring():
    """Stop the global performance monitor."""
    monitor.stop()

def get_current_metrics() -> Dict[str, Any]:
    """
    Get the current performance metrics.
    
    Returns:
        Dict[str, Any]: Dictionary containing all performance metrics
    """
    return monitor.get_metrics()

def monitor_system_performance():
    """
    Alias for start_monitoring for backward compatibility.
    Starts the performance monitoring system.
    """
    start_monitoring()
    return get_current_metrics()

def add_metrics_callback(callback: Callable[[Dict[str, Any]], None]):
    """
    Add a callback function to be called when metrics are updated.
    
    Args:
        callback (Callable[[Dict[str, Any]], None]): The callback function
    """
    monitor.add_update_callback(callback)

def remove_metrics_callback(callback: Callable[[Dict[str, Any]], None]):
    """
    Remove a callback function.
    
    Args:
        callback (Callable[[Dict[str, Any]], None]): The callback function to remove
    """
    monitor.remove_update_callback(callback)

if __name__ == "__main__":
    # Test the performance monitor when run directly
    def print_metrics(metrics):
        print(f"CPU: {metrics['cpu']['usage']:.1f}% ({metrics['cpu']['temperature']:.1f}°C)")
        print(f"Memory: {metrics['memory']['usage']:.1f}% ({metrics['memory']['total']} GB)")
        print(f"GPU: {metrics['gpu']['usage']:.1f}% ({metrics['gpu']['temperature']:.1f}°C)")
        print(f"Disk: {metrics['disk']['usage']:.1f}% ({metrics['disk']['used']}/{metrics['disk']['total']} GB)")
        print("-" * 40)
    
    # Add the callback
    add_metrics_callback(print_metrics)
    
    # Start monitoring
    start_monitoring()
    
    try:
        # Run for 10 seconds
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop monitoring
        stop_monitoring()
