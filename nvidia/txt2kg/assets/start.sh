#!/bin/bash

# Setup script for txt2kg project

# Parse command line arguments
DEV_FRONTEND=false
USE_VLLM=false
USE_COMPLETE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --dev-frontend)
      DEV_FRONTEND=true
      shift
      ;;
    --vllm)
      USE_VLLM=true
      shift
      ;;
    --complete)
      USE_COMPLETE=true
      shift
      ;;
    --help|-h)
      echo "Usage: ./start.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --dev-frontend   Run frontend in development mode (without Docker)"
      echo "  --vllm           Use vLLM instead of Ollama for LLM inference"
      echo "  --complete       Use complete stack with MinIO S3 storage"
      echo "  --help, -h       Show this help message"
      echo ""
      echo "Default: Starts with Ollama, ArangoDB, local Pinecone, and Next.js frontend"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Run './start.sh --help' for usage information"
      exit 1
      ;;
  esac
done

if [ "$DEV_FRONTEND" = true ]; then
  echo "Starting frontend in development mode..."
  cd frontend
  if ! command -v pnpm &> /dev/null; then
    echo "Error: pnpm is not installed. Install it with: npm install -g pnpm"
    exit 1
  fi
  pnpm run dev
  exit 0
fi

# Check for GPU support
echo "Checking for GPU support..."
if command -v nvidia-smi &> /dev/null; then
  if nvidia-smi &> /dev/null; then
    echo "✓ NVIDIA GPU detected"
    GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -n1)
    echo "  GPU: $GPU_INFO"
  else
    echo "⚠ NVIDIA GPU not accessible. Services will run in CPU mode (slower)."
  fi
else
  echo "⚠ nvidia-smi not found. Services will run in CPU mode (slower)."
fi

# Check which Docker Compose version is available
DOCKER_COMPOSE_CMD=""
if docker compose version &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker compose"
  echo "Using Docker Compose V2"
elif command -v docker-compose &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker-compose"
  echo "Using Docker Compose V1 (deprecated - consider upgrading)"
else
  echo "Error: Neither 'docker compose' nor 'docker-compose' is available"
  echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
  exit 1
fi

# Build the docker-compose command
if [ "$USE_VLLM" = true ]; then
  CMD="$DOCKER_COMPOSE_CMD -f $(pwd)/deploy/compose/docker-compose.vllm.yml"
  echo "Using vLLM for GPU-accelerated LLM inference with FP8 quantization..."
elif [ "$USE_COMPLETE" = true ]; then
  CMD="$DOCKER_COMPOSE_CMD -f $(pwd)/deploy/compose/docker-compose.complete.yml"
  echo "Using complete stack with MinIO S3 storage..."
else
  CMD="$DOCKER_COMPOSE_CMD -f $(pwd)/deploy/compose/docker-compose.yml"
  echo "Using default configuration (Ollama + ArangoDB + local Pinecone)..."
fi

# Execute the command
echo ""
echo "Starting services..."
echo "Running: $CMD up -d"
cd $(dirname "$0")
eval "$CMD up -d"

echo ""
echo "=========================================="
echo "txt2kg is now running!"
echo "=========================================="
echo ""
echo "Services:"
echo "  • Web UI: http://localhost:3001"
echo "  • ArangoDB: http://localhost:8529"
echo "  • Ollama API: http://localhost:11434"
echo "  • Local Pinecone: http://localhost:5081"
echo ""

if [ "$USE_VLLM" = true ]; then
  echo "  • vLLM API: http://localhost:8001"
  echo ""
fi

echo "Next steps:"
echo "  1. Pull an Ollama model (if not already done):"
echo "     docker exec ollama-compose ollama pull llama3.1:8b"
echo ""
echo "  2. Open http://localhost:3001 in your browser"
echo "  3. Upload documents and start building your knowledge graph!"
echo ""
echo "Other options:"
echo "  • Run frontend in dev mode: ./start.sh --dev-frontend"
echo "  • Use vLLM instead of Ollama: ./start.sh --vllm"
echo "  • View logs: docker compose logs -f"
echo "" 
