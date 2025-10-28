# Basic Idea

SGLang is a fast serving framework for large language models and vision language models that makes
your interaction with models faster and more controllable by co-designing the backend runtime and
frontend language. This setup uses the optimized NVIDIA SGLang NGC Container on a single NVIDIA
Spark device with Blackwell architecture, providing GPU-accelerated inference with all dependencies
pre-installed.

# What you'll accomplish

You'll deploy SGLang in both server and offline inference modes on your NVIDIA Spark device,
enabling high-performance LLM serving with support for text generation, chat completion, and
vision-language tasks using models like DeepSeek-V2-Lite.

# What to know before starting

- Working in a terminal environment on Linux systems
- Basic understanding of Docker containers and container management
- Familiarity with NVIDIA GPU drivers and CUDA toolkit concepts
- Experience with HTTP API endpoints and JSON request/response handling

# Prerequisites

- NVIDIA Spark device with Blackwell architecture
- Docker Engine installed and running: `docker --version`
- NVIDIA GPU drivers installed: `nvidia-smi`
- NVIDIA Container Toolkit configured: `docker run --rm --gpus all nvidia/cuda:12.9-base nvidia-smi`
- Sufficient disk space (>20GB available): `df -h`
- Network connectivity for pulling NGC containers: `ping nvcr.io`

# Ancillary files

- An offline inference python script [found here on GitHub](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/offline-inference.py)

## Time & risk

**Duration:** 15-30 minutes for initial setup and validation

**Risk level:** Low - Uses pre-built, validated NGC container with minimal configuration

**Rollback:** Stop and remove containers with `docker stop` and `docker rm` commands
