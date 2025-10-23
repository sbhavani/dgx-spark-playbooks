| Symptom | Cause | Fix |
|---------|--------|-----|
| CUDA out of memory during training | Batch size too large for GPU VRAM | Reduce `per_device_train_batch_size` or increase `gradient_accumulation_steps` |
| Cannot access gated repo for URL | Certain HuggingFace models have restricted access | Regenerate your [HuggingFace token](https://huggingface.co/docs/hub/en/security-tokens); and request access to the [gated model](https://huggingface.co/docs/hub/en/models-gated#customize-requested-information) on your web browser |
| Model download fails or is slow | Network connectivity or Hugging Face Hub issues | Check internet connection, try using `HF_HUB_OFFLINE=1` for cached models |
| Training loss not decreasing | Learning rate too high/low or insufficient data | Adjust `learning_rate` parameter or check dataset quality |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU. 
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within 
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
