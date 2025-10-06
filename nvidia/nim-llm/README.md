# Use a NIM on Spark

> Run a NIM on Spark

## Table of Contents

- [Overview](#overview)
  - [Basic Idea](#basic-idea)
  - [What you'll accomplish](#what-youll-accomplish)
  - [What to know before starting](#what-to-know-before-starting)
  - [Prerequisites](#prerequisites)
  - [Time & risk](#time-risk)
- [Instructions](#instructions)
  - [Step 2. Configure NGC authentication](#step-2-configure-ngc-authentication)

---

## Overview

### Basic Idea

NVIDIA Inference Microservices (NIMs) provide optimized containers for deploying large language
models with simplified APIs. This playbook demonstrates how to run LLM NIMs on DGX Spark devices,
enabling GPU-accelerated inference through Docker containers. You'll set up authentication with
NVIDIA's registry, launch a containerized LLM service, and perform basic inference testing to
verify functionality.

### What you'll accomplish

You'll deploy an LLM NIM container on your DGX Spark device, configure it for GPU acceleration,
and establish a working inference endpoint that responds to HTTP API calls with generated text
completions.

### What to know before starting

- Working in a terminal environment
- Using Docker commands and GPU-enabled containers
- Basic familiarity with REST APIs and curl commands
- Understanding of NVIDIA GPU environments and CUDA

### Prerequisites

- DGX Spark device with NVIDIA drivers installed
  ```bash
  nvidia-smi
  ```
- Docker with NVIDIA Container Toolkit configured, instructions here: https://******.nvidia.com/dgx-docs/review/621/dgx-spark/latest/nvidia-container-runtime-for-docker.html
  ```bash
  docker run -it --gpus=all nvcr.io/nvidia/cuda:13.0.1-devel-ubuntu24.04 nvidia-smi
  ```
- NGC account with API key from https://ngc.nvidia.com/setup/api-key
  ```bash
  echo $NGC_API_KEY | grep -E '^[a-zA-Z0-9]{86}=='
  ```
- Sufficient disk space for model caching (varies by model, typically 10-50GB)
  ```bash
  df -h ~
  ```


### Time & risk

**Estimated time:** 15-30 minutes for setup and validation

**Risks:**
- Large model downloads may take significant time depending on network speed
- GPU memory requirements vary by model size
- Container startup time depends on model loading

**Rollback:** Stop and remove containers with `docker stop <CONTAINER_NAME> && docker rm <CONTAINER_NAME>`. Remove cached models from `~/.cache/nim` if disk space recovery is needed.

## Instructions

## Step 1. Verify environment prerequisites

Check that your system meets the basic requirements for running GPU-enabled containers.

```bash
nvidia-smi
docker --version
docker run --rm --gpus all nvidia/cuda:12.0-base-ubuntu20.04 nvidia-smi
```

### Step 2. Configure NGC authentication

Set up access to NVIDIA's container registry using your NGC API key.

```bash
export NGC_API_KEY="<YOUR_NGC_API_KEY>"
echo "$NGC_API_KEY" | docker login nvcr.io --username '$oauthtoken' --password-stdin
```

## Step 3. Select and configure NIM container

Choose a specific LLM NIM from NGC and set up local caching for model assets.

```bash
export CONTAINER_NAME="nim-llm-demo"
export IMG_NAME="nvcr.io/nim/meta/llama-3.1-8b-instruct-dgx-spark:latest"
export LOCAL_NIM_CACHE=~/.cache/nim
mkdir -p "$LOCAL_NIM_CACHE"
chmod -R a+w "$LOCAL_NIM_CACHE"
```

## Step 4. Launch NIM container

Start the containerized LLM service with GPU acceleration and proper resource allocation.

```bash
docker run -it --rm --name=$CONTAINER_NAME \
  --runtime=nvidia \
  --gpus all \
  --shm-size=16GB \
  -e NGC_API_KEY=$NGC_API_KEY \
  -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
  -u $(id -u) \
  -p 8000:8000 \
  $IMG_NAME
```

The container will download the model on first run and may take several minutes to start. Look for
startup messages indicating the service is ready.

## Step 5. Validate inference endpoint

Test the deployed service with a basic completion request to verify functionality. Run the following curl command in a new terminal.


```bash
curl -X 'POST' \
    'http://0.0.0.0:8000/v1/chat/completions' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
      "model": "meta/llama-3.1-8b-instruct",
      "messages": [
        {
          "role":"system",
          "content":"detailed thinking on"
        },
        {
          "role":"user",
          "content":"Can you write me a song?"
        }
      ],
      "top_p": 1,
      "n": 1,
      "max_tokens": 15,
      "frequency_penalty": 1.0,
      "stop": ["hello"]

    }'
    
```

Expected output should be a JSON response containing a completion field with generated text.

## Step 6. Troubleshooting

| Symptom | Cause | Fix |
|---------|--------|-----|
| Container fails to start with GPU error | NVIDIA Container Toolkit not configured | Install nvidia-container-toolkit and restart Docker |
| "Invalid credentials" during docker login | Incorrect NGC API key format | Verify API key from NGC portal, ensure no extra whitespace |
| Model download hangs or fails | Network connectivity or insufficient disk space | Check internet connection and available disk space in cache directory |
| API returns 404 or connection refused | Container not fully started or wrong port | Wait for container startup completion, verify port 8000 is accessible |
| runtime not found | NVIDIA Container Toolkit not properly configured | Run `sudo nvidia-ctk runtime configure --runtime=docker` and restart Docker |

## Step 8. Cleanup and rollback

Remove the running container and optionally clean up cached model files.

> **Warning:** Removing cached models will require re-downloading on next run.

```bash
docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME
```

To remove cached models and free disk space:
```bash
rm -rf "$LOCAL_NIM_CACHE"
```

## Step 7. Next steps

With a working NIM deployment, you can:

- Integrate the API endpoint into your applications using the OpenAI-compatible interface
- Experiment with different models available in the NGC catalog
- Scale the deployment using container orchestration tools
- Monitor resource usage and optimize container resource allocation

Test the integration with your preferred HTTP client or SDK to begin building applications.
