# Ollama Apple Silicon Troubleshooting Guide

## 🔧 **Common Issues & Solutions**

### **Installation & Setup Issues**

#### **Issue: Container Won't Start**
```
Error: no such image: docker.io/ollama/ollama:latest
```

**Solution:**
```bash
# Pull the image manually
podman pull ollama/ollama:latest

# Verify image exists
podman images | grep ollama

# Try starting again
podman-compose up -d
```

#### **Issue: Permission Denied Errors**
```
Permission denied: '/root/.ollama'
```

**Solution:**
```bash
# Fix volume permissions
sudo chown -R $(id -u):$(id -g) ~/Singularity/ollama

# Or use user mapping in compose
user: "$(id -u):$(id -g)"
```

#### **Issue: Port Already in Use**
```
Error: bind: address already in use
```

**Solution:**
```bash
# Check what's using port 11434
lsof -i :11434

# Kill the process or change port
# In compose file: "11435:11434"
```

### **Performance Issues**

#### **Issue: Slow Model Loading**
**Symptoms:**
- Models take 30+ seconds to load
- High disk I/O during loading
- System becomes unresponsive

**Diagnosis:**
```bash
# Check available memory
free -h

# Monitor disk I/O
iostat -x 1

# Check Ollama logs
podman logs singularity-ollama-m4-optimized
```

**Solutions:**
```bash
# 1. Increase model cache
export OLLAMA_MODEL_CACHE_SIZE=8G

# 2. Enable memory mapping
export OLLAMA_MMAP=1

# 3. Reduce concurrent requests
export OLLAMA_PARALLEL_REQUESTS=2

# 4. Use faster storage (if possible)
# Move ~/Singularity/ollama to SSD
```

#### **Issue: High Memory Usage**
**Symptoms:**
- System runs out of memory
- Ollama container gets killed
- Swap usage increases dramatically

**Diagnosis:**
```bash
# Check memory usage
docker stats singularity-ollama-m4-optimized

# Check system memory
vm_stat

# Check swap usage
sysctl vm.swapusage
```

**Solutions:**
```bash
# 1. Reduce memory allocation for your M4 variant
# M4 Base (16GB total)
export OLLAMA_MAX_MEMORY=10G

# M4 Pro (24GB total)
export OLLAMA_MAX_MEMORY=18G

# 2. Reduce model cache
export OLLAMA_MODEL_CACHE_SIZE=2G

# 3. Lower context size
export OLLAMA_CONTEXT_SIZE=4096

# 4. Use smaller models
# Instead of 13B, use 7B models
```

#### **Issue: Thermal Throttling**
**Symptoms:**
- Performance degrades over time
- CPU frequency drops
- Fan noise increases significantly

**Diagnosis:**
```bash
# Check CPU temperature (requires additional tools)
sudo powermetrics -n 1 -i 1000 | grep -i temp

# Monitor CPU frequency
sysctl -n machdep.cpu.max_basic
```

**Solutions:**
```bash
# 1. Lower CPU limits
export OLLAMA_CPU_LIMIT=0.70

# 2. Enable power efficient mode
export OLLAMA_POWER_EFFICIENT=1

# 3. Reduce thermal throttle threshold
export OLLAMA_THERMAL_THROTTLE=80

# 4. Improve cooling
# - Clean dust from vents
# - Use laptop cooling pad
# - Ensure proper ventilation
```

### **Apple Silicon Specific Issues**

#### **Issue: Metal GPU Not Working**
**Symptoms:**
- GPU utilization shows 0%
- Performance similar to CPU-only
- No Metal-related logs

**Diagnosis:**
```bash
# Check Metal support
system_profiler SPDisplaysDataType | grep -i metal

# Check Ollama Metal usage
podman logs singularity-ollama-m4-optimized | grep -i metal
```

**Solutions:**
```bash
# 1. Ensure Metal is enabled
export OLLAMA_USE_METAL=1
export OLLAMA_METAL_DEVICE_ID=0

# 2. Verify platform architecture
podman inspect ollama/ollama:latest | grep Architecture
# Should show: "arm64"

# 3. Update to latest Ollama
podman pull ollama/ollama:latest

# 4. Check macOS version
# Metal requires macOS 10.15+
sw_vers
```

#### **Issue: ARM64 vs AMD64 Image**
**Symptoms:**
- Warning about platform mismatch
- Slower performance than expected
- Rosetta translation warnings

**Diagnosis:**
```bash
# Check image architecture
podman inspect ollama/ollama:latest | grep Architecture

# Check running container architecture
podman exec singularity-ollama-m4-optimized uname -m
# Should show: "aarch64"
```

**Solutions:**
```bash
# 1. Force ARM64 platform
podman pull --platform linux/arm64 ollama/ollama:latest

# 2. Verify in compose file
platform: linux/arm64

# 3. Build native image if needed
# See M4 Dockerfile guide
```

### **Network & Connectivity Issues**

#### **Issue: Can't Access Ollama API**
**Symptoms:**
- Connection refused on port 11434
- API calls timeout
- Open-WebUI can't connect

