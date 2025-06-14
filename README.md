# Singularity Launcher v2.5

![Singularity Launcher](static/images/logo.png)

A Streamlit UI for deploying Lab and AI Environments with support for various CPU and GPU architectures.
Now featuring comprehensive Apple Silicon M4 optimizations and enhanced UI experience.

## Features

### Core Features
- **Multi-Platform Support**: NVIDIA, AMD, Apple Silicon, and x86 CPU
- **Container Management**: Start, stop, and monitor containers
- **System Detection**: Automatic hardware detection and optimization
- **Performance Monitoring**: Real-time system resource monitoring
- **Lab Environment**: Ready-to-use lab environment with JupyterLab, VSCode, and more
- **Local AI**: Deploy and manage local AI models with Ollama, Open WebUI, and more

### New in v2.5
- **Enhanced UI**: Improved responsiveness and visual hierarchy
- **Robust Initialization**: Proper error handling and recovery
- **Improved State Management**: Reliable session state with validation
- **Error Boundaries**: Prevent cascading failures in UI components
- **Debugging Mode**: Troubleshooting tools for easier problem resolution
- **Accessibility Improvements**: Better screen reader support with ARIA attributes
- **Loading States**: Clear feedback during operations
- **Comprehensive Error Messaging**: Actionable guidance for error resolution

### Apple Silicon Optimizations
- **M4 Support**: Optimized for M4 Base, M4 Pro, and M4 Max
- **Enhanced Detection**: Automatic optimization based on detected M4 variant
- **Model Caching**: Intelligent memory management for faster model switching

## Quick Start

### Prerequisites
- Docker or Podman installed
- Python 3.8+ with pip
- 8GB+ RAM recommended (16GB+ for AI workloads)
- NVIDIA GPU, AMD GPU, or Apple Silicon for hardware acceleration

### Installation

1. Clone the repository:
```bash
git clone https://github.com/CaptainASIC/Singularity-Launcher.git
cd Singularity-Launcher
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Launch the application:
```bash
# On Linux/macOS
./launch.sh

# Or directly with Streamlit
streamlit run main.py
```

4. Access the UI in your browser at http://localhost:8501

## Platform-Specific Configurations

### Apple Silicon (M1-M4)
```yaml
# Apple Silicon specific
platform: linux/arm64
environment:
  - MPS_ENABLE=1
  - PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
deploy:
  resources:
    limits:
      memory: 16G  # Adjust based on model
      cpus: '0.8'  # Use 80% of available CPUs
```

### NVIDIA (RTX/GeForce)
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

### NVIDIA Jetson
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

### AMD
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

## Best Practices

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

## Common Issues and Troubleshooting

### Application Won't Start
- Verify Python version (3.8+ required)
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Ensure Streamlit is properly installed: `streamlit --version`

### Container Issues
- Verify Docker/Podman is running: `docker info` or `podman info`
- Check for permission issues: Run with sudo or add user to docker group
- Verify network connectivity for pulling images
- Check disk space for container storage

### Performance Issues
- Enable debug mode to view system resource usage
- Adjust resource limits in compose files based on your hardware
- Close other resource-intensive applications
- For Apple Silicon, ensure MPS acceleration is enabled

### UI Not Rendering Properly
- Clear browser cache and refresh
- Try a different browser
- Check for JavaScript errors in browser console
- Restart the application: `streamlit run main.py`

## Advanced Usage

### Debug Mode
Enable debug mode by clicking the gear icon in the sidebar and toggling "Debug Mode". This provides:
- Detailed error information
- Session state inspection
- System resource monitoring
- Log viewer

### Custom Configurations
Create a `.env` file in the project root to customize settings:
```
# Example .env file
DATA_DIR=/path/to/custom/data
COMPOSE_PROJECT_NAME=my-singularity
ENABLE_ADVANCED_FEATURES=true
```

### Keyboard Shortcuts
- `Ctrl+H`: Toggle sidebar
- `Ctrl+R`: Refresh page
- `Ctrl+D`: Toggle debug mode
- `Ctrl+/`: Show keyboard shortcuts

## Architecture

Singularity Launcher is built with a modular architecture:

- **Core**: System detection, hardware optimization, and container management
- **UI**: Streamlit-based user interface with responsive design
- **Modules**: Specialized components for different functionalities (Lab Setup, Local AI)
- **Utils**: Helper functions for system operations and performance monitoring

## Project Structure

```
Singularity-Launcher/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── .gitignore              # Git ignore file
├── launch.sh               # Launch script for Linux/macOS
├── lib/                    # Library modules
│   ├── __init__.py
│   ├── system.py           # System detection and information
│   ├── containers.py       # Container management
│   ├── performance.py      # Performance monitoring
│   ├── ui.py               # UI components
│   └── utils/              # Utility functions
│       ├── __init__.py
│       ├── state_management.py    # Session state management
│       ├── ui_components.py       # UI utility components
│       ├── initialization.py      # Application initialization
│       └── performance.py         # Performance utilities
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Created by Captain ASIC
- Inspired by FusionLoom and AI-Garage projects
- Built with Streamlit for a responsive and interactive UI
- Uses Podman for secure, rootless containers
- Integrates Open WebUI for a user-friendly interface to Ollama

## Version History

### v2.5.0 (2025-06-14)
- Enhanced UI with improved responsiveness and visual hierarchy
- Robust initialization sequence with proper error handling
- Improved session state management
- Error boundaries around UI components
- Debugging mode for troubleshooting
- Improved accessibility with ARIA attributes
- Enhanced loading states and indicators
- Comprehensive error messaging with actionable guidance

### v2.0.0 (2024-12-13)
- Apple Silicon M4 support (M4 Base, M4 Pro, M4 Max)
- Enhanced Apple Silicon variant detection (M1-M4)
- M4-specific optimizations with advanced MPS support
- Dynamic resource allocation based on Apple Silicon variant
- Thermal management and power efficiency controls
- Performance profiles: Ultra, High, Optimized, Balanced, Conservative
- M4-optimized compose files for all services
- Comprehensive M4 performance benchmarks
- Enhanced system detection with Apple Silicon optimizations
- Backwards compatibility with M1, M2, and M3 variants

### v1.0.0 (2024-06-01)
- Initial release
- Basic Apple Silicon support
- NVIDIA GPU optimizations
- AMD GPU support
- Multi-platform container deployment
