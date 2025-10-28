# Basic idea

NVFP4 is a 4-bit floating-point format introduced with NVIDIA Blackwell GPUs to maintain model accuracy while reducing memory bandwidth and storage requirements for inference workloads. 
Unlike uniform INT4 quantization, NVFP4 retains floating-point semantics with a shared exponent and a compact mantissa, allowing higher dynamic range and more stable convergence.
NVIDIA Blackwell Tensor Cores natively support mixed-precision execution across FP16, FP8, and FP4, enabling models to use FP4 for weights and activations while accumulating in higher precision (typically FP16). 
This design minimizes quantization error during matrix multiplications and supports efficient conversion pipelines in TensorRT-LLM for fine-tuned layer-wise quantization.

Immediate benefits are:
- Cut memory use ~3.5x vs FP16 and ~1.8x vs FP8
- Maintain accuracy close to FP8 (usually <1% loss)
- Improve speed and energy efficiency for inference


# What you'll accomplish

You'll quantize the DeepSeek-R1-Distill-Llama-8B model using NVIDIA's TensorRT Model Optimizer
inside a TensorRT-LLM container, producing an NVFP4 quantized model for deployment on NVIDIA DGX Spark.

The examples use NVIDIA FP4 quantized models which help reduce model size by approximately 2x by reducing the precision of model layers.
This quantization approach aims to preserve accuracy while providing significant throughput improvements. However, it's important to note that quantization can potentially impact model accuracy - we recommend running evaluations to verify if the quantized model maintains acceptable performance for your use case.

# What to know before starting

- Working with Docker containers and GPU-accelerated workloads
- Understanding of model quantization concepts and their impact on inference performance
- Experience with NVIDIA TensorRT and CUDA toolkit environments
- Familiarity with Hugging Face model repositories and authentication

# Prerequisites

- NVIDIA Spark device with Blackwell architecture GPU
- Docker installed with GPU support
- NVIDIA Container Toolkit configured
- Available storage for model files and outputs
- Hugging Face account with access to the target model

Verify your setup:
```bash
# Check Docker GPU access
docker run --rm --gpus all nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev nvidia-smi

# Verify sufficient disk space
df -h .
```

# Time & risk

* **Estimated duration**: 45-90 minutes depending on network speed and model size
* **Risks**:
* Model download may fail due to network issues or Hugging Face authentication problems
* Quantization process is memory-intensive and may fail on systems with insufficient GPU memory
* Output files are large (several GB) and require adequate storage space
* **Rollback**: Remove the output directory and any pulled Docker images to restore original state.
