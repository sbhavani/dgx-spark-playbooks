# Basic idea

This playbook demonstrates how to build and deploy a comprehensive knowledge graph generation and visualization solution that serves as a reference for knowledge graph extraction.
The unified memory architecture enables running larger, more accurate models that produce higher-quality knowledge graphs and deliver superior downstream GraphRAG performance.

This txt2kg playbook transforms unstructured text documents into structured knowledge graphs using:
- **Knowledge Triple Extraction**: Using Ollama with GPU acceleration for local LLM inference to extract subject-predicate-object relationships
- **Graph Database Storage**: ArangoDB for storing and querying knowledge triples with relationship traversal
- **GPU-Accelerated Visualization**: Three.js WebGPU rendering for interactive 2D/3D graph exploration

> **Future Enhancements**: Vector embeddings and GraphRAG capabilities are planned enhancements.

# What you'll accomplish

You will have a fully functional system capable of processing documents, generating and editing knowledge graphs, and providing querying, accessible through an interactive web interface.
The setup includes:
- **Local LLM Inference**: Ollama for GPU-accelerated LLM inference with no API keys required
- **Graph Database**: ArangoDB for storing and querying triples with relationship traversal
- **Interactive Visualization**: GPU-accelerated graph rendering with Three.js WebGPU
- **Modern Web Interface**: Next.js frontend with document management and query interface
- **Fully Containerized**: Reproducible deployment with Docker Compose and GPU support

# Prerequisites

-  DGX Spark with latest NVIDIA drivers
-  Docker installed and configured with NVIDIA Container Toolkit
-  Docker Compose


# Time & risk

- **Duration**:
  - 2-3 minutes for initial setup and container deployment
  - 5-10 minutes for Ollama model download (depending on model size)
  - Immediate document processing and knowledge graph generation

- **Risks**:
  - GPU memory requirements depend on chosen Ollama model size
  - Document processing time scales with document size and complexity

- **Rollback**: Stop and remove Docker containers, delete downloaded models if needed
- **Last Updated**: 11/19/2025
  - Updated GPU Visualization Service