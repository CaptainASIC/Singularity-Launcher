"""
Container Management Module

This module provides functions and classes for managing containers using Podman or Docker,
including starting, stopping, and monitoring containers.
"""

import os
import subprocess
import json
import time
import threading
from typing import Dict, Any, List, Tuple, Optional, Callable

# Try to import podman-py (optional)
PODMAN_PY_AVAILABLE = False
try:
    import podman
    PODMAN_PY_AVAILABLE = True
except ImportError:
    pass

# Import system module for container engine detection
from lib.system import detect_container_engine

class ContainerManager:
    """
    A class for managing containers using Podman or Docker.
    
    This class provides methods for starting, stopping, and monitoring containers,
    as well as retrieving container information.
    """
    
    def __init__(self, update_interval: float = 5.0):
        """
        Initialize the container manager.
        
        Args:
            update_interval (float): The interval in seconds between container status updates
        """
        self.update_interval = update_interval
        self.running = False
        self.thread = None
        
        # Detect container engine
        self.engine = detect_container_engine()
        
        # Container data
        self.containers = {}
        
        # Callbacks
        self.update_callbacks = []
    
    def start(self):
        """Start the container monitoring thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the container monitoring thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
    
    def _monitor_loop(self):
        """Main monitoring loop that updates container status."""
        while self.running:
            self._update_containers()
            
            # Call update callbacks
            for callback in self.update_callbacks:
                try:
                    callback(self.get_containers())
                except Exception as e:
                    print(f"Error in update callback: {e}")
            
            time.sleep(self.update_interval)
    
    def _update_containers(self):
        """Update container information."""
        if self.engine == "none":
            return
        
        try:
            if self.engine == "podman":
                self._update_podman_containers()
            elif self.engine == "docker":
                self._update_docker_containers()
        except Exception as e:
            print(f"Error updating containers: {e}")
    
    def _update_podman_containers(self):
        """Update container information using Podman."""
        try:
            # Get all containers
            result = subprocess.run(
                ["podman", "ps", "-a", "--format", "json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                print(f"Error getting Podman containers: {result.stderr}")
                return
            
            # Parse JSON output
            containers_data = json.loads(result.stdout)
            
            # Update containers dictionary
            new_containers = {}
            for container in containers_data:
                container_id = container.get("Id", "")
                name = container.get("Names", [""])[0]
                status = container.get("State", "unknown")
                image = container.get("Image", "")
                
                new_containers[container_id] = {
                    "id": container_id,
                    "name": name,
                    "status": status,
                    "image": image,
                    "engine": "podman"
                }
            
            # Update the containers dictionary
            self.containers = new_containers
        
        except Exception as e:
            print(f"Error updating Podman containers: {e}")
    
    def _update_docker_containers(self):
        """Update container information using Docker."""
        try:
            # Get all containers
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{json .}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                print(f"Error getting Docker containers: {result.stderr}")
                return
            
            # Parse JSON output (one container per line)
            new_containers = {}
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                
                try:
                    container = json.loads(line)
                    container_id = container.get("ID", "")
                    name = container.get("Names", "")
                    status = container.get("State", "unknown")
                    image = container.get("Image", "")
                    
                    new_containers[container_id] = {
                        "id": container_id,
                        "name": name,
                        "status": status,
                        "image": image,
                        "engine": "docker"
                    }
                except json.JSONDecodeError:
                    continue
            
            # Update the containers dictionary
            self.containers = new_containers
        
        except Exception as e:
            print(f"Error updating Docker containers: {e}")
    
    def get_containers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all containers.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of containers indexed by container ID
        """
        return self.containers
    
    def get_container(self, container_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information for a specific container.
        
        Args:
            container_id (str): The container ID
        
        Returns:
            Optional[Dict[str, Any]]: Container information or None if not found
        """
        return self.containers.get(container_id)
    
    def start_container(self, container_id: str) -> bool:
        """
        Start a container.
        
        Args:
            container_id (str): The container ID
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.engine == "none":
            return False
        
        try:
            if self.engine == "podman":
                result = subprocess.run(
                    ["podman", "start", container_id],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
            elif self.engine == "docker":
                result = subprocess.run(
                    ["docker", "start", container_id],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
            else:
                return False
            
            # Update containers immediately
            self._update_containers()
            
            return result.returncode == 0
        
        except Exception as e:
            print(f"Error starting container {container_id}: {e}")
            return False
    
    def stop_container(self, container_id: str) -> bool:
        """
        Stop a container.
        
        Args:
            container_id (str): The container ID
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.engine == "none":
            return False
        
        try:
            if self.engine == "podman":
                result = subprocess.run(
                    ["podman", "stop", container_id],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
            elif self.engine == "docker":
                result = subprocess.run(
                    ["docker", "stop", container_id],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
            else:
                return False
            
            # Update containers immediately
            self._update_containers()
            
            return result.returncode == 0
        
        except Exception as e:
            print(f"Error stopping container {container_id}: {e}")
            return False
    
    def restart_container(self, container_id: str) -> bool:
        """
        Restart a container.
        
        Args:
            container_id (str): The container ID
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.engine == "none":
            return False
        
        try:
            if self.engine == "podman":
                result = subprocess.run(
                    ["podman", "restart", container_id],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
            elif self.engine == "docker":
                result = subprocess.run(
                    ["docker", "restart", container_id],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
            else:
                return False
            
            # Update containers immediately
            self._update_containers()
            
            return result.returncode == 0
        
        except Exception as e:
            print(f"Error restarting container {container_id}: {e}")
            return False
    
    def get_container_logs(self, container_id: str, lines: int = 100) -> str:
        """
        Get logs for a container.
        
        Args:
            container_id (str): The container ID
            lines (int): Number of lines to retrieve
        
        Returns:
            str: Container logs
        """
        if self.engine == "none":
            return ""
        
        try:
            if self.engine == "podman":
                result = subprocess.run(
                    ["podman", "logs", "--tail", str(lines), container_id],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
            elif self.engine == "docker":
                result = subprocess.run(
                    ["docker", "logs", "--tail", str(lines), container_id],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
            else:
                return ""
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error getting logs: {result.stderr}"
        
        except Exception as e:
            return f"Error getting logs: {e}"
    
    def run_compose(self, compose_file: str, project_name: str = None, up: bool = True, 
                   env_vars: Dict[str, str] = None, log_file: str = None) -> Tuple[bool, str]:
        """
        Run a compose file.
        
        Args:
            compose_file (str): Path to the compose file
            project_name (str, optional): Project name
            up (bool): True to run 'up', False to run 'down'
            env_vars (Dict[str, str], optional): Environment variables to pass to the compose command
            log_file (str, optional): Path to a log file to write output
        
        Returns:
            Tuple[bool, str]: (success, output) where success is True if successful, False otherwise,
                             and output is the command output
        """
        if self.engine == "none":
            return False, "No container engine available"
        
        try:
            # Convert to absolute path if it's a relative path
            if not os.path.isabs(compose_file):
                # Get the absolute path to the project directory
                project_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                compose_file = os.path.join(project_dir, compose_file)
            
            cmd = []
            
            if self.engine == "podman":
                cmd = ["podman compose"]
            elif self.engine == "docker":
                cmd = ["docker compose"]
            else:
                return False, f"Unsupported container engine: {self.engine}"
            
            if project_name:
                cmd.extend(["-p", project_name])
            
            cmd.extend(["-f", compose_file])
            
            if up:
                cmd.append("up")
                cmd.append("-d")  # Detached mode
            else:
                cmd.append("down")
            
            # Create environment for the subprocess
            env = os.environ.copy()
            if env_vars:
                for key, value in env_vars.items():
                    env[key] = value
            
            # Run the command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                env=env
            )
            
            # Combine stdout and stderr for the output
            output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
            
            # Write to log file if provided
            if log_file:
                log_dir = os.path.dirname(log_file)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                
                with open(log_file, "w") as f:
                    f.write(f"Command: {' '.join(cmd)}\n")
                    f.write(f"Environment variables: {env_vars}\n")
                    f.write(f"Return code: {result.returncode}\n\n")
                    f.write(output)
            
            # Update containers immediately
            self._update_containers()
            
            return result.returncode == 0, output
        
        except Exception as e:
            error_msg = f"Error running compose file {compose_file}: {e}"
            print(error_msg)
            
            # Write to log file if provided
            if log_file:
                log_dir = os.path.dirname(log_file)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                
                with open(log_file, "w") as f:
                    f.write(f"Command: {' '.join(cmd) if 'cmd' in locals() else 'Unknown'}\n")
                    f.write(f"Environment variables: {env_vars}\n")
                    f.write(f"Exception: {str(e)}\n")
            
            return False, error_msg
    
    def add_update_callback(self, callback: Callable[[Dict[str, Dict[str, Any]]], None]):
        """
        Add a callback function to be called when container status is updated.
        
        Args:
            callback (Callable[[Dict[str, Dict[str, Any]]], None]): The callback function
        """
        self.update_callbacks.append(callback)
    
    def remove_update_callback(self, callback: Callable[[Dict[str, Dict[str, Any]]], None]):
        """
        Remove a callback function.
        
        Args:
            callback (Callable[[Dict[str, Dict[str, Any]]], None]): The callback function to remove
        """
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)

# Singleton instance for global use
manager = ContainerManager()

def start_container_monitoring():
    """Start the global container manager."""
    manager.start()

def stop_container_monitoring():
    """Stop the global container manager."""
    manager.stop()

def get_all_containers() -> Dict[str, Dict[str, Any]]:
    """
    Get all containers.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of containers indexed by container ID
    """
    return manager.get_containers()

def get_container(container_id: str) -> Optional[Dict[str, Any]]:
    """
    Get information for a specific container.
    
    Args:
        container_id (str): The container ID
    
    Returns:
        Optional[Dict[str, Any]]: Container information or None if not found
    """
    return manager.get_container(container_id)

def start_container(container_id: str) -> bool:
    """
    Start a container.
    
    Args:
        container_id (str): The container ID
    
    Returns:
        bool: True if successful, False otherwise
    """
    return manager.start_container(container_id)

def stop_container(container_id: str) -> bool:
    """
    Stop a container.
    
    Args:
        container_id (str): The container ID
    
    Returns:
        bool: True if successful, False otherwise
    """
    return manager.stop_container(container_id)

def restart_container(container_id: str) -> bool:
    """
    Restart a container.
    
    Args:
        container_id (str): The container ID
    
    Returns:
        bool: True if successful, False otherwise
    """
    return manager.restart_container(container_id)

def get_container_logs(container_id: str, lines: int = 100) -> str:
    """
    Get logs for a container.
    
    Args:
        container_id (str): The container ID
        lines (int): Number of lines to retrieve
    
    Returns:
        str: Container logs
    """
    return manager.get_container_logs(container_id, lines)

def run_compose(compose_file: str, project_name: str = None, up: bool = True, 
               env_vars: Dict[str, str] = None, log_file: str = None) -> Tuple[bool, str]:
    """
    Run a compose file.
    
    Args:
        compose_file (str): Path to the compose file
        project_name (str, optional): Project name
        up (bool): True to run 'up', False to run 'down'
        env_vars (Dict[str, str], optional): Environment variables to pass to the compose command
        log_file (str, optional): Path to a log file to write output
    
    Returns:
        Tuple[bool, str]: (success, output) where success is True if successful, False otherwise,
                         and output is the command output
    """
    # Convert to absolute path if it's a relative path
    if not os.path.isabs(compose_file):
        # Get the absolute path to the project directory
        project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        compose_file = os.path.join(project_dir, compose_file)
    
    return manager.run_compose(compose_file, project_name, up, env_vars, log_file)

def add_container_callback(callback: Callable[[Dict[str, Dict[str, Any]]], None]):
    """
    Add a callback function to be called when container status is updated.
    
    Args:
        callback (Callable[[Dict[str, Dict[str, Any]]], None]): The callback function
    """
    manager.add_update_callback(callback)

def remove_container_callback(callback: Callable[[Dict[str, Dict[str, Any]]], None]):
    """
    Remove a callback function.
    
    Args:
        callback (Callable[[Dict[str, Dict[str, Any]]], None]): The callback function to remove
    """
    manager.remove_update_callback(callback)

if __name__ == "__main__":
    # Test the container manager when run directly
    def print_containers(containers):
        print(f"Found {len(containers)} containers:")
        for container_id, container in containers.items():
            print(f"  {container['name']} ({container_id[:12]}): {container['status']}")
        print("-" * 40)
    
    # Add the callback
    add_container_callback(print_containers)
    
    # Start monitoring
    start_container_monitoring()
    
    try:
        # Run for 10 seconds
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop monitoring
        stop_container_monitoring()
