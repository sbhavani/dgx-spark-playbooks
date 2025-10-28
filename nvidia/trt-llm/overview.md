# Basic idea

**NVIDIA TensorRT-LLM (TRT-LLM)** is an open-source library for optimizing and accelerating large language model (LLM) inference on NVIDIA GPUs.

It provides highly efficient kernels, memory management, and parallelism strategies—like tensor, pipeline, and sequence parallelism—so developers can serve LLMs with lower latency and higher throughput.

TRT-LLM integrates with frameworks like Hugging Face and PyTorch, making it easier to deploy state-of-the-art models at scale.


# What you'll accomplish

You'll set up TensorRT-LLM to optimize and deploy large language models on NVIDIA Spark with
Blackwell GPUs, achieving significantly higher throughput and lower latency than standard PyTorch
inference through kernel-level optimizations, efficient memory layouts, and advanced quantization.

# What to know before starting

- Python proficiency and experience with PyTorch or similar ML frameworks
- Command-line comfort for running CLI tools and Docker containers
- Basic understanding of GPU concepts including VRAM, batching, and quantization (FP16/INT8)
- Familiarity with NVIDIA software stack (CUDA Toolkit, drivers)
- Experience with inference servers and containerized environments

# Prerequisites

- NVIDIA Spark device with Blackwell architecture GPUs
- NVIDIA drivers compatible with CUDA 12.x: `nvidia-smi`
- Docker installed and GPU support configured: `docker run --rm --gpus all nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev nvidia-smi`
- Hugging Face account with token for model access: `echo $HF_TOKEN`
- Sufficient GPU VRAM (16GB+ recommended for 70B models)
- Internet connectivity for downloading models and container images
- Network: open TCP ports 8355 (LLM) and 8356 (VLM) on host for OpenAI-compatible serving

# Ancillary files

All required assets can be found [here on GitHub](${GITLAB_ASSET_BASEURL})

- [**trtllm-mn-entrypoint.sh**](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/trtllm-mn-entrypoint.sh) — container entrypoint script for multi-node setup
- [**docker-compose.yml**](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/docker-compose.yml) — Docker Compose configuration for multi-node deployment

# Model Support Matrix

The following models are supported with TensorRT-LLM on Spark. All listed models are available and ready to use:

| Model | Quantization | Support Status | HF Handle |
|-------|-------------|----------------|-----------|
| **GPT-OSS-20B** | MXFP4 | ✅ | `openai/gpt-oss-20b` |
| **GPT-OSS-120B** | MXFP4 | ✅ | `openai/gpt-oss-120b` |
| **Llama-3.1-8B-Instruct** | FP8 | ✅ | `nvidia/Llama-3.1-8B-Instruct-FP8` |
| **Llama-3.1-8B-Instruct** | NVFP4 | ✅ | `nvidia/Llama-3.1-8B-Instruct-FP4` |
| **Llama-3.3-70B-Instruct** | NVFP4 | ✅ | `nvidia/Llama-3.3-70B-Instruct-FP4` |
| **Qwen3-8B** | FP8 | ✅ | `nvidia/Qwen3-8B-FP8` |
| **Qwen3-8B** | NVFP4 | ✅ | `nvidia/Qwen3-8B-FP4` |
| **Qwen3-14B** | FP8 | ✅ | `nvidia/Qwen3-14B-FP8` |
| **Qwen3-14B** | NVFP4 | ✅ | `nvidia/Qwen3-14B-FP4` |
| **Qwen3-32B** | NVFP4 | ✅ | `nvidia/Qwen3-32B-FP4` |
| **Phi-4-multimodal-instruct** | FP8 | ✅ | `nvidia/Phi-4-multimodal-instruct-FP8` |
| **Phi-4-multimodal-instruct** | NVFP4 | ✅ | `nvidia/Phi-4-multimodal-instruct-FP4` |
| **Phi-4-reasoning-plus** | FP8 | ✅ | `nvidia/Phi-4-reasoning-plus-FP8` |
| **Phi-4-reasoning-plus** | NVFP4 | ✅ | `nvidia/Phi-4-reasoning-plus-FP4` |
| **Llama-3_3-Nemotron-Super-49B-v1_5** | FP8 | ✅ | `nvidia/Llama-3_3-Nemotron-Super-49B-v1_5-FP8` |
| **Qwen3-30B-A3B** | NVFP4 | ✅ | `nvidia/Qwen3-30B-A3B-FP4` |
| **Qwen2.5-VL-7B-Instruct** | FP8 | ✅ | `nvidia/Qwen2.5-VL-7B-Instruct-FP8` |
| **Qwen2.5-VL-7B-Instruct** | NVFP4 | ✅ | `nvidia/Qwen2.5-VL-7B-Instruct-FP4` |
| **Llama-4-Scout-17B-16E-Instruct** | NVFP4 | ✅ | `nvidia/Llama-4-Scout-17B-16E-Instruct-FP4` |
| **Qwen3-235B-A22B (two Sparks only)** | NVFP4 | ✅ | `nvidia/Qwen3-235B-A22B-FP4` |

> [!NOTE]
> You can use the NVFP4 Quantization documentation to generate your own NVFP4-quantized checkpoints for your favorite models. This enables you to take advantage of the performance and memory benefits of NVFP4 quantization even for models not already published by NVIDIA.

Reminder: not all model architectures are supported for NVFP4 quantization.

# Time & risk

* **Duration**: 45-60 minutes for setup and API server deployment
* **Risk level**: Medium - container pulls and model downloads may fail due to network issues
* **Rollback**: Stop inference servers and remove downloaded models to free resources.
