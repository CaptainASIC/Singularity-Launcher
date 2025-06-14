"""
State management utilities for Singularity Launcher
Provides robust session state initialization, validation, and error handling.

Version 2.5.0 - Enhanced UI & Optimized Scripts
"""
import streamlit as st
from typing import Any, Dict, List, Optional, Union, Callable
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("singularity_launcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("singularity_launcher")

class StateManager:
    """
    Manages Streamlit session state with validation and error handling.
    Provides a more structured approach to state management.
    """
    
    @staticmethod
    def initialize_state(defaults: Dict[str, Any]) -> None:
        """
        Initialize session state variables with defaults if they don't exist.
        
        Args:
            defaults: Dictionary of default values for session state variables
        """
        try:
            for key, value in defaults.items():
                if key not in st.session_state:
                    st.session_state[key] = value
            logger.info("Session state initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing session state: {str(e)}")
            logger.error(traceback.format_exc())
            st.error(f"Error initializing application state. Please refresh the page or restart the application.")
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Safely get a value from session state with validation.
        
        Args:
            key: The session state key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            The value from session state or the default
        """
        try:
            return st.session_state.get(key, default)
        except Exception as e:
            logger.error(f"Error retrieving session state key '{key}': {str(e)}")
            return default
    
    @staticmethod
    def set(key: str, value: Any) -> bool:
        """
        Safely set a value in session state with error handling.
        
        Args:
            key: The session state key to set
            value: The value to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            st.session_state[key] = value
            return True
        except Exception as e:
            logger.error(f"Error setting session state key '{key}': {str(e)}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """
        Safely delete a key from session state.
        
        Args:
            key: The session state key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if key in st.session_state:
                del st.session_state[key]
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting session state key '{key}': {str(e)}")
            return False
    
    @staticmethod
    def clear_button_states() -> None:
        """
        Clear all button states in session state to prevent multiple triggers.
        """
        try:
            keys_to_clear = []
            for key in st.session_state:
                if isinstance(st.session_state[key], bool) and st.session_state[key] is True:
                    if key.startswith(("start_", "stop_", "restart_", "build_")):
                        keys_to_clear.append(key)
            
            for key in keys_to_clear:
                st.session_state[key] = False
                
            logger.debug(f"Cleared {len(keys_to_clear)} button states")
        except Exception as e:
            logger.error(f"Error clearing button states: {str(e)}")

class ErrorBoundary:
    """
    Provides error boundary functionality for UI components.
    """
    
    @staticmethod
    def wrap(func: Callable, error_message: str = "An error occurred in this component") -> Callable:
        """
        Wrap a function with error handling to prevent cascading failures.
        
        Args:
            func: The function to wrap
            error_message: Message to display on error
            
        Returns:
            Wrapped function with error handling
        """
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in component: {str(e)}")
                logger.error(traceback.format_exc())
                st.error(f"{error_message}: {str(e)}")
                with st.expander("Error Details", expanded=False):
                    st.code(traceback.format_exc())
                return None
        return wrapped

def safe_get_container_status(container_id: str) -> str:
    """
    Safely get container status with error handling.
    
    Args:
        container_id: Container ID to check
        
    Returns:
        Container status or "unknown" on error
    """
    try:
        # This is a placeholder - actual implementation would call the containers module
        # Return a default for now
        return "unknown"
    except Exception as e:
        logger.error(f"Error getting container status for {container_id}: {str(e)}")
        return "unknown"

def is_debug_mode() -> bool:
    """
    Check if debug mode is enabled.
    
    Returns:
        True if debug mode is enabled, False otherwise
    """
    return StateManager.get("debug_mode", False)

def toggle_debug_mode() -> None:
    """
    Toggle debug mode on/off.
    """
    current = StateManager.get("debug_mode", False)
    StateManager.set("debug_mode", not current)
    logger.info(f"Debug mode {'enabled' if not current else 'disabled'}")
