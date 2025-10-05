# Vision-Language Model Fine-tuning

> Fine-tune Vision-Language Models for image and video understanding tasks using Qwen2.5-VL and InternVL3

## Table of Contents

- [Overview](#overview)
- [Instructions](#instructions)
  - [Video VLM Testing](#video-vlm-testing)

---

## Overview

## Basic Idea

This playbook demonstrates how to fine-tune Vision-Language Models (VLMs) for both image and video understanding tasks on DGX Spark. 
With 128GB of unified memory and powerful GPU acceleration, DGX Spark provides an ideal environment for training VRAM intensive multimodal models that can understand and reason about visual content.

The playbook covers two distinct VLM fine-tuning approaches:
- **Image VLM Fine-tuning**: Using Qwen2.5-VL-7B for wildfire detection from satellite imagery with GRPO (Generalized Reward Preference Optimization)
- **Video VLM Fine-tuning**: Using InternVL3 8B for dangerous driving detection and structured metadata generation from driving videos

Both approaches leverage advanced training techniques including LoRA fine-tuning, preference optimization, and structured reasoning to achieve superior performance on specialized tasks.

## What you'll accomplish

You will have fine-tuned VLM models capable of understanding and analyzing both images and videos for specialized use cases, accessible through interactive Web UIs.
The setup includes:
- **Image VLM**: Qwen2.5-VL fine-tuned for wildfire detection with reasoning capability
- **Video VLM**: InternVL3 fine-tuned for dangerous driving analysis and structured metadata generation
- Interactive Streamlit interfaces for both training and inference
- Side-by-side model comparison (base vs fine-tuned) in the Web UIs
- Docker containerization for reproducible environments

## Prerequisites

-  DGX Spark device is set up and accessible
-  No other processes running on the DGX Spark GPU
-  Enough disk space for model downloads and datasets
-  NVIDIA Docker installed and configured
-  Weights & Biases account for training monitoring (optional but recommended)


## Time & risk

**Duration**:
- 15-20 minutes for initial setup and model downloads
- 30-60 minutes for image VLM training (depending on dataset size)
- 1-2 hours for video VLM training (depending on video dataset size)

**Risks**:
- Docker permission issues may require user group changes and session restart
- Large model downloads and datasets may require significant disk space and time
- Training requires sustained GPU usage and memory
- Dataset preparation may require manual steps (Kaggle downloads, video processing)

**Rollback**: Stop and remove Docker containers, delete downloaded models and datasets if needed

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

In a terminal, clone the repository and navigate to the VLM fine-tuning directory.

```bash
git clone https://gitlab.com/nvidia/dgx-spark/temp-external-playbook-assets/dgx-spark-playbook-assets/-/blob/main dgx-spark-playbooks
```

## Step 3. Build the Docker container

Build the Docker image. This will set up the environment for both image and video VLM fine-tuning:

```bash
docker build -t vlm-finetuning .
```

## Step 4. Run the Docker container

```bash
## Run with GPU support and mount current directory
docker run --gpus all -it --rm \
    -v $(pwd):/workspace \
    -p 8501:8501 \
    -p 8888:8888 \
    -p 6080:6080 \
    vlm-finetuning
```

## Step 5. [Option A] For image VLM fine-tuning (Wildfire Detection)
#### 5.1. Set up Weights & Biases

Configure your wandb credentials for training monitoring:

```bash
export WANDB_ENTITY=<your_wandb_username>
export WANDB_PROJECT="vlm_finetuning"
export WANDB_API_KEY=<your_wandb_api_key>
```

#### 5.2. Download the wildfire dataset from Kaggle and place it in the `data` directory

The wildfire dataset can be found here: https://www.kaggle.com/datasets/abdelghaniaaba/wildfire-prediction-dataset

#### 5.3. Launch the Image VLM UI

```bash
cd ui_image
streamlit run Image_VLM_Finetuning.py
```

Access the interface at `http://localhost:8501`

#### 5.4. Configure and start training

- Configure training parameters through the web interface
- Choose fine-tuning method (LoRA, QLoRA, or Full-Finetuning)
- Set hyperparameters (epochs, batch size, learning rate)
- Click "▶️ Start Finetuning" to begin GRPO training
- Monitor progress via embedded wandb charts

#### 5.5. Test the fine-tuned model

After training completes:
1. Bring down the UI with Ctrl+C
2. Edit `src/image_vlm_config.yaml` and update `finetuned_model_id` to point to your model in `saved_model/`
3. Restart the interface to test your fine-tuned model

## Step 6. [Option B] For video VLM fine-tuning (Driver Behaviour Analysis)

#### 6.1. Prepare your video dataset

Structure your dataset as follows:
```
dataset/
├── videos/
│   ├── video1.mp4
│   ├── video2.mp4
│   └── ...
└── metadata.jsonl
```

#### 6.2. Start Jupyter Lab

```bash
jupyter lab --ip=0.0.0.0 --port=8888 --allow-root
```

Access Jupyter at `http://localhost:8888`

#### 6.3. Run the training notebook

```bash
cd ui_video/train
## Open and run internvl3_dangerous_driving.ipynb
## Update dataset path in the notebook to point to your data
```

#### 6.4. Run inference

### Video VLM Testing
- Use the inference notebook to test on dashcam footage videos
- Generate structured JSON metadata for dangerous driving events
- Analyze traffic violations and safety risks

## Step 7. Cleanup

Exit the container and optionally remove the Docker image:

```bash
## Exit container
exit

## Remove Docker image (optional)
docker stop <container_id>
docker rmi vlm-finetuning
```

## Step 8. Next steps

- Train on your own custom datasets for specialized use cases
- Combine multiple VLM models for comprehensive multimodal analysis
- Explore other VLM architectures and training techniques
- Deploy fine-tuned models in production environments