**Diagnosis:**
```bash
# Check if Ollama is running
podman ps | grep ollama

# Check port binding
podman port singularity-ollama-m4-optimized

# Test local connection
curl http://localhost:11434/api/tags
```

**Solutions:**
```bash
# 1. Verify host binding
export OLLAMA_HOST=0.0.0.0

# 2. Check firewall settings
# macOS: System Preferences > Security & Privacy > Firewall

# 3. Verify network configuration
# In compose file:
networks:
  - singularity_net

# 4. Check container logs
podman logs singularity-ollama-m4-optimized
```

#### **Issue: Open-WebUI Connection Problems**
**Symptoms:**
- WebUI shows "Ollama not connected"
- 502 Bad Gateway errors
- Intermittent connectivity

**Diagnosis:**
```bash
# Check WebUI logs
podman logs singularity-open-webui-m4-optimized

# Test Ollama from WebUI container
podman exec singularity-open-webui-m4-optimized \
  curl http://singularity-ollama-m4-optimized:11434/api/tags
```

**Solutions:**
```bash
# 1. Verify service dependency
depends_on:
  ollama:
    condition: service_healthy

# 2. Check internal network
# Both containers must be on same network

# 3. Update base URL
export OLLAMA_BASE_URL=http://singularity-ollama-m4-optimized:11434

# 4. Restart services in order
podman-compose restart ollama
podman-compose restart open-webui
```

### **Model-Specific Issues**

#### **Issue: Model Download Failures**
**Symptoms:**
- Downloads timeout or fail
- Partial model files
- Corruption errors

**Diagnosis:**
```bash
# Check available disk space
df -h ~/Singularity/ollama

# Check download logs
podman logs singularity-ollama-m4-optimized | grep download

# Verify model integrity
ls -la ~/Singularity/ollama/models/
```

**Solutions:**
```bash
# 1. Ensure sufficient disk space
# 7B model: ~4GB
# 13B model: ~7GB
# 30B model: ~15GB

# 2. Retry download
podman exec singularity-ollama-m4-optimized ollama pull llama2

# 3. Manual download with resume
# Use ollama CLI with --resume flag

# 4. Check network stability
# Use wired connection if possible
```

#### **Issue: Model Loading Errors**
**Symptoms:**
- "Model not found" errors
- Loading hangs indefinitely
- Memory allocation failures

**Diagnosis:**
```bash
# List available models
curl http://localhost:11434/api/tags

# Check model files
ls -la ~/Singularity/ollama/models/manifests/

# Check memory usage during loading
top -pid $(pgrep ollama)
```

**Solutions:**
```bash
# 1. Verify model exists
podman exec singularity-ollama-m4-optimized ollama list

# 2. Re-download corrupted models
podman exec singularity-ollama-m4-optimized ollama rm llama2
podman exec singularity-ollama-m4-optimized ollama pull llama2

# 3. Adjust memory settings for model size
# For 13B models on M4 Base:
export OLLAMA_MAX_MEMORY=14G
export OLLAMA_CONTEXT_SIZE=4096
```

### **Advanced Troubleshooting**

#### **Debug Mode**
```bash
# Enable debug logging
export OLLAMA_LOG_LEVEL=DEBUG

# Restart with debug
podman-compose down
podman-compose up -d

# View detailed logs
podman logs -f singularity-ollama-m4-optimized
```

#### **Performance Profiling**
```bash
# Monitor system resources
top -pid $(pgrep ollama)

# Check GPU usage (if available)
sudo powermetrics -n 1 -i 1000 | grep -i gpu

# Profile memory usage
vmmap $(pgrep ollama)

# Network monitoring
netstat -an | grep 11434
```

#### **Container Debugging**
```bash
# Enter container for debugging
podman exec -it singularity-ollama-m4-optimized /bin/bash

# Check container environment
podman exec singularity-ollama-m4-optimized env | grep OLLAMA

# Verify file permissions
podman exec singularity-ollama-m4-optimized ls -la /root/.ollama
```

### **Getting Help**

#### **Log Collection**
```bash
# Collect all relevant logs
mkdir ollama-debug-$(date +%Y%m%d)
cd ollama-debug-$(date +%Y%m%d)

# Container logs
podman logs singularity-ollama-m4-optimized > ollama.log
podman logs singularity-open-webui-m4-optimized > webui.log

# System information
system_profiler SPHardwareDataType > hardware.txt
sw_vers > macos_version.txt
podman version > podman_version.txt

# Configuration
podman inspect singularity-ollama-m4-optimized > ollama_config.json
```

#### **Community Support**
- **GitHub Issues**: Report bugs and feature requests
- **Discord/Forums**: Community troubleshooting
- **Documentation**: Check latest updates

#### **Professional Support**
For production deployments or complex issues:
- **Ollama Enterprise Support**
- **Apple Developer Support** (for Metal/Apple Silicon issues)
- **Container Platform Support** (Podman/Docker)

This troubleshooting guide covers the most common issues you'll encounter with Ollama on Apple Silicon M4 systems!

