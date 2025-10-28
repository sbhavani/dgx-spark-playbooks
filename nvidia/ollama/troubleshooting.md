| Symptom | Cause | Fix |
|---------|--------|-----|
| "Connection refused" on localhost:11434 | SSH tunnel not active | Start Ollama Server in NVIDIA Sync custom apps |
| Model download fails with disk space error | Insufficient storage on Spark | Free up space or choose smaller model (e.g., qwen2.5:7b) |
| Ollama command not found after install | Installation path not in PATH | Restart terminal session or run `source ~/.bashrc` |
| API returns "model not found" error | Model not pulled or wrong name | Run `ollama list` to verify available models |
| Slow inference on Spark | Model too large for GPU memory | Try smaller model or check GPU memory with `nvidia-smi` |
