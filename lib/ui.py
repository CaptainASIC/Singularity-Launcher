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
        
        cols = st.columns(len(containers) + 1 if containers else 2)
        
        # Container engine status
        with cols[0]:
            st.markdown("### Container Engine")
            engine_status = "Running" if containers else "Not Available"
            st.markdown(f"Status: {engine_status}")
        
        # Container statuses
        if containers:
            for i, (container_id, container) in enumerate(containers.items(), 1):
                with cols[i]:
                    st.markdown(f"### {container['name']}")
                    
                    # Status indicator
                    status_class = "status-running" if container['status'] == "running" else "status-stopped"
                    st.markdown(f'<span class="container-status {status_class}"></span> {container["status"].capitalize()}', unsafe_allow_html=True)
                    
                    # Container controls
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if container['status'] != "running":
                            st.button(f"Start {container['name']}", key=f"start_{container_id}")
                    with col2:
                        if container['status'] == "running":
                            st.button(f"Stop {container['name']}", key=f"stop_{container_id}")
                    with col3:
                        st.button(f"Restart {container['name']}", key=f"restart_{container_id}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def create_performance_widgets(metrics: Dict[str, Any]):
    """
    Create performance monitoring widgets.
    
    Args:
        metrics (Dict[str, Any]): Performance metrics
    """
    # Create a 2x2 grid for the metrics
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    # CPU usage gauge
    with col1:
        fig_cpu = create_gauge_chart(
            value=metrics['cpu']['usage'],
            title="CPU Usage",
            suffix="%"
        )
        st.plotly_chart(fig_cpu, use_container_width=True)
    
    # Memory usage gauge
    with col2:
        fig_memory = create_gauge_chart(
            value=metrics['memory']['usage'],
            title="Memory Usage",
            suffix="%"
        )
        st.plotly_chart(fig_memory, use_container_width=True)
    
    # GPU usage gauge (if available)
    with col3:
        if metrics['gpu']['type'] != "cpu":
            fig_gpu = create_gauge_chart(
                value=metrics['gpu']['usage'],
                title="GPU Usage",
                suffix="%"
            )
            st.plotly_chart(fig_gpu, use_container_width=True)
        else:
            st.info("No dedicated GPU detected")
    
    # Disk usage gauge
    with col4:
        fig_disk = create_gauge_chart(
            value=metrics['disk']['usage'],
            title="Disk Usage",
            suffix="%"
        )
        st.plotly_chart(fig_disk, use_container_width=True)
    
    # Additional metrics in a table
    metrics_data = {
        "Metric": [
            "CPU Temperature",
            "Memory Total",
            "GPU Temperature",
            "Disk Space"
        ],
        "Value": [
            f"{metrics['cpu']['temperature']:.1f}°C" if metrics['cpu']['temperature'] > 0 else "N/A",
            f"{metrics['memory']['total']} GB",
            f"{metrics['gpu']['temperature']:.1f}°C" if metrics['gpu']['temperature'] > 0 else "N/A",
            f"{metrics['disk']['used']}/{metrics['disk']['total']} GB"
        ]
    }
    
    metrics_df = pd.DataFrame(metrics_data)
    st.dataframe(metrics_df, hide_index=True, use_container_width=True)

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
                if system_info['gpu']['memory_total'] > 0:
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
    """Create the local AI screen."""
    st.title("Local AI")
    
    # Create tabs for different AI categories
    tab1, tab2, tab3, tab4 = st.tabs(["LLM", "Image Generation", "Audio", "Video"])
    
    with tab1:
        st.header("Large Language Models")
        
        # LLM platforms
        st.subheader("LLM Platforms")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ollama = st.checkbox("Ollama", value=True)
            st.markdown("Run large language models locally.")
            
            if ollama:
                ollama_models = st.multiselect(
                    "Ollama Models",
                    ["llama3", "mistral", "phi", "gemma", "codellama", "llava"],
                    default=["llama3"]
                )
        
        with col2:
            llm_webui = st.checkbox("Text Generation WebUI")
            st.markdown("Advanced interface for text generation models.")
            
            if llm_webui:
                llm_webui_models = st.multiselect(
                    "Text Generation WebUI Models",
                    ["llama-3-8b", "mistral-7b", "phi-2", "gemma-7b", "codellama-7b"],
                    default=[]
                )
        
        with col3:
            koboldai = st.checkbox("KoboldAI")
            st.markdown("User-friendly interface for text generation.")
            
            if koboldai:
                koboldai_models = st.multiselect(
                    "KoboldAI Models",
                    ["llama-3-8b", "mistral-7b", "phi-2", "gemma-7b"],
                    default=[]
                )
        
        # LLM chat interfaces
        st.subheader("LLM Chat Interfaces")
        col1, col2 = st.columns(2)
        
        with col1:
            sillytavern = st.checkbox("SillyTavern")
            st.markdown("Advanced chat UI for LLMs.")
        
        with col2:
            tavernai = st.checkbox("TavernAI")
            st.markdown("Character-based chat UI for LLMs.")
        
        # Apply button
        if st.button("Deploy LLM Containers"):
            st.success("LLM container deployment initiated. This may take a few minutes.")
    
    with tab2:
        st.header("Image Generation")
        
        # Image generation platforms
        st.subheader("Image Generation Platforms")
        col1, col2 = st.columns(2)
        
        with col1:
            sd_webui = st.checkbox("Stable Diffusion WebUI")
            st.markdown("AUTOMATIC1111's web interface for Stable Diffusion.")
            
            if sd_webui:
                sd_models = st.multiselect(
                    "Stable Diffusion Models",
                    ["SD 1.5", "SD 2.1", "SDXL", "SDXL Turbo", "Dreamshaper", "RealisticVision"],
                    default=["SDXL"]
                )
        
        with col2:
            comfyui = st.checkbox("ComfyUI")
            st.markdown("Node-based UI for Stable Diffusion.")
            
            if comfyui:
                comfyui_models = st.multiselect(
                    "ComfyUI Models",
                    ["SD 1.5", "SD 2.1", "SDXL", "SDXL Turbo", "Dreamshaper", "RealisticVision"],
                    default=["SDXL"]
                )
        
        # Apply button
        if st.button("Deploy Image Generation Containers"):
            st.success("Image generation container deployment initiated. This may take a few minutes.")
    
    with tab3:
        st.header("Audio Processing")
        
        # Audio processing platforms
        st.subheader("Audio Processing Platforms")
        col1, col2 = st.columns(2)
        
        with col1:
            tts = st.checkbox("Text-to-Speech")
            st.markdown("Convert text to natural-sounding speech.")
            
            if tts:
                tts_models = st.multiselect(
                    "TTS Models",
                    ["XTTS", "Bark", "Coqui TTS", "Piper TTS"],
                    default=["XTTS"]
                )
        
        with col2:
            stt = st.checkbox("Speech-to-Text")
            st.markdown("Convert speech to text.")
            
            if stt:
                stt_models = st.multiselect(
                    "STT Models",
                    ["Whisper", "Vosk", "DeepSpeech"],
                    default=["Whisper"]
                )
        
        # Apply button
        if st.button("Deploy Audio Processing Containers"):
            st.success("Audio processing container deployment initiated. This may take a few minutes.")
    
    with tab4:
        st.header("Video Processing")
        
        # Video processing platforms
        st.subheader("Video Processing Platforms")
        col1, col2 = st.columns(2)
        
        with col1:
            video_generation = st.checkbox("Video Generation")
            st.markdown("Generate videos from text prompts or images.")
            
            if video_generation:
                video_models = st.multiselect(
                    "Video Generation Models",
                    ["Stable Video Diffusion", "ModelScope", "AnimateDiff"],
                    default=["Stable Video Diffusion"]
                )
        
        with col2:
            video_upscaling = st.checkbox("Video Upscaling")
            st.markdown("Enhance video quality and resolution.")
            
            if video_upscaling:
                upscaling_models = st.multiselect(
                    "Video Upscaling Models",
                    ["Real-ESRGAN", "BSRGAN", "SwinIR"],
                    default=["Real-ESRGAN"]
                )
        
        # Apply button
        if st.button("Deploy Video Processing Containers"):
            st.success("Video processing container deployment initiated. This may take a few minutes.")

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
