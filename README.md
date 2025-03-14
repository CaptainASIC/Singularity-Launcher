# Singularity Launcher

A Streamlit UI for deploying Lab and AI Environments with support for various CPU and GPU architectures.

## Overview

Singularity Launcher is a powerful tool designed to simplify the deployment of software and AI containers locally. It provides an intuitive interface for managing your development environment and AI tools, with optimizations for different hardware configurations.

### Key Features

- **Hardware Detection**: Automatically detects and optimizes for your CPU (AMD/ARM/Intel/Apple) and GPU (AMD/Apple/NVIDIA/CPU-Only)
- **DGX and Jetson Optimizations**: Special configurations for NVIDIA DGX and Jetson devices
- **Lab Setup**: Tools for configuring your development environment
- **Local AI**: Deploy and manage AI containers with ease
- **Container Management**: Start, stop, and restart containers directly from the UI
- **Performance Monitoring**: Real-time monitoring of system resources

## Requirements

- Python 3.8+
- Podman (recommended) or Docker
- Internet connection for downloading container images

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Singularity-Launcher.git
   cd Singularity-Launcher
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the launcher:
   ```bash
   python main.py
   ```

## Usage

1. **Lab Setup**: Configure your development environment with the necessary tools and libraries.
2. **Local AI**: Deploy AI containers optimized for your hardware.
3. **Container Management**: Use the footer controls to start, stop, or restart containers.
4. **Exit**: Safely shut down the application and optionally stop running containers.

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
│   └── podman/             # Podman-specific configurations
└── data/                   # Data directory for containers
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by FusionLoom and AI-Garage projects
- Built with Streamlit for a responsive and interactive UI
- Uses Podman for secure, rootless containers
