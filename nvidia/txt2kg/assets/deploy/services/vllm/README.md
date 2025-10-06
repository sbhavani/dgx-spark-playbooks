# vLLM NVFP4 Deployment

This setup deploys the NVIDIA Llama 4 Scout model with NVFP4 quantization using vLLM, optimized for Blackwell and Hopper GPU architectures.

## Quick Start

1. **Set up your HuggingFace token:**
   ```bash
   cp env.example .env
   # Edit .env and add your HF_TOKEN
   ```

2. **Build and run:**
   ```bash
   docker-compose up --build
   ```

3. **Test the deployment:**
   ```bash
   curl -X POST "http://localhost:8001/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "nvidia/Llama-4-Scout-17B-16E-Instruct-FP4",
       "messages": [{"role": "user", "content": "Hello! How are you?"}],
       "max_tokens": 100
     }'
   ```

## Model Information

- **Model**: `nvidia/Llama-4-Scout-17B-16E-Instruct-FP4`
- **Quantization**: NVFP4 (optimized for Blackwell architecture)
- **Alternative**: `nvidia/Llama-4-Scout-17B-16E-Instruct-FP8` (for Hopper architecture)

## Performance Tuning

The startup script automatically detects your GPU architecture and applies optimal settings:

### Blackwell (Compute Capability 10.0)
- Enables FlashInfer backend
- Uses NVFP4 quantization
- Enables async scheduling
- Applies fusion optimizations

### Hopper (Compute Capability 9.0)
- Uses FP8 quantization
- Disables async scheduling (due to vLLM limitations)
- Standard optimization settings

### Configuration Options

Adjust these environment variables in your `.env` file:

- `VLLM_TENSOR_PARALLEL_SIZE`: Number of GPUs to use (default: 2)
- `VLLM_MAX_NUM_SEQS`: Batch size (default: 128)
- `VLLM_MAX_NUM_BATCHED_TOKENS`: Token batching limit (default: 8192)
- `VLLM_GPU_MEMORY_UTILIZATION`: GPU memory usage (default: 0.9)

### Performance Scenarios

- **Maximum Throughput**: `VLLM_TENSOR_PARALLEL_SIZE=1`, increase `VLLM_MAX_NUM_SEQS`
- **Minimum Latency**: `VLLM_TENSOR_PARALLEL_SIZE=4-8`, `VLLM_MAX_NUM_SEQS=8`
- **Balanced**: `VLLM_TENSOR_PARALLEL_SIZE=2`, `VLLM_MAX_NUM_SEQS=128` (default)

## Benchmarking

To benchmark performance:

```bash
docker exec -it vllm-nvfp4-server vllm bench serve \
  --host 0.0.0.0 \
  --port 8001 \
  --model nvidia/Llama-4-Scout-17B-16E-Instruct-FP4 \
  --dataset-name random \
  --random-input-len 1024 \
  --random-output-len 1024 \
  --max-concurrency 128 \
  --num-prompts 1280
```

## Requirements

- NVIDIA GPU with Blackwell or Hopper architecture
- CUDA Driver 575 or above
- Docker with NVIDIA Container Toolkit
- HuggingFace token (for model access)

## Troubleshooting

- Check GPU compatibility: `nvidia-smi`
- View logs: `docker-compose logs -f vllm-nvfp4`
- Monitor GPU usage: `nvidia-smi -l 1`
