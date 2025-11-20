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

On both nodes, download the [**pytorch-ft-entrypoint.sh**](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/pytorch-ft-entrypoint.sh) script into the directory containing your finetuning scripts and configuration files and run the following command to make it executable:

```bash
chmod +x $PWD/pytorch-ft-entrypoint.sh
```

On your primary node, deploy the Finetuning multi-node stack by downloading the [**docker-compose.yml**](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/docker-compose.yml) file into the same directory as in the previous step and running the following command:
```bash
docker stack deploy -c $PWD/docker-compose.yml finetuning-multinode
```
> [!NOTE]
> Ensure you download both files into the same directory from which you are running the command.

You can verify the status of your worker nodes using the following
```bash
docker stack ps finetuning-multinode
```

If everything is healthy, you should see a similar output to the following:
```
nvidia@spark-1b3b:~$ docker stack ps finetuning-multinode
ID             NAME                                IMAGE                              NODE         DESIRED STATE   CURRENT STATE            ERROR     PORTS
vlun7z9cacf9   finetuning-multinode_finetunine.1   nvcr.io/nvidia/pytorch:25.10-py3   spark-1d84   Running         Starting 2 seconds ago             
tjl49zicvxoi   finetuning-multinode_finetunine.2   nvcr.io/nvidia/pytorch:25.10-py3   spark-1b3b   Running         Starting 2 seconds ago             

```

> [!NOTE]
> If your "Current state" is not "Running", see troubleshooting section for more information.

## Step 7. Find your Docker container ID

You can use `docker ps` to find your Docker container ID. You can save the container ID in a variable as shown below. Run this command on both nodes.
```bash
export FINETUNING_CONTAINER=$(docker ps -q -f name=finetuning-multinode)
```

## Step 9. Adapt the configuration files

For multi-node runs, we provide 2 configuration files:
- [**config_finetuning.yaml**](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/configs/config_finetuning.yaml) used for full finetuning of Llama3 3B.
- [**config_fsdp_lora.yaml**](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/configs/config_fsdp_lora.yaml) used for finetuning with LoRa and FSDP of Llama3 8B and Llama3 70B.

These configuration files need to be adapted:
- Set `machine_rank` on each of your nodes according to its rank. Your master node should have a rank `0`. The second node has a rank `1`.
- Set the correct IP address of your master node. Use `ifconfig` to find the correct value for your CX-7 IP address.
- Set a port number that can be used on your main node.

The fields that need to be filled in your YAML files:

```bash
machine_rank: 0
main_process_ip: < TODO: specify IP >
main_process_port: < TODO: specify port >
```

## Step 10. Run finetuning scripts

Once you successfully run the previous steps, you can use one of the `run-multi-llama_*` scripts for finetuning. Here is an example for Llama3 70B using LoRa for finetuning and FSDP2.

```bash
# Need to specify huggingface token for model download.
export HF_TOKEN=<your-huggingface-token>

docker exec \
  -e HF_TOKEN=$HF_TOKEN \
  -it $FINETUNING_CONTAINER bash -c '
  bash /workspace/install-requirements;
  accelerate launch --config_file=/workspace/configs/config_fsdp_lora.yaml /workspace/Llama3_70B_LoRA_finetuning.py'
```

## Step 14. Cleanup and rollback

Stop and remove containers by using the following command on the leader node:

```bash
docker stack rm finetuning-multinode
```

Remove downloaded models to free disk space:

```bash
rm -rf $HOME/.cache/huggingface/hub/models--meta-llama* $HOME/.cache/huggingface/hub/datasets*
```