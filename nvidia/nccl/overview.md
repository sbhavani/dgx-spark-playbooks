# Basic idea

NCCL (NVIDIA Collective Communication Library) enables high-performance GPU-to-GPU communication
across multiple nodes. This walkthrough sets up NCCL for multi-node distributed training on
DGX Spark systems with Blackwell architecture. You'll configure networking, build NCCL from
source with Blackwell support, and validate communication between nodes.

# What you'll accomplish

You'll have a working multi-node NCCL environment that enables high-bandwidth GPU communication
across DGX Spark systems for distributed training workloads, with validated network performance
and proper GPU topology detection.

# What to know before starting

- Working with Linux network configuration and netplan
- Basic understanding of MPI (Message Passing Interface) concepts
- SSH key management and passwordless authentication setup

# Prerequisites

- Two DGX Spark systems
- Completed the Connect two Sparks playbook
- NVIDIA driver installed: `nvidia-smi`
- CUDA toolkit available: `nvcc --version`
- Root/sudo privileges: `sudo whoami`

# Time & risk

- **Duration**: 30 minutes for setup and validation
- **Risk level**: Medium - involves network configuration changes
- **Rollback**: The NCCL & NCCL Tests repositories can be deleted from DGX Spark
