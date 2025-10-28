# Common issues for running on a single Spark

| Symptom | Cause | Fix |
|---------|-------|-----|
| Cannot access gated repo for URL | Certain HuggingFace models have restricted access | Regenerate your [HuggingFace token](https://huggingface.co/docs/hub/en/security-tokens); and request access to the [gated model](https://huggingface.co/docs/hub/en/models-gated#customize-requested-information) on your web browser |
| OOM during weight loading (e.g., [Nemotron Super 49B](https://huggingface.co/nvidia/Llama-3_3-Nemotron-Super-49B-v1_5)) | Parallel weight-loading memory pressure | `export TRT_LLM_DISABLE_LOAD_WEIGHTS_IN_PARALLEL=1` |
| "CUDA out of memory" | GPU VRAM insufficient for model | Reduce `free_gpu_memory_fraction: 0.9` or batch size or use smaller model |
| "Model not found" error | HF_TOKEN invalid or model inaccessible | Verify token and model permissions |
| Container pull timeout | Network connectivity issues | Retry pull or use local mirror |
| Import tensorrt_llm fails | Container runtime issues | Restart Docker daemon and retry |

# Common Issues for running on two Starks

| Symptom | Cause | Fix |
|---------|-------|-----|
| MPI hostname test returns single hostname | Network connectivity issues | Verify both nodes are on reachable IP addresses |
| "Permission denied" on HuggingFace download | Invalid or missing HF_TOKEN | Set valid token: `export HF_TOKEN=<TOKEN>` |
| Cannot access gated repo for URL | Certain HuggingFace models have restricted access | Regenerate your [HuggingFace token](https://huggingface.co/docs/hub/en/security-tokens); and request access to the [gated model](https://huggingface.co/docs/hub/en/models-gated#customize-requested-information) on your web browser |
| "CUDA out of memory" errors | Insufficient GPU memory | Reduce `--max_batch_size` or `--max_num_tokens` |
| Container exits immediately | Missing entrypoint script | Ensure `trtllm-mn-entrypoint.sh` download succeeded and has executable permissions, also ensure you are not running the container already on your node. If port 2233 is already utilized, the entrypoint script will not start. |
| Error response from daemon: error while validating Root CA Certificate | System clock out of sync or expired certificates | Update system time to sync with NTP server `sudo timedatectl set-ntp true`|
| "invalid mount config for type 'bind'" | Missing or non-executable entrypoint script | Run `docker inspect <container_id>` to see full error message. Verify `trtllm-mn-entrypoint.sh` exists on both nodes in your home directory (`ls -la $HOME/trtllm-mn-entrypoint.sh`) and has executable permissions (`chmod +x $HOME/trtllm-mn-entrypoint.sh`) |
| "task: non-zero exit (255)" | Container exit with error code 255 | Check container logs with `docker ps -a --filter "name=trtllm-multinode_trtllm"` to get container ID, then `docker logs <container_id>` to see detailed error messages |
| Docker state stuck in "Pending" with "no suitable node (insufficien...)" | Docker daemon not properly configured for GPU access | Verify steps 2-4 were completed successfully and check that `/etc/docker/daemon.json` contains correct GPU configuration |

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU.
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
