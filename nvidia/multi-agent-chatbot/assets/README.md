# Chatbot Spark: A Local Multi-Agent System for DGX Spark 

## Project Overview

Chatbot Spark is a fully local multi-agent system built on DGX Spark. With 128GB of unified memory, DGX Spark can run multiple LLMs and VLMs in parallel — enabling interactions across agents. 

At the core is a supervisor agent powered by GPT-OSS-120B, orchestrating specialized downstream agents for coding, retrieval-augmented generation (RAG), and image understanding. Thanks to DGX Spark’s out-of-the-box support for popular AI frameworks and libraries, development and prototyping were fast and frictionless. Together, these components demonstrate how complex, multimodal workflows can be executed efficiently on local, high-performance hardware.

This project was built to be customizable, serving as a framework that developers can customize. 

## Key Features
  - **MCP Server Integration**: Chatbot Spark also showcases the ability to connect to custom MCP servers through a simple and customizable multi-server client

  - **Tool Calling**: This project uses an agents-as-tools framework and showcases the ability to create additional agents connected as tools. General tools can also be added.

  - **Easily Swappable Models**: Models are loaded and served using Llama CPP and Ollama and served through the OpenAI API. Any OpenAI-compatible model can be integrated into the project.

  - **Vector Indexing & Retrieval**: GPU-accelerated Milvus for high-performance document retrieval.

  - **Real-time LLM Streaming**: We present custom LLM-streaming infrastructure, making it easy for developers to stream supervisor responses from any OpenAI compatible model. 

  - **gpt-oss Integration**: The default chat/tool-calling model is gpt-oss:120b, providing seamless integration with OpenAI's latest open sorce tool-calling model.


## System Overview
<img src="assets/system-diagram.png" alt="System Diagram" style="max-width:600px;border-radius:5px;justify-content:center">

## Default Models
| Model                        | Quantization | Model Type | VRAM        |
|------------------------------|--------------|------------|-------------|
| GPT-OSS:120B                 | MXFP4        | Chat       | ~ 63.5 GB   |
| Deepseek-Coder:6.7B-Instruct | Q8           | Coding     | ~ 9.5  GB   |
| Qwen2.5-VL:7B-Instruct       | BF16         | Image      | ~ 35.4 GB   |
| Qwen3-Embedding-4B           | Q8           | Embedding  | ~ 5.39 GB   |

**Total VRAM required:** ~114 GB

> **Warning**:
> Since the default models use majority of available VRAM, ensure that you don't have anything already running on DGX Spark using `nvidia-smi`. If you do, switch to `gpt-oss-20b` following [this guide](#using-different-models).

---

## Quick Start
#### 1. Clone the repository and change directories to the multi-agent chatbot directory.

#### 2. Run the setup script
The setup script will take care of pulling model GGUF files from HuggingFace, building base llama cpp server images and starting all the required docker services to serve models, the backend API server as well as the frontend UI.
```bash
chmod +x setup.sh
./setup.sh
```
Wait for all the containers to become ready and healthy. 
```bash
watch 'docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"'
```
> Note: Downloading model files may take ~10 minutes and starting containers may take another 10 minutes depending on network speed. Look for "server is listening on http://0.0.0.0:8000" in the logs of model server containers.


#### 3. Access the frontend UI

Open your browser and go to: [http://localhost:3000](http://localhost:3000)

> Note:  If you are running this on a remote GPU via an ssh connection, in a new terminal window, you need to run to be able to access the UI at localhost:3000 and for the UI to be able to communicate to the backend at localhost:8000:
>```bash
> ssh -L 3000:localhost:3000 -L 8000:localhost:8000  username@IP-address
>```

You should see the following UI in your browser:
<img src="assets/multi-agent-chatbot.png" alt="Frontend UI" style="max-width:600px;border-radius:5px;justify-content:center">

### 4. Try out the sample prompts
Click on any of the tiles on the frontend to try out the supervisor and the other agents.

#### RAG Agent:
Before trying out the RAG agent, upload the example PDF document [NVIDIA Blackwell Whitepaper](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) as context by clicking on the "Attach" icon in the text input space at the botton of the UI and then make sure to check the box in the "Select Sources" section on the left side of the UI.
<img src="assets/upload-image.png" alt="Upload Image" style="max-width:300px;border-radius:5px;justify-content:center">
<img src="assets/document-ingestion.png" alt="Ingest Documents" style="max-width:300px;border-radius:5px;justify-content:center">

#### Image Understanding Agent:
You can either provide URLs or drag and drop images.

**Example Prompt:**


Describe this image: https://en.wikipedia.org/wiki/London_Bridge#/media/File:London_Bridge_from_St_Olaf_Stairs.jpg


## Customizations

### Using different models

You can use swap the model that the supervisor agent is using, for example to gpt-oss-20b.

1. In `setup.sh`, uncomment the line to download gpt-oss-20b.
> Note: If you already have the model files downloaded, you can skip to step 2.
2. In `docker-compose-models.yml`, uncomment the block for gpt-oss-20b. 
> Note: Since the default models use all of the existing VRAM, you will need to comment out the block for gpt-oss-120b in `docker-compose-models.yml`.
3. In `docker-compose.yml`, add `gpt-oss-20b` to the `MODELS` environment variable (line 40).
> Note: This name should match the container name that you set for this model in `docker-compose-models.yml`.

### Adding MCP servers and tools

1. You can add more MCP servers and tools under [backend/tools/mcp_servers](backend/tools/mcp_servers/) following existing examples.

2. If you added an MCP server, remember to add it to the server configs in [backend/client.py](backend/client.py)
