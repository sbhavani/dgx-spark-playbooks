# Fine tune with Pytorch

> Use Pytorch to fine-tune models locally

## Table of Contents

- [Overview](#overview)
- [Instructions](#instructions)

---

## Overview

## Basic Idea

This playbook guides you through setting up and using Pytorch for fine-tuning large language models and vision-language models on NVIDIA Spark devices. NeMo AutoModel provides GPU-accelerated, end-to-end training for Hugging Face models with native PyTorch support, enabling instant fine-tuning without conversion delays. The framework supports distributed training across single GPU to multi-node clusters, with optimized kernels and memory-efficient recipes specifically designed for ARM64 architecture and Blackwell GPU systems.

## What you'll accomplish

You'll establish a complete fine-tuning environment for large language models (1-70B parameters) and vision-language models using NeMo AutoModel on your NVIDIA Spark device. By the end, you'll have a working installation that supports parameter-efficient fine-tuning (PEFT), supervised fine-tuning (SFT), and distributed training capabilities with FP8 precision optimizations, all while maintaining compatibility with the Hugging Face ecosystem.

## What to know before starting



## Prerequisites



## Ancillary files



## Time & risk

**Time estimate:** 

**Risks:** Model downloads can be large (several GB), ARM64 package compatibility issues may require troubleshooting, distributed training setup complexity increases with multi-node configurations

**Rollback:**

## Instructions

## Step 1. Verify system requirements

Check your NVIDIA Spark device meets the prerequisites for NeMo AutoModel installation. This step runs on the host system to confirm CUDA toolkit availability and Python version compatibility.

```bash
## Verify CUDA installation
nvcc --version

## Verify GPU accessibility
nvidia-smi

## Check available system memory
free -h
```

## Step 2. Get the container image

```bash
docker pull nvcr.io/nvidia/pytorch:25.08-py3
```

## Step 3. Launch Docker

```bash
docker run \
  --gpus all \
  --ulimit memlock=-1 \
  -it --ulimit stack=67108864 \
  --entrypoint /usr/bin/bash \
  --rm nvcr.io/nvidia/pytorch:25.08-py3
```





## Step 10. Troubleshooting

Common issues and solutions for NeMo AutoModel setup on NVIDIA Spark devices.

| Symptom | Cause | Fix |
|---------|--------|-----|
| `nvcc: command not found` | CUDA toolkit not in PATH | Add CUDA toolkit to PATH: `export PATH=/usr/local/cuda/bin:$PATH` |
| `pip install uv` permission denied | System-level pip restrictions | Use `pip3 install --user uv` and update PATH |
| GPU not detected in training | CUDA driver/runtime mismatch | Verify driver compatibility: `nvidia-smi` and reinstall CUDA if needed |
| Out of memory during training | Model too large for available GPU memory | Reduce batch size, enable gradient checkpointing, or use model parallelism |
| ARM64 package compatibility issues | Package not available for ARM architecture | Use source installation or build from source with ARM64 flags |

## Step 11. Cleanup and rollback

Remove the installation and restore the original environment if needed. These commands safely remove all installed components.

> **Warning:** This will delete all virtual environments and downloaded models. Ensure you have backed up any important training checkpoints.

```bash
## Remove virtual environment
rm -rf .venv

## Remove cloned repository
cd ..
rm -rf Automodel

## Remove uv (if installed with --user)
pip3 uninstall uv

## Clear Python cache
rm -rf ~/.cache/pip
```

## Step 12. Next steps
