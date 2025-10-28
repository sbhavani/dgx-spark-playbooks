| Symptom | Cause | Fix |
|---------|--------|-----|
| Container fails to start with GPU error | NVIDIA Container Toolkit not configured | Install nvidia-container-toolkit and restart Docker |
| "Invalid credentials" during docker login | Incorrect NGC API key format | Verify API key from NGC portal, ensure no extra whitespace |
| Model download hangs or fails | Network connectivity or insufficient disk space | Check internet connection and available disk space in cache directory |
| API returns 404 or connection refused | Container not fully started or wrong port | Wait for container startup completion, verify port 8000 is accessible |
| runtime not found | NVIDIA Container Toolkit not properly configured | Run `sudo nvidia-ctk runtime configure --runtime=docker` and restart Docker |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
