"""
UI error handling and component utilities for Singularity Launcher
Provides error boundaries, loading states, and accessibility improvements.

Version 2.5.0 - Enhanced UI & Optimized Scripts
"""
import streamlit as st
from typing import Any, Dict, List, Optional, Union, Callable
import time
import logging
from functools import wraps

from lib.utils.state_management import StateManager, is_debug_mode

logger = logging.getLogger("singularity_launcher")

def ui_error_boundary(component_name: str):
    """
    Decorator to create an error boundary around UI components.
    
    Args:
        component_name: Name of the component for error reporting
        
    Returns:
        Decorated function with error handling
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {component_name}: {str(e)}")
                st.error(f"Error loading {component_name}")
                
                if is_debug_mode():
                    with st.expander("Error Details", expanded=True):
                        st.code(f"Error in {component_name}: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                
                # Return a placeholder element to prevent layout breaks
                st.info(f"Please refresh the page or restart the application to resolve this issue.")
                return None
        return wrapper
    return decorator

def with_loading_state(message: str = "Loading..."):
    """
    Decorator to add loading state to UI components.
    
    Args:
        message: Loading message to display
        
    Returns:
        Decorated function with loading state
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with st.spinner(message):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def create_accessibility_container(aria_label: str, role: str = None):
    """
    Create a container with proper accessibility attributes.
    
    Args:
        aria_label: Accessible label for screen readers
        role: ARIA role for the container
        
    Returns:
        Streamlit container with accessibility attributes
    """
    container = st.container()
    
    # Use markdown to inject a div with ARIA attributes
    if role:
        container.markdown(f"""
        <div role="{role}" aria-label="{aria_label}">
        </div>
        """, unsafe_allow_html=True)
    else:
        container.markdown(f"""
        <div aria-label="{aria_label}">
        </div>
        """, unsafe_allow_html=True)
    
    return container

def create_status_indicator(status: str, label: str):
    """
    Create an accessible status indicator with consistent styling.
    
    Args:
        status: Status value (running, stopped, error)
        label: Label for the status
    """
    status_colors = {
        "running": "green",
        "stopped": "gray",
        "error": "red",
        "unknown": "orange"
    }
    
    color = status_colors.get(status.lower(), "blue")
    
    st.markdown(f"""
    <div role="status" aria-live="polite" style="display: flex; align-items: center;">
        <div style="width: 12px; height: 12px; border-radius: 50%; background-color: {color}; margin-right: 8px;"></div>
        <span>{label}: <strong>{status}</strong></span>
    </div>
    """, unsafe_allow_html=True)

def create_keyboard_shortcut_help():
    """
    Create a help section for keyboard shortcuts.
    """
    with st.expander("Keyboard Shortcuts", expanded=False):
        st.markdown("""
        | Key | Action |
        | --- | ------ |
        | `Ctrl+H` | Toggle sidebar |
        | `Ctrl+R` | Refresh page |
        | `Ctrl+D` | Toggle debug mode |
        | `Ctrl+/` | Show keyboard shortcuts |
        """)

def inject_custom_css():
    """
    Inject custom CSS for improved UI.
    """
    st.markdown("""
    <style>
    /* Improved visual hierarchy */
    h1 {
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 1px solid rgba(49, 51, 63, 0.2) !important;
    }
    
    h2 {
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Card-like containers */
    div.stBlock {
        border-radius: 0.5rem !important;
        padding: 1rem !important;
        margin-bottom: 1rem !important;
        border: 1px solid rgba(49, 51, 63, 0.1) !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Improved button styling */
    .stButton > button {
        border-radius: 0.25rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Improved sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(245, 245, 250, 0.1) !important;
    }
    
    /* Improved expander */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
    }
    
    /* Improved metrics */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        padding: 0.5rem !important;
        border-radius: 0.25rem !important;
    }
    
    /* Improved tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 0.25rem 0.25rem 0 0 !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* Improved container status indicators */
    .container-status-running {
        color: #28a745 !important;
    }
    
    .container-status-stopped {
        color: #6c757d !important;
    }
    
    .container-status-error {
        color: #dc3545 !important;
    }
    
    /* Improved form elements */
    input, select, textarea {
        border-radius: 0.25rem !important;
    }
    
    /* Improved tooltips */
    .stTooltip {
        border-radius: 0.25rem !important;
    }
    
    /* Improved loading spinner */
    .stSpinner > div {
        border-color: #4e8cff transparent transparent !important;
    }
    
    /* Improved alerts */
    .stAlert {
        border-radius: 0.25rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

def create_debug_panel():
    """
    Create a debug panel for troubleshooting.
    Only visible when debug mode is enabled.
    """
    if is_debug_mode():
        with st.expander("Debug Panel", expanded=False):
            st.subheader("Session State")
            st.json({k: str(v) for k, v in st.session_state.items()})
            
            st.subheader("Actions")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Clear Session State"):
                    for key in list(st.session_state.keys()):
                        if key != "debug_mode":  # Keep debug mode
                            StateManager.delete(key)
                    st.success("Session state cleared")
                    time.sleep(1)
                    st.rerun()
            
            with col2:
                if st.button("Reload Application"):
                    st.rerun()
            
            st.subheader("System Info")
            import platform
            import psutil
            
            st.text(f"Python: {platform.python_version()}")
            st.text(f"Platform: {platform.platform()}")
            st.text(f"CPU Cores: {psutil.cpu_count()}")
            st.text(f"Memory: {psutil.virtual_memory().total / (1024**3):.2f} GB")
            
            st.subheader("Log Viewer")
            try:
                with open("singularity_launcher.log", "r") as f:
                    log_content = f.readlines()
                    # Show last 20 lines
                    st.code("".join(log_content[-20:]))
            except Exception as e:
                st.error(f"Could not read log file: {e}")
