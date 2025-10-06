#!/bin/bash
set -e

# Start Ollama server in the background
echo "Starting Ollama server..."
/bin/ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "Ollama is ready!"
        break
    fi
    attempt=$((attempt + 1))
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "ERROR: Ollama failed to start within the timeout period"
    exit 1
fi

# Check if any models are present
echo "Checking for existing models..."
MODELS=$(curl -s http://localhost:11434/api/tags | grep -o '"models":\s*\[\]' || echo "has_models")

if [[ "$MODELS" == *'"models": []'* ]]; then
    echo "No models found. Pulling llama3.1:8b..."
    /bin/ollama pull llama3.1:8b
    echo "Successfully pulled llama3.1:8b"
else
    echo "Models already exist, skipping pull."
fi

# Keep the container running
echo "Setup complete. Ollama is running."
wait $OLLAMA_PID

