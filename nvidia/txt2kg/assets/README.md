# NVIDIA txt2kg

Use the following documentation to learn about NVIDIA txt2kg.
- [Overview](#overview)
- [Key Features](#key-features)
- [Target Audience](#target-audience)
- [Software Components](#software-components)
- [Technical Diagram](#technical-diagram)
- [GPU-Accelerated Visualization](#gpu-accelerated-visualization)
- [Minimum System Requirements](#minimum-system-requirements)
  - [OS Requirements](#os-requirements)
  - [Deployment Options](#deployment-options)
  - [Driver Versions](#driver-versions)
  - [Hardware Requirements](#hardware-requirements)
- [Next Steps](#next-steps)
- [Deployment Guide](#deployment-guide)
  - [Standard Deployment](#standard-deployment)
  - [PyGraphistry GPU-Accelerated Deployment](#pygraphistry-gpu-accelerated-deployment)
- [Available Customizations](#available-customizations)
- [License](#license)

## Overview

This blueprint serves as a reference solution for knowledge graph extraction and querying with Retrieval Augmented Generation (RAG). This txt2kg blueprint extracts knowledge triples from text and constructs a knowledge graph for visualization and querying, creating a more structured form of information retrieval compared to traditional RAG approaches. By leveraging graph databases and entity relationships, this blueprint delivers more contextually rich answers that better represent complex relationships in your data.

By default, this blueprint leverages **Ollama** for local LLM inference, providing a fully self-contained solution that runs entirely on your own hardware. You can optionally use NVIDIA-hosted models available in the [NVIDIA API Catalog](https://build.nvidia.com) or vLLM for advanced GPU-accelerated inference.

## Key Features

![Screenshot](/frontend/public/txt2kg.png)

[Watch the demo video](https://drive.google.com/file/d/1a0VG67zx_pGT4WyPTPH2ynefhfy2I0Py/view?usp=sharing)

- Knowledge triple extraction from text documents
- Knowledge graph construction and visualization
- **Local-first architecture** with Ollama for LLM inference
- Graph-based RAG for more contextual answers
- Graph database integration with ArangoDB
- Local vector embeddings with Pinecone-compatible storage
- GPU-accelerated LLM inference with Ollama and optional vLLM
- Sentence Transformers for efficient embedding generation
- Interactive knowledge graph visualization with Three.js WebGPU
- Optional NVIDIA API integration for cloud-based models
- Fully containerized deployment with Docker Compose
- Decomposable and customizable

## Target Audience

This blueprint is for:

- **Developers**: Developers who want to quickly set up a local-first Graph-based RAG solution
- **Data Scientists**: Data scientists who want to extract structured knowledge from unstructured text
- **Enterprise Architects**: Architects seeking to combine knowledge graph and RAG solutions for their organization
- **Privacy-Conscious Users**: Organizations requiring fully local, air-gapped deployments
- **GPU Researchers**: Researchers wanting to leverage GPU acceleration for LLM inference and graph visualization

## Software Components

The following are the default components included in this blueprint:

* **LLM Inference**
  * **Ollama** (default): Local LLM inference with GPU acceleration
    * Default model: `llama3.1:8b`
    * Supports any Ollama-compatible model
  * **vLLM** (optional): Advanced GPU-accelerated inference with quantization
    * Default model: `meta-llama/Llama-3.2-3B-Instruct`
  * **NVIDIA API** (optional): Cloud-based models via NVIDIA API Catalog
* **Vector Database & Embedding**
  * **SentenceTransformer**: Local embedding generation
    * Model: `all-MiniLM-L6-v2`
  * **Pinecone (Local)**: Self-hosted vector storage and similarity search
    * No cloud API key required
    * Compatible with Pinecone client libraries
* **Knowledge Graph Database**
  * **ArangoDB**: Graph database for storing knowledge triples (entities and relationships)
    * Web interface on port 8529
    * No authentication required (configurable)
* **Graph Visualization**
  * **Three.js WebGPU**: Client-side GPU-accelerated graph rendering
  * Optional remote WebGPU clustering for large graphs
* **Frontend & API**
  * **Next.js**: Modern React framework with API routes

## Technical Diagram

The architecture follows this workflow:
1. User uploads documents through the txt2kg web UI
2. Documents are processed and chunked for analysis
3. **Ollama** extracts knowledge triples (subject-predicate-object) from the text using local LLM inference
4. Triples are stored in **ArangoDB** graph database
5. **SentenceTransformer** generates entity embeddings
6. Embeddings are stored in local **Pinecone** vector database
7. User queries are processed through graph-based RAG:
   - KNN search identifies relevant entities in the vector database
   - Graph traversal enhances context with entity relationships from ArangoDB
   - Ollama generates responses using the enriched context
8. Results are visualized with **Three.js WebGPU** rendering in the browser

## GPU-Accelerated LLM Inference

This blueprint includes **GPU-accelerated LLM inference** with Ollama:

### Ollama Features
- **Fully local inference**: No cloud dependencies or API keys required
- **GPU acceleration**: Automatic CUDA support with NVIDIA GPUs
- **Multiple model support**: Use any Ollama-compatible model
- **Optimized performance**: Flash attention, KV cache optimization, and quantization
- **Easy model management**: Pull and switch models with simple commands
- **Privacy-first**: All data processing happens on your hardware

### Default Configuration
- Model: `llama3.1:8b`
- GPU memory fraction: 0.9 (90% of available VRAM)
- Flash attention enabled
- Q8_0 KV cache for memory efficiency

### Using Different Models
```bash
# Pull a different model
docker exec ollama-compose ollama pull llama3.1:70b

# Update environment variable in docker-compose.yml
OLLAMA_MODEL=llama3.1:70b
```

## Minimum System Requirements

### OS Requirements

Ubuntu 22.04 or later

### Deployment Options

- [Standard Docker Compose](./deploy/compose/docker-compose.yml) (Default - Ollama + ArangoDB + Pinecone)
- [vLLM Docker Compose](./deploy/compose/docker-compose.vllm.yml) (Advanced - vLLM for FP8 and NVFP4 quantization)
- [Complete Docker Compose](./deploy/compose/docker-compose.complete.yml) (Full stack with MinIO S3)

### Driver Versions

- GPU Driver - 530.30.02+
- CUDA version - 12.0+
### Hardware Requirements

- **For Ollama LLM inference**:
  - NVIDIA GPU with CUDA support (GTX 1060 or newer, RTX series recommended)
  - VRAM requirements depend on model size:
    - 8B models: 6-8GB VRAM
    - 70B models: 48GB+ VRAM (or use quantized versions)
  - System RAM: 16GB+ recommended
- **For vLLM (optional)**:
  - NVIDIA GPU with Ampere architecture or newer (RTX 30xx+, A100, H100)
  - Support for FP8 quantization for optimal performance
  - Similar VRAM requirements as Ollama

## Next Steps

- Clone the repository
- Install Docker and NVIDIA Container Toolkit
- Deploy with Docker Compose (no API keys required!)
- Pull your preferred Ollama model
- Upload documents and explore the knowledge graph
- Customize for your specific use case

## Deployment Guide

### Environment Variables

**No API keys required for default deployment!** All services run locally.

The default configuration uses:
- Local Ollama (no API key needed)
- Local Pinecone (no API key needed)
- Local ArangoDB (no authentication by default)
- Local SentenceTransformer embeddings

#### Optional Environment Variables

```bash
# Ollama configuration (optional - defaults are set)
OLLAMA_BASE_URL=http://ollama:11434/v1
OLLAMA_MODEL=llama3.1:8b

# NVIDIA API (optional - for cloud models)
NVIDIA_API_KEY=your-nvidia-api-key

# vLLM configuration (optional)
VLLM_BASE_URL=http://vllm:8001/v1
VLLM_MODEL=meta-llama/Llama-3.2-3B-Instruct
```

### Standard Deployment

1. **Clone the repository:**
```bash
git clone <repository-url>
cd txt2kg
```

2. **Start the application:**
```bash
./start.sh
```

That's it! No configuration needed. The script will:
- Start all required services with Docker Compose
- Set up ArangoDB database
- Initialize local Pinecone vector storage
- Launch Ollama with GPU acceleration
- Start the Next.js frontend

3. **Pull an Ollama model (first time only):**
```bash
docker exec ollama-compose ollama pull llama3.1:8b
```

4. **Access the application:**
- **Web UI**: http://localhost:3001
- **ArangoDB**: http://localhost:8529 (no authentication required)
- **Ollama API**: http://localhost:11434

### Advanced Deployment Options

#### Using vLLM for FP8 Quantization

vLLM provides advanced GPU acceleration with FP8 quantization for smaller memory footprint:

```bash
# Use vLLM compose file
docker compose -f deploy/compose/docker-compose.vllm.yml up -d
```

vLLM is recommended for:
- Newer NVIDIA GPUs (Ampere architecture or later)
- Production deployments requiring maximum throughput
- Memory-constrained environments (FP8 uses less VRAM)

#### GPU Setup Prerequisites

1. **Install NVIDIA Container Toolkit**:
   ```bash
   # Ubuntu/Debian
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

2. **Verify GPU Access**:
   ```bash
   docker run --rm --gpus all nvidia/cuda:12.0-base-ubuntu22.04 nvidia-smi
   ```

#### Troubleshooting

**Check Service Logs**:
```bash
# View all service logs
docker compose logs -f

# View Ollama logs
docker compose logs -f ollama

# View vLLM logs (if using vLLM)
docker compose -f deploy/compose/docker-compose.vllm.yml logs -f vllm
```

**GPU Issues**:
```bash
# Check GPU availability
nvidia-smi

# Verify Docker GPU access
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

**Ollama Model Management**:
```bash
# List available models
docker exec ollama-compose ollama list

# Pull a different model
docker exec ollama-compose ollama pull mistral

# Remove a model to free space
docker exec ollama-compose ollama rm llama3.1:8b
```

## Available Customizations

The following are some of the customizations you can make:

- **Switch Ollama models**: Use any model from Ollama's library (Llama, Qwen, etc.)
- **Modify extraction prompts**: Customize how triples are extracted from text
- **Adjust embedding parameters**: Change the SentenceTransformer model
- **Implement custom entity relationships**: Define domain-specific relationship types
- **Add domain-specific knowledge sources**: Integrate external ontologies or taxonomies
- **Configure GPU settings**: Optimize VRAM usage and performance for your hardware
- **Switch to vLLM**: Use vLLM for advanced quantization and higher throughput
- **Use NVIDIA API**: Connect to cloud models for specific use cases

## License

[MIT](LICENSE)

This is licensed under the MIT License. This project will download and install additional third-party open source software projects and containers.
