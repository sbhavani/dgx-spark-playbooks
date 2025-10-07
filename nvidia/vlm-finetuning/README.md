# Vision-Language Model Fine-tuning

> Fine-tune Vision-Language Models for image and video understanding tasks using Qwen2.5-VL and InternVL3

## Table of Contents

- [Overview](#overview)
- [Instructions](#instructions)

---

## Overview

## Basic idea

This playbook demonstrates how to fine-tune Vision-Language Models (VLMs) for both image and video understanding tasks on DGX Spark. 
With 128GB of unified memory and powerful GPU acceleration, DGX Spark provides an ideal environment for training VRAM-intensive multimodal models that can understand and reason about visual content.

The playbook covers two distinct VLM fine-tuning approaches:
- **Image VLM Fine-tuning**: Using Qwen2.5-VL-7B for wildfire detection from satellite imagery with GRPO (Generalized Reward Preference Optimization)
- **Video VLM Fine-tuning**: Using InternVL3 8B for dangerous driving detection and structured metadata generation from driving videos

Both approaches leverage advanced training techniques, including LoRA fine-tuning, preference optimization, and structured reasoning to achieve superior performance on specialized tasks.

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
- Docker permission issues may require user group changes and a session restart
- Large model downloads and datasets may require significant disk space and time
- Training requires sustained GPU usage and memory
- Dataset preparation may require manual steps (Kaggle downloads, video processing)

**Rollback**: Stop and remove Docker containers, delete downloaded models and datasets if needed.

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
## Enter the correct directory for building the image
cd vlm-finetuning/assets

## Build the VLM fine-tuning container
docker build --build-arg HF_TOKEN=$HF_TOKEN -t vlm_demo .
```

## Step 4. Run the Docker container

```bash
## Run the container with GPU support
sh launch.sh

## Enter the mounted directory within the container
cd /vlm_finetuning
```
**Note**: The same Docker container and launch commands work for both image and video VLM recipes. The container features all necessary dependencies, including FFmpeg, Decord, and optimized libraries for both workflows.

## Step 5. [Option A] For image VLM fine-tuning (Wildfire Detection)

#### 5.1. Model download

```bash
hf download Qwen/Qwen2.5-VL-7B-Instruct
```

If you already have a fine-tuned checkpoint, place it in the `saved_model/` folder. Note that your checkpoint number can be different. For a comparative analysis against the base model, skip directly to the `Finetuned Model Inference` section.

#### 5.2. Download the wildfire dataset from Kaggle and place it in the `data` directory

The wildfire dataset can be found here: https://www.kaggle.com/datasets/abdelghaniaaba/wildfire-prediction-dataset.

#### 5.3. Base model inference

Before we start fine-tuning, let's spin up the demo UI to evaluate the base model's performance on this task.

```bash
streamlit run Image_VLM.py
```

Access the streamlit demo at http://localhost:8501/.

When you access the streamlit demo for the first time, the backend triggers vLLM servers to spin up for the base model. You will see a spinner on the demo site as vLLM is being brought up for optimized inference. This step can take up to 15 mins.

#### 5.4. GRPO fine-tuning

We will perform GRPO fine-tuning to add reasoning capabilities to our base model and improve the model's understanding of the underlying domain. Considering that you have already spun up the streamlit demo, scroll to the `GRPO Training section`.

After configuring all the parameters, hit `Start Finetuning` to begin the training process. You will need to wait about 15 minutes for the model to load and start recording metadata on the UI. As the training progresses, information such as the loss, step, and GRPO rewards will be recorded on a live table.

The default loaded configuration should give you reasonable accuracy, taking 100 steps of training over a period of up to 2 hours. We achieved our best accuracy with around 1000 steps of training, taking close to 16 hours.

After training is complete, the script automatically merges LoRA weights into the base model. After the training process has reached the desired number of training steps, it can take 5 mins to merge the LoRA weights.

Once you stop training, the UI will automatically bring up the vLLM servers for the base model and the newly fine-tuned model.

#### 5.5. Fine-tuned model inference

Now we are ready to perform a comparative analysis between the base model and the fine-tuned model. 

Regardless of whether you just spun up the demo or just stopped training, please wait about 15 minutes for the vLLM servers to be brought up.

Scroll down to the `Image Inference` section and enter your prompt in the provided chat box. 
Upon clicking `Generate` your prompt will be first sent to the base model and then to the fine-tuned model. You can use the following prompt to quickly test inference:

`Identify if this region has been affected by a wildfire`

If you trained your model sufficiently, you should see that the fine-tuned model is able to perform reasoning and provide a concise, accurate answer to the prompt. The reasoning steps are provided in the markdown format, while the final answer is bolded and provided at the end of the model's response.

## Step 6. [Option B] For video VLM fine-tuning (Driver Behaviour Analysis)

#### 6.1. Prepare your video dataset

Structure your dataset as follows. Ensure that `metadata.jsonl` contains rows of structured JSON data about each video.
```
dataset/
├── videos/
│   ├── video1.mp4
│   ├── video2.mp4
│   └── ...
└── metadata.jsonl
```

#### 6.2. Model download

> **Note**: These instructions assume you are already inside the Docker container. For container setup, refer to the main project README at `vlm-finetuning/assets/README.md`.

```bash
hf download OpenGVLab/InternVL3-8B
```

#### 6.3. Base model inference

Before going ahead to finetune our video VLM for this task, let's see how the base InternVL3-8B does.

```bash
## cd into vlm_finetuning/assets/ui_video if you haven't already
streamlit run Video_VLM.py
```

Access the streamlit demo at http://localhost:8501/.

When you access the streamlit demo for the first time, the backend triggers Huggingface to spin up the base model. You will see a spinner on the demo site as the model is being loaded, which can take up to 10 minutes.

First, let's select a video from our dashcam gallery. Upon clicking the green file open icon near a video, you should see the video render and play automatically for our reference.

If you are proceeding to train a fine-tuned model, ensure that the streamlit demo UI is brought down before proceeding to train. You can bring it up by interrupting the terminal with `Ctrl+C` keystroke.

> **Note**: To clear out any extra occupied memory from your system, execute the following command outside the container after interrupting the ComfyUI server.
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```

#### 6.4. Run the training notebook

```bash
## Enter the correct directory
cd /vlm-finetuning/ui_video/train

## Start Jupyter Lab
jupyter notebook video_vlm.ipynb
```
Access Jupyter at `http://localhost:8888`. Ensure that you set the path to your dataset correctly in the appropriate cell.

```python
dataset_path = "/path/to/your/dataset"
```
After training, ensure that you shutdown the jupyter kernel in the notebook and kill the jupyter server in the terminal with a `Ctrl+C` keystroke.

> **Note**: To clear out any extra occupied memory from your system, execute the following command outside the container after interrupting the ComfyUI server.
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
#### 6.5. Fine-tuned model inference

Now we are ready to perform a comparative analysis between the base model and the fine-tuned model. 

If you haven't spun up the streamlit demo already, execute the following command. If you have just stopped training and are still within the live UI, skip to the next step.

```bash
streamlit run Video_VLM.py
```

Access the streamlit demo at http://localhost:8501/.

If you trained your model sufficiently, you should see that the fine-tuned model is able to identify the salient events from the video and generate a structured output. 

Feel free to play around with additional videos available in the gallery.
