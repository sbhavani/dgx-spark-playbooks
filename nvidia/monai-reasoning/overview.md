# Basic idea

The MONAI Reasoning CXR 3B model is a **medical AI model** designed for **chest X-ray (CXR) interpretation** with reasoning capabilities. It combines imaging analysis with large-scale language modeling:

- **Medical focus**: Built within the MONAI framework for healthcare imaging tasks.  
- **Vision + language**: Takes CXR images as input and produces diagnostic text or reasoning outputs.  
- **Reasoning layer**: Goes beyond simple classification to explain intermediate steps (e.g., opacity → pneumonia suspicion).  
- **3B scale**: A moderately large multimodal model (~3 billion parameters).  
- **Trust and explainability**: Aims to make results more interpretable and clinically useful.

# What you'll accomplish

You'll deploy the MONAI-Reasoning-CXR-3B model, a specialized vision-language model for chest X-ray 
analysis, on an NVIDIA Spark device with Blackwell GPU architecture. By the end of this 
walkthrough, you will have a complete system running with VLLM serving the model for 
high-performance inference and Open WebUI providing an easy-to-use interface for interacting 
with the model. This setup is ideal for clinical demonstrations and research that requires 
transparent AI reasoning.

# What to know before starting

* Experience with the Linux command line and shell scripting
* A basic understanding of Docker, including running containers and managing images  
* Familiarity with Python and using pip for package management
* Knowledge of Large Language Models (LLMs) and how to interact with API endpoints
* Basic understanding of NVIDIA GPU hardware and CUDA drivers

# Prerequisites

**Hardware Requirements:**
* NVIDIA Spark device with ARM64 (AArch64) architecture
* NVIDIA Blackwell GPU architecture  
* At least 24GB of GPU VRAM

**Software Requirements:**

* **NVIDIA Driver**: Ensure the driver is installed and the GPU is recognized
```bash
nvidia-smi
```

* **Docker Engine**: Docker must be installed and the daemon running
```bash
docker --version
```

* **NVIDIA Container Toolkit**: Required for GPU access in containers
```bash
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

* **Hugging Face CLI**: You'll need this to download the model
```bash
pip install -U huggingface_hub  
huggingface-cli whoami
```

* **System Architecture**: Verify your system architecture for proper container selection
```bash
uname -m
# Should output: aarch64 for ARM64 systems like NVIDIA Spark
```

# Time & risk

* **Estimated time:** 20-35 minutes (not including model download)
* **Risk level:** Low. All steps use publicly available containers and models
* **Rollback:** The entire deployment is containerized. To roll back, you can simply stop and remove the Docker containers
