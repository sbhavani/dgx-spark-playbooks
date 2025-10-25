#!/bin/bash

# CUDA-X Data Science Playbook - Stop Script
# This script stops and removes the playbook containers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛑 Stopping CUDA-X Data Science Playbook..."

docker compose down

echo ""
echo "✅ Playbook containers stopped and removed."
echo ""
echo "🚀 To start again, run: ./start.sh"
echo ""
