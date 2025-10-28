# Basic idea

This playbook demonstrates how to fine-tune Vision-Language Models (VLMs) for both image and video understanding tasks on DGX Spark. 
With 128GB of unified memory and powerful GPU acceleration, DGX Spark provides an ideal environment for training VRAM-intensive multimodal models that can understand and reason about visual content.

The playbook covers two distinct VLM fine-tuning approaches:
- **Image VLM Fine-tuning**: Using Qwen2.5-VL-7B for wildfire detection from satellite imagery with GRPO (Generalized Reward Preference Optimization)
- **Video VLM Fine-tuning**: Using InternVL3 8B for dangerous driving detection and structured metadata generation from driving videos

Both approaches leverage advanced training techniques, including LoRA fine-tuning, preference optimization, and structured reasoning to achieve superior performance on specialized tasks.

# What you'll accomplish

You will have fine-tuned VLM models capable of understanding and analyzing both images and videos for specialized use cases, accessible through interactive Web UIs.
The setup includes:
- **Image VLM**: Qwen2.5-VL fine-tuned for wildfire detection with reasoning capability
- **Video VLM**: InternVL3 fine-tuned for dangerous driving analysis and structured metadata generation
- Interactive Streamlit interfaces for both training and inference
- Side-by-side model comparison (base vs fine-tuned) in the Web UIs
- Docker containerization for reproducible environments

# Prerequisites

-  DGX Spark device is set up and accessible
-  No other processes running on the DGX Spark GPU
-  Enough disk space for model downloads and datasets
-  NVIDIA Docker installed and configured
-  Weights & Biases account for training monitoring (optional but recommended)


# Time & risk

* **Duration**:
* 15-20 minutes for initial setup and model downloads
* 30-60 minutes for image VLM training (depending on dataset size)
* 1-2 hours for video VLM training (depending on video dataset size)
* **Risks**:
* Docker permission issues may require user group changes and a session restart
* Large model downloads and datasets may require significant disk space and time
* Training requires sustained GPU usage and memory
* Dataset preparation may require manual steps (Kaggle downloads, video processing)
* **Rollback**: Stop and remove Docker containers, delete downloaded models and datasets if needed.
