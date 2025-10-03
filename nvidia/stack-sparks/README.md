# Stack two Sparks

> Connect two Spark devices and setup them up for inference and fine-tuning

## Table of Contents

- [Overview](#overview)
- [Run on two Sparks](#run-on-two-sparks)
  - [Option 1: Automatic IP Assignment (Recommended)](#option-1-automatic-ip-assignment-recommended)
  - [Option 2: Manual IP Assignment (Advanced)](#option-2-manual-ip-assignment-advanced)

---

## Overview

## Basic Idea

Configure two DGX Spark systems for high-speed inter-node communication using 200GbE direct
QSFP connections and NCCL multi-node communication. This setup enables distributed training
and inference workloads across multiple Blackwell GPUs by establishing network connectivity,
configuring SSH authentication, and validating communication with NCCL performance tests.

## What you'll accomplish

You will physically connect two DGX Spark devices with a QSFP cable, configure network
interfaces for cluster communication, establish passwordless SSH between nodes, and validate
the setup with NCCL multi-node tests to create a functional distributed computing environment.

## What to know before starting

- Working with network interface configuration and netplan
- Using Docker containers with GPU and network access
- Basic understanding of distributed computing concepts
- Experience with SSH key management
- Familiarity with NVIDIA GPU architectures and CUDA environments

## Prerequisites

- [ ] Two DGX Spark systems with NVIDIA Blackwell GPUs available
- [ ] QSFP cable for direct 200GbE connection between devices
- [ ] Docker installed on both systems: `docker --version`
- [ ] CUDA toolkit installed: `nvcc --version` (should show 12.9 or higher)
- [ ] SSH access available on both systems: `ssh-keygen -t rsa` (if keys don't exist)
- [ ] Git available for source code compilation: `git --version`
- [ ] Root or sudo access on both systems: `sudo whoami`

## Ancillary files

All required files for this playbook can be found [here on GitHub](https://gitlab.com/nvidia/dgx-spark/temp-external-playbook-assets/dgx-spark-playbook-assets/-/blob/main/${MODEL}/)

- `discover-sparks` script for automatic node discovery and SSH key distribution
- `trtllm-mn-entrypoint.sh` container entrypoint script for multi-node setup
- Network interface mapping tools (`ibdev2netdev`, `ip link show`)

## Time & risk

**Duration:** 2-3 hours including validation tests
**Risk level:** Medium - involves network reconfiguration and container setup
**Rollback:** Network changes can be reversed by removing netplan configs or IP assignments

## Run on two Sparks

## Step 1. Physical Hardware Connection

Connect the QSFP cable between both DGX Spark systems using the rightmost QSFP interface
on each device. This establishes the 200GbE direct connection required for high-speed
inter-node communication.

```bash
## Check QSFP interface availability on both nodes
ip link show | grep enP2p1s0f1np1
```

Expected output shows the interface exists but may be down initially.

## Step 2. Network Interface Configuration

Choose one option based on your network requirements.

### Option 1: Automatic IP Assignment (Recommended)

Configure network interfaces using netplan on both DGX Spark nodes for automatic
link-local addressing:

```bash
## On both nodes, create the netplan configuration file
sudo tee /etc/netplan/40-cx7.yaml > /dev/null <<EOF
network:
  version: 2
  ethernets:
    enp1s0f0np0:
      link-local: [ ipv4 ]
    enp1s0f1np1:
      link-local: [ ipv4 ]
EOF

## On both nodes, set appropriate permissions
sudo chmod 600 /etc/netplan/40-cx7.yaml

## On both nodes, apply the netplan configuration
sudo netplan apply
```

### Option 2: Manual IP Assignment (Advanced)

Configure dedicated cluster networking with static IP addresses:

```bash
## On Node 1
sudo ip addr add 192.168.100.10/24 dev enP2p1s0f1np1
sudo ip link set enP2p1s0f1np1 up

## On Node 2
sudo ip addr add 192.168.100.11/24 dev enP2p1s0f1np1
sudo ip link set enP2p1s0f1np1 up

## Verify connectivity from Node 1
ping -c 3 192.168.100.11

## Verify connectivity from Node 2
ping -c 3 192.168.100.10
```

## Step 3. SSH Key Distribution

Automatically identify interconnected DGX Spark systems and configure SSH passwordless
authentication for multi-node operations. This step runs on either node.

```bash
## On either node, run the discovery script
./discover-sparks
```

Expected output:
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

## Step 4. Network Interface Validation

Check which ConnectX-7 network interfaces are active and available for communication:

```bash
ibdev2netdev
```

Expected output (showing "Up" for active interfaces):
```
rocep1s0f0 port 1 ==> enp1s0f0np0 (Up)
rocep1s0f1 port 1 ==> enp1s0f1np1 (Down)
roceP2p1s0f0 port 1 ==> enP2p1s0f0np0 (Up)
roceP2p1s0f1 port 1 ==> enP2p1s0f1np1 (Down)
```

Note the active interface names (marked "Up") for use in container configuration.

## Step 5. Launch Containers with Network Configuration

Start containers with appropriate network and GPU configuration for NCCL communication.
This step runs on both nodes.

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

## Step 6. Build NCCL with Blackwell Support

Execute these commands inside both containers to build NCCL from source with Blackwell
architecture support. Access the container with `docker exec -it trtllm bash`.

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

## Step 7. Build NCCL Test Suite

Compile the NCCL test suite to validate communication performance. This runs inside
both containers.

```bash
## Clone and build NCCL tests
git clone https://github.com/NVIDIA/nccl-tests.git /opt/nccl-tests/
cd /opt/nccl-tests/
make MPI=1
```

## Step 8. Run NCCL Communication Test

Execute multi-node NCCL performance test using the active network interface. This runs
from one of the containers.

```bash
## Set network interface environment variables (use your active interface from Step 4)
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

## Step 9. Validate NCCL Installation

Verify successful NCCL compilation and multi-node communication by checking built
components.

```bash
## Check NCCL library build
ls -la /opt/nccl/build/lib/

## Verify NCCL test binaries
ls -la /opt/nccl-tests/build/

## Check MPI configuration
mpirun --version
```

Expected output should show NCCL libraries in `/opt/nccl/build/lib/` and test binaries
in `/opt/nccl-tests/build/`.

## Step 10. Performance Validation

Review the all_gather test output for communication performance metrics from Step 8.

Expected metrics from the test output:
- Bandwidth measurements between nodes
- Latency for different message sizes
- GPU-to-GPU communication confirmation
- No error messages or communication failures

## Step 11. Additional NCCL Tests

Run additional performance validation tests to verify the complete setup.

```bash
## Example: Run a simple NCCL bandwidth test
/opt/nccl-tests/build/all_reduce_perf -b 1M -e 1G -f 2

## Example: Verify GPU topology detection
nvidia-smi topo -m
```

## Step 12. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Network unreachable" errors | Network interfaces not configured | Verify netplan config and `sudo netplan apply` |
| SSH authentication failures | SSH keys not properly distributed | Re-run `./discover-sparks` and enter passwords |
| NCCL build failures with Blackwell | Wrong compute capability specified | Verify `NVCC_GENCODE="-gencode=arch=compute_121,code=sm_121"` |
| MPI communication timeouts | Wrong network interfaces specified | Check `ibdev2netdev` and update interface names |
| Container networking issues | Host network mode problems | Ensure `--network host --ipc=host` in docker run |
| Node 2 not visible in cluster | Network connectivity issue | Verify QSFP cable connection, check IP configuration |

## Step 13. Cleanup and Rollback

> **Warning**: These steps will stop containers and reset network configuration.

```bash
## Stop containers on both nodes
docker stop trtllm
docker rm trtllm

## Rollback network configuration (if using Option 1)
sudo rm /etc/netplan/40-cx7.yaml
sudo netplan apply

## Rollback network configuration (if using Option 2)
sudo ip addr del 192.168.100.10/24 dev enP2p1s0f1np1  # Node 1
sudo ip addr del 192.168.100.11/24 dev enP2p1s0f1np1  # Node 2
sudo ip link set enP2p1s0f1np1 down
```

## Step 14. Next Steps

Your NCCL environment is ready for multi-node distributed training workloads on DGX Spark
systems with Blackwell GPUs.

```bash
## Test basic multi-node functionality
mpirun -np 2 -H 192.168.100.10:1,192.168.100.11:1 hostname

## Verify GPU visibility across nodes
mpirun -np 2 -H 192.168.100.10:1,192.168.100.11:1 nvidia-smi -L
```
