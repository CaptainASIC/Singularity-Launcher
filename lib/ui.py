"""
UI Components Module

This module provides UI components and utilities for the Streamlit interface,
including custom widgets, styling, and layout helpers.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, List, Tuple, Optional, Callable

def set_page_config():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="Singularity Launcher",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_custom_css():
    """Apply custom CSS styling to the Streamlit interface."""
    st.markdown("""
    <style>
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #1E1E1E;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Arial', sans-serif;
        font-weight: bold;
    }
    
    /* Performance metrics */
    .metric-container {
        background-color: rgba(0, 0, 0, 0.1);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #AAAAAA;
    }
    
    .metric-value {
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    /* Container status indicators */
    .container-status {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    
    .status-running {
        background-color: #00FF00;
    }
    
    .status-stopped {
        background-color: #FF0000;
    }
    
    .status-unknown {
        background-color: #FFFF00;
    }
    
    /* Footer */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #1E1E1E;
        padding: 10px;
        z-index: 999;
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 5px;
        font-weight: bold;
    }
    
    /* Card styling */
    .card {
        background-color: rgba(0, 0, 0, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #2C2C2C;
        border-radius: 5px 5px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4C4C4C;
    }
    </style>
    """, unsafe_allow_html=True)

def create_sidebar():
    """Create the sidebar with navigation menu."""
    with st.sidebar:
        st.title("🚀 Singularity")
        st.subheader("Launcher")
        
        # Add some space
        st.markdown("---")
        
        # Navigation menu
        st.subheader("Navigation")
        selected = st.radio(
            "Go to",
            ["Home", "Lab Setup", "Local AI", "Exit"],
            label_visibility="collapsed"
        )
        
        # Add some space
        st.markdown("---")
        
        # System information section
        st.subheader("System Information")
        
        return selected

def create_footer(containers: Dict[str, Dict[str, Any]]):
    """
    Create the footer with container controls.
    
    Args:
        containers (Dict[str, Dict[str, Any]]): Dictionary of containers
    """
    with st.container():
        st.markdown('<div class="footer">', unsafe_allow_html=True)
        
        # Create columns with the first column being smaller (1/3 the size)
        col_widths = [1] + [3] * len(containers) if containers else [1, 3]
        cols = st.columns(col_widths)
        
        # Container engine status (smaller column)
        with cols[0]:
            st.markdown("### Container Engine")
            engine_status = "Running" if containers else "Not Available"
            st.markdown(f"Status: {engine_status}")
        
        # Container statuses
        if containers:
            for i, (container_id, container) in enumerate(containers.items(), 1):
                with cols[i]:
                    # Status indicator with inline controls
                    status_class = "status-running" if container['status'] == "running" else "status-stopped"
                    
                    # Create a row with name and controls
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div>
                            <span style="font-weight: bold; font-size: 1.1rem;">{container['name']}</span>
                            <span class="container-status {status_class}" style="margin-left: 5px;"></span>
                            <span style="font-size: 0.9rem;">{container["status"].capitalize()}</span>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <span id="start_{container_id}_footer"></span>
                            <span id="stop_{container_id}_footer"></span>
                            <span id="restart_{container_id}_footer"></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Container controls as text links
                    controls_html = ""
                    
                    # Start link
                    if container['status'] != "running":
                        controls_html += f"""<a href="#" id="start_{container_id}_footer" 
                                            style="margin-right: 10px; color: #4CAF50; text-decoration: none;">Start</a>"""
                    else:
                        controls_html += f"""<span style="margin-right: 10px; color: #555555;">Start</span>"""
                    
                    # Stop link
                    if container['status'] == "running":
                        controls_html += f"""<a href="#" id="stop_{container_id}_footer" 
                                            style="margin-right: 10px; color: #F44336; text-decoration: none;">Stop</a>"""
                    else:
                        controls_html += f"""<span style="margin-right: 10px; color: #555555;">Stop</span>"""
                    
                    # Restart link
                    controls_html += f"""<a href="#" id="restart_{container_id}_footer" 
                                        style="color: #2196F3; text-decoration: none;">Restart</a>"""
                    
                    # Add the controls to the footer
                    st.markdown(f"""
                    <div style="text-align: right; font-size: 0.9rem;">
                        {controls_html}
                    </div>
                    """, unsafe_allow_html=True)
                    
        st.markdown('</div>', unsafe_allow_html=True)

def create_performance_widgets(metrics: Dict[str, Any]):
    """
    Create performance monitoring widgets optimized for sidebar display.
    
    Args:
        metrics (Dict[str, Any]): Performance metrics
    """
    # Create compact metrics display for sidebar
    # CPU and Memory in first row
    col1, col2 = st.columns(2)
    
    # CPU usage as a progress bar
    with col1:
        st.markdown("**CPU**")
        st.progress(metrics['cpu']['usage'] / 100)
        st.caption(f"{metrics['cpu']['usage']:.1f}% | {metrics['cpu']['temperature']:.1f}°C")
    
    # Memory usage as a progress bar
    with col2:
        st.markdown("**Memory**")
        st.progress(metrics['memory']['usage'] / 100)
        st.caption(f"{metrics['memory']['usage']:.1f}% | {metrics['memory']['total']} GB")
    
    # GPU and Disk in second row
    col3, col4 = st.columns(2)
    
    # GPU usage as a progress bar (if available)
    with col3:
        st.markdown("**GPU**")
        if metrics['gpu']['type'] != "cpu":
            st.progress(metrics['gpu']['usage'] / 100)
            st.caption(f"{metrics['gpu']['usage']:.1f}% | {metrics['gpu']['temperature']:.1f}°C")
        else:
            st.progress(0)
            st.caption("N/A")
    
    # Disk usage as a progress bar
    with col4:
        st.markdown("**Disk**")
        st.progress(metrics['disk']['usage'] / 100)
        st.caption(f"{metrics['disk']['usage']:.1f}% | {metrics['disk']['used']}/{metrics['disk']['total']} GB")

def create_gauge_chart(value: float, title: str, suffix: str = "") -> go.Figure:
    """
    Create a gauge chart for displaying metrics.
    
    Args:
        value (float): The value to display
        title (str): The title of the gauge
        suffix (str): Suffix to add to the value (e.g., "%")
    
    Returns:
        go.Figure: The Plotly gauge chart
    """
    # Define colors for different ranges
    if value < 60:
        color = "green"
    elif value < 80:
        color = "yellow"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 60], 'color': "rgba(0, 255, 0, 0.2)"},
                {'range': [60, 80], 'color': "rgba(255, 255, 0, 0.2)"},
                {'range': [80, 100], 'color': "rgba(255, 0, 0, 0.2)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        },
        number={'suffix': suffix}
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    
    return fig

def create_system_info_card(system_info: Dict[str, Any]):
    """
    Create a card displaying system information.
    
    Args:
        system_info (Dict[str, Any]): System information
    """
    with st.expander("System Information", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Hardware")
            st.markdown(f"**CPU:** {system_info['cpu']['brand']}")
            st.markdown(f"**Cores:** {system_info['cpu']['cores']}")
            st.markdown(f"**Architecture:** {system_info['cpu']['arch']}")
            st.markdown(f"**Memory:** {system_info['memory']['total']} GB")
            
            if system_info['gpu']['type'] != "cpu":
                st.markdown(f"**GPU:** {system_info['gpu']['name']}")
                # For Apple Silicon, GPU memory is shared with system memory
                if system_info['gpu']['type'] == "apple":
                    st.markdown("**GPU Memory:** Shared with system memory")
                elif 'memory_total' in system_info['gpu'] and system_info['gpu']['memory_total'] > 0:
                    st.markdown(f"**GPU Memory:** {system_info['gpu']['memory_total']} GB")
        
        with col2:
            st.markdown("### Software")
            st.markdown(f"**OS:** {system_info['os']['name']} {system_info['os']['release']}")
            st.markdown(f"**Platform:** {system_info['platform'].capitalize()}")
            
            if system_info['platform'] == "jetson" and system_info['jetson_model']:
                st.markdown(f"**Jetson Model:** {system_info['jetson_model'].replace('_', ' ').title()}")
            
            # Container engine info
            container_engine = system_info.get('container_engine', {})
            if container_engine and container_engine.get('available', False):
                st.markdown(f"**Container Engine:** {container_engine['name'].capitalize()} {container_engine['version']}")
            else:
                st.markdown("**Container Engine:** Not available")

def create_welcome_screen():
    """Create the welcome screen."""
    st.title("Welcome to Singularity Launcher")
    
    st.markdown("""
    Singularity Launcher is a powerful tool designed to simplify the deployment of software and AI containers locally.
    It provides an intuitive interface for managing your development environment and AI tools, with optimizations for
    different hardware configurations.
    
    ## Getting Started
    
    1. Use the sidebar to navigate between different sections
    2. The **Lab Setup** section allows you to configure your development environment
    3. The **Local AI** section lets you deploy and manage AI containers
    4. Use the footer controls to manage running containers
    
    ## Features
    
    - **Hardware Detection**: Automatically detects and optimizes for your CPU and GPU
    - **DGX and Jetson Optimizations**: Special configurations for NVIDIA DGX and Jetson devices
    - **Container Management**: Start, stop, and restart containers directly from the UI
    - **Performance Monitoring**: Real-time monitoring of system resources
    """)

def create_lab_setup_screen():
    """Create the lab setup screen."""
    st.title("Lab Setup")
    
    # Create tabs for different lab setup options
    tab1, tab2, tab3 = st.tabs(["Development Environment", "System Tools", "Custom Setup"])
    
    with tab1:
        st.header("Development Environment")
        
        # Programming languages section
        st.subheader("Programming Languages")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            python = st.checkbox("Python", value=True)
            st.markdown("Python development environment with common data science and ML libraries.")
            
            if python:
                python_version = st.selectbox("Python Version", ["3.8", "3.9", "3.10", "3.11", "3.12"])
                
                st.multiselect(
                    "Python Packages",
                    ["numpy", "pandas", "scikit-learn", "tensorflow", "pytorch", "matplotlib", "streamlit"],
                    default=["numpy", "pandas", "matplotlib", "streamlit"]
                )
        
        with col2:
            javascript = st.checkbox("JavaScript/Node.js")
            st.markdown("Node.js development environment with npm and common packages.")
            
            if javascript:
                node_version = st.selectbox("Node.js Version", ["16.x", "18.x", "20.x"])
                
                st.multiselect(
                    "Node.js Packages",
                    ["express", "react", "vue", "angular", "next", "typescript"],
                    default=[]
                )
        
        with col3:
            rust = st.checkbox("Rust")
            st.markdown("Rust development environment with cargo and common crates.")
            
            if rust:
                rust_version = st.selectbox("Rust Version", ["stable", "nightly"])
                
                st.multiselect(
                    "Rust Crates",
                    ["tokio", "serde", "clap", "reqwest", "rocket"],
                    default=[]
                )
        
        # Development tools section
        st.subheader("Development Tools")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            git = st.checkbox("Git", value=True)
            docker = st.checkbox("Docker")
            podman = st.checkbox("Podman", value=True)
        
        with col2:
            vscode = st.checkbox("VS Code")
            jupyter = st.checkbox("Jupyter")
            vim = st.checkbox("Vim/Neovim")
        
        with col3:
            cmake = st.checkbox("CMake")
            make = st.checkbox("Make")
            gcc = st.checkbox("GCC/Clang")
        
        # Apply button
        if st.button("Apply Development Environment Setup"):
            st.success("Development environment setup initiated. This may take a few minutes.")
    
    with tab2:
        st.header("System Tools")
        
        # System monitoring tools
        st.subheader("System Monitoring")
        col1, col2 = st.columns(2)
        
        with col1:
            htop = st.checkbox("htop")
            st.markdown("Interactive process viewer for Unix systems.")
            
            glances = st.checkbox("Glances")
            st.markdown("Cross-platform system monitoring tool.")
        
        with col2:
            btop = st.checkbox("btop++")
            st.markdown("Resource monitor with advanced features.")
            
            nvtop = st.checkbox("nvtop")
            st.markdown("NVIDIA GPU process monitoring.")
        
        # Network tools
        st.subheader("Network Tools")
        col1, col2 = st.columns(2)
        
        with col1:
            nmap = st.checkbox("Nmap")
            st.markdown("Network discovery and security auditing.")
            
            wireshark = st.checkbox("Wireshark")
            st.markdown("Network protocol analyzer.")
        
        with col2:
            iperf = st.checkbox("iperf")
            st.markdown("Network performance measurement tool.")
            
            mtr = st.checkbox("mtr")
            st.markdown("Network diagnostic tool combining ping and traceroute.")
        
        # Apply button
        if st.button("Apply System Tools Setup"):
            st.success("System tools setup initiated. This may take a few minutes.")
    
    with tab3:
        st.header("Custom Setup")
        
        # Custom package installation
        st.subheader("Custom Package Installation")
        
        package_manager = st.selectbox(
            "Package Manager",
            ["apt (Debian/Ubuntu)", "dnf (Fedora/RHEL)", "pacman (Arch)", "brew (macOS)", "chocolatey (Windows)"]
        )
        
        packages = st.text_area("Packages (one per line)")
        
        # Custom script execution
        st.subheader("Custom Script Execution")
        
        script = st.text_area("Shell Script")
        
        # Apply button
        if st.button("Apply Custom Setup"):
            if packages or script:
                st.success("Custom setup initiated. This may take a few minutes.")
            else:
                st.warning("Please specify packages or a script to execute.")

def create_local_ai_screen():
    """Create the local AI screen with chiclet-style boxes for each service."""
    st.title("Local AI")
    
    # Add custom CSS for chiclet boxes
    st.markdown("""
    <style>
    .chiclet-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: flex-start;
    }
    
    .chiclet-box {
        background-color: rgba(49, 51, 63, 0.7);
        border-radius: 10px;
        padding: 15px;
        width: 200px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .chiclet-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
    }
    
    .chiclet-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .chiclet-logo {
        width: 80px;
        height: 80px;
        margin: 10px auto;
        display: block;
    }
    
    .chiclet-controls {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: 15px;
    }
    
    .control-button {
        border: none;
        border-radius: 5px;
        padding: 5px 10px;
        cursor: pointer;
        font-size: 0.8rem;
    }
    
    .play-button {
        background-color: #4CAF50;
        color: white;
    }
    
    .restart-button {
        background-color: #2196F3;
        color: white;
    }
    
    .stop-button {
        background-color: #F44336;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Define the services with their logos (all using emojis)
    services = [
        {
            "name": "Ollama",
            "logo": "🦙",
            "description": "Run large language models locally",
            "default_url": "http://localhost:11434"
        },
        {
            "name": "Silly Tavern",
            "logo": "🍺",
            "description": "Advanced chat UI for LLMs",
            "default_url": "http://localhost:8000"
        },
        {
            "name": "Tavern AI",
            "logo": "🏮",
            "description": "Character-based chat UI for LLMs",
            "default_url": "http://localhost:8080"
        },
        {
            "name": "Oobabooga",
            "logo": "🤖",
            "description": "Text generation web UI",
            "default_url": "http://localhost:7860"
        },
        {
            "name": "A1111",
            "logo": "🖼️",
            "description": "Stable Diffusion web UI",
            "default_url": "http://localhost:7860"
        },
        {
            "name": "ComfyUI",
            "logo": "🎨",
            "description": "Node-based UI for Stable Diffusion",
            "default_url": "http://localhost:8188"
        },
        {
            "name": "n8n",
            "logo": "⚙️",
            "description": "Workflow automation tool",
            "default_url": "http://localhost:5678"
        },
        {
            "name": "Archon Agent",
            "logo": "🧠",
            "description": "AI agent framework",
            "default_url": "http://localhost:8501"
        },
        {
            "name": "Supabase",
            "logo": "🗄️",
            "description": "Open source Firebase alternative",
            "default_url": "http://localhost:3000"
        }
    ]
    
    # Create a grid layout for the chiclets
    # We'll use 5 columns to display the services
    num_services = len(services)
    num_rows = (num_services + 4) // 5  # Calculate number of rows needed (5 services per row)
    
    # Create each row
    for row in range(num_rows):
        # Create 5 columns for this row
        cols = st.columns(5)
        
        # Add up to 5 services in this row
        for col in range(5):
            service_index = row * 5 + col
            
            # Check if we still have services to display
            if service_index < num_services:
                service = services[service_index]
                
                # Create a unique key for this service
                service_key = service["name"].lower().replace(" ", "_")
                
                # Get container status if available
                container_status = "stopped"
                container_id = None
                
                # Look for a container with this service name
                for cid, container in st.session_state.containers.items():
                    if service["name"].lower() in container["name"].lower():
                        container_status = container["status"]
                        container_id = cid
                        break
                
                # Display the service in this column
                with cols[col]:
                    # Create a container for the chiclet
                    with st.container():
                        # Prepare control buttons HTML
                        status_color = "#4CAF50" if container_status == "running" else "#F44336"
                        status_text = "Running" if container_status == "running" else "Stopped"
                        
                        # We're using emoji logos for all services now
                        logo_html = f"""<div style="font-size: 36px; height: 50px; display: flex; align-items: center; 
                                      justify-content: center; margin: 10px 0;">{service["logo"]}</div>"""
                        
                        # Initialize service URL in session state if not already present
                        if f"{service_key}_url" not in st.session_state:
                            st.session_state[f"{service_key}_url"] = service["default_url"]
                        
                        # Create a header with title and config button
                        col1, col2 = st.columns([5, 1])
                        with col1:
                            st.markdown(f"<h3 style='text-align: center;'>{service['name']}</h3>", unsafe_allow_html=True)
                        with col2:
                            # Config button
                            if st.button("⚙️", key=f"config_{service_key}", help="Configure service URL"):
                                st.session_state[f"show_config_{service_key}"] = True
                        
                        # Show config dialog if button was clicked
                        if st.session_state.get(f"show_config_{service_key}", False):
                            with st.expander("Configure URL", expanded=True):
                                new_url = st.text_input("Service URL", value=st.session_state[f"{service_key}_url"], key=f"url_input_{service_key}")
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("Save", key=f"save_url_{service_key}"):
                                        st.session_state[f"{service_key}_url"] = new_url
                                        st.session_state[f"show_config_{service_key}"] = False
                                        st.rerun()
                                with col2:
                                    if st.button("Cancel", key=f"cancel_url_{service_key}"):
                                        st.session_state[f"show_config_{service_key}"] = False
                                        st.rerun()
                        
                        # Display clickable emoji logo with consistent height
                        if container_status == "running":
                            # Make the emoji clickable if the container is running
                            st.markdown(f"""
                            <div style='text-align: center; font-size: 48px; height: 80px; 
                                      display: flex; align-items: center; justify-content: center;'>
                                <a href="{st.session_state[f"{service_key}_url"]}" target="_blank" title="Launch Web UI">
                                    {service['logo']}
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # Non-clickable emoji if container is not running
                            st.markdown(f"""
                            <div style='text-align: center; font-size: 48px; height: 80px; 
                                      display: flex; align-items: center; justify-content: center;'>
                                {service['logo']}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Display description (centered)
                        st.markdown(f"<p style='text-align: center;'>{service['description']}</p>", unsafe_allow_html=True)
                        
                        # Display status indicator (centered)
                        status_color = "green" if container_status == "running" else "red"
                        status_text = "Running" if container_status == "running" else "Stopped"
                        
                        # Use a simple colored dot with text (centered)
                        st.markdown(f"""
                        <div style='text-align: center; margin: 10px 0;'>
                            <span style='color: {status_color};'>●</span> {status_text}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add the control buttons in a centered layout
                        button_cols = st.columns([1, 1, 1])
                        with button_cols[0]:
                            if container_status != "running" and container_id:
                                st.button("▶", key=f"start_{container_id}_chiclet_{service_key}", help="Start container")
                            else:
                                if container_status == "running":
                                    # Launch Web UI button (only enabled if container is running)
                                    if st.button("🌐", key=f"launch_{service_key}", help="Launch Web UI"):
                                        # Open the URL in a new tab
                                        st.markdown(f'<script>window.open("{st.session_state[f"{service_key}_url"]}", "_blank");</script>', unsafe_allow_html=True)
                                else:
                                    st.button("▶", key=f"{service_key}_start_placeholder", disabled=True, help="Start container")
                        
                        with button_cols[1]:
                            if container_id:
                                st.button("⟳", key=f"restart_{container_id}_chiclet_{service_key}", help="Restart container")
                            else:
                                st.button("⟳", key=f"{service_key}_restart_placeholder", disabled=True, help="Restart container")
                        
                        with button_cols[2]:
                            if container_status == "running" and container_id:
                                st.button("⏹", key=f"stop_{container_id}_chiclet_{service_key}", help="Stop container")
                            else:
                                st.button("⏹", key=f"{service_key}_stop_placeholder", disabled=True, help="Stop container")
                        
                        # Left-justify the autostart checkbox
                        autostart = st.checkbox("Autostart", key=f"{service_key}_autostart", value=False)

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
