# Step 1. Verify system prerequisites

Confirm your NVIDIA Spark system meets the requirements and has GPU access configured.

```bash
# Verify GPU access
nvidia-smi

# Verify ARM64 architecture  
uname -m

# Check Docker GPU support
docker run --gpus all --rm nvcr.io/nvidia/cuda:13.0.1-runtime-ubuntu24.04 nvidia-smi
```

If you see a permission denied error (something like permission denied while trying to connect to the Docker daemon socket), add your user to the docker group so that you don't need to run the command with sudo .

```bash
sudo usermod -aG docker $USER
newgrp docker
```

# Step 2. Clone the playbook repository

```bash
git clone ${GITLAB_REPO_BASEURL}
```

# Step 3. Build the Docker image


> [!WARNING]
> This command will download a base image and build a container locally to support this environment.

```bash
cd jax/assets
docker build -t jax-on-spark .
```

# Step 4. Launch Docker container

Run the JAX development environment in a Docker container with GPU support and port forwarding for marimo access.

```bash
docker run --gpus all --rm -it \
  --shm-size=1g --ulimit memlock=-1 --ulimit stack=67108864 \
  -p 8080:8080 \
  jax-on-spark
```

# Step 5. Access the marimo interface

Connect to the marimo notebook server to begin the JAX tutorial.

```bash
# Access via web browser
# Navigate to: http://localhost:8080
```

The interface will load a table-of-contents display and brief introduction to marimo.

# Step 6. Complete the JAX introduction tutorial

Work through the introductory material to understand JAX programming model differences from NumPy.

Navigate to and complete the JAX introduction notebook, which covers:
- JAX programming model fundamentals
- Key differences from NumPy
- Performance evaluation techniques

# Step 7. Implement NumPy baseline

Complete the NumPy-based self-organized map (SOM) implementation to establish a performance 
baseline.

Work through the NumPy SOM notebook to:
- Understand the SOM training algorithm
- Implement the algorithm using familiar NumPy operations
- Record performance metrics for comparison

# Step 8. Optimize with JAX implementations

Progress through the iteratively refined JAX implementations to see performance improvements.

Complete the JAX SOM notebook sections:
- Basic JAX port of NumPy implementation
- Performance-optimized JAX version
- GPU-accelerated parallel JAX implementation
- Compare performance across all versions

# Step 9. Validate performance gains

The notebooks will show you how to check the performance of each SOM training implementation; you'll see that that JAX implementations show performance improvements over NumPy baseline (and some will be quite a lot faster).

Visually inspect the SOM training output on random color data to confirm algorithm correctness.

# Step 10. Next steps

Apply JAX optimization techniques to your own NumPy-based machine learning code.

```bash
# Example: Profile your existing NumPy code
python -m cProfile your_numpy_script.py

# Then adapt to JAX and compare performance
```

Try adapting your favorite NumPy algorithms to JAX and measure performance improvements on 
Blackwell GPU architecture.
