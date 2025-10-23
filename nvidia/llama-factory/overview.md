# Basic idea
LLaMA Factory is an open-source framework that simplifies the process of training and fine 
tuning large language models. It offers a unified interface for a variety of cutting edge 
methods such as SFT, RLHF, and QLoRA techniques. It also supports a wide range of LLM 
architectures such as LLaMA, Mistral and Qwen. This playbook demonstrates how to fine-tune 
large language models using LLaMA Factory CLI on your NVIDIA Spark device.

# What you'll accomplish

You'll set up LLaMA Factory on NVIDIA Spark with Blackwell architecture to fine-tune large 
language models using LoRA, QLoRA, and full fine-tuning methods. This enables efficient 
model adaptation for specialized domains while leveraging hardware-specific optimizations.

# What to know before starting

- Basic Python knowledge for editing config files and troubleshooting
- Command line usage for running shell commands and managing environments  
- Familiarity with PyTorch and Hugging Face Transformers ecosystem
- GPU environment setup including CUDA/cuDNN installation and VRAM management
- Fine-tuning concepts: understanding tradeoffs between LoRA, QLoRA, and full fine-tuning
- Dataset preparation: formatting text data into JSON structure for instruction tuning
- Resource management: adjusting batch size and memory settings for GPU constraints

# Prerequisites

- NVIDIA Spark device with Blackwell architecture

- CUDA 12.9 or newer version installed: `nvcc --version`

- Docker installed and configured for GPU access: `docker run --gpus all nvidia/cuda:12.9-devel nvidia-smi`

- Git installed: `git --version`

- Python environment with pip: `python --version && pip --version`

- Sufficient storage space (>50GB for models and checkpoints): `df -h`

- Internet connection for downloading models from Hugging Face Hub

# Ancillary files

- Official LLaMA Factory repository: https://github.com/hiyouga/LLaMA-Factory

- NVIDIA PyTorch container: https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch

- Example training configuration: `examples/train_lora/llama3_lora_sft.yaml` (from repository)

- Documentation: https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html

# Time & risk

* **Duration:** 30-60 minutes for initial setup, 1-7 hours for training depending on model size and dataset.
* **Risks:** Model downloads require significant bandwidth and storage. Training may consume substantial GPU memory and require parameter tuning for hardware constraints.
* **Rollback:** Remove Docker containers and cloned repositories. Training checkpoints are saved locally and can be deleted to reclaim storage space.
