# Singularity Launcher

A Streamlit UI for deploying Lab and AI Environments with support for various CPU and GPU architectures.

## Overview

Singularity Launcher is a powerful tool designed to simplify the deployment of software and AI containers locally. It provides an intuitive interface for managing your development environment and AI tools, with optimizations for different hardware configurations.

### Key Features

- **Hardware Detection**: Automatically detects and optimizes for your CPU (AMD/ARM/Intel/Apple) and GPU (AMD/Apple/NVIDIA/CPU-Only)
- **Platform-Specific Optimizations**: 
  - **NVIDIA**: Optimized configurations for consumer GPUs, DGX systems, and Jetson devices
    - **DGX Systems**: Multi-GPU support with 128GB memory systems and 96GB allocation to Ollama
    - **Jetson Devices**: Detailed optimizations for specific Jetson models:
      - **Orin Nano 4GB**: 3GB memory allocation and 4 threads
      - **Orin Nano 8GB**: 6GB memory allocation and 6 threads
      - **Orin NX 8GB**: 6GB memory allocation and 8 threads
      - **Orin NX 16GB**: 12GB memory allocation and 8 threads
      - **AGX Orin 32GB**: 24GB memory allocation and 12 threads
      - **AGX Orin 64GB**: 48GB memory allocation and 16 threads
    - **RTX/GeForce**: Optimized for consumer NVIDIA GPUs
  - **AMD**: ROCm-enabled configurations for AMD GPUs
  - **Apple**: Optimized for Apple Silicon with Metal GPU acceleration
  - **x86**: Fallback configurations for CPU-only systems
- **Supported Applications**:
  - **Ollama**: Local LLM inference with Open WebUI interface
  - **TavernAI**: Character-based chat interface
  - **SillyTavern**: Advanced character-based chat interface with more features
  - **A1111 (Stable Diffusion Web UI)**: Image generation and editing
  - **ComfyUI**: Node-based UI for Stable Diffusion workflows
  - **n8n**: Workflow automation platform
  - **Text Generation WebUI (oobabooga)**: Advanced text generation interface
  - **Archon**: AI agent framework with MCP integration
  - **Supabase**: Open source Firebase alternative with PostgreSQL database
- **Integrated Web UI for Ollama**: All platform configurations now include Open WebUI, a powerful web interface for Ollama that provides:
  - User-friendly chat interface
  - Model management
  - Conversation history
  - Prompt templates
  - Document upload and analysis
  - Accessible via browser at http://localhost:3000
- **Interactive Service Management**:
  - Automatic detection of missing services
  - Hardware-appropriate container builds with one click
  - Intelligent compose file selection based on detected hardware
- **Lab Setup**: Tools for configuring your development environment
- **Local AI**: Deploy and manage AI containers with ease
- **Container Management**: Start, stop, and restart containers directly from the UI
- **Performance Monitoring**: Real-time monitoring of system resources

## Requirements

- Python 3.8+
- Podman (recommended) or Docker
- Internet connection for downloading container images
- Linux or macOS (Windows not supported)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Singularity-Launcher.git
   cd Singularity-Launcher
   ```

2. Run the launcher script:
   ```bash
   ./launch.sh
   ```

The script will automatically check for dependencies, install them if needed, and launch the application.

## Usage

1. **Lab Setup**: Configure your development environment with the necessary tools and libraries.
2. **Local AI**: Deploy AI containers optimized for your hardware.
   - Click on the start button (▶) for any service
   - If the service container doesn't exist, you'll be prompted to build it
   - The system will automatically select the appropriate compose file for your hardware
   - Once built, the service will start automatically
3. **Container Management**: Use the footer controls to start, stop, or restart containers.
4. **Exit**: Safely shut down the application and optionally stop running containers.

### Accessing Ollama Web UI

After starting the Ollama service:

1. Wait for both the Ollama and Open WebUI containers to start
2. Open your web browser and navigate to http://localhost:3000
3. The web interface will automatically connect to your local Ollama instance
4. You can now interact with your models through the user-friendly interface

### Hardware-Optimized Containers

Singularity Launcher automatically detects your hardware and selects the appropriate container configuration:

- **NVIDIA DGX Systems**: Uses multi-GPU configurations with optimized memory allocation
- **NVIDIA Jetson Devices**: Selects the specific configuration for your Jetson model (Orin Nano, Orin NX, AGX Orin)
- **NVIDIA Consumer GPUs**: Uses optimized configurations for RTX/GeForce cards
- **AMD GPUs**: Uses ROCm-enabled configurations
- **Apple Silicon**: Uses Metal-accelerated configurations
- **CPU-only systems**: Falls back to CPU-optimized configurations

## Container Configuration Guidelines

When creating or modifying container configurations, follow these guidelines to ensure compatibility across all platforms:

### General Structure

All service configurations should follow this general structure:

```yaml
version: '3'

