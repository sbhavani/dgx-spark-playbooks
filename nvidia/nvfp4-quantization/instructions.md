# Step 1. Configure Docker permissions

To easily manage containers without sudo, you must be in the `docker` group. If you choose to skip this step, you will need to run Docker commands with sudo.

Open a new terminal and test Docker access. In the terminal, run:

```bash
docker ps
```

If you see a permission denied error (something like permission denied while trying to connect to the Docker daemon socket), add your user to the docker group so that you don't need to run the command with sudo .

```bash
sudo usermod -aG docker $USER
newgrp docker
```

# Step 2. Prepare the environment

Create a local output directory where the quantized model files will be stored. This directory will be mounted into the container to persist results after the container exits.

```bash
mkdir -p ./output_models
chmod 755 ./output_models
```

# Step 3. Authenticate with Hugging Face

Ensure you have access to the DeepSeek model by setting your Hugging Face authentication token.

```bash
# Export your Hugging Face token as an environment variable
# Get your token from: https://huggingface.co/settings/tokens
export HF_TOKEN="your_token_here"
```

The token will be automatically used by the container for model downloads.

# Step 4. Run the TensorRT Model Optimizer container

Launch the TensorRT-LLM container with GPU access, IPC settings optimized for multi-GPU workloads, and volume mounts for model caching and output persistence.

```bash
docker run --rm -it --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 \
  -v "./output_models:/workspace/output_models" \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  -e HF_TOKEN=$HF_TOKEN \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c "
    git clone -b 0.35.0 --single-branch https://github.com/NVIDIA/TensorRT-Model-Optimizer.git /app/TensorRT-Model-Optimizer && \
    cd /app/TensorRT-Model-Optimizer && pip install -e '.[dev]' && \
    export ROOT_SAVE_PATH='/workspace/output_models' && \
    /app/TensorRT-Model-Optimizer/examples/llm_ptq/scripts/huggingface_example.sh \
    --model 'deepseek-ai/DeepSeek-R1-Distill-Llama-8B' \
    --quant nvfp4 \
    --tp 1 \
    --export_fmt hf
  "
```

Note: You may encounter this `pynvml.NVMLError_NotSupported: Not Supported`. This is expected in some environments, does not affect results, and will be fixed in an upcoming release.
Note: Please be aware that if your model is too large, you may encounter an out of memory error. You can try quantizing a smaller model instead.

This command:
- Runs the container with full GPU access and optimized shared memory settings
- Mounts your output directory to persist quantized model files
- Mounts your Hugging Face cache to avoid re-downloading the model
- Clones and installs the TensorRT Model Optimizer from source
- Executes the quantization script with NVFP4 quantization parameters

# Step 5. Monitor the quantization process

The quantization process will display progress information including:
- Model download progress from Hugging Face
- Quantization calibration steps
- Model export and validation phases

# Step 6. Validate the quantized model

After the container completes, verify that the quantized model files were created successfully.

```bash
# Check output directory contents
ls -la ./output_models/

# Verify model files are present
find ./output_models/ -name "*.bin" -o -name "*.safetensors" -o -name "config.json"
```

You should see model weight files, configuration files, and tokenizer files in the output directory.

# Step 7. Test model loading

First, set the path to your quantized model:

```bash
# Set path to quantized model directory
export MODEL_PATH="./output_models/saved_models_DeepSeek-R1-Distill-Llama-8B_nvfp4_hf/"
```

Now verify the quantized model can be loaded properly using a simple test:

```bash
docker run \
  -e HF_TOKEN=$HF_TOKEN \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  -v "$MODEL_PATH:/workspace/model" \
  --rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
  --gpus=all --ipc=host --network host \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
    python examples/llm-api/quickstart_advanced.py \
      --model_dir /workspace/model/ \
      --prompt "Paris is great because" \
      --max_tokens 64
    '
```

# Step 8. Serve the model with OpenAI-compatible API
Start the TensorRT-LLM OpenAI-compatible API server with the quantized model.
First, set the path to your quantized model:

```bash
# Set path to quantized model directory
export MODEL_PATH="./output_models/saved_models_DeepSeek-R1-Distill-Llama-8B_nvfp4_hf/"

docker run \
  -e HF_TOKEN=$HF_TOKEN \
  -v "$MODEL_PATH:/workspace/model" \
  --rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
  --gpus=all --ipc=host --network host \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  trtllm-serve /workspace/model \
    --backend pytorch \
    --max_batch_size 4 \
    --port 8000
```

Run the following to test the server with a client CURL request:

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
    "prompt": "What is artificial intelligence?",
    "max_tokens": 100,
    "temperature": 0.7,
    "stream": false
  }'
```

# Step 10. Cleanup and rollback

To clean up the environment and remove generated files:

> [!WARNING]
> This will permanently delete all quantized model files and cached data.

```bash
# Remove output directory and all quantized models
rm -rf ./output_models

# Remove Hugging Face cache (optional)
rm -rf ~/.cache/huggingface

# Remove Docker image (optional)
docker rmi nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev
```

# Step 11. Next steps

The quantized model is now ready for deployment. Common next steps include:
- Benchmarking inference performance compared to the original model.
- Integrating the quantized model into your inference pipeline.
- Deploying to NVIDIA Triton Inference Server for production serving.
- Running additional validation tests on your specific use cases.
