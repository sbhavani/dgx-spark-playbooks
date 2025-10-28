| Symptom | Cause | Fix |
|---------|-------|-----|
| VLLM container fails to start | Insufficient GPU memory | Reduce `--gpu-memory-utilization` to 0.25 |
| Model download fails | Network connectivity or HF auth | Check `huggingface-cli whoami` and internet |
| Cannot access gated repo for URL | Certain HuggingFace models have restricted access | Regenerate your HuggingFace token; and request access to the gated model on your web browser |
| Open WebUI shows connection error | Wrong backend URL | Verify `OPENAI_API_BASE_URL` is set correctly |
| Model doesn't show full reasoning | Reasoning tags enabled | Disable "Reasoning Tags" in Chat Controls → Advanced Params |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
