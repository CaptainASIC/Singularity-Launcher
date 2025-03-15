#!/usr/bin/env python3
"""
Singularity Launcher

A Streamlit UI for deploying Lab and AI Environments with support for various
CPU and GPU architectures.
"""

import os
import sys
import time
import subprocess
import streamlit as st
from typing import Dict, Any

# Fix module import issue by using absolute imports
# Get the absolute path to the project directory
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
# Add the project directory to the Python path
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Import library modules
try:
    # Try direct imports first
    try:
        from lib.system import get_system_info, get_container_engine_info
        from lib.performance import start_monitoring, stop_monitoring, get_current_metrics
        from lib.containers import start_container_monitoring, stop_container_monitoring, get_all_containers
        from lib.containers import start_container, stop_container, restart_container
        from lib.ui import set_page_config, apply_custom_css, create_sidebar, create_footer
        from lib.ui import create_performance_widgets, create_system_info_card
        from lib.ui import create_welcome_screen, create_lab_setup_screen, create_local_ai_screen, create_exit_screen
    except ImportError:
        # If that fails, try with a relative import
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from lib.system import get_system_info, get_container_engine_info
        from lib.performance import start_monitoring, stop_monitoring, get_current_metrics
        from lib.containers import start_container_monitoring, stop_container_monitoring, get_all_containers
        from lib.containers import start_container, stop_container, restart_container
        from lib.ui import set_page_config, apply_custom_css, create_sidebar, create_footer
        from lib.ui import create_performance_widgets, create_system_info_card
        from lib.ui import create_welcome_screen, create_lab_setup_screen, create_local_ai_screen, create_exit_screen
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.error(f"Current Python path: {sys.path}")
    st.error(f"Project directory: {PROJECT_DIR}")
    st.error("Please make sure you're running the application from the project directory.")
    
    # Create a simple UI to show the error
    st.title("Singularity Launcher - Error")
    st.error("Failed to import required modules. This is likely due to a Python path issue.")
    st.markdown("### Troubleshooting")
    st.markdown("1. Make sure you're running the application from the project directory")
    st.markdown("2. Try running with the launch script: `./launch.sh`")
    st.markdown("3. Check that the 'lib' directory exists and contains the required modules")
    
    # Show the directory structure to help with debugging
    try:
        st.markdown("### Project Directory Structure")
        result = subprocess.run(["ls", "-la", PROJECT_DIR], capture_output=True, text=True)
        st.code(result.stdout)
        
        st.markdown("### Lib Directory Structure")
        result = subprocess.run(["ls", "-la", os.path.join(PROJECT_DIR, "lib")], capture_output=True, text=True)
        st.code(result.stdout)
    except Exception as dir_error:
        st.error(f"Could not list directory structure: {dir_error}")
    
    sys.exit(1)

# Version information
__version__ = "0.1.0"
APP_NAME = "Singularity Launcher"
BUILD_DATE = "March 2025"

