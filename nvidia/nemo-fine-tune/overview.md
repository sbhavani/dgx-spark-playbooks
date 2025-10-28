# Basic idea

This playbook guides you through setting up and using NVIDIA NeMo AutoModel for fine-tuning large language models and vision-language models on NVIDIA Spark devices. NeMo AutoModel provides GPU-accelerated, end-to-end training for Hugging Face models with native PyTorch support, enabling instant fine-tuning without conversion delays. The framework supports distributed training across single GPU to multi-node clusters, with optimized kernels and memory-efficient recipes specifically designed for ARM64 architecture and Blackwell GPU systems.

# What you'll accomplish

You'll establish a complete fine-tuning environment for large language models (1-70B parameters) and vision-language models using NeMo AutoModel on your NVIDIA Spark device. By the end, you'll have a working installation that supports parameter-efficient fine-tuning (PEFT), supervised fine-tuning (SFT), and distributed training capabilities with FP8 precision optimizations, all while maintaining compatibility with the Hugging Face ecosystem.

# What to know before starting

- Working in Linux terminal environments and SSH connections
- Basic understanding of Python virtual environments and package management
- Familiarity with GPU computing concepts and CUDA toolkit usage
- Experience with containerized workflows and Docker/Podman operations
- Understanding of machine learning model training concepts and fine-tuning workflows

# Prerequisites

- NVIDIA Spark device with Blackwell architecture GPU access
- CUDA toolkit 12.0+ installed and configured: `nvcc --version`
- Python 3.10+ environment available: `python3 --version`
- Minimum 32GB system RAM for efficient model loading and training
- Active internet connection for downloading models and packages
- Git installed for repository cloning: `git --version`
- SSH access to your NVIDIA Spark device configured

# Ancillary files

All necessary files for the playbook can be found [here on GitHub](https://github.com/NVIDIA-NeMo/Automodel)

# Time & risk

* **Duration:** 45-90 minutes for complete setup and initial model fine-tuning
* **Risks:** Model downloads can be large (several GB), ARM64 package compatibility issues may require troubleshooting, distributed training setup complexity increases with multi-node configurations
* **Rollback:** Virtual environments can be completely removed; no system-level changes are made to the host system beyond package installations.
