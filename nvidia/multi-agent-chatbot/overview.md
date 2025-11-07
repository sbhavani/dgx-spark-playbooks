# Basic idea

This playbook shows you how to use DGX Spark to prototype, build, and deploy a fully local multi-agent system. 
With 128GB of unified memory, DGX Spark can run multiple LLMs and VLMs in parallel — enabling interactions across agents.

At the core is a supervisor agent powered by gpt-oss-120B, orchestrating specialized downstream agents for coding, retrieval-augmented generation (RAG), and image understanding. 
Thanks to DGX Spark's out-of-the-box support for popular AI frameworks and libraries, development and prototyping are fast and frictionless. 
Together, these components demonstrate how complex, multimodal workflows can be executed efficiently on local, high-performance hardware.

# What you'll accomplish

You will have a full-stack multi-agent chatbot system running on your DGX Spark, accessible through
your local web browser. 
The setup includes:
- LLM and VLM model serving using llama.cpp servers and TensorRT LLM servers
- GPU acceleration for both model inference and document retrieval
- Multi-agent system orchestration using a supervisor agent powered by gpt-oss-120B
- MCP (Model Context Protocol) servers as tools for the supervisor agent

# Prerequisites

-  DGX Spark device is set up and accessible
-  No other processes running on the DGX Spark GPU
-  Enough disk space for model downloads

> [!NOTE]
> This demo uses ~120 out of the 128GB of DGX Spark's memory by default. 
> Please ensure that no other workloads are running on your Spark using `nvidia-smi`, or switch to a smaller supervisor model like gpt-oss-20B.


# Time & risk

* **Estimated time**: 30 minutes to an hour
* **Risks**:
  * Docker permission issues may require user group changes and session restart
  * Setup includes downloading model files for gpt-oss-120B (~63GB), Deepseek-Coder:6.7B-Instruct (~7GB) and Qwen3-Embedding-4B (~4GB), which may take between 30 minutes to 2 hours depending on network speed
* **Rollback**: Stop and remove Docker containers using provided cleanup commands.
