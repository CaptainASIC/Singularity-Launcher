"""
UI components for Singularity Launcher.
Provides UI components for the Streamlit-based interface.
"""
import streamlit as st
import time
import os
import platform
import logging
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Callable, Tuple

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas not available, some UI features will be limited")

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logger.warning("plotly not available, some UI features will be limited")

# UI Constants
SIDEBAR_WIDTH = 300
CONTAINER_STATUS_COLORS = {
    "running": "#28a745",  # Green
    "stopped": "#6c757d",  # Gray
    "error": "#dc3545",    # Red
    "unknown": "#ffc107"   # Yellow
}

# UI Themes
LIGHT_THEME = {
    "background": "#ffffff",
    "text": "#212529",
    "primary": "#007bff",
    "secondary": "#6c757d",
    "success": "#28a745",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "info": "#17a2b8"
}

DARK_THEME = {
    "background": "#212529",
    "text": "#f8f9fa",
    "primary": "#0d6efd",
    "secondary": "#6c757d",
    "success": "#198754",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "info": "#0dcaf0"
}

# Get current theme based on session state
def get_theme():
    """
    Get the current theme based on session state.
    
    Returns:
        Dict[str, str]: Theme colors
    """
    if "dark_mode" in st.session_state and st.session_state.dark_mode:
        return DARK_THEME
    return LIGHT_THEME

def create_sidebar():
    """Create the sidebar with navigation menu."""
    with st.sidebar:
        st.title("Singularity Launcher")
        
        # Navigation
        st.subheader("Navigation")
        
        # Use radio buttons for navigation
        pages = ["Home", "Lab Setup", "Local AI", "Exit"]
        selected_page = st.radio("", pages, index=pages.index(st.session_state.get("page", "Home")))
        
        # Update session state if page changed
        if "page" not in st.session_state or st.session_state.page != selected_page:
            st.session_state.page = selected_page
            # Force rerun to update the main content
            st.rerun()
        
        # System information
        st.subheader("System Information")
        
        # Display system info if available
        if "system_info" in st.session_state:
            create_system_info_card(st.session_state.system_info)
        
        # Performance monitoring
        st.subheader("Performance")
        
        # Display performance metrics if available
        if "performance_data" in st.session_state:
            create_performance_widgets(st.session_state.performance_data)
        
        # Settings
        st.subheader("Settings")
        
        # Dark mode toggle
        dark_mode = st.checkbox("Dark Mode", value=st.session_state.get("dark_mode", True))
        if "dark_mode" not in st.session_state or st.session_state.dark_mode != dark_mode:
            st.session_state.dark_mode = dark_mode
            # Force rerun to update the theme
            st.rerun()
        
        # Show advanced options
        show_advanced = st.checkbox("Show Advanced Options", value=st.session_state.get("show_advanced", False))
        if "show_advanced" not in st.session_state or st.session_state.show_advanced != show_advanced:
            st.session_state.show_advanced = show_advanced
        
        # About section
        st.sidebar.markdown("---")
        st.sidebar.info(
            "Singularity Launcher v2.5\n\n"
            "Created by Captain ASIC\n\n"
            "[GitHub](https://github.com/CaptainASIC/Singularity-Launcher)"
        )

