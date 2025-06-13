# Advanced Ollama Configuration for Apple Silicon M4

## 🔬 **Advanced Configuration Options**

### **Environment Variable Reference**

#### **Core Ollama Settings**
```bash
# Basic Configuration
OLLAMA_HOST=0.0.0.0                    # Bind address (default: 127.0.0.1)
OLLAMA_ORIGINS=*                       # CORS origins (default: localhost)
OLLAMA_PORT=11434                      # Service port (default: 11434)

# Model Management
OLLAMA_MODELS=/path/to/models          # Model storage path
OLLAMA_KEEP_ALIVE=5m                   # Model memory retention
OLLAMA_MAX_LOADED_MODELS=3             # Concurrent loaded models
OLLAMA_PRELOAD_MODELS=llama2,codellama # Auto-load models on startup
```

#### **Apple Silicon M4 Optimizations**
```bash
# Metal GPU Configuration
OLLAMA_USE_METAL=1                     # Enable Metal acceleration
OLLAMA_METAL_DEVICE_ID=0               # GPU device selection
OLLAMA_CPU_ONLY=0                      # Force CPU-only mode (disable for M4)

# Performance Tuning
OLLAMA_NUM_THREADS=16                  # CPU threads (M4 Max: 16, Pro: 14, Base: 8)
OLLAMA_MAX_MEMORY=28G                  # Memory limit (adjust per M4 variant)
OLLAMA_CONTEXT_SIZE=16384              # Context window size
OLLAMA_FLASH_ATTENTION=1               # Enable Flash Attention optimization

# Concurrency & Batching
OLLAMA_PARALLEL_REQUESTS=6             # Concurrent request limit
OLLAMA_MAX_QUEUE=512                   # Request queue size
OLLAMA_THREADS_BATCH=12                # Batch processing threads

# Memory Management
OLLAMA_MMAP=1                          # Memory mapping (recommended)
OLLAMA_NUMA=0                          # NUMA optimization (disable for Apple Silicon)
OLLAMA_MODEL_CACHE_SIZE=8G             # Model cache size

# Thermal & Power Management
OLLAMA_THERMAL_THROTTLE=85             # Thermal throttling threshold (°C)
OLLAMA_POWER_EFFICIENT=0               # Power efficiency mode (0=performance, 1=efficient)

# Monitoring & Logging
OLLAMA_METRICS=1                       # Enable metrics collection
OLLAMA_LOG_LEVEL=INFO                  # Logging level (DEBUG, INFO, WARN, ERROR)
```

### **Advanced Model Configuration**

#### **Model-Specific Parameters**
```bash
# Large Language Models (7B-13B)
OLLAMA_LLM_BATCH_SIZE=512              # Batch size for LLM inference
OLLAMA_LLM_CONTEXT_LENGTH=8192         # Default context length
OLLAMA_LLM_ROPE_FREQ_BASE=10000        # RoPE frequency base
OLLAMA_LLM_ROPE_FREQ_SCALE=1.0         # RoPE frequency scaling

# Code Models
OLLAMA_CODE_COMPLETION_TEMP=0.1        # Temperature for code completion
OLLAMA_CODE_MAX_TOKENS=2048            # Max tokens for code generation

# Chat Models
OLLAMA_CHAT_TEMPLATE="auto"            # Chat template format
OLLAMA_CHAT_SYSTEM_PROMPT=""           # Default system prompt
```

#### **Quantization Settings**
```bash
# Model Quantization (Apple Silicon optimized)
OLLAMA_QUANTIZATION=q4_0               # Quantization level (q4_0, q4_1, q5_0, q5_1, q8_0)
OLLAMA_QUANTIZATION_CACHE=1            # Cache quantized models
OLLAMA_QUANTIZATION_THREADS=8          # Threads for quantization

# Memory-Optimized Quantization for M4 Base
OLLAMA_Q4_OPTIMIZED=1                  # Enable Q4 optimizations
OLLAMA_LOW_VRAM_MODE=1                 # Low memory mode (M4 Base with 16GB)
```

