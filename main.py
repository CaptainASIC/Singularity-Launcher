"""
Main entry point for Singularity Launcher
Streamlit UI for deploying Lab and AI Environments with support for various CPU and GPU architectures.

Version 2.5.0 - Enhanced UI & Optimized Scripts
"""
import streamlit as st
import time
import os
import sys
import logging
from typing import Dict, Any, List, Optional

# Add lib directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import utility modules
from lib.utils.initialization import InitializationManager
from lib.utils.state_management import StateManager
from lib.utils.ui_components import (
    ui_error_boundary, 
    with_loading_state,
    inject_custom_css,
    create_debug_panel,
    is_debug_mode
)

# Import core modules
from lib.system import get_system_info, detect_platform
from lib.containers import (
    get_containers, 
    start_container, 
    stop_container, 
    restart_container
)
from lib.performance import monitor_system_performance, stop_monitoring
from lib.ui import (
    create_sidebar, 
    create_home_screen, 
    create_lab_setup_screen,
    create_local_ai_screen, 
    create_exit_screen,
    create_footer
)

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

# Start container monitoring
from lib.containers import start_container_monitoring, stop_container_monitoring

@ui_error_boundary("Main Application")
def main():
    """Main application entry point."""
    # Set page config
    st.set_page_config(
        page_title="Singularity Launcher v2.5",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inject custom CSS for improved UI
    inject_custom_css()
    
    # Initialize application if not already done
    if not InitializationManager.check_initialization():
        with st.spinner("Initializing Singularity Launcher..."):
            success = InitializationManager.initialize_application()
            if not success:
                InitializationManager.recovery_ui()
                return
    
    # Create sidebar navigation
    create_sidebar()
    
    # Get selected page from session state
    selected_page = StateManager.get("page", "Home")
    
    # Create the selected page
    if selected_page == "Home":
        create_home_screen()
    elif selected_page == "Lab Setup":
        create_lab_setup_screen()
    elif selected_page == "Local AI":
        create_local_ai_screen()
    elif selected_page == "Exit":
        create_exit_screen()
        # If we get here, the user canceled the exit
        st.rerun()
    
    # Create the footer with container controls
    create_footer(StateManager.get("containers", {}))
    
    # Create debug panel if debug mode is enabled
    create_debug_panel()
    
    # Handle container control buttons
    try:
        # Create a copy of the session state keys to avoid modification during iteration
        session_keys = list(st.session_state.keys())
        
        # Track which buttons were clicked to handle them
        clicked_buttons = []
        
        for container_id, container in StateManager.get("containers", {}).items():
            # Check for any button press for this container across all services
            for key in session_keys:
                # Only process keys that are boolean and True (button clicks)
                if not isinstance(StateManager.get(key), bool) or not StateManager.get(key):
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
            if start_key in session_keys and isinstance(StateManager.get(start_key), bool) and StateManager.get(start_key):
                clicked_buttons.append((start_key, container_id, container['name'], 'start'))
            
            # Stop button
            stop_key = f"stop_{container_id}"
            if stop_key in session_keys and isinstance(StateManager.get(stop_key), bool) and StateManager.get(stop_key):
                clicked_buttons.append((stop_key, container_id, container['name'], 'stop'))
            
            # Restart button
            restart_key = f"restart_{container_id}"
            if restart_key in session_keys and isinstance(StateManager.get(restart_key), bool) and StateManager.get(restart_key):
                clicked_buttons.append((restart_key, container_id, container['name'], 'restart'))
        
        # Process clicked buttons after collecting them all
        if clicked_buttons:
            # Take only the first button click to process
            key, container_id, container_name, action = clicked_buttons[0]
            
            # Create a new session state variable to track that we're processing this action
            processing_key = f"processing_{action}_{container_id}"
            if processing_key not in st.session_state:
                StateManager.set(processing_key, True)
                
                # Perform the action
                if action == 'start':
                    with st.spinner(f"Starting {container_name}..."):
                        if start_container(container_id):
                            st.success(f"Started container: {container_name}")
                            time.sleep(1)  # Give the container time to start
                        else:
                            st.error(f"Failed to start container: {container_name}")
                
                elif action == 'stop':
                    with st.spinner(f"Stopping {container_name}..."):
                        if stop_container(container_id):
                            st.success(f"Stopped container: {container_name}")
                            time.sleep(1)  # Give the container time to stop
                        else:
                            st.error(f"Failed to stop container: {container_name}")
                
                elif action == 'restart':
                    with st.spinner(f"Restarting {container_name}..."):
                        if restart_container(container_id):
                            st.success(f"Restarted container: {container_name}")
                            time.sleep(1)  # Give the container time to restart
                        else:
                            st.error(f"Failed to restart container: {container_name}")
                
                # Clear all button states on next rerun
                st.rerun()
    except Exception as e:
        logger.error(f"Error handling container controls: {e}")
        if is_debug_mode():
            st.error(f"Error handling container controls: {e}")
        else:
            st.error("An error occurred while handling container controls. Enable debug mode for details.")

def cleanup():
    """Clean up resources before exiting."""
    stop_monitoring()
    stop_container_monitoring()
    
    # Clean up any other resources
    from lib.utils.performance import AsyncTaskManager
    AsyncTaskManager.shutdown()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error(f"An unexpected error occurred. Please check the logs for details.")
        if is_debug_mode():
            st.error(f"Error details: {e}")
            import traceback
            st.code(traceback.format_exc())
    finally:
        # This won't actually run in Streamlit since the script keeps running,
        # but it's good practice to include it
        cleanup()
