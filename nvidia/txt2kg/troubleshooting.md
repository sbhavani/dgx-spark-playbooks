| Symptom | Cause | Fix |
|---------|--------|-----|
| Ollama performance issues | Suboptimal settings for DGX Spark | Set environment variables:<br>`OLLAMA_FLASH_ATTENTION=1` (enables flash attention for better performance)<br>`OLLAMA_KEEP_ALIVE=30m` (keeps model loaded for 30 minutes)<br>`OLLAMA_MAX_LOADED_MODELS=1` (avoids VRAM contention)<br>`OLLAMA_KV_CACHE_TYPE=q8_0` (reduces KV cache VRAM with minimal performance impact) |
| VRAM exhausted or memory pressure (e.g. when switching between Ollama models) | Linux buffer cache consuming GPU memory | Flush buffer cache: `sudo sync; sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'` |
| Slow triple extraction | Large model or large context window | Reduce document chunk size or use faster models |
| ArangoDB connection refused | Service not fully started | Wait 30s after start.sh, verify with `docker ps` |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