def main():
    """Main application entry point."""
    # Configure the page
    set_page_config()
    apply_custom_css()
    
    # Initialize session state if not already done
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.system_info = get_system_info()
        st.session_state.system_info['container_engine'] = get_container_engine_info()
        st.session_state.metrics = {
            "cpu": {"usage": 0.0, "temperature": 0.0, "type": st.session_state.system_info['cpu']['type']},
            "memory": {"usage": 0.0, "total": st.session_state.system_info['memory']['total'], "unit": "GB"},
            "gpu": {"usage": 0.0, "temperature": 0.0, "memory_usage": 0.0, "memory_total": 0, "type": st.session_state.system_info['gpu']['type']},
            "disk": {"usage": 0.0, "total": 0, "used": 0, "unit": "GB"}
        }
        st.session_state.containers = {}
        
        # Start monitoring
        start_monitoring()
        start_container_monitoring()
    
    # Update metrics and containers
    st.session_state.metrics = get_current_metrics()
    st.session_state.containers = get_all_containers()
    
    # Create the sidebar, display system info and performance metrics there
    selected_page = create_sidebar()
    
    # Display system information in sidebar
    with st.sidebar:
        st.markdown("---")
        create_system_info_card(st.session_state.system_info)
        
        # Display performance widgets in sidebar
        st.markdown("---")
        st.subheader("Performance Metrics")
        create_performance_widgets(st.session_state.metrics)
    
    # Display the selected page in main area
    if selected_page == "Home":
        create_welcome_screen()
    elif selected_page == "Lab Setup":
        create_lab_setup_screen()
    elif selected_page == "Local AI":
        create_local_ai_screen()
    elif selected_page == "Exit":
        create_exit_screen()
        # If we get here, the user canceled the exit
        st.rerun()
    
    # Create the footer with container controls
    create_footer(st.session_state.containers)
    
    # Handle container control buttons
    try:
        # Create a copy of the session state keys to avoid modification during iteration
        session_keys = list(st.session_state.keys())
        
        # Track which buttons were clicked to handle them
        clicked_buttons = []
        
        for container_id, container in st.session_state.containers.items():
            # Check for any button press for this container across all services
            for key in session_keys:
                # Only process keys that are boolean and True (button clicks)
                if not isinstance(st.session_state.get(key), bool) or not st.session_state.get(key):
                    continue
                    
                # Start buttons
                if key.startswith(f"start_{container_id}_"):
                    clicked_buttons.append((key, container_id, container['name'], 'start'))
                
                # Stop buttons
                elif key.startswith(f"stop_{container_id}_"):
                    clicked_buttons.append((key, container_id, container['name'], 'stop'))
                
                # Restart buttons
                elif key.startswith(f"restart_{container_id}_"):
                    clicked_buttons.append((key, container_id, container['name'], 'restart'))
            
            # Also check the original button keys from the footer
            # Start button
            start_key = f"start_{container_id}"
            if start_key in session_keys and isinstance(st.session_state.get(start_key), bool) and st.session_state.get(start_key):
                clicked_buttons.append((start_key, container_id, container['name'], 'start'))
            
            # Stop button
            stop_key = f"stop_{container_id}"
            if stop_key in session_keys and isinstance(st.session_state.get(stop_key), bool) and st.session_state.get(stop_key):
                clicked_buttons.append((stop_key, container_id, container['name'], 'stop'))
            
            # Restart button
            restart_key = f"restart_{container_id}"
            if restart_key in session_keys and isinstance(st.session_state.get(restart_key), bool) and st.session_state.get(restart_key):
                clicked_buttons.append((restart_key, container_id, container['name'], 'restart'))
        
        # Process clicked buttons after collecting them all
        if clicked_buttons:
            # Take only the first button click to process
            key, container_id, container_name, action = clicked_buttons[0]
            
            # Create a new session state variable to track that we're processing this action
            processing_key = f"processing_{action}_{container_id}"
            if processing_key not in st.session_state:
                st.session_state[processing_key] = True
                
                # Perform the action
                if action == 'start':
                    if start_container(container_id):
                        st.success(f"Started container: {container_name}")
                        time.sleep(1)  # Give the container time to start
                    else:
                        st.error(f"Failed to start container: {container_name}")
                
                elif action == 'stop':
                    if stop_container(container_id):
                        st.success(f"Stopped container: {container_name}")
                        time.sleep(1)  # Give the container time to stop
                    else:
                        st.error(f"Failed to stop container: {container_name}")
                
                elif action == 'restart':
                    if restart_container(container_id):
                        st.success(f"Restarted container: {container_name}")
                        time.sleep(1)  # Give the container time to restart
                    else:
                        st.error(f"Failed to restart container: {container_name}")
                
                # Clear all button states on next rerun
                st.rerun()
    except Exception as e:
        st.error(f"Error handling container controls: {e}")

def cleanup():
    """Clean up resources before exiting."""
    stop_monitoring()
    stop_container_monitoring()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        # This won't actually run in Streamlit since the script keeps running,
        # but it's good practice to include it
        cleanup()
