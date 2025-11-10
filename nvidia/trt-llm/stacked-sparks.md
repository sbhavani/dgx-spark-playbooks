## Step 1. Configure network connectivity

Follow the network setup instructions from the [Connect two Sparks](https://build.nvidia.com/spark/connect-two-sparks/stacked-sparks) playbook to establish connectivity between your DGX Spark nodes.

This includes:
- Physical QSFP cable connection
- Network interface configuration (automatic or manual IP assignment)
- Passwordless SSH setup
- Network connectivity verification

## Step 2. Configure Docker permissions

To easily manage containers without sudo, you must be in the `docker` group. If you choose to skip this step, you will need to run Docker commands with sudo.

Open a new terminal and test Docker access. In the terminal, run:

```bash
docker ps
```

If you see a permission denied error (something like permission denied while trying to connect to the Docker daemon socket), add your user to the docker group so that you don't need to run the command with sudo .

```bash
sudo usermod -aG docker $USER
newgrp docker
```
## Step 3. Install NVIDIA Container Toolkit & setup Docker environment

Ensure the NVIDIA drivers and the NVIDIA Container Toolkit are installed on each node (both manager and workers) that will provide GPU resources. This package enables Docker containers to access the host's GPU hardware. Ensure you complete the [installation steps](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html), including the [Docker configuration](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuring-docker) for NVIDIA Container Toolkit.

## Step 4. Enable resource advertising

First, find your GPU UUID by running:
```bash
nvidia-smi -a | grep UUID
```

Next, modify the Docker daemon configuration to advertise the GPU to Swarm. Edit **/etc/docker/daemon.json**:

```bash
sudo nano /etc/docker/daemon.json
```

Add or modify the file to include the nvidia runtime and GPU UUID (replace **GPU-45cbf7b3-f919-7228-7a26-b06628ebefa1** with your actual GPU UUID):

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
    "NVIDIA_GPU=GPU-45cbf7b3-f919-7228-7a26-b06628ebefa1"
    ]
}
```

Modify the NVIDIA Container Runtime to advertise the GPUs to the Swarm by uncommenting the swarm-resource line in the **config.toml** file. You can do this either with your preferred text editor (e.g., vim, nano...) or with the following command:
```bash
sudo sed -i 's/^#\s*\(swarm-resource\s*=\s*".*"\)/\1/' /etc/nvidia-container-runtime/config.toml
```

Finally, restart the Docker daemon to apply all changes:
```bash
sudo systemctl restart docker
```

Repeat these steps on all nodes.

## Step 5. Initialize Docker Swarm

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

## Step 6. Join worker nodes and deploy

Now we can proceed with setting up the worker nodes of your cluster. Repeat these steps on all worker nodes.

Run the command suggested by the docker swarm init on each worker node to join the Docker swarm
```bash
docker swarm join --token <worker-token> <advertise-addr>:<port>
```

On both nodes, download the [**trtllm-mn-entrypoint.sh**](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/trtllm-mn-entrypoint.sh) script into your home directory and run the following command to make it executable:

```bash
chmod +x $HOME/trtllm-mn-entrypoint.sh
```

On your primary node, deploy the TRT-LLM multi-node stack by downloading the [**docker-compose.yml**](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/docker-compose.yml) file into your home directory and running the following command:
```bash
docker stack deploy -c $HOME/docker-compose.yml trtllm-multinode
```
> [!NOTE]
> Ensure you download both files into the same directory from which you are running the command.

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

> [!NOTE]
> If your "Current state" is not "Running", see troubleshooting section for more information.

## Step 7. Create hosts file

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

## Step 8. Find your Docker container ID

You can use `docker ps` to find your Docker container ID. Alternatively, you can save the container ID in a variable:
```bash
export TRTLLM_MN_CONTAINER=$(docker ps -q -f name=trtllm-multinode)
```

## Step 9. Generate configuration file

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

## Step 10. Download model

We can download a model using the following command. You can replace `nvidia/Qwen3-235B-A22B-FP4` with the model of your choice.
```bash
# Need to specify huggingface token for model download.
export HF_TOKEN=<your-huggingface-token>

docker exec \
  -e MODEL="nvidia/Qwen3-235B-A22B-FP4" \
  -e HF_TOKEN=$HF_TOKEN \
  -it $TRTLLM_MN_CONTAINER bash -c 'mpirun -x HF_TOKEN bash -c "huggingface-cli download $MODEL"'
```

## Step 11. Serve the model

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
      --port 8355'
```

This will start the TensorRT-LLM server on port 8355. You can then make inference requests to `http://localhost:8355` using the OpenAI-compatible API format.

> [!NOTE]
> You might see a warning such as `UCX  WARN  network device 'enp1s0f0np0' is not available, please use one or more of`. You can ignore this warning if your inference is successful, as it's related to only one of your two CX-7 ports being used, and the other being left unused.

**Expected output:** Server startup logs and ready message.

## Step 12. Validate API server
Once the server is running, you can test it with a CURL request. Please ensure the CURL request is run on the primary node where you previously ran Step 11.

```bash
curl -s http://localhost:8355/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nvidia/Qwen3-235B-A22B-FP4",
    "messages": [{"role": "user", "content": "Paris is great because"}],
    "max_tokens": 64
  }'
```

**Expected output:** JSON response with generated text completion.

## Step 14. Cleanup and rollback

Stop and remove containers by using the following command on the leader node:

```bash
docker stack rm trtllm-multinode
```

> [!WARNING]
> This removes all inference data and performance reports. Copy `/opt/*perf-report.json` files before cleanup if needed.

Remove downloaded models to free disk space:

```bash
rm -rf $HOME/.cache/huggingface/hub/models--nvidia--Qwen3*
```

## Step 15. Next steps

You can now deploy other models on your DGX Spark cluster.
