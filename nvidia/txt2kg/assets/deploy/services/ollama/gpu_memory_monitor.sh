#!/bin/bash
#
# Ollama GPU Memory Monitor - runs inside a sidecar container
# Automatically detects and fixes unified memory buffer cache issues
#

set -e

# Configuration
CHECK_INTERVAL=${CHECK_INTERVAL:-60}  # Check every 60 seconds
MIN_AVAILABLE_PERCENT=${MIN_AVAILABLE_PERCENT:-70}  # Alert if less than 70% available
AUTO_FIX=${AUTO_FIX:-true}  # Automatically fix issues

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

check_ollama_memory() {
    # Wait for Ollama to be ready
    if ! curl -s http://ollama:11434/api/tags > /dev/null 2>&1; then
        log "Ollama not ready, skipping check"
        return 0
    fi

    # Get Ollama logs to find inference compute info
    local compute_log=$(docker logs ollama-server 2>&1 | grep "inference compute" | tail -1)
    
    if [ -z "$compute_log" ]; then
        log "No inference compute logs found"
        return 0
    fi

    # Extract memory info
    local total_mem=$(echo "$compute_log" | grep -o 'total="[^"]*"' | cut -d'"' -f2)
    local available_mem=$(echo "$compute_log" | grep -o 'available="[^"]*"' | cut -d'"' -f2)
    
    if [ -z "$total_mem" ] || [ -z "$available_mem" ]; then
        log "Could not parse memory information"
        return 0
    fi

    # Convert to numeric (assuming GiB)
    local total_num=$(echo "$total_mem" | sed 's/ GiB//')
    local available_num=$(echo "$available_mem" | sed 's/ GiB//')
    
    # Calculate percentage
    local available_percent=$(echo "scale=1; $available_num * 100 / $total_num" | bc)
    
    log "GPU Memory: $available_mem / $total_mem available (${available_percent}%)"
    
    # Check if we need to take action
    if (( $(echo "$available_percent < $MIN_AVAILABLE_PERCENT" | bc -l) )); then
        log "WARNING: Low GPU memory availability detected (${available_percent}%)"
        
        if [ "$AUTO_FIX" = "true" ]; then
            log "Attempting to fix by clearing buffer cache..."
            fix_memory_issue
        else
            log "Auto-fix disabled. Manual intervention required."
        fi
        
        return 1
    else
        log "GPU memory availability OK (${available_percent}%)"
        return 0
    fi
}

fix_memory_issue() {
    log "Clearing system buffer cache..."
    
    # Clear buffer cache from host (requires privileged container)
    echo 1 > /proc/sys/vm/drop_caches 2>/dev/null || {
        log "Cannot clear buffer cache from container. Trying host command..."
        # Alternative: use nsenter to run on host
        nsenter -t 1 -m -p sh -c 'sync && echo 1 > /proc/sys/vm/drop_caches' 2>/dev/null || {
            log "Failed to clear buffer cache. Manual intervention required."
            return 1
        }
    }
    
    # Wait a moment
    sleep 5
    
    # Restart Ollama container
    log "Restarting Ollama container..."
    docker restart ollama-server
    
    # Wait for restart
    sleep 15
    
    log "Fix applied. Ollama should have better memory detection now."
}

main() {
    log "Starting Ollama GPU Memory Monitor"
    log "Check interval: ${CHECK_INTERVAL}s, Min available: ${MIN_AVAILABLE_PERCENT}%, Auto-fix: ${AUTO_FIX}"
    
    while true; do
        check_ollama_memory || true  # Don't exit on check failures
        sleep "$CHECK_INTERVAL"
    done
}

# Handle signals gracefully
trap 'log "Shutting down monitor..."; exit 0' SIGTERM SIGINT

main
