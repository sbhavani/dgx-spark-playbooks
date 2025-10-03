# Build and Deploy a Multi-Agent Chatbot

> Deploy a multi-agent chatbot system and chat with agents on your Spark

## Table of Contents

- [Overview](#overview)
- [Instructions](#instructions)

---

## Overview

## Basic Idea

This playbook shows you how to use DGX Spark to prototype, build and deploy a fully local multi-agent system. 
With 128GB of unified memory, DGX Spark can run multiple LLMs and VLMs in parallel — enabling interactions across agents.

At the core is a supervisor agent powered by gpt-oss-120B, orchestrating specialized downstream agents for coding, retrieval-augmented generation (RAG), and image understanding. Thanks to DGX Spark's out-of-the-box support for popular AI frameworks and libraries, development and prototyping were fast and frictionless. 
Together, these components demonstrate how complex, multimodal workflows can be executed efficiently on local, high-performance hardware.

## What you'll accomplish

You will have a full-stack multi-agent chatbot system running on your DGX Spark, accessible through
your local web browser. 
The setup includes:
- LLM and VLM model serving using llama.cpp servers and TensorRT LLM servers
- GPU acceleration for both model inference and document retrieval
- Multi-agent system orchestration using a supervisor agent powered by gpt-oss-120B
- MCP (Model Context Protocol) servers as tools for the supervisor agent

## Prerequisites

-  DGX Spark device is set up and accessible
-  No other processes running on the DGX Spark GPU
-  Enough disk space for model downloads


## Time & risk

**Duration**: 30 minutes for initial setup, plus model download time (varies by model size)

**Risks**:
- Docker permission issues may require user group changes and session restart
- Large model downloads may take significant time depending on network speed

**Rollback**: Stop and remove Docker containers using provided cleanup commands

## Instructions

## Step 1. Configure Docker permissions

To easily manage containers without sudo, you must be in the `docker` group. If you choose to skip this step, you will need to run Docker commands with sudo.

Open a new terminal and test Docker access. In the terminal, run:

```bash
docker ps
```

If you see a permission denied error (something like `permission denied while trying to connect to the Docker daemon socket`), add your user to the docker group:

```bash
sudo usermod -aG docker $USER
```

> **Warning**: After running usermod, you must log out and log back in to start a new
> session with updated group permissions.

## Step 2. Clone the repository

In a terminal, clone the [GitHub](https://gitlab.com/nvidia/dgx-spark/temp-external-playbook-assets/dgx-spark-playbook-assets/-/blob/main) repository and navigate to the root directory of the multi-agent-chatbot project.

```bash
cd multi-agent-chatbot
```

## Step 3. Run the setup script

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Pull model GGUF files from HuggingFace
- Build base llama cpp server images
- Start the required docker containers - model servers, the backend API server as well as the frontend UI.

## Step 4. Wait for all the containers to become ready and healthy.

```bash
watch 'docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"'
```

This step can take ~20 minutes - pulling model files may take 10 minutes and starting containers may take another 10 minutes depending on network speed.

## Step 5. Access the frontend UI

Open your browser and go to: http://localhost:3000

> **Note**: If you are running this on a remote GPU via an ssh connection, in a new terminal window, you need to run the following command to be able to access the UI at localhost:3000 and for the UI to be able to communicate to the backend at localhost:8000.

>```ssh -L 3000:localhost:3000 -L 8000:localhost:8000  username@IP-address```

## Step 6. Try out the sample prompts

Click on any of the tiles on the frontend to try out the supervisor and the other agents.

**RAG Agent**:
Before trying out the RAG agent, upload the example PDF document NVIDIA Blackwell Whitepaper as context by clicking on the "Attach" icon in the text input space at the botton of the UI.
Make sure to check the box in the "Select Sources" section on the left side of the UI before submitting the query.


## Step 8. Cleanup and rollback

Steps to completely remove the containers and free up resources.

From the root directory of the multi-agent-chatbot project, run the following commands:

```bash
docker compose -f docker-compose.yml -d docker-compose-models.yml down
docker volume rm chatbot-spark_model-data chatbot-spark_postgres_data
```

## Step 9. Next steps

- Try different prompts with the multi-agent chatbot system.
- Try different models by following the instructions in the repository.
- Try adding new MCP (Model Context Protocol) servers as tools for the supervisor agent.
