## Basic idea

NVIDIA NIM is containerized software for fast, reliable AI model serving and inference on NVIDIA GPUs. This playbook demonstrates how to run NIM microservices for LLMs on DGX Spark devices, enabling local GPU inference through a simple Docker workflow. You'll authenticate with NVIDIA's registry, launch the NIM inference microservice, and perform basic inference testing to verify functionality.

## What you'll accomplish

You'll launch a NIM container on your DGX Spark device to expose a GPU-accelerated HTTP endpoint for text completions. While these instructions feature working with the Llama 3.1 8B NIM, additional NIM including the [Qwen3-32 NIM](https://catalog.ngc.nvidia.com/orgs/nim/teams/qwen/containers/qwen3-32b-dgx-spark) are available for DGX Spark (see them [here](https://docs.nvidia.com/nim/large-language-models/1.14.0/release-notes.html#new-language-models%20)).

## What to know before starting

- Working in a terminal environment
- Using Docker commands and GPU-enabled containers
- Basic familiarity with REST APIs and curl commands
- Understanding of NVIDIA GPU environments and CUDA

## Prerequisites

- DGX Spark device with NVIDIA drivers installed
  ```bash
  nvidia-smi
  ```
- Docker with NVIDIA Container Toolkit configured, instructions [here](https://docs.nvidia.com/dgx/dgx-spark/nvidia-container-runtime-for-docker.html)
  ```bash
  docker run -it --gpus=all nvcr.io/nvidia/cuda:13.0.1-devel-ubuntu24.04 nvidia-smi
  ```
- NGC account with API key from [here](https://ngc.nvidia.com/setup/api-key)
  ```bash
  echo $NGC_API_KEY | grep -E '^[a-zA-Z0-9]{86}=='
  ```
- Sufficient disk space for model caching (varies by model, typically 10-50GB)
  ```bash
  df -h ~
  ```


## Time & risk

* **Estimated time:** 15-30 minutes for setup and validation
* **Risks:**
  * Large model downloads may take significant time depending on network speed
  * GPU memory requirements vary by model size
  * Container startup time depends on model loading
* **Rollback:** Stop and remove containers with `docker stop <CONTAINER_NAME> && docker rm <CONTAINER_NAME>`. Remove cached models from `~/.cache/nim` if disk space recovery is needed.
