| Symptom | Cause | Fix |
|---------|-------|-----|
| "CUDA out of memory" error | Insufficient VRAM for model | Use FP8/FP4 quantization or smaller model |
| "Invalid HF token" error | Missing or expired HuggingFace token | Set valid token: `export HF_TOKEN=<YOUR_TOKEN>` |
| Cannot access gated repo for URL | Certain HuggingFace models have restricted access | Regenerate your [HuggingFace token](https://huggingface.co/docs/hub/en/security-tokens); and request access to the [gated model](https://huggingface.co/docs/hub/en/models-gated#customize-requested-information) on your web browser |
| Model download timeouts | Network issues or rate limiting | Retry command or pre-download models |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
