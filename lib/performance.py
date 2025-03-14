"""
Performance Monitoring Module

This module provides functions and classes for monitoring system performance,
including CPU, GPU, memory, and disk usage.
"""

import time
import threading
import platform
from typing import Dict, Any, List, Tuple, Optional, Callable

# Try to import hardware monitoring libraries
# These are optional and the module will work without them
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. Performance monitoring will be limited.")

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False
    print("Warning: GPUtil not available. GPU monitoring will be limited.")

# Import system module for hardware detection
from lib.system import detect_gpu_type, detect_cpu_type, get_system_memory

class PerformanceMonitor:
    """
    A class for monitoring system performance metrics.
    
    This class provides methods for collecting and retrieving performance data
    for CPU, GPU, memory, and disk usage.
    """
    
    def __init__(self, update_interval: float = 1.0):
        """
        Initialize the performance monitor.
        
        Args:
            update_interval (float): The interval in seconds between updates
        """
        self.update_interval = update_interval
        self.running = False
        self.thread = None
        
        # Performance data
        self.cpu_usage = 0.0
        self.cpu_temp = 0.0
        self.memory_usage = 0.0
        self.memory_total = get_system_memory()
        self.gpu_usage = 0.0
        self.gpu_temp = 0.0
        self.gpu_memory_usage = 0.0
        self.gpu_memory_total = 0
        self.disk_usage = 0.0
        self.disk_total = 0
        self.disk_used = 0
        
        # Hardware types
        self.cpu_type = detect_cpu_type()
        self.gpu_type = detect_gpu_type()
        
        # Callbacks
        self.update_callbacks = []
    
    def start(self):
        """Start the performance monitoring thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the performance monitoring thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
    
    def _monitor_loop(self):
        """Main monitoring loop that updates performance metrics."""
        while self.running:
            self._update_metrics()
            
            # Call update callbacks
            for callback in self.update_callbacks:
                try:
                    callback(self.get_metrics())
                except Exception as e:
                    print(f"Error in update callback: {e}")
            
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
            # Update CPU usage
            self.cpu_usage = psutil.cpu_percent(interval=None)
            
            # Update CPU temperature
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    # Different systems report CPU temp under different keys
                    for key in ["coretemp", "k10temp", "cpu_thermal"]:
                        if key in temps and temps[key]:
                            self.cpu_temp = temps[key][0].current
                            break
        else:
            # Fallback to simple CPU usage estimation
            self.cpu_usage = self._estimate_cpu_usage()
    
    def _update_memory_metrics(self):
        """Update memory usage metrics."""
        if PSUTIL_AVAILABLE:
            mem = psutil.virtual_memory()
            self.memory_usage = mem.percent
            self.memory_total = round(mem.total / (1024**3))  # Convert to GB
        else:
            # No fallback for memory usage
            pass
    
    def _update_gpu_metrics(self):
        """Update GPU usage and temperature metrics."""
        if self.gpu_type == "nvidia" and GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    self.gpu_usage = gpus[0].load * 100  # Convert to percentage
                    self.gpu_temp = gpus[0].temperature
                    self.gpu_memory_usage = gpus[0].memoryUtil * 100  # Convert to percentage
                    self.gpu_memory_total = round(gpus[0].memoryTotal / 1024)  # Convert to GB
            except:
                pass
        elif self.gpu_type == "amd":
            # Try to get AMD GPU metrics
            self._update_amd_gpu_metrics()
        elif self.gpu_type == "apple":
            # Apple Silicon GPU metrics not easily available
            pass
    
    def _update_amd_gpu_metrics(self):
        """Update AMD GPU metrics."""
        if platform.system() == "Linux":
            try:
                # Try to read GPU usage from sysfs
                with open("/sys/class/drm/card0/device/gpu_busy_percent", "r") as f:
                    self.gpu_usage = float(f.read().strip())
                
                # Try to read GPU temperature from sysfs
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
