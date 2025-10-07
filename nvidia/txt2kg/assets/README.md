# NVIDIA txt2kg

## Overview

This playbook serves as a reference solution for knowledge graph extraction and querying with Retrieval Augmented Generation (RAG). This txt2kg playbook extracts knowledge triples from text and constructs a knowledge graph for visualization and querying, creating a more structured form of information retrieval compared to traditional RAG approaches. By leveraging graph databases and entity relationships, this playbook delivers more contextually rich answers that better represent complex relationships in your data.

<details>
<summary>📋 Table of Contents</summary>


- [Overview](#overview)
- [Key Features](#key-features)
- [Software Components](#software-components)
- [Technical Diagram](#technical-diagram)
- [Minimum System Requirements](#minimum-system-requirements)
- [Deployment Guide](#deployment-guide)
- [Available Customizations](#available-customizations)
- [License](#license)

</details>

By default, this playbook leverages **Ollama** for local LLM inference, providing a fully self-contained solution that runs entirely on your own hardware. You can optionally use NVIDIA-hosted models available in the [NVIDIA API Catalog](https://build.nvidia.com) for advanced capabilities.

## Key Features

![Screenshot](./frontend/public/txt2kg.png)

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

## Software Components

The following are the default components included in this playbook:

* **LLM Inference**
  * **Ollama** (default): Local LLM inference with GPU acceleration
    * Default model: `llama3.1:8b`
    * Supports any Ollama-compatible model
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

This playbook includes **GPU-accelerated LLM inference** with Ollama:

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

## Minimum System Requirements

**OS Requirements:**
- Ubuntu 22.04 or later

**Driver Versions:**
- GPU Driver: 530.30.02+
- CUDA: 12.0+

**Hardware Requirements:**
- NVIDIA GPU with CUDA support (GTX 1060 or newer, RTX series recommended)
- VRAM requirements depend on model size:
  - 8B models: 6-8GB VRAM
  - 70B models: 48GB+ VRAM (or use quantized versions)
- System RAM: 16GB+ recommended

## Deployment Guide

### Environment Variables

**No API keys required for default deployment!** All services run locally.

The default configuration uses:
- Local Ollama (no API key needed)
- Local Pinecone (no API key needed)
- Local ArangoDB (no authentication by default)
- Local SentenceTransformer embeddings

Optional environment variables for customization:
```bash
# Ollama configuration (optional - defaults are set)
OLLAMA_BASE_URL=http://ollama:11434/v1
OLLAMA_MODEL=llama3.1:8b

# NVIDIA API (optional - for cloud models)
NVIDIA_API_KEY=your-nvidia-api-key
```

### Quick Start

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

## Available Customizations

- **Switch Ollama models**: Use any model from Ollama's library (Llama, Mistral, Qwen, etc.)
- **Modify extraction prompts**: Customize how triples are extracted from text
- **Adjust embedding parameters**: Change the SentenceTransformer model
- **Implement custom entity relationships**: Define domain-specific relationship types
- **Add domain-specific knowledge sources**: Integrate external ontologies or taxonomies
- **Use NVIDIA API**: Connect to cloud models for specific use cases

## License

[MIT](LICENSE)

This is licensed under the MIT License. This project will download and install additional third-party open source software projects and containers.