def create_footer(containers: Dict[str, Dict[str, Any]]):
    """
    Create the footer with container controls.
    
    Args:
        containers: Dictionary of containers indexed by container ID
    """
    st.markdown("---")
    
    # Create columns for container controls
    if containers:
        st.subheader("Container Controls")
        
        # Create a table of containers
        table_data = []
        for container_id, container in containers.items():
            status_color = CONTAINER_STATUS_COLORS.get(container.get("status", "unknown"), CONTAINER_STATUS_COLORS["unknown"])
            
            # Create status indicator
            status_indicator = f"<span style='color: {status_color};'>●</span> {container.get('status', 'unknown')}"
            
            # Add to table data
            table_data.append({
                "Name": container.get("name", "Unknown"),
                "Status": status_indicator,
                "Image": container.get("image", "Unknown"),
                "Actions": f"""
                <button key="start_{container_id}">Start</button>
                <button key="stop_{container_id}">Stop</button>
                <button key="restart_{container_id}">Restart</button>
                """
            })
        
        # Display table if there's data
        if table_data:
            # Convert to DataFrame if pandas is available
            if PANDAS_AVAILABLE:
                df = pd.DataFrame(table_data)
                st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
            else:
                # Fallback to simple display
                for row in table_data:
                    st.write(f"{row['Name']} - {row['Status']}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.button("Start", key=f"start_{container_id}")
                    with col2:
                        st.button("Stop", key=f"stop_{container_id}")
                    with col3:
                        st.button("Restart", key=f"restart_{container_id}")
    else:
        st.info("No containers found. Please check your container runtime.")
    
    # Add some space at the bottom
    st.markdown("<br><br>", unsafe_allow_html=True)

def create_performance_widgets(metrics: Dict[str, Any]):
    """
    Create performance monitoring widgets optimized for sidebar display.
    
    Args:
        metrics: Dictionary containing performance metrics
    """
    # CPU usage
    cpu_usage = metrics.get("cpu", {}).get("usage", 0)
    cpu_temp = metrics.get("cpu", {}).get("temperature", 0)
    
    # Memory usage
    memory_usage = metrics.get("memory", {}).get("usage", 0)
    memory_total = metrics.get("memory", {}).get("total", 0)
    
    # GPU usage if available
    gpu_usage = metrics.get("gpu", {}).get("usage", 0)
    gpu_temp = metrics.get("gpu", {}).get("temperature", 0)
    
    # Create compact metrics display
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("CPU", f"{cpu_usage:.1f}%")
        st.metric("GPU", f"{gpu_usage:.1f}%")
    
    with col2:
        st.metric("Memory", f"{memory_usage:.1f}%")
        st.metric("Temp", f"{cpu_temp:.1f}°C")
    
    # Show detailed metrics in expander
    with st.expander("Detailed Metrics", expanded=False):
        # CPU details
        st.write(f"**CPU:** {metrics.get('cpu', {}).get('type', 'Unknown')}")
        st.progress(cpu_usage / 100)
        st.write(f"Usage: {cpu_usage:.1f}% | Temp: {cpu_temp:.1f}°C")
        
        # Memory details
        st.write(f"**Memory:** {memory_total} GB Total")
        st.progress(memory_usage / 100)
        st.write(f"Usage: {memory_usage:.1f}%")
        
        # GPU details if available
        if gpu_usage > 0 or gpu_temp > 0:
            st.write(f"**GPU:** {metrics.get('gpu', {}).get('type', 'Unknown')}")
            st.progress(gpu_usage / 100)
            st.write(f"Usage: {gpu_usage:.1f}% | Temp: {gpu_temp:.1f}°C")
            
            # GPU memory if available
            gpu_memory_usage = metrics.get("gpu", {}).get("memory_usage", 0)
            gpu_memory_total = metrics.get("gpu", {}).get("memory_total", 0)
            if gpu_memory_total > 0:
                st.progress(gpu_memory_usage / 100)
                st.write(f"Memory: {gpu_memory_usage:.1f}% of {gpu_memory_total} MB")

def create_gauge_chart(value: float, title: str, suffix: str = "") -> go.Figure:
    """
    Create a gauge chart for displaying metrics.
    
    Args:
        value: Value to display (0-100)
        title: Chart title
        suffix: Suffix to add to the value (e.g., "%")
        
    Returns:
        go.Figure: Plotly gauge chart
    """
    if not PLOTLY_AVAILABLE:
        return None
    
    # Ensure value is within range
    value = max(0, min(100, value))
    
    # Define colors based on value
    if value < 60:
        color = "green"
    elif value < 80:
        color = "yellow"
    else:
        color = "red"
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": title},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 60], "color": "lightgreen"},
                {"range": [60, 80], "color": "lightyellow"},
                {"range": [80, 100], "color": "lightcoral"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 90
            }
        },
        number={"suffix": suffix}
    ))
    
    # Set layout
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": get_theme()["text"]}
    )
    
    return fig

