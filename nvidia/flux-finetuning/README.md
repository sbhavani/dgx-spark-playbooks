# FLUX.1 Dreambooth LoRA Fine-tuning

> Fine-tune FLUX.1-dev 11B model using multi-concept Dreambooth LoRA for custom image generation

## Table of Contents

- [Overview](#overview)
- [Instructions](#instructions)

---

## Overview

## Basic Idea

This playbook demonstrates how to fine-tune the FLUX.1-dev 11B model using multi-concept Dreambooth LoRA (Low-Rank Adaptation) for custom image generation on DGX Spark. 
With 128GB of unified memory and powerful GPU acceleration, DGX Spark provides an ideal environment for training an image generation model with multiple models loaded in memory, such as the Diffusion Transformer, CLIP Text Encoder, T5 Text Encoder, and the Autoencoder.

Multi-concept Dreambooth LoRA fine-tuning allows you to teach FLUX.1 new concepts, characters, and styles. The trained LoRA weights can be easily integrated into existing ComfyUI workflows, making it perfect for prototyping and experimentation.
Moreover, this playbook demonstrates how DGX Spark can not only load several models in memory, but also run train and generate high-resolution images such as 1024px and higher.

## What you'll accomplish

You will have a fine-tuned FLUX.1 model capable of generating images with your custom concepts, readily available for ComfyUI workflows.
The setup includes:
- FLUX.1-dev model fine-tuning using Dreambooth LoRA technique
- Training on custom concepts ("tjtoy" toy and "sparkgpu" GPU)
- High-resolution 1K diffusion training and inference
- ComfyUI integration for intuitive visual workflows
- Docker containerization for reproducible environments

## Prerequisites

-  DGX Spark device is set up and accessible
-  No other processes running on the DGX Spark GPU
-  Enough disk space for model downloads
-  NVIDIA Docker installed and configured


## Time & risk

**Duration**:
- 15 minutes for initial setup model download time
- 1-2 hours for dreambooth lora training

**Risks**:
- Docker permission issues may require user group changes and session restart
- The recipe would require hyperparameter tuning and a high-quality dataset for the best results

**Rollback**: Stop and remove Docker containers, delete downloaded models if needed

## Instructions

## Step 1. Configure Docker permissions

To easily manage containers without sudo, you must be in the `docker` group. If you choose to skip this step, you will need to run Docker commands with sudo.

Open a new terminal and test Docker access. In the terminal, run:

```bash
docker ps
```

If you see a permission denied error (something like `permission denied while trying to connect to the Docker daemon socket`), add your user to the docker group:

```bash
sudo usermod -aG docker $USER
```

> **Warning**: After running usermod, you must log out and log back in to start a new
> session with updated group permissions.

## Step 2. Clone the repository

In a terminal, clone the repository and navigate to the flux-finetuning directory.

```bash
git clone https://******/spark-playbooks/dgx-spark-playbook-assets.git
cd dgx-spark-playbook-assets/flux-finetuning
```

## Step 3. Build the Docker container

This docker image will download the required models and set up the environment for training and inference.
- `flux1-dev.safetensors`
- `ae.safetensors`
- `clip_l.safetensors`
- `t5xxl_fp16.safetensors`
```bash
docker build -t flux-training .
```

## Step 4. Run the Docker container

```bash
## Run with GPU support and mount current directory
docker run --gpus all -it --rm \
    -v $(pwd):/workspace \
    -p 8188:8188 \
    flux-training
```

## Step 5. Train the model

Inside the container, navigate to the sd-scripts directory and run the training script:

```bash
cd /workspace/sd-scripts
../train.sh
```

The training will:
- Use LoRA with dimension 256
- Train for 100 epochs (saves every 25 epochs)
- Learn custom concepts: "tjtoy toy" and "sparkgpu gpu"
- Output trained LoRA weights to `saved_models/flux_dreambooth.safetensors`

## Step 6. Generate images with command-line inference

After training completes, generate sample images:

```bash
../inference.sh
```

This will generate several images demonstrating the learned concepts, stored in the `outputs` directory.

## Step 7. Spin up ComfyUI for visual workflows

Start ComfyUI for an intuitive interface:

```bash
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

Access ComfyUI at `http://localhost:8188`

## Step 8. Deploy the trained LoRA in ComfyUI

Feel free to deploy the trained LoRA in ComfyUI in existing or custom workflows.
Use your trained concepts in prompts:
- `"tjtoy toy"` - Your custom toy concept
- `"sparkgpu gpu"` - Your custom GPU concept
- `"tjtoy toy holding sparkgpu gpu"` - Combined concepts

## Step 9. Cleanup

Exit the container and optionally remove the Docker image:

```bash
## Exit container
exit

## Remove Docker image (optional)
docker stop <container_id>
docker rmi flux-training
```

## Step 10. Next steps

- Experiment with different LoRA strengths (0.8-1.2) in ComfyUI
- Train on your own custom concepts by replacing images in the `data/` directory
- Combine multiple LoRA models for complex compositions
- Integrate the trained LoRA into other FLUX workflows
