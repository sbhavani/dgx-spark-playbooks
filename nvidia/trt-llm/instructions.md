## Step 1. Configure Docker permissions

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

## Step 2. Verify environment prerequisites

Confirm your Spark device has the required GPU access and network connectivity for downloading
models and containers.

```bash
# Check GPU visibility and driver
nvidia-smi

# Verify Docker GPU support
docker run --rm --gpus all nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev nvidia-smi

```

## Step 3. Set environment variables

Set `HF_TOKEN` for model access.

```bash
export HF_TOKEN=<your-huggingface-token>
```

## Step 4. Validate TensorRT-LLM installation

After confirming GPU access, verify that TensorRT-LLM can be imported inside the container.

```bash
docker run --rm -it --gpus all \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  python -c "import tensorrt_llm; print(f'TensorRT-LLM version: {tensorrt_llm.__version__}')"
```

Expected output:
```
[TensorRT-LLM] TensorRT-LLM version: 1.1.0rc3
TensorRT-LLM version: 1.1.0rc3
```

## Step 5. Create cache directory

Set up local caching to avoid re-downloading models on subsequent runs.

```bash
# Create Hugging Face cache directory
mkdir -p $HOME/.cache/huggingface/
```

## Step 6. Validate setup with quickstart_advanced

This quickstart validates your TensorRT-LLM setup end-to-end by testing model loading, inference engine initialization, and GPU execution with real text generation. It's the fastest way to confirm everything works before starting the inference API server.

**LLM quickstart example**

### Llama 3.1 8B Instruct
```bash
export MODEL_HANDLE="nvidia/Llama-3.1-8B-Instruct-FP4"

docker run \
  -e MODEL_HANDLE=$MODEL_HANDLE \
  -e HF_TOKEN=$HF_TOKEN \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  --rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
  --gpus=all --ipc=host --network host \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
    hf download $MODEL_HANDLE && \
    python examples/llm-api/quickstart_advanced.py \
      --model_dir $MODEL_HANDLE \
      --prompt "Paris is great because" \
      --max_tokens 64
    '
```

### GPT-OSS 20B
```bash
export MODEL_HANDLE="openai/gpt-oss-20b"

docker run \
  -e MODEL_HANDLE=$MODEL_HANDLE \
  -e HF_TOKEN=$HF_TOKEN \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  --rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
  --gpus=all --ipc=host --network host \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
    export TIKTOKEN_ENCODINGS_BASE="/tmp/harmony-reqs" && \
    mkdir -p $TIKTOKEN_ENCODINGS_BASE && \
    wget -P $TIKTOKEN_ENCODINGS_BASE https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken && \
    wget -P $TIKTOKEN_ENCODINGS_BASE https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken && \
    hf download $MODEL_HANDLE && \
    python examples/llm-api/quickstart_advanced.py \
      --model_dir $MODEL_HANDLE \
      --prompt "Paris is great because" \
      --max_tokens 64
    '
```

### GPT-OSS 120B
```bash
export MODEL_HANDLE="openai/gpt-oss-120b"

docker run \
  -e MODEL_HANDLE=$MODEL_HANDLE \
  -e HF_TOKEN=$HF_TOKEN \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  --rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
  --gpus=all --ipc=host --network host \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
    export TIKTOKEN_ENCODINGS_BASE="/tmp/harmony-reqs" && \
    mkdir -p $TIKTOKEN_ENCODINGS_BASE && \
    wget -P $TIKTOKEN_ENCODINGS_BASE https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken && \
    wget -P $TIKTOKEN_ENCODINGS_BASE https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken && \
    hf download $MODEL_HANDLE && \
    python examples/llm-api/quickstart_advanced.py \
      --model_dir $MODEL_HANDLE \
      --prompt "Paris is great because" \
      --max_tokens 64
    '
```
## Step 7. Validate setup with quickstart_multimodal

**VLM quickstart example**

This demonstrates vision-language model capabilities by running inference with image understanding. The example uses multimodal inputs to validate both text and vision processing pipelines.

### Qwen2.5-VL-7B-Instruct

