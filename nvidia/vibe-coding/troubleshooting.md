| Symptom | Cause | Fix |
|---------|-------|-----|
|Ollama not starting|GPU drivers may not be installed correctly|Run `nvidia-smi` in the terminal. If the command fails check DGX Dashboard for updates to your DGX Spark.|
|Continue can't connect over the network|Port 11434 may not be open or accessible|Run command `ss -tuln \| grep 11434`. If the output does not reflect ` tcp   LISTEN 0      4096               *:11434            *:*  `, go back to step 2 and run the ufw command.|
|Continue can't detect a locally running Ollama model|Configuration not properly set or detected|Check `OLLAMA_HOST` and `OLLAMA_ORIGINS` in `/etc/systemd/system/ollama.service.d/override.conf` file. If `OLLAMA_HOST` and `OLLAMA_ORIGINS` are set correctly, add these lines to your `~/.bashrc` file.|
|High memory usage|Model size too big|Confirm no other large models or containers are running with `nvidia-smi`. Use smaller models such as `gpt-oss:20b` for lightweight usage.|

> [!NOTE]
> DGX Spark uses a Unified Memory Architecture (UMA), which enables dynamic memory sharing between the GPU and CPU.
> With many applications still updating to take advantage of UMA, you may encounter memory issues even when within
> the memory capacity of DGX Spark. If that happens, manually flush the buffer cache with:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
