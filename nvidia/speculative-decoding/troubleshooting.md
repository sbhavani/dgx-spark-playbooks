| Symptom | Cause | Fix |
|---------|--------|-----|
| "CUDA out of memory" error | Insufficient GPU memory | Reduce `kv_cache_free_gpu_memory_fraction` to 0.9 or use a device with more VRAM |
| Container fails to start | Docker GPU support issues | Verify `nvidia-docker` is installed and `--gpus=all` flag is supported |
| Model download fails | Network or authentication issues | Check HuggingFace authentication and network connectivity |
| Cannot access gated repo for URL | Certain HuggingFace models have restricted access | Regenerate your [HuggingFace token](https://huggingface.co/docs/hub/en/security-tokens); and request access to the [gated model](https://huggingface.co/docs/hub/en/models-gated#customize-requested-information) on your web browser |
| Server doesn't respond | Port conflicts or firewall | Check if port 8000 is available and not blocked |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
