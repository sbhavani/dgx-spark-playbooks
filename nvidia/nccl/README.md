# NCCL for Two Sparks

> Install and test NCCL on two Sparks

## Table of Contents

- [Overview](#overview)
- [Run on two Sparks](#run-on-two-sparks)

---

## Overview

## Basic idea

NCCL (NVIDIA Collective Communication Library) enables high-performance GPU-to-GPU communication
across multiple nodes. This walkthrough sets up NCCL for multi-node distributed training on
DGX Spark systems with Blackwell architecture. You'll configure networking, build NCCL from
source with Blackwell support, and validate communication performance between nodes.

## What you'll accomplish

You'll have a working multi-node NCCL environment that enables high-bandwidth GPU communication
across DGX Spark systems for distributed training workloads, with validated network performance
and proper GPU topology detection.

## What to know before starting

- Working with Linux network configuration and netplan
- Docker container management and multi-container deployments
- Basic understanding of MPI (Message Passing Interface) concepts
- SSH key management and passwordless authentication setup
- NVIDIA GPU architecture fundamentals and CUDA toolkit usage

## Prerequisites

- Two DGX Spark systems with Blackwell GPUs: `nvidia-smi --query-gpu=gpu_name --format=csv`
- ConnectX-7 InfiniBand network cards installed: `ibdev2netdev`
- Docker installed on both nodes: `docker --version`
- CUDA toolkit available: `nvcc --version`
- SSH access between nodes: `ssh <OTHER_NODE_IP> echo "success"`
- Root/sudo privileges: `sudo whoami`

## Ancillary files

- `cx7-netplan.yaml` - Network configuration template for ConnectX-7 interfaces
- `discover-sparks` - Script to discover DGX Spark nodes and configure SSH keys
- `trtllm-mn-entrypoint.sh` - Container entrypoint script for multi-node setup

## Time & risk

**Duration**: 45-60 minutes for setup and validation

**Risk level**: Medium - involves network configuration changes and container networking

**Rollback**: Network changes can be reverted using `sudo netplan apply` with original configs,
containers can be stopped with `docker stop`

## Run on two Sparks

## Step 1. Configure network connectivity

Follow the network setup instructions from the Connect two Sparks playbook to establish connectivity between your DGX Spark nodes.

This includes:
- Physical QSFP cable connection
- Network interface configuration (automatic or manual IP assignment)
- Passwordless SSH setup
- Network connectivity verification

## Step 2. Launch TensorRT-LLM containers on both nodes

Start containers with appropriate network and GPU configuration for NCCL communication:

```bash
## On both nodes, launch the container
docker run --name trtllm --rm -d \
  --gpus all --network host --ipc=host \
  --ulimit memlock=-1 --ulimit stack=67108864 \
  -e UCX_NET_DEVICES=enp1s0f0np0,enp1s0f1np1 \
  -e NCCL_SOCKET_IFNAME=enp1s0f0np0,enp1s0f1np1 \
  -e OMPI_MCA_btl_tcp_if_include=enp1s0f0np0,enp1s0f1np1 \
  -e OMPI_ALLOW_RUN_AS_ROOT=1 \
  -e OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 \
  -v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
  -v ./trtllm-mn-entrypoint.sh:/opt/trtllm-mn-entrypoint.sh \
  -v ~/.ssh:/tmp/.ssh:ro \
  --entrypoint /opt/trtllm-mn-entrypoint.sh \
  nvcr.io/nvidia/tensorrt-llm/release:1.0.0rc3
```

## Step 3. Build NCCL with Blackwell support

Execute these commands inside both containers to build NCCL from source with Blackwell
architecture support:

```bash
## Install dependencies and build NCCL
sudo apt-get update && sudo apt-get install -y libopenmpi-dev
git clone -b v2.28.3-1 https://github.com/NVIDIA/nccl.git /opt/nccl/
cd /opt/nccl/
make -j src.build NVCC_GENCODE="-gencode=arch=compute_121,code=sm_121"

## Set environment variables
export MPI_HOME="/usr/lib/aarch64-linux-gnu/openmpi"
export NCCL_HOME="/opt/nccl/build/"
export LD_LIBRARY_PATH="$NCCL_HOME/lib:$CUDA_HOME/lib64/:$MPI_HOME/lib:$LD_LIBRARY_PATH"
```

## Step 4. Build NCCL test suite

Compile the NCCL test suite to validate communication performance:

```bash
## Clone and build NCCL tests
git clone https://github.com/NVIDIA/nccl-tests.git /opt/nccl-tests/
cd /opt/nccl-tests/
make MPI=1
```

## Step 5. Run NCCL communication test

Execute multi-node NCCL performance test using the active network interface:

```bash
## Set network interface environment variables (use your active interface from Step 3)
export UCX_NET_DEVICES=enp1s0f0np0
export NCCL_SOCKET_IFNAME=enp1s0f0np0
export OMPI_MCA_btl_tcp_if_include=enp1s0f0np0

## Run the all_gather performance test across both nodes
mpirun -np 2 -H 192.168.100.10:1,192.168.100.11:1 \
  -x NCCL_DEBUG=VERSION -x NCCL_DEBUG_SUBSYS=TUNING \
  -x LD_LIBRARY_PATH=$LD_LIBRARY_PATH \
  -x NCCL_MERGE_LEVEL=SYS -x NCCL_PROTO="SIMPLE" \
  /opt/nccl-tests/build/all_gather_perf -b 32G -e 32G -f 2
```

## Step 6. Validate NCCL installation

Verify successful NCCL compilation and multi-node communication:

```bash
## Check NCCL library build
ls -la /opt/nccl/build/lib/

## Verify NCCL test binaries
ls -la /opt/nccl-tests/build/

## Check MPI configuration
mpirun --version
```

Expected output should show NCCL libraries in `/opt/nccl/build/lib/` and test binaries in
`/opt/nccl-tests/build/`.

## Step 7. Cleanup and rollback

**Warning**: These steps will stop containers and reset network configuration.

```bash
## Stop containers on both nodes
docker stop trtllm

## Remove containers (optional)
docker rm trtllm

## Rollback network configuration (if needed)
sudo rm /etc/netplan/40-cx7.yaml
sudo netplan apply
```

## Step 8. Next steps

Test your NCCL setup with a simple distributed training example:

```bash
## Example: Run a simple NCCL bandwidth test
/opt/nccl-tests/build/all_reduce_perf -b 1M -e 1G -f 2

## Example: Verify GPU topology detection
nvidia-smi topo -m
```

Your NCCL environment is ready for multi-node distributed training workloads on DGX Spark
systems with Blackwell GPUs.
