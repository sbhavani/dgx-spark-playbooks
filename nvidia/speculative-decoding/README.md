# Speculative Decoding

> Learn how to setup speculative decoding for fast inference on Spark

## Table of Contents

- [Overview](#overview)
- [How to run inference with speculative decoding](#how-to-run-inference-with-speculative-decoding)
  - [Step 1. Run Eagle3 with GPT-OSS 120B](#step-1-run-eagle3-with-gpt-oss-120b)
  - [Step 2. Test the Eagle3 setup](#step-2-test-the-eagle3-setup)
  - [Step 1. Run Draft-Target Speculative Decoding](#step-1-run-draft-target-speculative-decoding)
  - [Step 2. Test the Draft-Target setup](#step-2-test-the-draft-target-setup)
  - [Troubleshooting](#troubleshooting)
  - [Cleanup](#cleanup)
  - [Next Steps](#next-steps)

---

## Overview

## Basic idea

Speculative decoding speeds up text generation by using a **small, fast model** to draft several tokens ahead, then having the **larger model** quickly verify or adjust them.
This way, the big model doesn’t need to predict every token step-by-step, reducing latency while keeping output quality.

## What you'll accomplish

You'll explore two different speculative decoding approaches using TensorRT-LLM on NVIDIA Spark:
1. **Eagle3 with GPT-OSS 120B** - Advanced speculative decoding using Eagle3 draft models
2. **Traditional Draft-Target** - Classic speculative decoding with smaller model pairs (coming soon)

These examples demonstrate how to accelerate large language model inference while maintaining output quality.

## What to know before starting

- Experience with Docker and containerized applications
- Understanding of speculative decoding concepts (Eagle3 vs traditional draft-target)
- Familiarity with TensorRT-LLM serving and API endpoints
- Knowledge of GPU memory management for large language models

## Prerequisites

- [ ] NVIDIA Spark device with sufficient GPU memory available (80GB+ recommended for GPT-OSS 120B)
- [ ] Docker with GPU support enabled
  ```bash
  docker run --gpus all nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev nvidia-smi
  ```
- [ ] Access to NVIDIA's internal container registry (for Eagle3 example)
- [ ] HuggingFace authentication configured (if needed for model downloads)
  ```bash
  huggingface-cli login
  ```
- [ ] Network connectivity for model downloads


## Time & risk

**Duration:** 10-20 minutes for Eagle3 setup, additional time for model downloads (varies by network speed)

**Risks:** GPU memory exhaustion with large models, container registry access issues, network timeouts during downloads

**Rollback:** Stop Docker containers and optionally clean up downloaded model cache

## How to run inference with speculative decoding

## Example 1: Eagle3 Speculative Decoding with GPT-OSS 120B

Eagle3 is an advanced speculative decoding technique that uses a specialized draft model to accelerate inference of large language models.

### Step 1. Run Eagle3 with GPT-OSS 120B

Execute the following command to download models and run Eagle3 speculative decoding:

```bash
docker run \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  --rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
  --gpus=all --ipc=host --network host nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
    hf download openai/gpt-oss-120b && \
    hf download nvidia/gpt-oss-120b-Eagle3 \
        --local-dir /opt/gpt-oss-120b-Eagle3/ && \
    cat > /tmp/extra-llm-api-config.yml <<EOF
enable_attention_dp: false
disable_overlap_scheduler: true
enable_autotuner: false
cuda_graph_config:
    max_batch_size: 1
speculative_config:
    decoding_type: Eagle
    max_draft_len: 4
    speculative_model_dir: /opt/gpt-oss-120b-Eagle3/

kv_cache_config:
    enable_block_reuse: false
EOF
    trtllm-serve openai/gpt-oss-120b \
      --backend pytorch --tp_size 1 \
      --max_batch_size 1 \
      --kv_cache_free_gpu_memory_fraction 0.95 \
      --extra_llm_api_options /tmp/extra-llm-api-config.yml'
```

### Step 2. Test the Eagle3 setup

Once the server is running, you can test it with curl commands:

```bash
## Test completion endpoint
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-oss-120b",
    "prompt": "The future of AI is",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```


## Example 2: Traditional Draft-Target Speculative Decoding

This example demonstrates traditional speculative decoding using a smaller draft model to accelerate a larger target model.

### Step 1. Run Draft-Target Speculative Decoding

Execute the following command to set up and run traditional speculative decoding:

```bash
docker run \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  --rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
  --gpus=all --ipc=host --network host nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c "
#    # Download models
    hf download nvidia/Llama-3.3-70B-Instruct-FP4 && \
    hf download nvidia/Llama-3.1-8B-Instruct-FP4 \
    --local-dir /opt/Llama-3.1-8B-Instruct-FP4/ && \

#    # Create configuration file
    cat <<EOF > extra-llm-api-config.yml
print_iter_log: false
disable_overlap_scheduler: true
speculative_config:
  decoding_type: DraftTarget
  max_draft_len: 4
  speculative_model_dir: /opt/Llama-3.1-8B-Instruct-FP4/
kv_cache_config:
  enable_block_reuse: false
EOF

#    # Start TensorRT-LLM server
    trtllm-serve nvidia/Llama-3.3-70B-Instruct-FP4 \
      --backend pytorch --tp_size 1 \
      --max_batch_size 1 \
      --kv_cache_free_gpu_memory_fraction 0.9 \
      --extra_llm_api_options ./extra-llm-api-config.yml
  "
```

### Step 2. Test the Draft-Target setup

Once the server is running, test it with API calls:

```bash
## Test completion endpoint
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nvidia/Llama-3.3-70B-Instruct-FP4",
    "prompt": "Explain the benefits of speculative decoding:",
    "max_tokens": 150,
    "temperature": 0.7
  }'
```

#### Key Features of Draft-Target:
- **Efficient resource usage**: 8B draft model accelerates 70B target model
- **Flexible configuration**: Adjustable draft token length for optimization
- **Memory efficient**: Uses FP4 quantized models for reduced memory footprint
- **Compatible models**: Uses Llama family models with consistent tokenization

### Troubleshooting

Common issues and solutions:

| Symptom | Cause | Fix |
|---------|--------|-----|
| "CUDA out of memory" error | Insufficient GPU memory | Reduce `kv_cache_free_gpu_memory_fraction` to 0.9 or use a device with more VRAM |
| Container fails to start | Docker GPU support issues | Verify `nvidia-docker` is installed and `--gpus=all` flag is supported |
| Model download fails | Network or authentication issues | Check HuggingFace authentication and network connectivity |
| Server doesn't respond | Port conflicts or firewall | Check if port 8000 is available and not blocked |

### Cleanup

Stop the Docker container when finished:

```bash
## Find and stop the container
docker ps
docker stop <container_id>

## Optional: Clean up downloaded models from cache
## rm -rf $HOME/.cache/huggingface/hub/models--*gpt-oss*
```

### Next Steps

- Compare both Eagle3 and Draft-Target performance with baseline inference
- Experiment with different `max_draft_len` values (1, 2, 3, 4, 8) for both approaches
- Monitor token acceptance rates and throughput improvements across different model pairs
- Test with different prompt lengths and generation parameters
- Compare Eagle3 vs Draft-Target approaches for your specific use case
- Benchmark memory usage differences between the two methods
