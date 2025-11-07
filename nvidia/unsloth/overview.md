# Basic idea

- **Performance-first**: It claims to speed up training (e.g. 2× faster on single GPU, up to 30× in multi-GPU setups) and reduce memory usage compared to standard methods.   
- **Kernel-level optimizations**: Core compute is built with custom kernels (e.g. with Triton) and hand-optimized math to boost throughput and efficiency.  
- **Quantization & model formats**: Supports dynamic quantization (4-bit, 16-bit) and GGUF formats to reduce footprint, while aiming to retain accuracy.    
- **Broad model support**: Works with many LLMs (LLaMA, Mistral, Qwen, DeepSeek, etc.) and allows training, fine-tuning, exporting to formats like Ollama, vLLM, GGUF, Hugging Face.   
- **Simplified interface**: Provides easy-to-use notebooks and tools so users can fine-tune models with minimal boilerplate.  

# What you'll accomplish

You'll set up Unsloth for optimized fine-tuning of large language models on NVIDIA Spark devices, 
achieving up to 2x faster training speeds with reduced memory usage through efficient 
parameter-efficient fine-tuning methods like LoRA and QLoRA.

# What to know before starting

- Python package management with pip and virtual environments
- Hugging Face Transformers library basics (loading models, tokenizers, datasets)
- GPU fundamentals (CUDA/GPU vs CPU, VRAM constraints, device availability)
- Basic understanding of LLM training concepts (loss functions, checkpoints)
- Familiarity with prompt engineering and base model interaction
- Optional: LoRA/QLoRA parameter-efficient fine-tuning knowledge

# Prerequisites

- NVIDIA Spark device with Blackwell GPU architecture
- `nvidia-smi` shows a summary of GPU information
- CUDA 13.0 installed: `nvcc --version`
- Internet access for downloading models and datasets

# Ancillary files

The Python test script can be found [here on GitHub](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/test_unsloth.py)


# Time & risk

* **Duration**: 30-60 minutes for initial setup and test run
* **Risks**: 
  * Triton compiler version mismatches may cause compilation errors
  * CUDA toolkit configuration issues may prevent kernel compilation
  * Memory constraints on smaller models require batch size adjustments
* **Rollback**: Uninstall packages with `pip uninstall unsloth torch torchvision`.
