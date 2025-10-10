# TRT LLM for Inference

> Install and configure TRT LLM to run on a single Spark or on two Sparks

## Table of Contents

- [Overview](#overview)
- [Single Spark](#single-spark)
  - [Step 1. Configure Docker permissions](#step-1-configure-docker-permissions)
  - [Step 2. Verify environment prerequisites](#step-2-verify-environment-prerequisites)
  - [Step 3. Set environment variables](#step-3-set-environment-variables)
  - [Step 4. Validate TensorRT-LLM installation](#step-4-validate-tensorrt-llm-installation)
  - [Step 5. Create cache directory](#step-5-create-cache-directory)
  - [Step 6. Validate setup with quickstart_advanced](#step-6-validate-setup-with-quickstartadvanced)
  - [Step 7. Validate setup with quickstart_multimodal](#step-7-validate-setup-with-quickstartmultimodal)
  - [Step 8. Serve LLM with OpenAI-compatible API](#step-8-serve-llm-with-openai-compatible-api)
  - [Step 10. Cleanup and rollback](#step-10-cleanup-and-rollback)
- [Run on two Sparks](#run-on-two-sparks)
  - [Step 1. User prerequisites](#step-1-user-prerequisites)
  - [Step 2. Configure Docker permissions](#step-2-configure-docker-permissions)
  - [Step 3. Configure network connectivity](#step-3-configure-network-connectivity)
  - [Step 4. Install NVIDIA Container Toolkit & setup Docker environment](#step-4-install-nvidia-container-toolkit-setup-docker-environment)
  - [Step 5. Enable resource advertising](#step-5-enable-resource-advertising)
  - [Step 6. Initialize Docker Swarm](#step-6-initialize-docker-swarm)
  - [Step 7. Join worker nodes and deploy](#step-7-join-worker-nodes-and-deploy)
  - [Step 8. Create hosts file](#step-8-create-hosts-file)
  - [Step 9. Find your Docker container ID](#step-9-find-your-docker-container-id)
  - [Step 10. Generate configuration file](#step-10-generate-configuration-file)
  - [Step 11. Download model](#step-11-download-model)
  - [Step 12. Serve the model](#step-12-serve-the-model)
  - [Step 13. Validate API server](#step-13-validate-api-server)
  - [Step 15. Cleanup and rollback](#step-15-cleanup-and-rollback)
  - [Step 16. Next steps](#step-16-next-steps)
- [Troubleshooting](#troubleshooting)

---

## Overview

## Basic idea

**NVIDIA TensorRT-LLM (TRT-LLM)** is an open-source library for optimizing and accelerating large language model (LLM) inference on NVIDIA GPUs.

It provides highly efficient kernels, memory management, and parallelism strategies—like tensor, pipeline, and sequence parallelism—so developers can serve LLMs with lower latency and higher throughput.

TRT-LLM integrates with frameworks like Hugging Face and PyTorch, making it easier to deploy state-of-the-art models at scale.


## What you'll accomplish

You'll set up TensorRT-LLM to optimize and deploy large language models on NVIDIA Spark with
Blackwell GPUs, achieving significantly higher throughput and lower latency than standard PyTorch
inference through kernel-level optimizations, efficient memory layouts, and advanced quantization.

## What to know before starting

- Python proficiency and experience with PyTorch or similar ML frameworks
- Command-line comfort for running CLI tools and Docker containers
- Basic understanding of GPU concepts including VRAM, batching, and quantization (FP16/INT8)
- Familiarity with NVIDIA software stack (CUDA Toolkit, drivers)
- Experience with inference servers and containerized environments

## Prerequisites

- NVIDIA Spark device with Blackwell architecture GPUs
- NVIDIA drivers compatible with CUDA 12.x: `nvidia-smi`
- Docker installed and GPU support configured: `docker run --rm --gpus all nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev nvidia-smi`
- Hugging Face account with token for model access: `echo $HF_TOKEN`
- Sufficient GPU VRAM (16GB+ recommended for 70B models)
- Internet connectivity for downloading models and container images
- Network: open TCP ports 8355 (LLM) and 8356 (VLM) on host for OpenAI-compatible serving

## Ancillary files

All required assets can be found [here on GitHub](https://gitlab.com/nvidia/dgx-spark/temp-external-playbook-assets/dgx-spark-playbook-assets/-/blob/main)

- [**discover-sparks.sh**](https://gitlab.com/nvidia/dgx-spark/temp-external-playbook-assets/dgx-spark-playbook-assets/-/blob/main/${MODEL}/assets/discover-sparks.sh) — script to automatically discover and configure SSH between Spark nodes
- [**trtllm-mn-entrypoint.sh**](https://gitlab.com/nvidia/dgx-spark/temp-external-playbook-assets/dgx-spark-playbook-assets/-/blob/main/${MODEL}/assets/trtllm-mn-entrypoint.sh) — container entrypoint script for multi-node setup
- [**docker-compose.yml**](https://gitlab.com/nvidia/dgx-spark/temp-external-playbook-assets/dgx-spark-playbook-assets/-/blob/main/${MODEL}/assets/docker-compose.yml) — Docker Compose configuration for multi-node deployment

## Model Support Matrix

The following models are supported with TensorRT-LLM on Spark. All listed models are available and ready to use:

| Model | Quantization | Support Status | HF Handle |
|-------|-------------|----------------|-----------|
| **GPT-OSS-20B** | MXFP4 | ✅ | `openai/gpt-oss-20b` |
| **GPT-OSS-120B** | MXFP4 | ✅ | `openai/gpt-oss-120b` |
| **Llama-3.1-8B-Instruct** | FP8 | ✅ | `nvidia/Llama-3.1-8B-Instruct-FP8` |
| **Llama-3.1-8B-Instruct** | NVFP4 | ✅ | `nvidia/Llama-3.1-8B-Instruct-FP4` |
| **Llama-3.3-70B-Instruct** | NVFP4 | ✅ | `nvidia/Llama-3.3-70B-Instruct-FP4` |
| **Qwen3-8B** | FP8 | ✅ | `nvidia/Qwen3-8B-FP8` |
| **Qwen3-8B** | NVFP4 | ✅ | `nvidia/Qwen3-8B-FP4` |
| **Qwen3-14B** | FP8 | ✅ | `nvidia/Qwen3-14B-FP8` |
| **Qwen3-14B** | NVFP4 | ✅ | `nvidia/Qwen3-14B-FP4` |
| **Phi-4-multimodal-instruct** | FP8 | ✅ | `nvidia/Phi-4-multimodal-instruct-FP8` |
| **Phi-4-multimodal-instruct** | NVFP4 | ✅ | `nvidia/Phi-4-multimodal-instruct-FP4` |
| **Phi-4-reasoning-plus** | FP8 | ✅ | `nvidia/Phi-4-reasoning-plus-FP8` |
| **Phi-4-reasoning-plus** | NVFP4 | ✅ | `nvidia/Phi-4-reasoning-plus-FP4` |
| **Llama-3_3-Nemotron-Super-49B-v1_5** | FP8 | ✅ | `nvidia/Llama-3_3-Nemotron-Super-49B-v1_5-FP8` |
| **Qwen3-30B-A3B** | NVFP4 | ✅ | `nvidia/Qwen3-30B-A3B-FP4` |
| **Qwen2.5-VL-7B-Instruct** | FP8 | ✅ | `nvidia/Qwen2.5-VL-7B-Instruct-FP8` |
| **Qwen2.5-VL-7B-Instruct** | NVFP4 | ✅ | `nvidia/Qwen2.5-VL-7B-Instruct-FP4` |
| **Llama-4-Scout-17B-16E-Instruct** | NVFP4 | ✅ | `nvidia/Llama-4-Scout-17B-16E-Instruct-FP4` |
| **Qwen3-235B-A22B (two Sparks only)** | NVFP4 | ✅ | `nvidia/Qwen3-235B-A22B-FP4` |

**Note:** You can use the NVFP4 Quantization documentation to generate your own NVFP4-quantized checkpoints for your favorite models. This enables you to take advantage of the performance and memory benefits of NVFP4 quantization even for models not already published by NVIDIA.

Reminder: not all model architectures are supported for NVFP4 quantization.

## Time & risk

* **Duration**: 45-60 minutes for setup and API server deployment
* **Risk level**: Medium - container pulls and model downloads may fail due to network issues
* **Rollback**: Stop inference servers and remove downloaded models to free resources.

## Single Spark

### Step 1. Configure Docker permissions

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


### Step 2. Verify environment prerequisites

Confirm your Spark device has the required GPU access and network connectivity for downloading
models and containers.

```bash
## Check GPU visibility and driver
nvidia-smi

## Verify Docker GPU support
docker run --rm --gpus all nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev nvidia-smi

```

### Step 3. Set environment variables

Set `HF_TOKEN` for model access.

```bash
export HF_TOKEN=<your-huggingface-token>
```

### Step 4. Validate TensorRT-LLM installation

After confirming GPU access, verify that TensorRT-LLM can be imported inside the container.

```bash
docker run --rm -it --gpus all \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  python -c "import tensorrt_llm; print(f'TensorRT-LLM version: {tensorrt_llm.__version__}')"
```

Expected output:
```
[TensorRT-LLM] TensorRT-LLM version: 1.1.0rc3
TensorRT-LLM version: 1.1.0rc3
```

### Step 5. Create cache directory

Set up local caching to avoid re-downloading models on subsequent runs.

```bash
## Create Hugging Face cache directory
mkdir -p $HOME/.cache/huggingface/
```

### Step 6. Validate setup with quickstart_advanced

This quickstart validates your TensorRT-LLM setup end-to-end by testing model loading, inference engine initialization, and GPU execution with real text generation. It's the fastest way to confirm everything works before starting the inference API server.

**LLM quickstart example**

#### Llama 3.1 8B Instruct
```bash
export MODEL_HANDLE="nvidia/Llama-3.1-8B-Instruct-FP4"

docker run \
  -e MODEL_HANDLE=$MODEL_HANDLE \
  -e HF_TOKEN=$HF_TOKEN \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  --rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
  --gpus=all --ipc=host --network host \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
    hf download $MODEL_HANDLE && \
    python examples/llm-api/quickstart_advanced.py \
      --model_dir $MODEL_HANDLE \
      --prompt "Paris is great because" \
      --max_tokens 64
    '
```

#### GPT-OSS 20B
```bash
export MODEL_HANDLE="openai/gpt-oss-20b"

docker run \
  -e MODEL_HANDLE=$MODEL_HANDLE \
  -e HF_TOKEN=$HF_TOKEN \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  --rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
  --gpus=all --ipc=host --network host \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
    export TIKTOKEN_ENCODINGS_BASE="/tmp/harmony-reqs" && \
    mkdir -p $TIKTOKEN_ENCODINGS_BASE && \
    wget -P $TIKTOKEN_ENCODINGS_BASE https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken && \
    wget -P $TIKTOKEN_ENCODINGS_BASE https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken && \
    hf download $MODEL_HANDLE && \
    python examples/llm-api/quickstart_advanced.py \
      --model_dir $MODEL_HANDLE \
      --prompt "Paris is great because" \
      --max_tokens 64
    '
```

#### GPT-OSS 120B
```bash
export MODEL_HANDLE="openai/gpt-oss-120b"

docker run \
  -e MODEL_HANDLE=$MODEL_HANDLE \
  -e HF_TOKEN=$HF_TOKEN \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  --rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
  --gpus=all --ipc=host --network host \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
    export TIKTOKEN_ENCODINGS_BASE="/tmp/harmony-reqs" && \
    mkdir -p $TIKTOKEN_ENCODINGS_BASE && \
    wget -P $TIKTOKEN_ENCODINGS_BASE https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken && \
    wget -P $TIKTOKEN_ENCODINGS_BASE https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken && \
    hf download $MODEL_HANDLE && \
    python examples/llm-api/quickstart_advanced.py \
      --model_dir $MODEL_HANDLE \
      --prompt "Paris is great because" \
      --max_tokens 64
    '
```
### Step 7. Validate setup with quickstart_multimodal

**VLM quickstart example**

This demonstrates vision-language model capabilities by running inference with image understanding. The example uses multimodal inputs to validate both text and vision processing pipelines.

#### Qwen2.5-VL-7B-Instruct

```bash
export MODEL_HANDLE="nvidia/Qwen2.5-VL-7B-Instruct-FP4"

docker run \
  -e MODEL_HANDLE=$MODEL_HANDLE \
  -e HF_TOKEN=$HF_TOKEN \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  --rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
  --gpus=all --ipc=host --network host \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
  python3 examples/llm-api/quickstart_multimodal.py \
    --model_dir $MODEL_HANDLE \
    --modality image \
    --media "https://huggingface.co/datasets/YiYiXu/testing-images/resolve/main/seashore.png" \
    --prompt "What is happening in this image?" \
  '
```

#### Phi-4-multimodal-instruct

This model requires LoRA (Low-Rank Adaptation) configuration as it uses parameter-efficient fine-tuning. The `--load_lora` flag enables loading the LoRA weights that adapt the base model for multimodal instruction following.
```bash
export MODEL_HANDLE="nvidia/Phi-4-multimodal-instruct-FP4"

docker run \
  -e MODEL_HANDLE=$MODEL_HANDLE \
  -e HF_TOKEN=$HF_TOKEN \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  --rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
  --gpus=all --ipc=host --network host \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
  python3 examples/llm-api/quickstart_multimodal.py \
    --model_type phi4mm \
    --model_dir $MODEL_HANDLE \
    --modality image \
    --media "https://huggingface.co/datasets/YiYiXu/testing-images/resolve/main/seashore.png" \
    --prompt "What is happening in this image?" \
    --load_lora \
    --auto_model_name Phi4MMForCausalLM
  '
```


> Note: If you hit a host OOM during downloads or first run, free the OS page cache on the host (outside the container) and retry:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```

### Step 8. Serve LLM with OpenAI-compatible API

Serve with OpenAI-compatible API via trtllm-serve:

#### Llama 3.1 8B Instruct
```bash
export MODEL_HANDLE="nvidia/Llama-3.1-8B-Instruct-FP4"

docker run --name trtllm_llm_server --rm -it --gpus all --ipc host --network host \
  -e HF_TOKEN=$HF_TOKEN \
  -e MODEL_HANDLE="$MODEL_HANDLE" \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
    hf download $MODEL_HANDLE && \
    cat > /tmp/extra-llm-api-config.yml <<EOF
print_iter_log: false
kv_cache_config:
  dtype: "auto"
  free_gpu_memory_fraction: 0.9
cuda_graph_config:
  enable_padding: true
disable_overlap_scheduler: true
EOF
    trtllm-serve "$MODEL_HANDLE" \
      --max_batch_size 64 \
      --trust_remote_code \
      --port 8355 \
      --extra_llm_api_options /tmp/extra-llm-api-config.yml
  '
```

#### GPT-OSS 20B
```bash
export MODEL_HANDLE="openai/gpt-oss-20b"

docker run --name trtllm_llm_server --rm -it --gpus all --ipc host --network host \
  -e HF_TOKEN=$HF_TOKEN \
  -e MODEL_HANDLE="$MODEL_HANDLE" \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
  bash -c '
    export TIKTOKEN_ENCODINGS_BASE="/tmp/harmony-reqs" && \
    mkdir -p $TIKTOKEN_ENCODINGS_BASE && \
    wget -P $TIKTOKEN_ENCODINGS_BASE https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken && \
    wget -P $TIKTOKEN_ENCODINGS_BASE https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken && \
    hf download $MODEL_HANDLE && \
    cat > /tmp/extra-llm-api-config.yml <<EOF
print_iter_log: false
kv_cache_config:
  dtype: "auto"
  free_gpu_memory_fraction: 0.9
cuda_graph_config:
  enable_padding: true
disable_overlap_scheduler: true
EOF
    trtllm-serve "$MODEL_HANDLE" \
      --max_batch_size 64 \
      --trust_remote_code \
      --port 8355 \
      --extra_llm_api_options /tmp/extra-llm-api-config.yml
  '
```

Minimal OpenAI-style chat request. Run this from a separate terminal.

```bash
curl -s http://localhost:8355/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"$MODEL_HANDLE"'",
    "messages": [{"role": "user", "content": "Paris is great because"}],
    "max_tokens": 64
  }'
```

### Step 10. Cleanup and rollback

Remove downloaded models and containers to free up space when testing is complete.

> **Warning:** This will delete all cached models and may require re-downloading for future runs.

```bash
## Remove Hugging Face cache
sudo chown -R "$USER:$USER" "$HOME/.cache/huggingface"
rm -rf $HOME/.cache/huggingface/

## Clean up Docker images
docker image prune -f
docker rmi nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev
```

## Run on two Sparks

### Step 1. User prerequisites
Ensure all your DGX Spark nodes are set up and accessible with the same username. If your DGX Spark nodes are set up with different usernames, you will need to create a shared username for all the nodes.
You can create a common user `nvidia` by running the following command:

```bash
sudo usermod -aG docker nvidia
```

### Step 2. Configure Docker permissions

To easily manage containers without sudo, you must be in the `docker` group. If you choose to skip this step, you will need to run Docker commands with sudo.

Open a new terminal and test Docker access. In the terminal, run:

```bash
docker ps
```

If you see a permission denied error (something like `permission denied while trying to connect to the Docker daemon socket`), add your user to the docker group:

```bash
sudo usermod -aG docker nvidia
```
Note: Replace `nvidia` with the username of the user you want to allow Docker access to.
Note: After running usermod, you must log out and log back in to start a new session with updated group permissions.

### Step 3. Configure network connectivity

You have two options for configuring network connectivity between your DGX Spark nodes:

#### Option 1: Automatic IP assignment (recommended)

Follow these steps on both DGX Spark nodes to configure network interfaces using netplan:

```bash
## Create the netplan configuration file
sudo tee /etc/netplan/40-cx7.yaml > /dev/null <<EOF
network:
  version: 2
  ethernets:
    enp1s0f0np0:
      link-local: [ ipv4 ]
    enp1s0f1np1:
      link-local: [ ipv4 ]
EOF

## Set appropriate permissions
sudo chmod 600 /etc/netplan/40-cx7.yaml

## Apply the configuration
sudo netplan apply
```

#### Option 2: Manual IP assignment (advanced)

First, identify which network ports are available and up:

```bash
## Check network port status
ibdev2netdev
```

Example output:
```
roceP2p1s0f0 port 1 ==> enP2p1s0f0np0 (Up)
roceP2p1s0f1 port 1 ==> enP2p1s0f1np1 (Down)
rocep1s0f0 port 1 ==> enp1s0f0np0 (Up)
rocep1s0f1 port 1 ==> enp1s0f1np1 (Down)
```

Use an interface that shows as "(Up)" in your output. In this example, we'll use **enp1s0f0np0**.

On Node 1:
```bash
## Assign static IP and bring up interface
sudo ip addr add 192.168.100.10/24 dev enp1s0f0np0
sudo ip link set enp1s0f0np0 up
```

On Node 2:
```bash
## Assign static IP and bring up interface
sudo ip addr add 192.168.100.11/24 dev enp1s0f0np0
sudo ip link set enp1s0f0np0 up
```


#### Set up passwordless SSH authentication

Run the DGX Spark [**discover-sparks.sh**](https://gitlab.com/nvidia/dgx-spark/temp-external-playbook-assets/dgx-spark-playbook-assets/-/blob/main/${MODEL}/assets/discover-sparks.sh) script on both nodes to automatically configure SSH:

```bash
bash ./discover-sparks.sh
```

Expected output similar to the below, with different IPs and node names. The first time you run the script, you'll be prompted for your password for each node.
```
Found: 192.168.100.10 (spark-1b3b.local)
Found: 192.168.100.11 (spark-1d84.local)

Copying your SSH public key to all discovered nodes using ssh-copy-id.
You may be prompted for your password on each node.
Copying SSH key to 192.168.100.10 ...
Copying SSH key to 192.168.100.11 ...
nvidia@192.168.100.11's password:

SSH key copy process complete. These two sparks can now talk to each other.
```

### Step 4. Install NVIDIA Container Toolkit & setup Docker environment

Ensure the NVIDIA drivers and the NVIDIA Container Toolkit are installed on each node (both manager and workers) that will provide GPU resources. This package enables Docker containers to access the host's GPU hardware. Ensure you complete the [installation steps](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html), including the [Docker configuration](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuring-docker) for NVIDIA Container Toolkit.

### Step 5. Enable resource advertising

First, find your GPU UUID by running:
```bash
nvidia-smi -a | grep UUID
```

Next, modify the Docker daemon configuration to advertise the GPU to Swarm. Edit /etc/docker/daemon.json:

```bash
sudo nano /etc/docker/daemon.json
```

Add or modify the file to include the nvidia runtime and GPU UUID (replace GPU-45cbf7b3-f919-7228-7a26-b06628ebefa1 with your actual GPU ID):

```json
{
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  },
  "default-runtime": "nvidia",
  "node-generic-resources": [
    "gpu=GPU-45cbf7b3-f919-7228-7a26-b06628ebefa1"
    ]
}
```

Modify the NVIDIA Container Runtime to advertise the GPUs to the Swarm by uncommenting the swarm-resource line in the config.toml file. You can do this either with your preferred text editor (e.g., vim, nano...) or with the following command:
```bash
sudo sed -i 's/^#\s*\(swarm-resource\s*=\s*".*"\)/\1/' /etc/nvidia-container-runtime/config.toml
```

Finally, restart the Docker daemon to apply all changes:
```bash
sudo systemctl restart docker
```

### Step 6. Initialize Docker Swarm

On whichever node you want to use as primary, run the following swarm initialization command
```bash
docker swarm init --advertise-addr $(ip -o -4 addr show enp1s0f0np0 | awk '{print $4}' | cut -d/ -f1) $(ip -o -4 addr show enp1s0f1np1 | awk '{print $4}' | cut -d/ -f1)
```

The typical output of the above would be similar to the following:
```
Swarm initialized: current node (node-id) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join --token <worker-token> <advertise-addr>:<port>

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```

### Step 7. Join worker nodes and deploy

Now we can proceed with setting up other nodes of your cluster.

Run the command suggested by the docker swarm init on each worker node to join the Docker swarm
```bash
docker swarm join --token <worker-token> <advertise-addr>:<port>
```

On your primary node, deploy the TRT-LLM multi-node stack by downloading the [**docker-compose.yml**](https://gitlab.com/nvidia/dgx-spark/temp-external-playbook-assets/dgx-spark-playbook-assets/-/blob/main/${MODEL}/assets/docker-compose.yml) and [**trtllm-mn-entrypoint.sh**](https://gitlab.com/nvidia/dgx-spark/temp-external-playbook-assets/dgx-spark-playbook-assets/-/blob/main/${MODEL}/assets/trtllm-mn-entrypoint.sh) files into your home directory and running the following command:

```bash
chmod +x $HOME/trtllm-mn-entrypoint.sh
docker stack deploy -c $HOME/docker-compose.yml trtllm-multinode
```
Note: Ensure you download both files into the same directory from which you are running the command.

You can verify the status of your worker nodes using the following
```bash
docker stack ps trtllm-multinode
```

If everything is healthy, you should see a similar output to the following:
```
nvidia@spark-1b3b:~$ docker stack ps trtllm-multinode
ID             NAME                            IMAGE                                          NODE         DESIRED STATE   CURRENT STATE             ERROR     PORTS
oe9k5o6w41le   trtllm-multinode_trtllm.1       nvcr.io/nvidia/tensorrt-llm/release:1.0.0rc3   spark-1d84   Running         Running 2 minutes ago
phszqzk97p83   trtllm-multinode_trtllm.2       nvcr.io/nvidia/tensorrt-llm/release:1.0.0rc3   spark-1b3b   Running         Running 2 minutes ago
```

### Step 8. Create hosts file

You can check the available nodes using `docker node ls`
```
nvidia@spark-1b3b:~$ docker node ls
ID                            HOSTNAME     STATUS    AVAILABILITY   MANAGER STATUS   ENGINE VERSION
hza2b7yisatqiezo33zx4in4i *   spark-1b3b   Ready     Active         Leader           28.3.3
m1k22g3ktgnx36qz4jg5fzhr4     spark-1d84   Ready     Active                          28.3.3
```

Generate a file containing all Docker Swarm node addresses for MPI operations, and then copy it over to your container:
```bash
docker node ls --format '{{.ID}}' | xargs -n1 docker node inspect --format '{{ .Status.Addr }}' > ~/openmpi-hostfile
docker cp ~/openmpi-hostfile $(docker ps -q -f name=trtllm-multinode):/etc/openmpi-hostfile
```

### Step 9. Find your Docker container ID

You can use `docker ps` to find your Docker container ID. Alternatively, you can save the container ID in a variable:
```bash
export TRTLLM_MN_CONTAINER=$(docker ps -q -f name=trtllm-multinode)
```

### Step 10. Generate configuration file

```bash
docker exec $TRTLLM_MN_CONTAINER bash -c 'cat <<EOF > /tmp/extra-llm-api-config.yml
print_iter_log: false
kv_cache_config:
  dtype: "auto"
  free_gpu_memory_fraction: 0.9
cuda_graph_config:
  enable_padding: true
EOF'
```

### Step 11. Download model

```bash
## Need to specify huggingface token for model download.
export HF_TOKEN=<your-huggingface-token>

docker exec \
  -e MODEL="nvidia/Qwen3-235B-A22B-FP4" \
  -e HF_TOKEN=$HF_TOKEN \
  -it $TRTLLM_MN_CONTAINER bash -c 'mpirun -x HF_TOKEN bash -c "huggingface-cli download $MODEL"'
```

### Step 12. Serve the model

```bash
docker exec \
  -e MODEL="nvidia/Qwen3-235B-A22B-FP4" \
  -e HF_TOKEN=$HF_TOKEN \
  -it $TRTLLM_MN_CONTAINER bash -c '
    mpirun -x HF_TOKEN trtllm-llmapi-launch trtllm-serve $MODEL \
      --tp_size 2 \
      --backend pytorch \
      --max_num_tokens 32768 \
      --max_batch_size 4 \
      --extra_llm_api_options /tmp/extra-llm-api-config.yml \
      --port 8000'
```

This will start the TensorRT-LLM server on port 8000. You can then make inference requests to `http://localhost:8000` using the OpenAI-compatible API format.

**Expected output:** Server startup logs and ready message.

### Step 13. Validate API server

Verify successful deployment by checking container status and testing the API endpoint.

```bash
docker stack ps trtllm-multinode
```

**Expected output:** Two running containers in the stack across different nodes.

Once the server is running, you can test it with a CURL request. Please ensure the CURL request is run on the primary node where you previously ran Step 11.

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nvidia/Qwen3-235B-A22B-FP4",
    "prompt": "What is artificial intelligence?",
    "max_tokens": 100,
    "temperature": 0.7,
    "stream": false
  }'
```

**Expected output:** JSON response with generated text completion.

### Step 15. Cleanup and rollback

Stop and remove containers by using the following command on the leader node:

```bash
docker stack rm trtllm-multinode
```

> **Warning:** This removes all inference data and performance reports. Copy `/opt/*perf-report.json` files before cleanup if needed.

Remove downloaded models to free disk space:

```bash
rm -rf $HOME/.cache/huggingface/hub/models--nvidia--Qwen3*
```

### Step 16. Next steps

Compare performance metrics between speculative decoding and baseline reports to quantify speed improvements. Use the multi-node setup as a foundation for deploying other large models requiring tensor parallelism, or scale to additional nodes for higher throughput workloads.

## Troubleshooting

## Common issues for running on a single Spark

| Symptom | Cause | Fix |
|---------|-------|-----|
| Cannot access gated repo for URL | Certain HuggingFace models have restricted access | Regenerate your [HuggingFace token](https://huggingface.co/docs/hub/en/security-tokens); and request access to the [gated model](https://huggingface.co/docs/hub/en/models-gated#customize-requested-information) on your web browser |
| OOM during weight loading (e.g., [Nemotron Super 49B](https://huggingface.co/nvidia/Llama-3_3-Nemotron-Super-49B-v1_5)) | Parallel weight-loading memory pressure | `export TRT_LLM_DISABLE_LOAD_WEIGHTS_IN_PARALLEL=1` |
| "CUDA out of memory" | GPU VRAM insufficient for model | Reduce `free_gpu_memory_fraction: 0.9` or batch size or use smaller model |
| "Model not found" error | HF_TOKEN invalid or model inaccessible | Verify token and model permissions |
| Container pull timeout | Network connectivity issues | Retry pull or use local mirror |
| Import tensorrt_llm fails | Container runtime issues | Restart Docker daemon and retry |

## Common Issues for running on two Starks

| Symptom | Cause | Fix |
|---------|-------|-----|
| MPI hostname test returns single hostname | Network connectivity issues | Verify both nodes are on reachable IP addresses |
| "Permission denied" on HuggingFace download | Invalid or missing HF_TOKEN | Set valid token: `export HF_TOKEN=<TOKEN>` |
| Cannot access gated repo for URL | Certain HuggingFace models have restricted access | Regenerate your [HuggingFace token](https://huggingface.co/docs/hub/en/security-tokens); and request access to the [gated model](https://huggingface.co/docs/hub/en/models-gated#customize-requested-information) on your web browser |
| "CUDA out of memory" errors | Insufficient GPU memory | Reduce `--max_batch_size` or `--max_num_tokens` |
| Container exits immediately | Missing entrypoint script | Ensure `trtllm-mn-entrypoint.sh` download succeeded and has executable permissions, also ensure you are not running the container already on your node. If port 2233 is already utilized, the entrypoint script will not start. |

> **Note:** DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
