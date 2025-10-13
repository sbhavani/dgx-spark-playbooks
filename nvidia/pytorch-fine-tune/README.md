# Fine tune with Pytorch

> Use Pytorch to fine-tune models locally

## Table of Contents

- [Overview](#overview)
- [Instructions](#instructions)
- [Troubleshooting](#troubleshooting)

---

## Overview

## Basic idea

This playbook guides you through setting up and using Pytorch for fine-tuning large language models on NVIDIA Spark devices.

## What you'll accomplish

You'll establish a complete fine-tuning environment for large language models (1-70B parameters) on your NVIDIA Spark device. 
By the end, you'll have a working installation that supports parameter-efficient fine-tuning (PEFT) and supervised fine-tuning (SFT).

## What to know before starting

- Previous experience with fine-tuning in Pytorch
- Working with Docker



## Prerequisites
Recipes are specifically for DIGITS SPARK. Please make sure that OS and drivers are latest.


## Ancillary files

ALl files required for fine-tuning are included in the folder in [the GitHub repository here](https://github.com/NVIDIA/dgx-spark-playbooks/blob/main/nvidia/pytorch-fine-tune).

## Time & risk

* **Time estimate:** 30-45 mins for setup and runing fine-tuning. Fine-tuning run time varies depending on model size 
* **Risks:** Model downloads can be large (several GB), ARM64 package compatibility issues may require troubleshooting.

## Instructions

## Step 1. Configure Docker permissions

To easily manage containers without sudo, you must be in the `docker` group. If you choose to skip this step, you will need to run Docker commands with sudo.

Open a new terminal and test Docker access. In the terminal, run:

```bash
docker ps
```

If you see a permission denied error (something like permission denied while trying to connect to the Docker daemon socket), add your user to the docker group so that you don't need to run the command with sudo .

```bash
sudo usermod -aG docker $USER
newgrp docker
```

## Step 2.  Pull the latest Pytorch container

```bash
docker pull nvcr.io/nvidia/pytorch:25.09-py3
```

## Step 3. Launch Docker

```bash
docker run --gpus all -it --rm --ipc=host \
-v $HOME/.cache/huggingface:/root/.cache/huggingface \
-v ${PWD}:/workspace -w /workspace \
nvcr.io/nvidia/pytorch:25.09-py3
```

## Step 4. Install dependencies inside the container

```bash
pip install transformers peft datasets "trl==0.19.1" "bitsandbytes==0.48"
```

## Step 5: Authenticate with Huggingface

```bash
huggingface-cli login
##<input your huggingface token.
##<Enter n for git credential>
```

## Step 6:  Clone the git repo with fine-tuning recipes

```bash
git clone https://github.com/NVIDIA/dgx-spark-playbooks
cd nvidia/pytorch-fine-tune/assets
```

## Step7: Run the fine-tuning recipes

To run LoRA on Llama3-8B use the following command:
```bash
python Llama3_8B_LoRA_finetuning.py
```

To run qLoRA fine-tuning on llama3-70B use the following command:
```bash
python Llama3_70B_qLoRA_finetuning.py
```

To run full fine-tuning on llama3-3B use the following command:
```bash
python Llama3_3B_full_finetuning.py
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|--------|-----|
| Cannot access gated repo for URL | Certain HuggingFace models have restricted access | Regenerate your [HuggingFace token](https://huggingface.co/docs/hub/en/security-tokens); and request access to the [gated model](https://huggingface.co/docs/hub/en/models-gated#customize-requested-information) on your web browser |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
