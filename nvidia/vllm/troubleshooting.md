# Common issues for running on a single Spark

| Symptom | Cause | Fix |
|---------|--------|-----|
| CUDA version mismatch errors | Wrong CUDA toolkit version | Reinstall CUDA 12.9 using exact installer |
| Container registry authentication fails | Invalid or expired GitLab token | Generate new auth token |
| SM_121a architecture not recognized | Missing LLVM patches | Verify SM_121a patches applied to LLVM source |

# Common Issues for running on two Sparks
| Symptom | Cause | Fix |
|---------|--------|-----|
| Node 2 not visible in Ray cluster | Network connectivity issue | Verify QSFP cable connection, check IP configuration |
| Cannot access gated repo for URL | Certain HuggingFace models have restricted access | Regenerate your [HuggingFace token](https://huggingface.co/docs/hub/en/security-tokens); and request access to the [gated model](https://huggingface.co/docs/hub/en/models-gated#customize-requested-information) on your web browser |
| Model download fails | Authentication or network issue | Re-run `huggingface-cli login`, check internet access |
| Cannot access gated repo for URL | Certain HuggingFace models have restricted access | Regenerate your HuggingFace token; and request access to the gated model on your web browser |
| CUDA out of memory with 405B | Insufficient GPU memory | Use 70B model or reduce max_model_len parameter |
| Container startup fails | Missing ARM64 image | Rebuild vLLM image following ARM64 instructions |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU.
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