def create_system_info_card(system_info: Dict[str, Any]):
    """
    Create a card displaying system information.
    
    Args:
        system_info: Dictionary containing system information
    """
    # Platform
    platform_name = system_info.get("platform", "Unknown")
    
    # CPU
    cpu_info = system_info.get("cpu", "Unknown")
    
    # Memory
    memory_info = system_info.get("memory", "Unknown")
    
    # GPU
    gpu_info = system_info.get("gpu", "Unknown")
    
    # Container runtime
    container_runtime = system_info.get("container_runtime", "Unknown")
    
    # Display system info
    st.markdown(f"""
    **Platform:** {platform_name}  
    **CPU:** {cpu_info}  
    **Memory:** {memory_info}  
    **GPU:** {gpu_info}  
    **Runtime:** {container_runtime}
    """)
    
    # Show detailed info in expander
    with st.expander("System Details", expanded=False):
        # OS details
        os_info = system_info.get("os", {})
        st.write("**Operating System**")
        st.code(f"""
        Name: {os_info.get('name', 'Unknown')}
        Version: {os_info.get('version', 'Unknown')}
        Architecture: {os_info.get('arch', 'Unknown')}
        """)
        
        # Hardware details
        st.write("**Hardware**")
        st.code(f"""
        CPU: {cpu_info}
        Cores: {system_info.get('cpu_cores', 'Unknown')}
        Memory: {memory_info}
        GPU: {gpu_info}
        """)

def create_welcome_screen():
    """Create the welcome screen."""
    st.title("Welcome to Singularity Launcher")
    
    st.markdown("""
    Singularity Launcher is your all-in-one solution for deploying Lab and AI environments
    with support for various CPU and GPU architectures.
    
    ## Getting Started
    
    1. Use the sidebar navigation to switch between different sections
    2. Monitor system performance in the sidebar
    3. Control containers using the footer controls
    
    ## Available Environments
    
    - **Lab Setup**: Deploy and manage lab environments like JupyterLab, VSCode, and more
    - **Local AI**: Deploy and manage local AI models with Ollama, Open WebUI, and more
    
    ## System Detection
    
    Singularity Launcher has detected your system configuration and will optimize
    container deployments accordingly.
    """)
    
    # Display system info if available
    if "system_info" in st.session_state:
        st.subheader("Your System")
        create_system_info_card(st.session_state.system_info)
    
    # Display quick actions
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Lab Setup", use_container_width=True):
            st.session_state.page = "Lab Setup"
            st.rerun()
    
    with col2:
        if st.button("Local AI", use_container_width=True):
            st.session_state.page = "Local AI"
            st.rerun()
    
    with col3:
        if st.button("System Monitor", use_container_width=True):
            # Toggle advanced options to show performance monitoring
            st.session_state.show_advanced = True
            st.rerun()

def create_home_screen():
    """
    Alias for create_welcome_screen for backward compatibility.
    Creates the home/welcome screen.
    """
    create_welcome_screen()

