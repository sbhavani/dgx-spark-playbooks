#!/bin/bash

# CUDA-X Data Science Playbook - Start Script
# This script helps you quickly start the playbook containers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting CUDA-X Data Science Playbook..."
echo ""

# Check if kaggle.json exists
if [ ! -f "kaggle.json" ]; then
    echo "⚠️  Warning: kaggle.json not found!"
    echo "   The cudf_pandas_demo.ipynb notebook requires Kaggle credentials."
    echo "   Create a kaggle.json file with your Kaggle API credentials."
    echo "   See: https://www.kaggle.com/discussions/general/74235"
    echo ""
fi

# Start containers
echo "📦 Building and starting Docker containers..."
docker compose up --build -d

# Wait for Jupyter to start
echo "⏳ Waiting for Jupyter to start..."
sleep 5

# Check if container is running
if docker ps | grep -q cuda-x-data-science; then
    echo ""
    echo "✅ CUDA-X Data Science Playbook is running!"
    echo ""
    echo "📓 Access Jupyter Notebook:"
    echo "   http://localhost:8888"
    echo ""
    echo "📚 Available notebooks:"
    echo "   - cudf_pandas_demo.ipynb     (GPU-accelerated pandas)"
    echo "   - cuml_sklearn_demo.ipynb    (GPU-accelerated ML: UMAP, HDBSCAN, LinearSVC)"
    echo ""
    echo "🛑 To stop the playbook:"
    echo "   docker compose down"
    echo "   or run: ./stop.sh"
    echo ""
else
    echo ""
    echo "❌ Failed to start containers. Check the logs:"
    echo "   docker compose logs"
    exit 1
fi
