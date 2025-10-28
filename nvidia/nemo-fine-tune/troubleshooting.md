| Symptom | Cause | Fix |
|---------|--------|-----|
| `nvcc: command not found` | CUDA toolkit not in PATH | Add CUDA toolkit to PATH: `export PATH=/usr/local/cuda/bin:$PATH` |
| `pip install uv` permission denied | System-level pip restrictions | Use `pip3 install --user uv` and update PATH |
| GPU not detected in training | CUDA driver/runtime mismatch | Verify driver compatibility: `nvidia-smi` and reinstall CUDA if needed |
| Out of memory during training | Model too large for available GPU memory | Reduce batch size, enable gradient checkpointing, or use model parallelism |
| ARM64 package compatibility issues | Package not available for ARM architecture | Use source installation or build from source with ARM64 flags |
| Cannot access gated repo for URL | Certain HuggingFace models have restricted access | Regenerate your [HuggingFace token](https://huggingface.co/docs/hub/en/security-tokens); and request access to the [gated model](https://huggingface.co/docs/hub/en/models-gated#customize-requested-information) on your web browser |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU.
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
