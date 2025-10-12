# Fine-tune with NeMo

> Use NVIDIA NeMo to fine-tune models locally

## Table of Contents

- [Overview](#overview)
- [Instructions](#instructions)
- [Troubleshooting](#troubleshooting)

---

## Overview

## Basic idea

This playbook guides you through setting up and using NVIDIA NeMo AutoModel for fine-tuning large language models and vision-language models on NVIDIA Spark devices. NeMo AutoModel provides GPU-accelerated, end-to-end training for Hugging Face models with native PyTorch support, enabling instant fine-tuning without conversion delays. The framework supports distributed training across single GPU to multi-node clusters, with optimized kernels and memory-efficient recipes specifically designed for ARM64 architecture and Blackwell GPU systems.

## What you'll accomplish

You'll establish a complete fine-tuning environment for large language models (1-70B parameters) and vision-language models using NeMo AutoModel on your NVIDIA Spark device. By the end, you'll have a working installation that supports parameter-efficient fine-tuning (PEFT), supervised fine-tuning (SFT), and distributed training capabilities with FP8 precision optimizations, all while maintaining compatibility with the Hugging Face ecosystem.

## What to know before starting

- Working in Linux terminal environments and SSH connections
- Basic understanding of Python virtual environments and package management
- Familiarity with GPU computing concepts and CUDA toolkit usage
- Experience with containerized workflows and Docker/Podman operations
- Understanding of machine learning model training concepts and fine-tuning workflows

## Prerequisites

- NVIDIA Spark device with Blackwell architecture GPU access
- CUDA toolkit 12.0+ installed and configured: `nvcc --version`
- Python 3.10+ environment available: `python3 --version`
- Minimum 32GB system RAM for efficient model loading and training
- Active internet connection for downloading models and packages
- Git installed for repository cloning: `git --version`
- SSH access to your NVIDIA Spark device configured

## Ancillary files

All necessary files for the playbook can be found [here on GitHub](https://github.com/NVIDIA-NeMo/Automodel)

## Time & risk

* **Duration:** 45-90 minutes for complete setup and initial model fine-tuning
* **Risks:** Model downloads can be large (several GB), ARM64 package compatibility issues may require troubleshooting, distributed training setup complexity increases with multi-node configurations
* **Rollback:** Virtual environments can be completely removed; no system-level changes are made to the host system beyond package installations.

## Instructions

## Step 1. Verify system requirements

Check your NVIDIA Spark device meets the prerequisites for NeMo AutoModel installation. This step runs on the host system to confirm CUDA toolkit availability and Python version compatibility.

```bash
## Verify CUDA installation
nvcc --version

## Check Python version (3.10+ required)
python3 --version

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

## Step 4. Install package management tools

Install `uv` for efficient package management and virtual environment isolation. NeMo AutoModel uses `uv` for dependency management and automatic environment handling.

```bash
## Install uv package manager
pip3 install uv

## Verify installation
uv --version
```

**If system installation fails:**

```bash
## Install for current user only
pip3 install --user uv

## Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

## Step 5. Clone NeMo AutoModel repository

Clone the official NeMo AutoModel repository to access recipes and examples. This provides ready-to-use training configurations for various model types and training scenarios.

```bash
## Clone the repository
git clone https://github.com/NVIDIA-NeMo/Automodel.git

## Navigate to the repository
cd Automodel
```

## Step 6. Install NeMo AutoModel

Set up the virtual environment and install NeMo AutoModel. Choose between wheel package installation for stability or source installation for latest features.

**Install from wheel package (recommended):**

```bash
## Initialize virtual environment
uv venv --system-site-packages

## Install packages with uv
uv sync --inexact --frozen --all-extras \
  --no-install-package torch \
  --no-install-package torchvision \
  --no-install-package triton \
  --no-install-package nvidia-cublas-cu12 \
  --no-install-package nvidia-cuda-cupti-cu12 \
  --no-install-package nvidia-cuda-nvrtc-cu12 \
  --no-install-package nvidia-cuda-runtime-cu12 \
  --no-install-package nvidia-cudnn-cu12 \
  --no-install-package nvidia-cufft-cu12 \
  --no-install-package nvidia-cufile-cu12 \
  --no-install-package nvidia-curand-cu12 \
  --no-install-package nvidia-cusolver-cu12 \
  --no-install-package nvidia-cusparse-cu12 \
  --no-install-package nvidia-cusparselt-cu12 \
  --no-install-package nvidia-nccl-cu12 \
  --no-install-package transformer-engine \
  --no-install-package nvidia-modelopt \
  --no-install-package nvidia-modelopt-core \
  --no-install-package flash-attn \
  --no-install-package transformer-engine-cu12 \
  --no-install-package transformer-engine-torch

## Install bitsandbytes
CMAKE_ARGS="-DCOMPUTE_BACKEND=cuda -DCOMPUTE_CAPABILITY=80;86;87;89;90" \
CMAKE_BUILD_PARALLEL_LEVEL=8 \
uv pip install --no-deps git+https://github.com/bitsandbytes-foundation/bitsandbytes.git@50be19c39698e038a1604daf3e1b939c9ac1c342
```

## Step 7. Verify installation

Confirm NeMo AutoModel is properly installed and accessible. This step validates the installation and checks for any missing dependencies.

```bash
## Test NeMo AutoModel import
uv run --frozen --no-sync python -c "import nemo_automodel; print('✅ NeMo AutoModel ready')"

## Check available examples
ls -la examples/
```

## Step 8. Explore available examples

Review the pre-configured training recipes available for different model types and training scenarios. These recipes provide optimized configurations for ARM64 and Blackwell architecture.

```bash
## List LLM fine-tuning examples
ls examples/llm_finetune/

## View example recipe configuration
cat examples/llm_finetune/finetune.py | head -20
```

## Step 9. Run sample fine-tuning
The following commands show how to perform full fine-tuning (SFT), parameter-efficient fine-tuning (PEFT) with LoRA and QLoRA.

First, export your HF_TOKEN so that gated models can be downloaded.

```bash
## Run basic LLM fine-tuning example
export HF_TOKEN=<your_huggingface_token>
```
> [!NOTE]
> Please Replace `<your_huggingface_token>` with your Hugging Face access token to access gated models (e.g., Llama).

**Full Fine-tuning example:**

Once inside the `Automodel` directory you cloned from github, run:

```bash
uv run --frozen --no-sync \
examples/llm_finetune/finetune.py \
-c examples/llm_finetune/llama3_2/llama3_2_1b_squad.yaml \
--step_scheduler.local_batch_size 1 \
--loss_fn._target_ nemo_automodel.components.loss.te_parallel_ce.TEParallelCrossEntropy \
--model.pretrained_model_name_or_path Qwen/Qwen3-8B
```
These overrides ensure the Qwen3-8B SFT run behaves as expected:
- `--model.pretrained_model_name_or_path`: selects the Qwen/Qwen3-8B model to fine-tune (weights fetched via your Hugging Face token).
- `--loss_fn._target_`: uses the TransformerEngine-parallel cross-entropy loss variant compatible with tensor-parallel training for large LLMs.
- `--step_scheduler.local_batch_size`: sets the per-GPU micro-batch size to 1 to fit in memory; overall effective batch size is still driven by gradient accumulation and data/tensor parallel settings from the recipe.

**LoRA fine-tuning example:**

Execute a basic fine-tuning example to validate the complete setup. This demonstrates parameter-efficient fine-tuning using a small model suitable for testing.

```bash
## Run basic LLM fine-tuning example
uv run --frozen --no-sync \
examples/llm_finetune/finetune.py \
-c examples/llm_finetune/llama3_2/llama3_2_1b_squad_peft.yaml \
--model.pretrained_model_name_or_path meta-llama/Llama-3.1-8B
```
**QLoRA fine-tuning example:**

We can use QLoRA to fine-tune large models in a memory-efficient manner.

```bash
uv run --frozen --no-sync \
examples/llm_finetune/finetune.py \
-c examples/llm_finetune/llama3_1/llama3_1_8b_squad_qlora.yaml \
--model.pretrained_model_name_or_path meta-llama/Meta-Llama-3-70B \
--loss_fn._target_ nemo_automodel.components.loss.te_parallel_ce.TEParallelCrossEntropy \
--step_scheduler.local_batch_size 1
```

These overrides ensure the 70B QLoRA run behaves as expected:
- `--model.pretrained_model_name_or_path`: selects the 70B base model to fine-tune (weights fetched via your Hugging Face token).
- `--loss_fn._target_`: uses the TransformerEngine-parallel cross-entropy loss variant compatible with tensor-parallel training for large LLMs.
- `--step_scheduler.local_batch_size`: sets the per-GPU micro-batch size to 1 to fit 70B in memory; overall effective batch size is still driven by gradient accumulation and data/tensor parallel settings from the recipe. 

## Step 10. Validate training output

Check that fine-tuning completed successfully and inspect the generated model artifacts. This confirms the training pipeline works correctly on your Spark device.

```bash
## Check training logs
ls -la logs/

## Verify model checkpoint creation
ls -la checkpoints/

## Test model inference (if applicable)
uv run python -c "
import torch
print('GPU available:', torch.cuda.is_available())
print('GPU count:', torch.cuda.device_count())
"
```

## Step 11. Validate complete setup

Perform final validation to ensure all components are working correctly. This comprehensive check confirms the environment is ready for production fine-tuning workflows.

```bash
## Test complete pipeline
uv run python -c "
import nemo_automodel
import torch
print('✅ NeMo AutoModel version:', nemo_automodel.__version__)
print('✅ CUDA available:', torch.cuda.is_available())
print('✅ GPU count:', torch.cuda.device_count())
print('✅ Setup complete')
"
```

## Step 13. Cleanup and rollback

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

## Step 14. Next steps

Begin using NeMo AutoModel for your specific fine-tuning tasks. Start with provided recipes and customize based on your model requirements and dataset.

```bash
## Copy a recipe for customization
cp recipes/llm_finetune/finetune.py my_custom_training.py

## Edit configuration for your specific model and data
## Then run: uv run my_custom_training.py
```

Explore the [NeMo AutoModel GitHub repository](https://github.com/NVIDIA-NeMo/Automodel) for advanced recipes, documentation, and community examples. Consider setting up custom datasets, experimenting with different model architectures, and scaling to multi-node distributed training for larger models.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|--------|-----|
| `nvcc: command not found` | CUDA toolkit not in PATH | Add CUDA toolkit to PATH: `export PATH=/usr/local/cuda/bin:$PATH` |
| `pip install uv` permission denied | System-level pip restrictions | Use `pip3 install --user uv` and update PATH |
| GPU not detected in training | CUDA driver/runtime mismatch | Verify driver compatibility: `nvidia-smi` and reinstall CUDA if needed |
| Out of memory during training | Model too large for available GPU memory | Reduce batch size, enable gradient checkpointing, or use model parallelism |
| ARM64 package compatibility issues | Package not available for ARM architecture | Use source installation or build from source with ARM64 flags |
| Cannot access gated repo for URL | Certain HuggingFace models have restricted access | Regenerate your [HuggingFace token](https://huggingface.co/docs/hub/en/security-tokens); and request access to the [gated model](https://huggingface.co/docs/hub/en/models-gated#customize-requested-information) on your web browser |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
