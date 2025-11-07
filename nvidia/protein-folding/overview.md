# What you'll accomplish

You'll set up a GPU-accelerated protein folding workflow on NVIDIA Spark devices using OpenFold
with TensorRT optimization and MMseqs2-GPU. After completing this walkthrough, you'll be able to
fold proteins in under 60 seconds using either NVIDIA's cloud UI or running locally on your
RTX Pro 6000 or DGX Spark workstation.

# What to know before starting

- Installing Python packages via pip
- Using Docker and the NVIDIA Container Toolkit for GPU workflows
- Running basic Linux commands and setting environment variables
- Understanding FASTA files and basics of protein structure workflows
- Working with CUDA-enabled applications

# Prerequisites

- NVIDIA GPU (RTX Pro 6000 or DGX Spark recommended)
```bash
nvidia-smi  # Should show GPU with CUDA ≥12.9
```
- NVIDIA drivers and CUDA toolkit installed
```bash
nvcc --version  # Should show CUDA 12.9 or higher
```
- Docker with NVIDIA Container Toolkit
```bash
docker run --rm --gpus all nvidia/cuda:12.9.0-base-ubuntu22.04 nvidia-smi
```
- Python 3.8+ environment
```bash
python3 --version  # Should show 3.8 or higher
```
- Sufficient disk space for databases (>3TB recommended)
```bash
df -h  # Check available space
```

# Ancillary files

- OpenFold parameters (`finetuning_ptm_2.pt`) — pre-trained model weights for structure prediction
- PDB70 database — template structures for homology modeling
- UniRef90 database — sequence database for MSA generation
- MGnify database — metagenomic sequences for MSA generation
- Uniclust30 database — clustered UniProt sequences for MSA generation
- BFD database — large sequence database for MSA generation
- MMCIF files — template structure files in mmCIF format
- py3Dmol package — Python library for 3D protein visualization

# Time & risk

**Duration:** Initial setup takes 2-4 hours (mainly downloading databases). Each protein fold takes
<60 seconds on GPU vs hours on CPU.

**Risks:**
- Database downloads may fail due to network interruptions
- Insufficient disk space for full databases
- GPU memory limitations for very large proteins (>2000 residues)

**Rollback:** All operations are read-only after setup. Remove downloaded databases and output
directories to clean up.
