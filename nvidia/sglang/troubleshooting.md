Common issues and their resolutions:

| Symptom | Cause | Fix |
|---------|-------|-----|
| Container fails to start with GPU errors | NVIDIA drivers/toolkit missing | Install nvidia-container-toolkit, restart Docker |
| Server responds with 404 or connection refused | Server not fully initialized | Wait 60 seconds, check container logs |
| Out of memory errors during model loading | Insufficient GPU memory | Use smaller model or increase --tp parameter |
| Model download fails | Network connectivity issues | Check internet connection, retry download |
| Permission denied accessing /tmp | Volume mount issues | Use full path: -v /tmp:/tmp or create dedicated directory |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
