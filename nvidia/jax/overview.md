# Basic idea

JAX lets you write **NumPy-style Python code** and run it fast on GPUs without writing CUDA. It does this by:

- **NumPy on accelerators**: Use `jax.numpy` just like NumPy, but arrays live on the GPU.  
- **Function transformations**:  
  - `jit` → Compiles your function into fast GPU code  
  - `grad` → Gives you automatic differentiation 
  - `vmap` → Vectorizes your function across batches  
  - `pmap` → Runs across multiple GPUs in parallel 
- **XLA backend**: JAX hands your code to XLA (Accelerated Linear Algebra compiler), which fuses operations and generates optimized GPU kernels.

# What you'll accomplish

You'll set up a JAX development environment on NVIDIA Spark with Blackwell architecture that enables 
high-performance machine learning prototyping using familiar NumPy-like abstractions, complete with 
GPU acceleration and performance optimization capabilities.

# What to know before starting

- Comfortable with Python and NumPy programming
- General understanding of machine learning workflows and techniques
- Experience working in a terminal
- Experience using and building containers
- Familiarity with different versions of CUDA
- Basic understanding of linear algebra (high-school level math sufficient)

# Prerequisites

- NVIDIA Spark device with Blackwell architecture
- ARM64 (AArch64) processor architecture
- Docker or container runtime installed
- NVIDIA Container Toolkit configured
- Verify GPU access: `nvidia-smi`
- Port 8080 available for marimo notebook access

# Ancillary files

All required assets can be found [here on GitHub](${GITLAB_ASSET_BASEURL})

- [**JAX introduction notebook**](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/jax-intro.py) — covers JAX programming model differences from NumPy and performance evaluation
- [**NumPy SOM implementation**](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/numpy-som.py) — reference implementation of self-organized map training algorithm in NumPy  
- [**JAX SOM implementations**](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/som-jax.py) — multiple iteratively refined implementations of SOM algorithm in JAX
- [**Environment configuration**](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/Dockerfile) — package dependencies and container setup specifications


# Time & risk

* **Duration:** 2-3 hours including setup, tutorial completion, and validation
* **Risks:** 
  * Package dependency conflicts in Python environment
  * Performance validation may require architecture-specific optimizations
* **Rollback:** Container environments provide isolation; remove containers and restart to reset state.
