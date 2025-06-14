"""
Initialization and error handling utilities for Singularity Launcher
Provides robust application initialization and error recovery.

Version 2.5.0 - Enhanced UI & Optimized Scripts
"""
import streamlit as st
import os
import sys
import logging
import traceback
from typing import Dict, Any, Optional, Callable, Tuple

from lib.utils.state_management import StateManager

logger = logging.getLogger("singularity_launcher")

class InitializationManager:
    """
    Manages application initialization with proper error handling and recovery.
    """
    
    @staticmethod
    def initialize_application() -> bool:
        """
        Initialize the application with proper error handling.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Set up application defaults
            app_defaults = {
                "page": "Home",
                "containers": {},
                "system_info": {},
                "performance_data": {},
                "debug_mode": False,
                "initialization_complete": False,
                "dark_mode": True,
                "show_advanced": False,
                "auto_refresh": True,
                "refresh_interval": 5,
            }
            
            # Initialize session state with defaults
            StateManager.initialize_state(app_defaults)
            
            # Perform system detection
            InitializationManager._initialize_system_info()
            
            # Perform container detection
            InitializationManager._initialize_containers()
            
            # Mark initialization as complete
            StateManager.set("initialization_complete", True)
            
            logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during application initialization: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Set initialization status to failed but don't crash
            StateManager.set("initialization_error", str(e))
            StateManager.set("initialization_complete", False)
            
            return False
    
    @staticmethod
    def _initialize_system_info() -> None:
        """
        Initialize system information with error handling.
        """
        try:
            # Import here to avoid circular imports
            from lib.system import get_system_info
            
            system_info = get_system_info()
            StateManager.set("system_info", system_info)
            logger.info(f"System info initialized: {system_info.get('platform', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error initializing system info: {str(e)}")
            # Set fallback system info
            StateManager.set("system_info", {
                "platform": "unknown",
                "cpu": "unknown",
                "memory": "unknown",
                "gpu": "unknown",
                "os": "unknown",
                "container_runtime": "unknown"
            })
    
    @staticmethod
    def _initialize_containers() -> None:
        """
        Initialize container information with error handling.
        """
        try:
            # Import here to avoid circular imports
            from lib.containers import get_containers
            
            containers = get_containers()
            StateManager.set("containers", containers)
            logger.info(f"Container info initialized: {len(containers)} containers found")
            
        except Exception as e:
            logger.error(f"Error initializing containers: {str(e)}")
            # Set empty containers dict
            StateManager.set("containers", {})
    
    @staticmethod
    def check_initialization() -> bool:
        """
        Check if the application has been initialized.
        
        Returns:
            True if initialization is complete, False otherwise
        """
        return StateManager.get("initialization_complete", False)
    
    @staticmethod
    def get_initialization_error() -> Optional[str]:
        """
        Get the initialization error if any.
        
        Returns:
            Error message or None if no error
        """
        return StateManager.get("initialization_error", None)
    
    @staticmethod
    def recovery_ui() -> None:
        """
        Display a recovery UI when initialization fails.
        """
        st.error("⚠️ Singularity Launcher failed to initialize properly")
        
        error_msg = InitializationManager.get_initialization_error()
        if error_msg:
            st.error(f"Error: {error_msg}")
        
        st.markdown("""
        ### Troubleshooting Steps
        
        1. Check if your system meets the requirements
        2. Verify that Docker or Podman is installed and running
        3. Check permissions for accessing container runtime
        4. Try restarting the application
        """)
        
        if st.button("Retry Initialization"):
            if InitializationManager.initialize_application():
                st.success("Initialization successful! Reloading application...")
                st.rerun()
            else:
                st.error("Initialization failed again. Please check the logs for more information.")
        
        with st.expander("Advanced Troubleshooting", expanded=False):
            st.markdown("""
            ### Advanced Troubleshooting
            
            - Check the logs for detailed error information
            - Verify network connectivity for container image pulls
            - Check disk space for container storage
            - Verify Python environment and dependencies
            """)
            
            if st.button("Enable Debug Mode"):
                StateManager.set("debug_mode", True)
                st.info("Debug mode enabled. Reloading application...")
                st.rerun()
            
            if st.button("Reset Application State"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.info("Application state reset. Reloading application...")
                st.rerun()

def safe_import(module_name: str) -> Tuple[bool, Any, Optional[str]]:
    """
    Safely import a module with error handling.
    
    Args:
        module_name: Name of the module to import
        
    Returns:
        Tuple of (success, module/None, error_message/None)
    """
    try:
        module = __import__(module_name, fromlist=['*'])
        return True, module, None
    except ImportError as e:
        logger.error(f"Error importing {module_name}: {str(e)}")
        return False, None, str(e)
    except Exception as e:
        logger.error(f"Unexpected error importing {module_name}: {str(e)}")
        return False, None, str(e)
