# Basic idea

vLLM is an inference engine designed to run large language models efficiently. The key idea is **maximizing throughput and minimizing memory waste** when serving LLMs.

- It uses a memory-efficient attention algoritm called **PagedAttention** to handle long sequences without running out of GPU memory.
- New requests can be added to a batch already in process through **continuous batching** to keep GPUs fully utilized.
- It has an **OpenAI-compatible API** so applications built for the OpenAI API can switch to a vLLM backend with little or no modification.

# What you'll accomplish

You'll set up vLLM high-throughput LLM serving on DGX Spark with Blackwell architecture,
either using a pre-built Docker container or building from source with custom LLVM/Triton
support for ARM64.

# What to know before starting

- Experience building and configuring containers with Docker
- Familiarity with CUDA toolkit installation and version management
- Understanding of Python virtual environments and package management
- Knowledge of building software from source using CMake and Ninja
- Experience with Git version control and patch management

# Prerequisites

- DGX Spark device with ARM64 processor and Blackwell GPU architecture
- CUDA 13.0 toolkit installed: `nvcc --version` shows CUDA toolkit version.
- Docker installed and configured: `docker --version` succeeds
- NVIDIA Container Toolkit installed
- Python 3.12 available: `python3.12 --version` succeeds
- Git installed: `git --version` succeeds
- Network access to download packages and container images


# Time & risk

* **Duration:** 30 minutes for Docker approach
* **Risks:** Container registry access requires internal credentials
* **Rollback:** Container approach is non-destructive.
