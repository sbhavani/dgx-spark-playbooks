# Basic idea

Speculative decoding speeds up text generation by using a **small, fast model** to draft several tokens ahead, then having the **larger model** quickly verify or adjust them.
This way, the big model doesn't need to predict every token step-by-step, reducing latency while keeping output quality.

# What you'll accomplish

You'll explore speculative decoding using TensorRT-LLM on NVIDIA Spark using the traditional Draft-Target approach.
These examples demonstrate how to accelerate large language model inference while maintaining output quality.

# What to know before starting

- Experience with Docker and containerized applications
- Understanding of speculative decoding concepts
- Familiarity with TensorRT-LLM serving and API endpoints
- Knowledge of GPU memory management for large language models

# Prerequisites

- NVIDIA Spark device with sufficient GPU memory available
- Docker with GPU support enabled

  ```bash
  docker run --gpus all nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev nvidia-smi
  ```
- HuggingFace authentication configured (if needed for model downloads)

  ```bash
  huggingface-cli login
  ```
- Network connectivity for model downloads


# Time & risk

* **Duration:** 10-20 minutes for setup, additional time for model downloads (varies by network speed)
* **Risks:** GPU memory exhaustion with large models, container registry access issues, network timeouts during downloads
* **Rollback:** Stop Docker containers and optionally clean up downloaded model cache.