### **Network & Security Configuration**

#### **Advanced Network Settings**
```bash
# Network Configuration
OLLAMA_BIND_ADDRESS=0.0.0.0:11434      # Full bind specification
OLLAMA_PROXY_HEADERS=1                 # Trust proxy headers
OLLAMA_MAX_CONNECTIONS=100             # Maximum concurrent connections
OLLAMA_CONNECTION_TIMEOUT=30s          # Connection timeout
OLLAMA_READ_TIMEOUT=60s                # Read timeout
OLLAMA_WRITE_TIMEOUT=60s               # Write timeout

# TLS/SSL Configuration
OLLAMA_TLS_CERT=/path/to/cert.pem      # TLS certificate
OLLAMA_TLS_KEY=/path/to/key.pem        # TLS private key
OLLAMA_TLS_CLIENT_CA=/path/to/ca.pem   # Client CA certificate
```

#### **Security Hardening**
```bash
# Authentication & Authorization
OLLAMA_API_KEY=your-secret-key         # API key authentication
OLLAMA_ALLOWED_IPS=192.168.1.0/24      # IP whitelist
OLLAMA_RATE_LIMIT=100                  # Requests per minute per IP
OLLAMA_MAX_REQUEST_SIZE=10MB           # Maximum request size

# Security Headers
OLLAMA_CORS_ORIGINS=https://yourdomain.com
OLLAMA_SECURITY_HEADERS=1              # Enable security headers
OLLAMA_DISABLE_TELEMETRY=1             # Disable telemetry
```

### **Storage & Caching Configuration**

#### **Advanced Storage Settings**
```bash
# Storage Configuration
OLLAMA_STORAGE_BACKEND=filesystem      # Storage backend (filesystem, s3)
OLLAMA_STORAGE_PATH=/data/ollama       # Storage root path
OLLAMA_TEMP_DIR=/tmp/ollama            # Temporary files directory

# Model Storage Optimization
OLLAMA_MODEL_COMPRESSION=1             # Compress stored models
OLLAMA_MODEL_DEDUPLICATION=1           # Deduplicate model layers
OLLAMA_STORAGE_CACHE_SIZE=20G          # Storage cache size

# Backup & Sync
OLLAMA_AUTO_BACKUP=1                   # Enable automatic backups
OLLAMA_BACKUP_INTERVAL=24h             # Backup interval
OLLAMA_SYNC_MODELS=1                   # Sync models across instances
```

#### **Cache Optimization**
```bash
# Multi-Level Caching
OLLAMA_L1_CACHE_SIZE=2G                # L1 cache (fastest access)
OLLAMA_L2_CACHE_SIZE=8G                # L2 cache (model layers)
OLLAMA_L3_CACHE_SIZE=20G               # L3 cache (full models)

# Cache Policies
OLLAMA_CACHE_POLICY=lru                # Cache eviction policy (lru, lfu, fifo)
OLLAMA_CACHE_TTL=1h                    # Cache time-to-live
OLLAMA_PRELOAD_CACHE=1                 # Preload frequently used models
```

### **Monitoring & Observability**

#### **Metrics Configuration**
```bash
# Prometheus Metrics
OLLAMA_METRICS_ENABLED=1               # Enable metrics endpoint
OLLAMA_METRICS_PORT=9090               # Metrics port
OLLAMA_METRICS_PATH=/metrics           # Metrics endpoint path

# Custom Metrics
OLLAMA_TRACK_USAGE=1                   # Track model usage statistics
OLLAMA_TRACK_PERFORMANCE=1             # Track performance metrics
OLLAMA_TRACK_ERRORS=1                  # Track error rates
```

