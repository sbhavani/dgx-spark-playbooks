<!--
#!/bin/bash
#
# SPDX-FileCopyrightText: Copyright (c) 1993-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
-->

# TensorRT-LLM on Stacked Spark Instructions

## Step 1. Setup networking between nodes
Configure network interfaces using netplan on both DGX Spark nodes:

```bash
# On both nodes, create the netplan configuration file (also available in cx7-netplan.yaml in this repository)
sudo tee /etc/netplan/40-cx7.yaml > /dev/null <<EOF
network:
  version: 2
  ethernets:
    enp1s0f0np0:
      link-local: [ ipv4 ]
    enp1s0f1np1:
      link-local: [ ipv4 ]
EOF

# On both nodes, set appropriate permissions
sudo chmod 600 /etc/netplan/40-cx7.yaml

# On both nodes, apply the netplan configuration
sudo netplan apply
```

## Step 2: Run the DGX Spark discovery script
Automatically identify DGX Spark systems interconnected, and setup SSH passwordless authentication.
```
# On either node, run the following
$ ./discover-sparks
Found: 192.168.100.10 (spark-1b3b.local)
Found: 192.168.100.11 (spark-1d84.local)

Copying your SSH public key to all discovered nodes using ssh-copy-id.
You may be prompted for your password on each node.
Copying SSH key to 192.168.100.10 ...
Copying SSH key to 192.168.100.11 ...
nvidia@192.168.100.11's password:

SSH key copy process complete. These two sparks can now talk to each other.
```

## Step 3: Setup Docker Swarm with GPU support

### Substep A: Install NVIDIA Container Toolkit
Ensure the NVIDIA drivers and the NVIDIA Container Toolkit are installed on each node (both manager and workers) that will provide GPU resources. This package enables Docker containers to access the host's GPU hardware. Ensure you complete the [installation steps](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html), including the [Docker configuration](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuring-docker) for NVIDIA Container Toolkit.

### Substep B: Enable resource advertising
Modify the NVIDIA Container Runtime to advertise the GPUs to the Swarm by uncommenting the swarm-resource line in the config.toml file. You can do this either with your preferred text editor (e.g., vim, nano...) or with the following command:
```bash
sudo sed -i 's/^#\s*\(swarm-resource\s*=\s*".*"\)/\1/' /etc/nvidia-container-runtime/config.toml
```
To apply the changes, restart the Docker daemon
```
sudo systemctl restart docker
```

# Step 4: Run inference in TRT-LLM
### Substep A: Initialize Docker Swarm
On whichever node you want to use as primary, run the following swarm inititalization command
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

### Substep B: Join worker nodes and deploy
Now we can proceed with setting up other nodes of your cluster:

```bash
# Run the command suggested by the docker swarm init on each worker node to join the Docker swarm
docker swarm join --token <worker-token> <advertise-addr>:<port>

# On your primary node, deploy the stack using the following command
docker stack deploy -c docker-compose.yml trtllm-multinode

# You can verify the status of your worker nodes using the following
docker stack ps trtllm-multinode

# In case you see any errors reported by docker ps for any node, you can verify using
docker service logs <ID>
```

If everything is healthy, you should see a similar output to the following:
```
nvidia@spark-1b3b:~/draft-playbooks/trt-llm-on-stacked-spark$ docker stack ps trtllm-multinode
ID             NAME                            IMAGE                                          NODE         DESIRED STATE   CURRENT STATE             ERROR     PORTS
oe9k5o6w41le   trtllm-multinode_trtllm.1       nvcr.io/nvidia/tensorrt-llm/release:1.0.0rc3   spark-1d84   Running         Running 2 minutes ago
phszqzk97p83   trtllm-multinode_trtllm.2       nvcr.io/nvidia/tensorrt-llm/release:1.0.0rc3   spark-1b3b   Running         Running 2 minutes ago
```

### Substep C. Create hosts file


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

### Substep D. Find your Docker container ID
You can use `docker ps` to find your Docker container ID. Alternatively, you can save the container ID in a variable:
```
export TRTLLM_MN_CONTAINER=$(docker ps -q -f name=trtllm-multinode)
```

### Substep E. Generate configuration file

```bash
docker exec $TRTLLM_MN_CONTAINER bash -c 'cat <<EOF > /tmp/extra-llm-api-config.yml
print_iter_log: false
kv_cache_config:
  dtype: "fp8"
  free_gpu_memory_fraction: 0.9
cuda_graph_config:
  enable_padding: true
EOF'
```

### Substep F. Download model

```bash
docker exec \
  -e MODEL="nvidia/Qwen3-235B-A22B-FP4" \
  -e HF_TOKEN="hf_..." \
  -it $TRTLLM_MN_CONTAINER bash -c 'mpirun -x HF_TOKEN bash -c "huggingface-cli download $MODEL"'
```

### Substep G. Prepare dataset and benchmark

```bash
docker exec \
  -e ISL=128 -e OSL=128 \
  -e MODEL="nvidia/Qwen3-235B-A22B-FP4" \
  -e HF_TOKEN="" \
  -it $TRTLLM_MN_CONTAINER bash -c '
    mpirun -x HF_TOKEN bash -c "python benchmarks/cpp/prepare_dataset.py --tokenizer=$MODEL --stdout token-norm-dist --num-requests=1 --input-mean=$ISL --output-mean=$OSL --input-stdev=0 --output-stdev=0 > /tmp/dataset.txt" && \
    mpirun -x HF_TOKEN trtllm-llmapi-launch trtllm-bench -m $MODEL throughput \
      --tp 2 \
      --dataset /tmp/dataset.txt \
      --backend pytorch \
      --max_num_tokens 4096 \
      --concurrency 1 \
      --max_batch_size 4 \
      --extra_llm_api_options /tmp/extra-llm-api-config.yml \
      --streaming'
```

### Substep H. Serve the model

```bash
docker exec \
  -e MODEL="nvidia/Qwen3-235B-A22B-FP4" \
  -e HF_TOKEN="" \
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

### Example inference request

Once the server is running, you can test it with a CURL request. Please ensure the CURL request is run on the primary node where you previously ran Substep H.

```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nvidia/Qwen3-235B-A22B-FP4",
    "prompt": "What is artificial intelligence?",
    "max_tokens": 100,
    "temperature": 0.7,
    "stream": false
  }'
```

## Step 6. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| MPI hostname test returns single hostname | Network connectivity issues | Verify both nodes are on 192.168.100.0/24 subnet |
| "Permission denied" on HuggingFace download | Invalid or missing HF_TOKEN | Set valid token: `export HF_TOKEN=<TOKEN>` |
| "CUDA out of memory" errors | Insufficient GPU memory | Reduce `--max_batch_size` or `--max_num_tokens` |
| Container exits immediately | Missing entrypoint script | Ensure `trtllm-mn-entrypoint.sh` download succeeded and has executable permissions |

## Step 7. Cleanup and rollback

Stop and remove containers by using the following command on the leader node:

```bash
docker stack rm trtllm-multinode
```

> **Warning:** This removes all inference data and performance reports. Copy `/opt/*perf-report.json` files before cleanup if needed.

Remove downloaded models to free disk space:

```bash
rm -rf $HOME/.cache/huggingface/hub/models--nvidia--Qwen3*
```

## Step 8. Next steps

Compare performance metrics between speculative decoding and baseline reports to quantify speed improvements. Use the multi-node setup as a foundation for deploying other large models requiring tensor parallelism, or scale to additional nodes for higher throughput workloads.
