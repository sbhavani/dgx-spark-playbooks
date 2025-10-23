| Symptom | Cause | Fix |
|---------|-------|-----|
| PyTorch CUDA not available | Incorrect CUDA version or missing drivers | Verify `nvcc --version` matches cu129, reinstall PyTorch |
| Model download fails | Network connectivity or storage space | Check internet connection, verify 20GB+ available space |
| Web interface inaccessible | Firewall blocking port 8188 | Configure firewall to allow port 8188, check IP address |
| Out of GPU memory errors after manually flushing buffer cache | Insufficient VRAM for model | Use smaller models or enable CPU fallback mode |

> [!NOTE] 
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
