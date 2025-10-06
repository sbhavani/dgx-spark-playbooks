# Ollama GPU Memory Monitoring

This setup includes automatic monitoring and fixing of GPU memory detection issues that can occur on unified memory systems (like DGX Spark, Jetson, etc.).

## The Problem

On unified memory systems, Ollama sometimes can't detect the full amount of available GPU memory due to buffer cache not being reclaimable. This causes models to fall back to CPU inference, dramatically reducing performance.

**Symptoms:**
- Ollama logs show low "available" vs "total" GPU memory
- Models show mixed CPU/GPU processing instead of 100% GPU
- Performance is much slower than expected

## The Solution

This Docker Compose setup includes an optional GPU memory monitor that:

1. **Monitors** Ollama's GPU memory detection every 60 seconds
2. **Detects** when available memory drops below 70% of total
3. **Automatically fixes** the issue by clearing buffer cache and restarting Ollama
4. **Logs** all actions for debugging

## Usage

### Standard Setup (Most Systems)
```bash
docker compose up -d
```

### Unified Memory Systems (DGX Spark, Jetson, etc.)
```bash
docker compose --profile unified-memory up -d
```

This will start both Ollama and the GPU memory monitor.

## Configuration

The monitor can be configured via environment variables:

- `CHECK_INTERVAL=60` - How often to check (seconds)
- `MIN_AVAILABLE_PERCENT=70` - Threshold for triggering fixes (percentage)
- `AUTO_FIX=true` - Whether to automatically fix issues

## Manual Commands

You can still use the manual scripts if needed:

```bash
# Check current GPU memory status
./monitor_gpu_memory.sh

# Manually clear cache and restart
./clear_cache_and_restart.sh
```

## Monitoring Logs

To see what the monitor is doing:

```bash
docker logs ollama-gpu-monitor -f
```

## When to Use

Use the unified memory profile if you experience:
- Inconsistent Ollama performance
- Models loading on CPU instead of GPU
- GPU memory showing as much lower than system RAM
- You're on a system with unified memory (DGX, Jetson, etc.)

## Performance Impact

The monitor has minimal performance impact:
- Runs one check every 60 seconds
- Only takes action when issues are detected
- Automatic fixes typically resolve issues within 30 seconds