#### **Logging Configuration**
```bash
# Advanced Logging
OLLAMA_LOG_FORMAT=json                 # Log format (text, json)
OLLAMA_LOG_OUTPUT=/var/log/ollama.log  # Log output file
OLLAMA_LOG_ROTATION=daily              # Log rotation (daily, weekly, size)
OLLAMA_LOG_MAX_SIZE=100MB              # Maximum log file size
OLLAMA_LOG_MAX_FILES=10                # Maximum log files to keep

# Structured Logging
OLLAMA_LOG_INCLUDE_CALLER=1            # Include caller information
OLLAMA_LOG_INCLUDE_TIMESTAMP=1         # Include timestamps
OLLAMA_LOG_INCLUDE_LEVEL=1             # Include log levels
```

### **Development & Testing**

#### **Development Mode**
```bash
# Development Configuration
OLLAMA_DEV_MODE=1                      # Enable development mode
OLLAMA_DEBUG_MEMORY=1                  # Debug memory usage
OLLAMA_DEBUG_PERFORMANCE=1             # Debug performance metrics
OLLAMA_PROFILE_CPU=1                   # Enable CPU profiling
OLLAMA_PROFILE_MEMORY=1                # Enable memory profiling

# Testing Configuration
OLLAMA_TEST_MODE=1                     # Enable test mode
OLLAMA_MOCK_MODELS=1                   # Use mock models for testing
OLLAMA_BENCHMARK_MODE=1                # Enable benchmarking
```

#### **API Testing**
```bash
# Load Testing
OLLAMA_LOAD_TEST_CONCURRENT=10         # Concurrent test requests
OLLAMA_LOAD_TEST_DURATION=60s          # Test duration
OLLAMA_LOAD_TEST_MODEL=llama2          # Test model

# Performance Testing
OLLAMA_PERF_TEST_ENABLED=1             # Enable performance tests
OLLAMA_PERF_TEST_INTERVAL=5m           # Test interval
OLLAMA_PERF_TEST_METRICS=latency,throughput
```

### **Container-Specific Configuration**

#### **Docker/Podman Optimizations**
```yaml
# Resource Limits (compose.yaml)
deploy:
  resources:
    limits:
      cpus: '0.90'                     # CPU limit (90% for M4 Max)
      memory: 28G                      # Memory limit
      pids: 1000                       # Process limit
    reservations:
      cpus: '0.50'                     # CPU reservation
      memory: 8G                       # Memory reservation

# Health Checks
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
  interval: 30s                        # Check interval
  timeout: 10s                         # Check timeout
  retries: 3                           # Retry count
  start_period: 60s                    # Initial delay
```

#### **Volume Optimization**
```yaml
# Optimized Volume Mounts
volumes:
  - type: bind
    source: ${SINGULARITY_DRIVE}/ollama
    target: /root/.ollama
    bind:
      propagation: rprivate
  - type: bind
    source: ${SINGULARITY_DRIVE}/ollama/models
    target: /root/.ollama/models
    bind:
      propagation: rprivate
  - type: tmpfs
    target: /tmp
    tmpfs:
      size: 2G                         # Temporary storage
      mode: 1777
```

### **Production Deployment**

#### **High Availability Configuration**
```bash
# Clustering
OLLAMA_CLUSTER_ENABLED=1               # Enable clustering
OLLAMA_CLUSTER_NODES=node1,node2,node3 # Cluster nodes
OLLAMA_CLUSTER_ROLE=primary            # Node role (primary, secondary)

# Load Balancing
OLLAMA_LB_STRATEGY=round_robin         # Load balancing strategy
OLLAMA_LB_HEALTH_CHECK=1               # Enable health checks
OLLAMA_LB_FAILOVER=1                   # Enable automatic failover
```

#### **Scaling Configuration**
```bash
# Auto-scaling
OLLAMA_AUTO_SCALE=1                    # Enable auto-scaling
OLLAMA_SCALE_MIN_INSTANCES=2           # Minimum instances
OLLAMA_SCALE_MAX_INSTANCES=10          # Maximum instances
OLLAMA_SCALE_TARGET_CPU=70             # CPU threshold for scaling
OLLAMA_SCALE_TARGET_MEMORY=80          # Memory threshold for scaling
```

This advanced configuration guide provides fine-grained control over Ollama's behavior on Apple Silicon M4 systems!