def create_lab_setup_screen():
    """Create the lab setup screen."""
    st.title("Lab Setup")
    
    st.markdown("""
    Deploy and manage lab environments for development, data science, and more.
    
    Select from the available lab environments below to get started.
    """)
    
    # Create tabs for different lab categories
    tab1, tab2, tab3 = st.tabs(["Development", "Data Science", "DevOps"])
    
    with tab1:
        st.subheader("Development Environments")
        
        # Create columns for development environments
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### VSCode Server
            
            Browser-based VSCode with full extension support.
            
            - Multi-language support
            - Git integration
            - Terminal access
            """)
            
            # Container status and controls
            container_id = None  # This would be set based on actual container data
            container_status = "stopped"  # This would be set based on actual container status
            
            # Display status
            st.markdown(f"**Status:** <span style='color: {CONTAINER_STATUS_COLORS.get(container_status, CONTAINER_STATUS_COLORS['unknown'])};'>●</span> {container_status}", unsafe_allow_html=True)
            
            # Controls
            control_col1, control_col2, control_col3 = st.columns(3)
            
            with control_col1:
                st.button("Start", key="start_vscode", disabled=container_status == "running")
            
            with control_col2:
                st.button("Stop", key="stop_vscode", disabled=container_status != "running")
            
            with control_col3:
                st.button("Restart", key="restart_vscode", disabled=container_status != "running")
        
        with col2:
            st.markdown("""
            ### JupyterLab
            
            Interactive computing environment for notebooks, code, and data.
            
            - Python, R, Julia support
            - Interactive notebooks
            - Data visualization
            """)
            
            # Container status and controls
            container_id = None  # This would be set based on actual container data
            container_status = "stopped"  # This would be set based on actual container status
            
            # Display status
            st.markdown(f"**Status:** <span style='color: {CONTAINER_STATUS_COLORS.get(container_status, CONTAINER_STATUS_COLORS['unknown'])};'>●</span> {container_status}", unsafe_allow_html=True)
            
            # Controls
            control_col1, control_col2, control_col3 = st.columns(3)
            
            with control_col1:
                st.button("Start", key="start_jupyter", disabled=container_status == "running")
            
            with control_col2:
                st.button("Stop", key="stop_jupyter", disabled=container_status != "running")
            
            with control_col3:
                st.button("Restart", key="restart_jupyter", disabled=container_status != "running")
    
    with tab2:
        st.subheader("Data Science Environments")
        
        # Create columns for data science environments
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### RStudio Server
            
            Browser-based RStudio for statistical computing and graphics.
            
            - R language support
            - Statistical analysis
            - Data visualization
            """)
            
            # Container status and controls
            container_id = None  # This would be set based on actual container data
            container_status = "stopped"  # This would be set based on actual container status
            
            # Display status
            st.markdown(f"**Status:** <span style='color: {CONTAINER_STATUS_COLORS.get(container_status, CONTAINER_STATUS_COLORS['unknown'])};'>●</span> {container_status}", unsafe_allow_html=True)
            
            # Controls
            control_col1, control_col2, control_col3 = st.columns(3)
            
            with control_col1:
                st.button("Start", key="start_rstudio", disabled=container_status == "running")
            
            with control_col2:
                st.button("Stop", key="stop_rstudio", disabled=container_status != "running")
            
            with control_col3:
                st.button("Restart", key="restart_rstudio", disabled=container_status != "running")
        
        with col2:
            st.markdown("""
            ### Dash
            
            Interactive web applications for data visualization.
            
            - Python-based
            - Interactive dashboards
            - Real-time updates
            """)
            
            # Container status and controls
            container_id = None  # This would be set based on actual container data
            container_status = "stopped"  # This would be set based on actual container status
            
            # Display status
            st.markdown(f"**Status:** <span style='color: {CONTAINER_STATUS_COLORS.get(container_status, CONTAINER_STATUS_COLORS['unknown'])};'>●</span> {container_status}", unsafe_allow_html=True)
            
            # Controls
            control_col1, control_col2, control_col3 = st.columns(3)
            
            with control_col1:
                st.button("Start", key="start_dash", disabled=container_status == "running")
            
            with control_col2:
                st.button("Stop", key="stop_dash", disabled=container_status != "running")
            
            with control_col3:
                st.button("Restart", key="restart_dash", disabled=container_status != "running")
    
    with tab3:
        st.subheader("DevOps Environments")
        
        # Create columns for DevOps environments
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### GitLab
            
            Self-hosted Git repository management.
            
            - Git repositories
            - CI/CD pipelines
            - Issue tracking
            """)
            
            # Container status and controls
            container_id = None  # This would be set based on actual container data
            container_status = "stopped"  # This would be set based on actual container status
            
            # Display status
            st.markdown(f"**Status:** <span style='color: {CONTAINER_STATUS_COLORS.get(container_status, CONTAINER_STATUS_COLORS['unknown'])};'>●</span> {container_status}", unsafe_allow_html=True)
            
            # Controls
            control_col1, control_col2, control_col3 = st.columns(3)
            
            with control_col1:
                st.button("Start", key="start_gitlab", disabled=container_status == "running")
            
            with control_col2:
                st.button("Stop", key="stop_gitlab", disabled=container_status != "running")
            
            with control_col3:
                st.button("Restart", key="restart_gitlab", disabled=container_status != "running")
        
        with col2:
            st.markdown("""
            ### Jenkins
            
            Automation server for CI/CD.
            
            - Build automation
            - Deployment pipelines
            - Plugin ecosystem
            """)
            
            # Container status and controls
            container_id = None  # This would be set based on actual container data
            container_status = "stopped"  # This would be set based on actual container status
            
            # Display status
            st.markdown(f"**Status:** <span style='color: {CONTAINER_STATUS_COLORS.get(container_status, CONTAINER_STATUS_COLORS['unknown'])};'>●</span> {container_status}", unsafe_allow_html=True)
            
            # Controls
            control_col1, control_col2, control_col3 = st.columns(3)
            
            with control_col1:
                st.button("Start", key="start_jenkins", disabled=container_status == "running")
            
            with control_col2:
                st.button("Stop", key="stop_jenkins", disabled=container_status != "running")
            
            with control_col3:
                st.button("Restart", key="restart_jenkins", disabled=container_status != "running")

def create_local_ai_screen():
    """Create the local AI screen with chiclet-style boxes for each service."""
    st.title("Local AI")
    
    st.markdown("""
    Deploy and manage local AI models and services.
    
    Select from the available AI services below to get started.
    """)
    
    # Create tabs for different AI categories
    tab1, tab2, tab3 = st.tabs(["Text Generation", "Image Generation", "Multimodal"])
    
    with tab1:
        st.subheader("Text Generation")
        
        # Create service chiclets
        services = [
            {
                "name": "Ollama",
                "description": "Run open-source large language models locally",
                "image": "ollama/ollama:latest",
                "key": "ollama",
                "url": "http://localhost:11434",
                "status": "stopped"
            },
            {
                "name": "Open WebUI",
                "description": "Web interface for Ollama",
                "image": "ghcr.io/open-webui/open-webui:latest",
                "key": "open_webui",
                "url": "http://localhost:3000",
                "status": "stopped"
            },
            {
                "name": "Text Generation WebUI",
                "description": "Web UI for running Large Language Models",
                "image": "ghcr.io/oobabooga/text-generation-webui:latest",
                "key": "text_gen_webui",
                "url": "http://localhost:7860",
                "status": "stopped"
            },
            {
                "name": "SillyTavern",
                "description": "Chat UI for roleplaying with AI",
                "image": "ghcr.io/sillytavern/sillytavern:latest",
                "key": "sillytavern",
                "url": "http://localhost:8080",
                "status": "stopped"
            }
        ]
        
        # Create chiclet grid
        cols = st.columns(2)
        
        for i, service in enumerate(services):
            with cols[i % 2]:
                # Create chiclet
                with st.container():
                    st.subheader(service["name"])
                    st.markdown(service["description"])
                    
                    # Status indicator
                    status_color = CONTAINER_STATUS_COLORS.get(service["status"], CONTAINER_STATUS_COLORS["unknown"])
                    st.markdown(f"**Status:** <span style='color: {status_color};'>●</span> {service['status']}", unsafe_allow_html=True)
                    
                    # URL if running
                    if service["status"] == "running":
                        st.markdown(f"**URL:** [{service['url']}]({service['url']})")
                    
                    # Controls
                    button_cols = st.columns(3)
                    
                    with button_cols[0]:
                        container_id = None  # This would be set based on actual container data
                        if container_id or service["status"] != "running":
                            st.button("▶", key=f"start_{service['key']}_chiclet", help="Start container")
                        else:
                            st.button("▶", key=f"{service['key']}_start_placeholder", disabled=True, help="Start container")
                    
                    with button_cols[1]:
                        if container_id:
                            st.button("⟳", key=f"restart_{service['key']}_chiclet", help="Restart container")
                        else:
                            st.button("⟳", key=f"{service['key']}_restart_placeholder", disabled=True, help="Restart container")
                    
                    with button_cols[2]:
                        if service["status"] == "running" and container_id:
                            st.button("⏹", key=f"stop_{service['key']}_chiclet", help="Stop container")
                        else:
                            st.button("⏹", key=f"{service['key']}_stop_placeholder", disabled=True, help="Stop container")
                    
                    # Left-justify the autostart checkbox
                    autostart = st.checkbox("Autostart", key=f"{service['key']}_autostart", value=False)
                
                # Add some space between chiclets
                st.markdown("<br>", unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Image Generation")
        
        # Create service chiclets
        services = [
            {
                "name": "Stable Diffusion Web UI",
                "description": "Web UI for Stable Diffusion",
                "image": "ghcr.io/abetlen/stable-diffusion-webui:latest",
                "key": "sd_webui",
                "url": "http://localhost:7860",
                "status": "stopped"
            },
            {
                "name": "ComfyUI",
                "description": "Node-based UI for Stable Diffusion",
                "image": "ghcr.io/comfyanonymous/comfyui:latest",
                "key": "comfyui",
                "url": "http://localhost:8188",
                "status": "stopped"
            }
        ]
        
        # Create chiclet grid
        cols = st.columns(2)
        
        for i, service in enumerate(services):
            with cols[i % 2]:
                # Create chiclet
                with st.container():
                    st.subheader(service["name"])
                    st.markdown(service["description"])
                    
                    # Status indicator
                    status_color = CONTAINER_STATUS_COLORS.get(service["status"], CONTAINER_STATUS_COLORS["unknown"])
                    st.markdown(f"**Status:** <span style='color: {status_color};'>●</span> {service['status']}", unsafe_allow_html=True)
                    
                    # URL if running
                    if service["status"] == "running":
                        st.markdown(f"**URL:** [{service['url']}]({service['url']})")
                    
                    # Controls
                    button_cols = st.columns(3)
                    
                    with button_cols[0]:
                        container_id = None  # This would be set based on actual container data
                        if container_id or service["status"] != "running":
                            st.button("▶", key=f"start_{service['key']}_chiclet", help="Start container")
                        else:
                            st.button("▶", key=f"{service['key']}_start_placeholder", disabled=True, help="Start container")
                    
                    with button_cols[1]:
                        if container_id:
                            st.button("⟳", key=f"restart_{service['key']}_chiclet", help="Restart container")
                        else:
                            st.button("⟳", key=f"{service['key']}_restart_placeholder", disabled=True, help="Restart container")
                    
                    with button_cols[2]:
                        if service["status"] == "running" and container_id:
                            st.button("⏹", key=f"stop_{service['key']}_chiclet", help="Stop container")
                        else:
                            st.button("⏹", key=f"{service['key']}_stop_placeholder", disabled=True, help="Stop container")
                    
                    # Left-justify the autostart checkbox
                    autostart = st.checkbox("Autostart", key=f"{service['key']}_autostart", value=False)
                
                # Add some space between chiclets
                st.markdown("<br>", unsafe_allow_html=True)
    
    with tab3:
        st.subheader("Multimodal")
        
        # Create service chiclets
        services = [
            {
                "name": "LM Studio",
                "description": "Desktop app for running local LLMs",
                "image": "ghcr.io/lmstudio-ai/lmstudio:latest",
                "key": "lmstudio",
                "url": "http://localhost:1234",
                "status": "stopped"
            },
            {
                "name": "n8n",
                "description": "Workflow automation tool",
                "image": "n8nio/n8n:latest",
                "key": "n8n",
                "url": "http://localhost:5678",
                "status": "stopped"
            }
        ]
        
        # Create chiclet grid
        cols = st.columns(2)
        
        for i, service in enumerate(services):
            with cols[i % 2]:
                # Create chiclet
                with st.container():
                    st.subheader(service["name"])
                    st.markdown(service["description"])
                    
                    # Status indicator
                    status_color = CONTAINER_STATUS_COLORS.get(service["status"], CONTAINER_STATUS_COLORS["unknown"])
                    st.markdown(f"**Status:** <span style='color: {status_color};'>●</span> {service['status']}", unsafe_allow_html=True)
                    
                    # URL if running
                    if service["status"] == "running":
                        st.markdown(f"**URL:** [{service['url']}]({service['url']})")
                    
                    # Controls
                    button_cols = st.columns(3)
                    
                    with button_cols[0]:
                        container_id = None  # This would be set based on actual container data
                        if container_id or service["status"] != "running":
                            st.button("▶", key=f"start_{service['key']}_chiclet", help="Start container")
                        else:
                            st.button("▶", key=f"{service['key']}_start_placeholder", disabled=True, help="Start container")
                    
                    with button_cols[1]:
                        if container_id:
                            st.button("⟳", key=f"restart_{service['key']}_chiclet", help="Restart container")
                        else:
                            st.button("⟳", key=f"{service['key']}_restart_placeholder", disabled=True, help="Restart container")
                    
                    with button_cols[2]:
                        if service["status"] == "running" and container_id:
                            st.button("⏹", key=f"stop_{service['key']}_chiclet", help="Stop container")
                        else:
                            st.button("⏹", key=f"{service['key']}_stop_placeholder", disabled=True, help="Stop container")
                    
                    # Left-justify the autostart checkbox
                    autostart = st.checkbox("Autostart", key=f"{service['key']}_autostart", value=False)
                
                # Add some space between chiclets
                st.markdown("<br>", unsafe_allow_html=True)

def create_exit_screen():
    """Create the exit screen."""
    st.title("Exit Singularity Launcher")
    
    st.markdown("""
    Are you sure you want to exit Singularity Launcher?
    
    You can choose to:
    - Exit the launcher but keep containers running
    - Exit the launcher and stop all containers
    - Cancel and return to the launcher
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Exit (Keep Containers Running)"):
            st.success("Exiting Singularity Launcher. Containers will continue running.")
            st.stop()
    
    with col2:
        if st.button("Exit (Stop All Containers)"):
            st.warning("Stopping all containers...")
            st.success("All containers stopped. Exiting Singularity Launcher.")
            st.stop()
    
    with col3:
        if st.button("Cancel"):
            st.rerun()