```bash
export MODEL_HANDLE="nvidia/Qwen2.5-VL-7B-Instruct-FP4"

docker run \
  -e MODEL_HANDLE=$MODEL_HANDLE \
  -e HF_TOKEN=$HF_TOKEN \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  --rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
  --gpus=all --ipc=host --network host \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
  python3 examples/llm-api/quickstart_multimodal.py \
    --model_dir $MODEL_HANDLE \
    --modality image \
    --media "https://huggingface.co/datasets/YiYiXu/testing-images/resolve/main/seashore.png" \
    --prompt "What is happening in this image?" \
  '
```

### Phi-4-multimodal-instruct

This model requires LoRA (Low-Rank Adaptation) configuration as it uses parameter-efficient fine-tuning. The `--load_lora` flag enables loading the LoRA weights that adapt the base model for multimodal instruction following.
```bash
export MODEL_HANDLE="nvidia/Phi-4-multimodal-instruct-FP4"

docker run \
  -e MODEL_HANDLE=$MODEL_HANDLE \
  -e HF_TOKEN=$HF_TOKEN \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  --rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
  --gpus=all --ipc=host --network host \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
  python3 examples/llm-api/quickstart_multimodal.py \
    --model_type phi4mm \
    --model_dir $MODEL_HANDLE \
    --modality image \
    --media "https://huggingface.co/datasets/YiYiXu/testing-images/resolve/main/seashore.png" \
    --prompt "What is happening in this image?" \
    --load_lora \
    --auto_model_name Phi4MMForCausalLM
  '
```


> [!NOTE]
> If you hit a host OOM during downloads or first run, free the OS page cache on the host (outside the container) and retry:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```

## Step 8. Serve LLM with OpenAI-compatible API

Serve with OpenAI-compatible API via trtllm-serve:

### Llama 3.1 8B Instruct
```bash
export MODEL_HANDLE="nvidia/Llama-3.1-8B-Instruct-FP4"

  docker run --name trtllm_llm_server --rm -it --gpus all --ipc host --network host \
  -e HF_TOKEN=$HF_TOKEN \
  -e MODEL_HANDLE="$MODEL_HANDLE" \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
    hf download $MODEL_HANDLE && \
    cat > /tmp/extra-llm-api-config.yml <<EOF
print_iter_log: false
kv_cache_config:
  dtype: "auto"
  free_gpu_memory_fraction: 0.9
cuda_graph_config:
  enable_padding: true
disable_overlap_scheduler: true
EOF
    trtllm-serve "$MODEL_HANDLE" \
      --max_batch_size 64 \
      --trust_remote_code \
      --port 8355 \
      --extra_llm_api_options /tmp/extra-llm-api-config.yml
  '
```

### GPT-OSS 20B
```bash
export MODEL_HANDLE="openai/gpt-oss-20b"

  docker run --name trtllm_llm_server --rm -it --gpus all --ipc host --network host \
  -e HF_TOKEN=$HF_TOKEN \
  -e MODEL_HANDLE="$MODEL_HANDLE" \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
    export TIKTOKEN_ENCODINGS_BASE="/tmp/harmony-reqs" && \
    mkdir -p $TIKTOKEN_ENCODINGS_BASE && \
    wget -P $TIKTOKEN_ENCODINGS_BASE https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken && \
    wget -P $TIKTOKEN_ENCODINGS_BASE https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken && \
    hf download $MODEL_HANDLE && \
    cat > /tmp/extra-llm-api-config.yml <<EOF
print_iter_log: false
kv_cache_config:
  dtype: "auto"
  free_gpu_memory_fraction: 0.9
cuda_graph_config:
  enable_padding: true
disable_overlap_scheduler: true
EOF
    trtllm-serve "$MODEL_HANDLE" \
      --max_batch_size 64 \
      --trust_remote_code \
      --port 8355 \
      --extra_llm_api_options /tmp/extra-llm-api-config.yml
  '
```

Minimal OpenAI-style chat request. Run this from a separate terminal.

```bash
curl -s http://localhost:8355/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"$MODEL_HANDLE"'",
    "messages": [{"role": "user", "content": "Paris is great because"}],
    "max_tokens": 64
  }'
```

## Step 10. Cleanup and rollback

Remove downloaded models and containers to free up space when testing is complete.

> [!WARNING]
> This will delete all cached models and may require re-downloading for future runs.

```bash
# Remove Hugging Face cache
sudo chown -R "$USER:$USER" "$HOME/.cache/huggingface"
rm -rf $HOME/.cache/huggingface/

# Clean up Docker images
docker image prune -f
docker rmi nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev
```
