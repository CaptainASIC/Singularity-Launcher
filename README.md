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

### Hardware-Optimized Containers

Singularity Launcher automatically detects your hardware and selects the appropriate container configuration:

- **NVIDIA DGX Systems**: Uses multi-GPU configurations with optimized memory allocation
- **NVIDIA Jetson Devices**: Selects the specific configuration for your Jetson model (Orin Nano, Orin NX, AGX Orin)
- **NVIDIA Consumer GPUs**: Uses optimized configurations for RTX/GeForce cards
- **AMD GPUs**: Uses ROCm-enabled configurations
- **Apple Silicon**: Uses Metal-accelerated configurations
- **CPU-only systems**: Falls back to CPU-optimized configurations

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
│   │   │   └── jetson/     # Jetson-specific configurations
│   │   ├── amd/            # AMD GPU configurations
│   │   ├── apple/          # Apple Silicon configurations
│   │   └── x86/            # CPU-only configurations
│   └── podman/             # Podman-specific configurations
└── data/                   # Data directory for containers
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by FusionLoom and AI-Garage projects
- Built with Streamlit for a responsive and interactive UI
- Uses Podman for secure, rootless containers
