#!/bin/bash
#
# Monitor Ollama GPU memory usage and alert when buffer cache is consuming too much
# This helps detect when the unified memory issue is occurring
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Thresholds
MIN_AVAILABLE_PERCENT=70  # Alert if less than 70% GPU memory available

echo "🔍 Ollama GPU Memory Monitor"
echo "================================"

# Check if Ollama container is running
if ! docker ps | grep -q ollama-server; then
    echo -e "${RED}❌ Ollama container is not running${NC}"
    exit 1
fi

# Get the latest inference compute log
COMPUTE_LOG=$(docker logs ollama-server 2>&1 | grep "inference compute" | tail -1)

if [ -z "$COMPUTE_LOG" ]; then
    echo -e "${YELLOW}⚠️  No inference compute logs found. Model may not be loaded.${NC}"
    exit 1
fi

echo "Latest GPU memory status:"
echo "$COMPUTE_LOG"

# Extract total and available memory
TOTAL_MEM=$(echo "$COMPUTE_LOG" | grep -o 'total="[^"]*"' | cut -d'"' -f2)
AVAILABLE_MEM=$(echo "$COMPUTE_LOG" | grep -o 'available="[^"]*"' | cut -d'"' -f2)

# Convert to numeric values (assuming GiB)
TOTAL_NUM=$(echo "$TOTAL_MEM" | sed 's/ GiB//')
AVAILABLE_NUM=$(echo "$AVAILABLE_MEM" | sed 's/ GiB//')

# Calculate percentage
AVAILABLE_PERCENT=$(echo "scale=1; $AVAILABLE_NUM * 100 / $TOTAL_NUM" | bc)

echo ""
echo "Memory Analysis:"
echo "  Total GPU Memory: $TOTAL_MEM"
echo "  Available Memory: $AVAILABLE_MEM"
echo "  Available Percentage: ${AVAILABLE_PERCENT}%"

# Check if we need to alert
if (( $(echo "$AVAILABLE_PERCENT < $MIN_AVAILABLE_PERCENT" | bc -l) )); then
    echo ""
    echo -e "${RED}🚨 WARNING: Low GPU memory availability detected!${NC}"
    echo -e "${RED}   Only ${AVAILABLE_PERCENT}% of GPU memory is available${NC}"
    echo -e "${YELLOW}   This may cause models to run on CPU instead of GPU${NC}"
    echo ""
    echo "💡 Recommended action:"
    echo "   Run: ./clear_cache_and_restart.sh"
    echo ""
    
    # Show current system memory usage
    echo "Current system memory usage:"
    free -h
    
    exit 1
else
    echo ""
    echo -e "${GREEN}✅ GPU memory availability looks good (${AVAILABLE_PERCENT}%)${NC}"
fi

# Show current model status
echo ""
echo "Current loaded models:"
docker exec ollama-server ollama ps
