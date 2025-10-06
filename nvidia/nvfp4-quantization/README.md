# Quantize to NVFP4

> Quantize a model to NVFP4 to run on Spark

## Table of Contents

- [Overview](#overview)
  - [NVFP4 on Blackwell](#nvfp4-on-blackwell)
- [Desktop Access](#desktop-access)

---

## Overview

## Basic Idea

### NVFP4 on Blackwell

- **What it is:** A new 4-bit floating-point format for NVIDIA Blackwell GPUs.
- **How it works:** Uses two levels of scaling (local per-block + global tensor) to keep accuracy while using fewer bits.
- **Why it matters:**
  - Cuts memory use ~3.5× vs FP16 and ~1.8× vs FP8
  - Keeps accuracy close to FP8 (usually <1% loss)
  - Improves speed and energy efficiency for inference
- **Ecosystem:** Supported in NVIDIA tools (TensorRT, LLM Compressor, vLLM) and Hugging Face models.


## What you'll accomplish

You'll quantize the DeepSeek-R1-Distill-Llama-8B model using NVIDIA's TensorRT Model Optimizer
inside a TensorRT-LLM container, producing an NVFP4 quantized model for deployment on NVIDIA DGX Spark.


## What to know before starting

- Working with Docker containers and GPU-accelerated workloads
- Understanding of model quantization concepts and their impact on inference performance
- Experience with NVIDIA TensorRT and CUDA toolkit environments
- Familiarity with Hugging Face model repositories and authentication

## Prerequisites

- NVIDIA Spark device with Blackwell architecture GPU
- Docker installed with GPU support
- NVIDIA Container Toolkit configured
- At least 32GB of available storage for model files and outputs
- Hugging Face account with access to the target model

Verify your setup:
```bash
## Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:12.0-base-ubuntu20.04 nvidia-smi

## Verify sufficient disk space
df -h .

## Check Hugging Face CLI (install if needed: pip install huggingface_hub)
huggingface-cli whoami
```



## Time & risk

**Estimated duration**: 45-90 minutes depending on network speed and model size

**Risks**:
- Model download may fail due to network issues or Hugging Face authentication problems
- Quantization process is memory-intensive and may fail on systems with insufficient GPU memory
- Output files are large (several GB) and require adequate storage space

**Rollback**: Remove the output directory and any pulled Docker images to restore original state.

## Desktop Access

## Step 1. Prepare the environment

Create a local output directory where the quantized model files will be stored. This directory will be mounted into the container to persist results after the container exits.

```bash
mkdir -p ./output_models
chmod 755 ./output_models
```

## Step 2. Authenticate with Hugging Face

Ensure you have access to the DeepSeek model by logging in to Hugging Face. If you don't have the CLI installed, install it first.

```bash
## Install Hugging Face CLI if needed
pip install huggingface_hub

## Login to Hugging Face
huggingface-cli login
```

Enter your Hugging Face token when prompted. The token will be cached in `~/.cache/huggingface/token`.

## Step 3. Run the TensorRT Model Optimizer container

Launch the TensorRT-LLM container with GPU access, IPC settings optimized for multi-GPU workloads, and volume mounts for model caching and output persistence.

```bash
docker run --rm -it --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 \
  -v "$(pwd)/output_models:/workspace/outputs" \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  nvcr.io/nvidia/tensorrt-llm/release:1.1.0rc3 \
  bash -c "git clone --single-branch https://github.com/NVIDIA/TensorRT-Model-Optimizer.git /app/TensorRT-Model-Optimizer && \
  cd /app/TensorRT-Model-Optimizer && pip install -e '.[dev]' && \
  export ROOT_SAVE_PATH='/workspace/outputs' && \
  time /app/TensorRT-Model-Optimizer/examples/llm_ptq/scripts/huggingface_example.sh --model 'deepseek-ai/DeepSeek-R1-Distill-Llama-8B' --quant nvfp4 --tp 1 --export_fmt hf"
```

This command:
- Runs the container with full GPU access and optimized shared memory settings
- Mounts your output directory to persist quantized model files
- Mounts your Hugging Face cache to avoid re-downloading the model
- Clones and installs the TensorRT Model Optimizer from source
- Executes the quantization script with NVFP4 quantization parameters

## Step 4. Monitor the quantization process

The quantization process will display progress information including:
- Model download progress from Hugging Face
- Quantization calibration steps
- Model export and validation phases
- Total execution time

Expected output includes lines similar to:
```
Downloading model...
Starting quantization...
Calibrating with NVFP4...
Exporting to Hugging Face format...
```

## Step 5. Validate the quantized model

After the container completes, verify that the quantized model files were created successfully.

```bash
## Check output directory contents
ls -la ./output_models/

## Verify model files are present
find ./output_models/ -name "*.bin" -o -name "*.safetensors" -o -name "config.json"
```

You should see model weight files, configuration files, and tokenizer files in the output directory.

## Step 6. Test model loading

Verify the quantized model can be loaded properly using a simple Python test.

```bash
## Create test script
cat > test_model.py << 'EOF'
import os
from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = "./output_models"
try:
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    print(f"✓ Model loaded successfully from {model_path}")
    print(f"Model config: {model.config}")
except Exception as e:
    print(f"✗ Error loading model: {e}")
EOF

## Run the test
python test_model.py
```

## Step 7. Troubleshooting

| Symptom | Cause | Fix |
|---------|--------|-----|
| "Permission denied" when accessing Hugging Face | Missing or invalid HF token | Run `huggingface-cli login` with valid token |
| Container exits with CUDA out of memory | Insufficient GPU memory | Reduce batch size or use a machine with more GPU memory |
| Model files not found in output directory | Volume mount failed or wrong path | Verify `$(pwd)/output_models` resolves correctly |
| Git clone fails inside container | Network connectivity issues | Check internet connection and retry |
| Quantization process hangs | Container resource limits | Increase Docker memory limits or use --ulimit flags |

## Step 8. Cleanup and rollback

To clean up the environment and remove generated files:

> **Warning:** This will permanently delete all quantized model files and cached data.

```bash
## Remove output directory and all quantized models
rm -rf ./output_models

## Remove Hugging Face cache (optional)
rm -rf ~/.cache/huggingface

## Remove Docker image (optional)
docker rmi nvcr.io/nvidia/tensorrt-llm/release:1.1.0rc3
```

## Step 9. Next steps

The quantized model is now ready for deployment. Common next steps include:
- Benchmarking inference performance compared to the original model
- Integrating the quantized model into your inference pipeline
- Deploying to NVIDIA Triton Inference Server for production serving
- Running additional validation tests on your specific use cases
