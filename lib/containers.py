"""
Container management module for Singularity Launcher.
Provides functionality for managing containers using Docker or Podman.
"""
import os
import time
import subprocess
import threading
import json
import logging
import platform
import re
from typing import Dict, List, Any, Optional, Callable, Tuple

logger = logging.getLogger(__name__)

# Detect container runtime
def detect_container_runtime():
    """
    Detect available container runtime (Docker or Podman).
    
    Returns:
        str: 'docker', 'podman', or None if no runtime is available
    """
    # Check for Docker
    try:
        result = subprocess.run(['docker', 'version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True, 
                               check=False)
        if result.returncode == 0:
            return 'docker'
    except FileNotFoundError:
        pass
    
    # Check for Podman
    try:
        result = subprocess.run(['podman', 'version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True, 
                               check=False)
        if result.returncode == 0:
            return 'podman'
    except FileNotFoundError:
        pass
    
    return None

# Container runtime command
CONTAINER_RUNTIME = detect_container_runtime()

class ContainerManager:
    """
    Manager for container operations using Docker or Podman.
    """
    def __init__(self):
        """Initialize the container manager."""
        self.containers = {}
        self.running = False
        self.update_thread = None
        self.update_interval = 2  # seconds
        self.update_callbacks = []
        self.runtime = CONTAINER_RUNTIME
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
    
    def start(self):
        """Start the container monitoring thread."""
        if self.running:
            return
        
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        logger.info(f"Container monitoring started with {self.runtime}")
    
    def stop(self):
        """Stop the container monitoring thread."""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
            self.update_thread = None
        logger.info("Container monitoring stopped")
    
    def _update_loop(self):
        """Update container status periodically."""
        while self.running:
            try:
                self._update_containers()
                
                # Notify callbacks
                for callback in self.update_callbacks:
                    try:
                        callback(self.containers)
                    except Exception as e:
                        logger.error(f"Error in container update callback: {e}")
                
            except Exception as e:
                logger.error(f"Error updating containers: {e}")
            
            # Sleep for the update interval
            time.sleep(self.update_interval)
    
    def _update_containers(self):
        """Update container information."""
        if not self.runtime:
            logger.warning("No container runtime available")
            return
        
        try:
            # Get list of containers
            cmd = [self.runtime, 'ps', '-a', '--format', '{{json .}}']
            result = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True, 
                                   check=False)
            
            if result.returncode != 0:
                logger.error(f"Error getting container list: {result.stderr}")
                return
            
            # Parse container information
            new_containers = {}
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                try:
                    container_info = json.loads(line)
                    
                    # Extract container ID and name
                    container_id = container_info.get('ID', container_info.get('Id', ''))
                    container_name = container_info.get('Names', container_info.get('Name', ''))
                    
                    # Clean up container name (remove leading slash if present)
                    if container_name.startswith('/'):
                        container_name = container_name[1:]
                    
                    # Extract status
                    status = container_info.get('Status', '')
                    if 'Up' in status:
                        status = 'running'
                    elif 'Exited' in status or 'Dead' in status:
                        status = 'stopped'
                    else:
                        status = 'unknown'
                    
                    # Extract ports
                    ports = container_info.get('Ports', '')
                    
                    # Extract image
                    image = container_info.get('Image', '')
                    
                    # Store container information
                    new_containers[container_id] = {
                        'id': container_id,
                        'name': container_name,
                        'status': status,
                        'image': image,
                        'ports': ports,
                        'runtime': self.runtime
                    }
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse container info: {line}")
                except Exception as e:
                    logger.error(f"Error processing container info: {e}")
            
            # Update containers
            self.containers = new_containers
            
        except Exception as e:
            logger.error(f"Error updating containers: {e}")
    
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
        if not self.runtime:
            logger.warning("No container runtime available")
            return False
        
        try:
            cmd = [self.runtime, 'start', container_id]
            result = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True, 
                                   check=False)
            
            if result.returncode != 0:
                logger.error(f"Error starting container {container_id}: {result.stderr}")
                return False
            
            # Update container status
            self._update_containers()
            return True
            
        except Exception as e:
            logger.error(f"Error starting container {container_id}: {e}")
            return False
    
    def stop_container(self, container_id: str) -> bool:
        """
        Stop a container.
        
        Args:
            container_id (str): The container ID
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.runtime:
            logger.warning("No container runtime available")
            return False
        
        try:
            cmd = [self.runtime, 'stop', container_id]
            result = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True, 
                                   check=False)
            
            if result.returncode != 0:
                logger.error(f"Error stopping container {container_id}: {result.stderr}")
                return False
            
            # Update container status
            self._update_containers()
            return True
            
        except Exception as e:
            logger.error(f"Error stopping container {container_id}: {e}")
            return False
    
    def restart_container(self, container_id: str) -> bool:
        """
        Restart a container.
        
        Args:
            container_id (str): The container ID
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.runtime:
            logger.warning("No container runtime available")
            return False
        
        try:
            cmd = [self.runtime, 'restart', container_id]
            result = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True, 
                                   check=False)
            
            if result.returncode != 0:
                logger.error(f"Error restarting container {container_id}: {result.stderr}")
                return False
            
            # Update container status
            self._update_containers()
            return True
            
        except Exception as e:
            logger.error(f"Error restarting container {container_id}: {e}")
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
        if not self.runtime:
            logger.warning("No container runtime available")
            return ""
        
        try:
            cmd = [self.runtime, 'logs', '--tail', str(lines), container_id]
            result = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True, 
                                   check=False)
            
            if result.returncode != 0:
                logger.error(f"Error getting logs for container {container_id}: {result.stderr}")
                return f"Error: {result.stderr}"
            
            return result.stdout
            
        except Exception as e:
            logger.error(f"Error getting logs for container {container_id}: {e}")
            return f"Error: {str(e)}"
    
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
        if not self.runtime:
            logger.warning("No container runtime available")
            return False, "No container runtime available"
        
        try:
            # Determine compose command based on runtime
            if self.runtime == 'docker':
                compose_cmd = ['docker-compose']
            else:  # podman
                compose_cmd = ['podman-compose']
            
            # Build command
            cmd = compose_cmd + ['-f', compose_file]
            
            # Add project name if specified
            if project_name:
                cmd.extend(['-p', project_name])
            
            # Add up or down command
            cmd.append('up' if up else 'down')
            
            # Add -d flag for up command to run in detached mode
            if up:
                cmd.append('-d')
            
            # Set environment variables
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            
            # Run command
            logger.info(f"Running compose command: {' '.join(cmd)}")
            
            # Open log file if specified
            log_file_handle = None
            if log_file:
                log_file_handle = open(log_file, 'w')
            
            # Run command
            result = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE if not log_file_handle else log_file_handle,
                                   stderr=subprocess.PIPE if not log_file_handle else log_file_handle,
                                   text=True, 
                                   check=False,
                                   env=env)
            
            # Close log file if opened
            if log_file_handle:
                log_file_handle.close()
            
            if result.returncode != 0:
                logger.error(f"Error running compose file {compose_file}: {result.stderr}")
                
                # Read from log file if specified
                output = ""
                if log_file:
                    try:
                        with open(log_file, 'r') as f:
                            output = f.read()
                    except Exception as e:
                        logger.error(f"Error reading log file {log_file}: {e}")
                        output = f"Error reading log file: {str(e)}"
                else:
                    output = result.stderr
                
                return False, output
            
            # Read from log file if specified
            output = ""
            if log_file:
                try:
                    with open(log_file, 'r') as f:
                        output = f.read()
                except Exception as e:
                    logger.error(f"Error reading log file {log_file}: {e}")
                    output = f"Error reading log file: {str(e)}"
            else:
                output = result.stdout
            
            return True, output
            
        except Exception as e:
            logger.error(f"Error running compose file {compose_file}: {e}")
            return False, str(e)
    
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

def get_containers() -> Dict[str, Dict[str, Any]]:
    """
    Alias for get_all_containers for backward compatibility.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of containers indexed by container ID
    """
    return get_all_containers()

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
