# Vision-Language Model Fine-tuning

> Fine-tune Vision-Language Models for image and video understanding tasks using Qwen2.5-VL and InternVL3

## Table of Contents

- [Overview](#overview)
- [Instructions](#instructions)
- [Troubleshooting](#troubleshooting)

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
git clone https://gitlab.com/nvidia/dgx-spark/temp-external-playbook-assets/dgx-spark-playbook-assets
```

## Step 3. Build the Docker container

Build the Docker image. This will set up the environment for both image and video VLM fine-tuning.
Please export your Hugging Face token as an environment variable - `HF_TOKEN`. You may encounter warnings when building the image. This is expected and can be ignored.

```bash
## Enter the correct directory for building the image
cd dgx-spark-playbooks/nvidia/vlm-finetuning/assets

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

#### 5.2. Download the wildfire dataset

The project uses a **Wildfire Detection Dataset** with satellite imagery for training the model to identify wildfire-affected regions. The dataset includes:
- Satellite and aerial imagery from wildfire-affected areas
- Binary classification: wildfire vs no wildfire

```bash
mkdir -p ui_image/data
cd ui_image/data
```

For this fine-tuning playbook, we will use the [Wildfire Prediction Dataset](https://www.kaggle.com/datasets/abdelghaniaaba/wildfire-prediction-dataset) from Kaggle. Visit the kaggle dataset page [here](https://www.kaggle.com/datasets/abdelghaniaaba/wildfire-prediction-dataset) to click the download button. Select the `cURL` option in the `Download Via` dropdown and copy the curl command. 

> **Note**: You will need to be logged into Kaggle and may need to accept the dataset terms before the download link works.

Run the following commands in your container:

```bash
## Paste and run the curl command from Kaggle here, and then continue to unzip the dataset

unzip -qq wildfire-prediction-dataset.zip
rm wildfire-prediction-dataset.zip
cd ..
```

#### 5.3. Base model inference

Before we start fine-tuning, let's spin up the demo UI to evaluate the base model's performance on this task.

```bash
streamlit run Image_VLM.py
```

Access the streamlit demo at http://localhost:8501/.

When you access the streamlit demo for the first time, the backend triggers vLLM servers to spin up for the base model. You will see a spinner on the demo site as vLLM is being brought up for optimized inference. This step can take up to 15 mins.

Since we are currently focused on inferring the base model, let's scroll down to the `Image Inference` section of the UI. Here, you should see a sample pre-loaded satellite image of a potentially wildfire-affected region.

Enter your prompt in the chat box and hit `Generate`. Your prompt would be first sent to the base model and you should see the generation response on the left chat box. If you did not provide a fine-tuned model, you should not see any generations from the right chat box. You can use the following prompt to quickly test inference:

`Identify if this region has been affected by a wildfire`

As you can see, the base model is incapable of providing the right response for this domain-specific task. Let's try to improve the model's accuracy by performing GRPO fine-tuning.

#### 5.4. GRPO fine-tuning

We will perform GRPO fine-tuning to add reasoning capabilities to our base model and improve the model's understanding of the underlying domain. Considering that you have already spun up the streamlit demo, scroll to the `GRPO Training section`.

Configure the finetuning method and lora parameters based on the following options.

- `Finetuning Method`: Choose from Full Finetuning or LoRA
- `LoRA Parameters`: Adjustable rank (8-64) and alpha (8-64)

You can additionally choose whether the layers you want to fine-tune in the VLM. For the best performance, ensure that all options are toggled on. Note that this will increase the model training time as well.

In this section, we can select certain model parameters as relevant to our training run.

- `Steps`: 1-1000
- `Batch Size`: 1, 2, 4, 8, or 16
- `Learning Rate`: 1e-6 to 1e-2
- `Optimizer`: AdamW or Adafactor

For a GRPO setup, we also have the flexibility in choosing the reward that is assigned to the model based on certain criteria

- `Format Reward`: 2.0 (reward for proper reasoning format)
- `Correctness Reward`: 5.0 (reward for correct answers)
- `Number of Generations`: 4 (for preference optimization)

After configuring all the parameters, hit `Start Finetuning` to begin the training process. You will need to wait about 15 minutes for the model to load and start recording metadata on the UI. As the training progresses, information such as the loss, step, and GRPO rewards will be recorded on a live table.

The default loaded configuration should give you reasonable accuracy, taking 100 steps of training over a period of up to 2 hours. We achieved our best accuracy with around 1000 steps of training, taking close to 16 hours.

After training is complete, the script automatically merges LoRA weights into the base model. After the training process has reached the desired number of training steps, it can take 5 mins to merge the LoRA weights.

If you wish to stop training, just hit the `Stop Finetuning` button. Please use this button only to interrupt training. This button does not guarantee that the checkpoints will be properly stored or merged with lora adapter layers.

Once you stop training, the UI will automatically bring up the vLLM servers for the base model and the newly fine-tuned model.

#### 5.5. Fine-tuned model inference

Now we are ready to perform a comparative analysis between the base model and the fine-tuned model. 

If you haven't spun up the streamlit demo already, execute the following command. If had just just stopped training and are still within the live UI, skip this step.

```bash
streamlit run Image_VLM.py
```

Regardless of whether you just spun up the demo or just stopped training, please wait about 15 minutes for the vLLM servers to be brought up.

Scroll down to the `Image Inference` section and enter your prompt in the provided chat box. Upon clicking `Generate` your prompt will be first sent to the base model and then to the fine-tuned model. You can use the following prompt to quickly test inference:

`Identify if this region has been affected by a wildfire`

If you trained your model sufficiently, you should see that the fine-tuned model is able to perform reasoning and provide a concise, accurate answer to the prompt. The reasoning steps are provided in the markdown format, while the final answer is bolded and provided at the end of the model's response.

## Step 6. [Option B] For video VLM fine-tuning (Driver Behaviour Analysis)

Within the same container, navigate to the `ui_video` directory.

```bash
cd /vlm_finetuning/ui_video
```

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

> **Note**: These instructions assume you are already inside the Docker container. For container setup, refer to the section above to `Build the Docker container`.

```bash
hf download OpenGVLab/InternVL3-8B
```

#### 6.3. Base model inference

Before going ahead to fine-tune our video VLM for this task, let's see how the base InternVL3-8B does.

```bash
## cd into /vlm_finetuning/ui_video if you haven't already
streamlit run Video_VLM.py
```

Access the streamlit demo at http://localhost:8501/.

When you access the streamlit demo for the first time, the backend triggers Huggingface to spin up the base model. You will see a spinner on the demo site as the model is being loaded, which can take up to 10 minutes.

First, let's select a video from our dashcam gallery. Upon clicking the green file open icon near a video, you should see the video render and play automatically for our reference.

Scroll down, enter your prompt in the chat box and hit `Generate`. Your prompt would be first sent to the base model and you should see the generation response on the left chat box. If you did not provide a finetuned model, you should not see any generations from the right chat box. You can use the following prompt to quickly test inference:

`Analyze the dashcam footage for unsafe driver behavior`

If you are proceeding to train a fine-tuned model, ensure that the streamlit demo UI is brought down before proceeding to train. You can bring it down by interrupting the terminal with `Ctrl+C` keystroke.

> **Note**: To clear out any extra occupied memory from your system, execute the following command outside the container after interrupting the ComfyUI server.
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```

#### 6.4. Run the training notebook

```bash
## Enter the correct directory
cd train

## Start Jupyter Lab
jupyter notebook video_vlm.ipynb
```
Access Jupyter at `http://localhost:8888`. Ensure that you set the path to your dataset correctly in the appropriate cell.

```python
dataset_path = "/path/to/your/dataset"
```

Here are some of the key training parameters that are configurable. Please note that for reasonable quality, you will need to train your video VLM for atleast 24 hours given the complexity of processing spatio-temporal video sequences.

- **Model**: InternVL3-8B
- **Video Frames**: 12 to 16 frames per video
- **Sampling Mode**: Uniform temporal sampling
- **LoRA Configuration**: Efficient parameter updates for large-scale fine-tuning
- **Hyperparameters**: Exhaustive suite of hyperparameters to tune for video VLM fine-tuning

You can monitor and evaluate the training progress and metrics, as they will be continuously shown in the notebook.

After training, ensure that you shutdown the jupyter kernel in the notebook and kill the jupyter server in the terminal with a `Ctrl+C` keystroke.

> **Note**: To clear out any extra occupied memory from your system, execute the following command outside the container after interrupting the ComfyUI server.
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
#### 6.5. Fine-tuned model inference

Now we are ready to perform a comparative analysis between the base model and the fine-tuned model. 

If you haven't spun up the streamlit demo already, execute the following command. If you have just stopped training and are still within the live UI, skip to the next step.

```bash
## cd back to /vlm_finetuning/ui_video if you haven't already
streamlit run Video_VLM.py
```

Access the streamlit demo at http://localhost:8501/.

If you trained your model sufficiently, you should see that the fine-tuned model is able to identify the salient events from the video and generate a structured output.

Since the model's output adheres to the schema we trained, we can directly export the model's prediction into a database for video analytics.

Feel free to play around with additional videos available in the gallery.

## Troubleshooting

> **Note:** DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
