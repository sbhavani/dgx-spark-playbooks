# Basic idea

This playbook demonstrates how to fine-tune the FLUX.1-dev 12B model using multi-concept Dreambooth LoRA (Low-Rank Adaptation) for custom image generation on DGX Spark. 
With 128GB of unified memory and powerful GPU acceleration, DGX Spark provides an ideal environment for training an image generation model with multiple models loaded in memory, such as the Diffusion Transformer, CLIP Text Encoder, T5 Text Encoder, and the Autoencoder.

Multi-concept Dreambooth LoRA fine-tuning allows you to teach FLUX.1 new concepts, characters, and styles. The trained LoRA weights can be easily integrated into existing ComfyUI workflows, making it perfect for prototyping and experimentation.
Moreover, this playbook demonstrates how DGX Spark can not only load several models in memory, but also train and generate high-resolution images such as 1024px and higher.

# What you'll accomplish

You will have a fine-tuned FLUX.1 model capable of generating images with your custom concepts, readily available for ComfyUI workflows.
The setup includes:
- FLUX.1-dev model fine-tuning using Dreambooth LoRA technique
- Training on custom concepts ("tjtoy" toy and "sparkgpu" GPU)
- High-resolution 1K diffusion training and inference
- ComfyUI integration for intuitive visual workflows
- Docker containerization for reproducible environments

# Prerequisites

-  DGX Spark device is set up and accessible
-  No other processes running on the DGX Spark GPU
-  Enough disk space for model downloads
-  NVIDIA Docker installed and configured


# Time & risk

* **Duration**:
  * 30-45 minutes for initial setup model download time
  * 1-2 hours for dreambooth LoRA training
* **Risks**:
  * Docker permission issues may require user group changes and session restart
  * The recipe would require hyperparameter tuning and a high-quality dataset for the best results
**Rollback**: Stop and remove Docker containers, delete downloaded models if needed.
