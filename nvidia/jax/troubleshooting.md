| Symptom | Cause | Fix |
|---------|--------|-----|
| `nvidia-smi` not found | Missing NVIDIA drivers | Install NVIDIA drivers for ARM64 |
| Container fails to access GPU | Missing NVIDIA Container Toolkit | Install `nvidia-container-toolkit` |
| JAX only uses CPU | CUDA/JAX version mismatch | Reinstall JAX with CUDA support |
| Port 8080 unavailable | Port already in use | Use `-p 8081:8080` or kill process on 8080 |
| Package conflicts in Docker build | Outdated environment file | Update environment file for Blackwell |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
