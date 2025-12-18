#!/bin/bash
#
# SPDX-FileCopyrightText: Copyright (c) 1993-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Setup script for txt2kg project

# Parse command line arguments
DEV_FRONTEND=false
USE_COMPLETE=false
USE_VECTOR_SEARCH=false
USE_VLLM=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --dev-frontend)
      DEV_FRONTEND=true
      shift
      ;;
    --complete)
      USE_COMPLETE=true
      shift
      ;;
    --vector-search)
      USE_VECTOR_SEARCH=true
      shift
      ;;
    --vllm)
      USE_VLLM=true
      shift
      ;;
    --help|-h)
      echo "Usage: ./start.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --dev-frontend    Run frontend in development mode (without Docker)"
      echo "  --vllm            Use vLLM instead of Ollama (recommended for DGX Spark/GB300)"
      echo "  --complete        Use complete stack (vLLM, Pinecone, Sentence Transformers)"
      echo "  --vector-search   Enable vector search services in minimal stack (Qdrant + Sentence Transformers)"
      echo "  --help, -h        Show this help message"
      echo ""
      echo "Default: Starts minimal stack (Neo4j + Ollama + Next.js frontend)"
      echo ""
      echo "Examples:"
      echo "  ./start.sh                # Start minimal demo with Ollama"
      echo "  ./start.sh --vllm         # Start with vLLM for GPU acceleration (DGX Spark)"
      echo "  ./start.sh --vector-search # Start minimal demo + vector search services"
      echo "  ./start.sh --complete     # Start with all optional services"
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

# Check Docker daemon permissions
echo "Checking Docker permissions..."
if ! docker info &> /dev/null; then
  echo ""
  echo "=========================================="
  echo "ERROR: Docker Permission Denied"
  echo "=========================================="
  echo ""
  echo "You don't have permission to connect to the Docker daemon."
  echo ""
  echo "To fix this, run one of the following:"
  echo ""
  echo "Option 1 (Recommended): Add your user to the docker group"
  echo "  sudo usermod -aG docker \$USER"
  echo "  newgrp docker"
  echo ""
  echo "Option 2: Run this script with sudo (not recommended)"
  echo "  sudo ./start.sh"
  echo ""
  echo "After adding yourself to the docker group, you may need to log out"
  echo "and log back in for the changes to take effect."
  echo ""
  exit 1
fi
echo "✓ Docker permissions OK"

# Build the docker-compose command
if [ "$USE_COMPLETE" = true ]; then
  CMD="$DOCKER_COMPOSE_CMD -f $(pwd)/deploy/compose/docker-compose.complete.yml"
  echo "Using complete stack (Ollama, vLLM, Pinecone, Sentence Transformers)..."
elif [ "$USE_VLLM" = true ]; then
  if [ "$USE_VECTOR_SEARCH" = true ]; then
    CMD="$DOCKER_COMPOSE_CMD -f $(pwd)/deploy/compose/docker-compose.neo4j-vllm.yml --profile vector-search"
    echo "Using vLLM configuration + vector search (Neo4j + vLLM + Qdrant + Sentence Transformers)..."
  else
    CMD="$DOCKER_COMPOSE_CMD -f $(pwd)/deploy/compose/docker-compose.neo4j-vllm.yml"
    echo "Using vLLM configuration (Neo4j + vLLM + Next.js frontend)..."
    echo "  ⚡ GPU-accelerated inference with unified memory support for DGX Spark/GB300"
  fi
else
  if [ "$USE_VECTOR_SEARCH" = true ]; then
    CMD="$DOCKER_COMPOSE_CMD -f $(pwd)/deploy/compose/docker-compose.yml --profile vector-search"
    echo "Using minimal configuration + vector search (Neo4j + Ollama + Qdrant + Sentence Transformers)..."
  else
    CMD="$DOCKER_COMPOSE_CMD -f $(pwd)/deploy/compose/docker-compose.yml"
    echo "Using minimal configuration (Neo4j + Ollama + Next.js frontend)..."
  fi
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
echo "Core Services:"
echo "  • Web UI: http://localhost:3001"
echo "  • Neo4j Browser: http://localhost:7474"
if [ "$USE_VLLM" = true ] || [ "$USE_COMPLETE" = true ]; then
  echo "  • vLLM API: http://localhost:8001 (GPU-accelerated)"
else
  echo "  • Ollama API: http://localhost:11434"
fi
echo ""

if [ "$USE_COMPLETE" = true ]; then
  echo "Additional Services (Complete Stack):"
  echo "  • Local Pinecone: http://localhost:5081"
  echo "  • Sentence Transformers: http://localhost:8000"
  echo "  • Ollama API: http://localhost:11434"
  echo ""
elif [ "$USE_VLLM" = true ] && [ "$USE_VECTOR_SEARCH" = true ]; then
  echo "Additional Services (Vector Search Profile):"
  echo "  • Qdrant: http://localhost:6333"
  echo "  • Sentence Transformers: http://localhost:8000"
  echo ""
elif [ "$USE_VECTOR_SEARCH" = true ]; then
  echo "Additional Services (Vector Search Profile):"
  echo "  • Qdrant: http://localhost:6333"
  echo "  • Sentence Transformers: http://localhost:8000"
  echo ""
fi

echo "Next steps:"
if [ "$USE_VLLM" = true ] || [ "$USE_COMPLETE" = true ]; then
  echo "  1. Wait for vLLM to load the model (check logs with: docker logs vllm-service -f)"
  echo "     Note: First startup may take several minutes to download the model"
  echo ""
  echo "  2. Open http://localhost:3001 in your browser"
else
  echo "  1. Pull an Ollama model (if not already done):"
  echo "     docker exec ollama-compose ollama pull llama3.1:8b"
  echo ""
  echo "  2. Open http://localhost:3001 in your browser"
fi
echo "  3. Upload documents and start building your knowledge graph!"
echo ""
echo "Other options:"
echo "  • Stop services: ./stop.sh"
echo "  • Run frontend in dev mode: ./start.sh --dev-frontend"
echo "  • Use vLLM (GPU): ./start.sh --vllm (recommended for DGX Spark)"
echo "  • Use complete stack: ./start.sh --complete"
echo "  • View logs: docker compose logs -f"
echo "" 
