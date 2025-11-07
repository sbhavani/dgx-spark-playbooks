# Basic idea

Deploy NVIDIA's Video Search and Summarization (VSS) AI Blueprint to build intelligent video analytics systems that combine vision language models, large language models, and retrieval-augmented generation. The system transforms raw video content into real-time actionable insights with video summarization, Q&A, and real-time alerts. You'll set up either a completely local Event Reviewer deployment or a hybrid deployment using remote model endpoints.

# What you'll accomplish

You will deploy NVIDIA's VSS AI Blueprint on NVIDIA Spark hardware with Blackwell architecture, choosing between two deployment scenarios: VSS Event Reviewer (completely local with VLM pipeline) or Standard VSS (hybrid deployment with remote LLM/embedding endpoints). This includes setting up Alert Bridge, VLM Pipeline, Alert Inspector UI, Video Storage Toolkit, and optional DeepStream CV pipeline for automated video analysis and event review.

# What to know before starting

- Working with NVIDIA Docker containers and container registries
- Setting up Docker Compose environments with shared networks
- Managing environment variables and authentication tokens
- Basic understanding of video processing and analysis workflows

# Prerequisites

- NVIDIA Spark device with ARM64 architecture and Blackwell GPU
- NVIDIA DGX OS 7.2.3 or higher
- Driver version 580.95.05 or higher installed: `nvidia-smi | grep "Driver Version"`
- CUDA version 13.0 installed: `nvcc --version`
- Docker installed and running: `docker --version && docker compose version`
- Access to NVIDIA Container Registry with [NGC API Key](https://org.ngc.nvidia.com/setup/api-keys)
- [Optional] NVIDIA API Key for remote model endpoints (hybrid deployment only)
- Sufficient storage space for video processing (>10GB recommended in `/tmp/`)

# Ancillary files

- [VSS Blueprint GitHub Repository](https://github.com/NVIDIA-AI-Blueprints/video-search-and-summarization) - Main codebase and Docker Compose configurations
- [Sample CV Detection Pipeline](https://github.com/NVIDIA-AI-Blueprints/video-search-and-summarization/tree/main/examples/cv-event-detector) - Reference CV pipeline for event reviewer workflow
- [VSS Official Documentation](https://docs.nvidia.com/vss/latest/index.html) - Complete system documentation

# Time & risk

* **Duration:** 30-45 minutes for initial setup, additional time for video processing validation
* **Risks:**
* Container startup can be resource-intensive and time-consuming with large model downloads
* Network configuration conflicts if shared network already exists
* Remote API endpoints may have rate limits or connectivity issues (hybrid deployment)
* **Rollback:** Stop all containers with `docker compose down`, remove shared network with `docker network rm vss-shared-network`, and clean up temporary media directories.
