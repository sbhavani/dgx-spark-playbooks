# Fine tune with Pytorch

> Use Pytorch to fine-tune models locally

## Table of Contents

- [Overview](#overview)
- [Instructions](#instructions)

---

## Overview

## Basic Idea

This playbook guides you through setting up and using Pytorch for fine-tuning large language models on NVIDIA Spark devices.

## What you'll accomplish

You'll establish a complete fine-tuning environment for large language models (1-70B parameters) on your NVIDIA Spark device. By the end, you'll have a working installation that supports parameter-efficient fine-tuning (PEFT) and supervised fine-tuning (SFT)
## What to know before starting



## Prerequisites
recipes are specifically for DIGITS SPARK. Please make sure that OS and drivers are latest.


## Ancillary files

ALl files required for finetuning are included.

## Time & risk

**Time estimate:** 30-45 mins for setup and runing finetuning. Finetuning run time varies depending on model size 

**Risks:** Model downloads can be large (several GB), ARM64 package compatibility issues may require troubleshooting.

**Rollback:**

## Instructions

## Step 1.  Pull the latest Pytorch container

```bash
docker pull nvcr.io/nvidia/pytorch:25.09-py3
```

## Step 2. Launch Docker

```bash
docker run --gpus all -it --rm --ipc=host \
-v $HOME/.cache/huggingface:/root/.cache/huggingface \
-v ${PWD}:/workspace -w /workspace \
nvcr.io/nvidia/pytorch:25.09-py3

```

## Step 3. Install dependencies inside the contianer

```bash
pip install transformers peft datasets "trl==0.19.1" "bitsandbytes==0.48"
```

## Step 4: authenticate with huggingface

```bash
huggingface-cli login
##<input your huggingface token.
##<Enter n for git credential>

```
To run LoRA on Llama3 use the following command:

```bash
python Llama3_8B_LoRA_finetuning.py
```

To run qLoRA finetuning on llama3-70B use the following command:
```bash
python Llama3_70B_qLoRA_finetuning.py
```
To run full finetuning on llama3-3B use the following command:
```bash
python Llama3_3B_full_finetuning.py
```