services:
  primary-service:
    container_name: singularity-[service-name]
    image: [image-name]:[tag]
    restart: unless-stopped
    volumes:
      - ${SERVICE_VOLUME:-./data/[service-name]}:[container-path]
    environment:
      - KEY=value
    networks:
      - singularity_net
    # Platform-specific configurations follow

  web-ui:  # If applicable
    container_name: singularity-[service-name]-ui
    image: [ui-image-name]:[tag]
    volumes:
      - ${UI_VOLUME:-./data/[service-name]-ui}:[container-path]
    depends_on:
      - primary-service
    ports:
      - "[port]:8080"  # Standardize on 8080 internal port when possible
    environment:
      - 'SERVICE_URL=http://singularity-[service-name]:[port]'
    restart: unless-stopped
    networks:
      - singularity_net

networks:
  singularity_net:
    external: true
```

### Platform-Specific Configurations

#### Apple Silicon

```yaml
# Apple Silicon specific
environment:
  - USE_METAL=1  # If applicable
platform: linux/arm64
deploy:
  resources:
    limits:
      cpus: '0.8'  # Use up to 80% of available CPU
      memory: 24G  # Adjust based on model
```

#### NVIDIA (RTX/GeForce)

```yaml
# NVIDIA specific
environment:
  - NVIDIA_VISIBLE_DEVICES=all
  - NVIDIA_DRIVER_CAPABILITIES=all
runtime: nvidia
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
shm_size: 8g  # Adjust based on model
ulimits:
  memlock:
    soft: -1
    hard: -1
```

#### NVIDIA Jetson

```yaml
# Jetson specific
environment:
  - NVIDIA_VISIBLE_DEVICES=all
  - NVIDIA_DRIVER_CAPABILITIES=all
  - NUM_THREADS=8  # Adjust based on Jetson model
runtime: nvidia
deploy:
  resources:
    limits:
      memory: 6G  # Adjust based on Jetson model
      cpus: '8'   # Adjust based on Jetson model
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

#### AMD

```yaml
# AMD specific
devices:
  - /dev/kfd:/dev/kfd
  - /dev/dri:/dev/dri
group_add:
  - video
deploy:
  resources:
    reservations:
      devices:
        - driver: amd
          capabilities: [gpu]
```

### Best Practices

1. **Consistent Naming**: Use `singularity-[service-name]` for container names
2. **Volume Mounting**: Use environment variables with fallbacks for volume paths
3. **Network Configuration**: Always use the `singularity_net` external network
4. **Resource Limits**: Set appropriate resource limits based on platform capabilities
5. **Web UI Services**: 
   - Use port 3000-3999 range for web interfaces
   - Always include `depends_on` to ensure proper startup order
   - Connect to primary service using container name, not localhost
6. **Environment Variables**: Use uppercase for environment variable names
7. **Platform Specification**: Include `platform: linux/arm64` for Apple Silicon
8. **Avoid Host Network Mode**: Use the standard network configuration instead

### Common Issues to Avoid

1. **Extra Hosts Configuration**: Do not include `extra_hosts` entries as they can cause connectivity issues
2. **Host Network Mode**: Avoid using `network_mode: host` as it can cause conflicts
3. **Fixed Resource Limits**: Ensure resource limits are appropriate for the target platform
4. **Hardcoded Paths**: Use environment variables with fallbacks for all paths
5. **Missing Dependencies**: Ensure all required services are included in the `depends_on` section

## Architecture

Singularity Launcher is built with a modular architecture:

- **Core**: System detection, hardware optimization, and container management
- **UI**: Streamlit-based user interface with responsive design
- **Modules**: Specialized components for different functionalities (Lab Setup, Local AI)
- **Utils**: Helper functions for system operations and performance monitoring

## Development

### Project Structure

```
Singularity-Launcher/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── .gitignore              # Git ignore file
├── launch.sh               # Launch script for Linux/macOS
├── cfg/                    # Configuration files
│   └── config.sample.ini   # Sample configuration
├── lib/                    # Library modules
│   ├── __init__.py
│   ├── system.py           # System detection and information
│   ├── containers.py       # Container management
│   ├── performance.py      # Performance monitoring
│   └── ui.py               # UI components
├── compose/                # Container compose files
│   ├── platforms/          # Platform-specific configurations
│   │   ├── nvidia/         # NVIDIA GPU configurations
│   │   │   ├── dgx/        # DGX-specific configurations
│   │   │   ├── rtx/        # RTX/GeForce configurations
│   │   │   └── jetson/     # Jetson-specific configurations
│   │   ├── amd/            # AMD GPU configurations
│   │   ├── apple/          # Apple Silicon configurations
│   │   └── x86/            # CPU-only configurations
│   └── podman/             # Podman-specific configurations
└── data/                   # Data directory for containers
    ├── ollama/             # Ollama data directory
    ├── open-webui/         # Open WebUI data directory
    ├── n8n/                # n8n data directory
    ├── oobabooga/          # Text Generation WebUI data directory
    ├── tavernai/           # TavernAI data directory
    ├── sillytavern/        # SillyTavern data directory
    ├── a1111/              # Stable Diffusion Web UI data directory
    ├── comfyui/            # ComfyUI data directory
    ├── archon/             # Archon data directory
    └── supabase/           # Supabase data directory
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by FusionLoom and AI-Garage projects
- Built with Streamlit for a responsive and interactive UI
- Uses Podman for secure, rootless containers
- Integrates Open WebUI for a user-friendly interface to Ollama
