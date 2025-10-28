# Common issues with setting up via NVIDIA Sync

| Symptom | Cause | Fix |
|---------|-------|-----|
| Permission denied on docker ps | User not in docker group | Run Step 1 completely, including terminal restart |
| Browser doesn't open automatically | Auto-open setting disabled | Manually navigate to localhost:12000 |
| Model download fails | Network connectivity issues | Check internet connection, retry download |
| GPU not detected in container | Missing `--gpus=all flag` | Recreate container with correct start script |
| Port 12000 already in use | Another application using port | Change port in Custom App settings or stop conflicting service |

# Common issues with manual setup

| Symptom | Cause | Fix |
|---------|-------|-----|
| Permission denied on docker ps | User not in docker group | Run Step 1 completely, including logging out and logging back in or use sudo|
| Model download fails | Network connectivity issues | Check internet connection, retry download |
| GPU not detected in container | Missing `--gpus=all flag` | Recreate container with correct command |
| Port 8080 already in use | Another application using port | Change port in docker command or stop conflicting service |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
