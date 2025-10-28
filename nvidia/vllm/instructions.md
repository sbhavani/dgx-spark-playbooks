# Step 1. Pull vLLM container image

Find the latest container build from https://catalog.ngc.nvidia.com/orgs/nvidia/containers/vllm?version=25.09-py3
```
docker pull nvcr.io/nvidia/vllm:25.09-py3
```

# Step 2. Test vLLM in container

Launch the container and start vLLM server with a test model to verify basic functionality.

```bash
docker run -it --gpus all -p 8000:8000 \
nvcr.io/nvidia/vllm:25.09-py3 \
vllm serve "Qwen/Qwen2.5-Math-1.5B-Instruct"
```

Expected output should include:
- Model loading confirmation
- Server startup on port 8000
- GPU memory allocation details

In another terminal, test the server:

```bash
curl http://localhost:8000/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
  "model": "Qwen/Qwen2.5-Math-1.5B-Instruct",
  "messages": [{"role": "user", "content": "12*17"}],
  "max_tokens": 500
}'
```

Expected response should contain `"content": "204"` or similar mathematical calculation.

# Step 3. Cleanup and rollback

For container approach (non-destructive):

```bash
docker rm $(docker ps -aq --filter ancestor=nvcr.io/nvidia/vllm:25.09-py3)
docker rmi nvcr.io/nvidia/vllm
```


To remove CUDA 12.9:

```bash
sudo /usr/local/cuda-12.9/bin/cuda-uninstaller
```

# Step 4. Next steps

- **Production deployment:** Configure vLLM with your specific model requirements
- **Performance tuning:** Adjust batch sizes and memory settings for your workload
- **Monitoring:** Set up logging and metrics collection for production use
- **Model management:** Explore additional model formats and quantization options
