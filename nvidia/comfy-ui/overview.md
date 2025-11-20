# Basic idea

ComfyUI is an open-source web server application for AI image generation using diffusion-based models like SDXL, Flux and others.
It has a browser-based UI that lets you create, edit and run image generation and editing workflows with multiple steps.
Generation and editing steps (e.g. loading a model, adding text or sampling) are configurable in the UI as a node, and you connect nodes with wires to form a workflow.  

ComfyUI uses the host's GPU for inference, so you can install it on your Spark and do all of your image generation and editing directly on device.  

Workflows are saved as JSON files, so you can version them for future work, collaboration and reproducibility.

# What you'll accomplish

You'll install and configure ComfyUI on your NVIDIA DGX Spark device so you can use the unified memory to work with large models.

# What to know before starting

- Experience working with Python virtual environments and package management
- Familiarity with command line operations and terminal usage
- Basic understanding of deep learning model deployment and checkpoints
- Knowledge of container workflows and GPU acceleration concepts
- Understanding of network configuration for accessing web services

# Prerequisites

**Hardware Requirements:**
-  NVIDIA Spark device with Blackwell architecture
-  Minimum 8GB GPU memory for Stable Diffusion models
-  At least 20GB available storage space

**Software Requirements:**
- Python 3.8 or higher installed: `python3 --version`
- pip package manager available: `pip3 --version`
- CUDA toolkit compatible with Blackwell: `nvcc --version`
- Git version control: `git --version`
- Network access to download models from Hugging Face
- Web browser access to `<SPARK_IP>:8188` port

# Ancillary files

All required assets can be found [in the ComfyUI repository on GitHub](https://github.com/comfyanonymous/ComfyUI)

- `requirements.txt` - Python dependencies for ComfyUI installation
- `main.py` - Primary ComfyUI server application entry point
- `v1-5-pruned-emaonly-fp16.safetensors` - Stable Diffusion 1.5 checkpoint model

# Time & risk

* **Estimated time:** 30-45 minutes (including model download)
* **Risk level:** Medium
  * Model downloads are large (~2GB) and may fail due to network issues
  * Port 8188 must be accessible for web interface functionality
* **Rollback:** Virtual environment can be deleted to remove all installed packages. Downloaded models can be removed manually from the checkpoints directory.
* **Last Updated:** 11/10/2025
  * Update ComfyUI PyTorch to CUDA 13.0
 
