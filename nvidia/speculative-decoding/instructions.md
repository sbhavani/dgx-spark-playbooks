## Step 1. Configure Docker permissions

To easily manage containers without sudo, you must be in the `docker` group. If you choose to skip this step, you will need to run Docker commands with sudo.

Open a new terminal and test Docker access. In the terminal, run:

```bash
docker ps
```

If you see a permission denied error (something like permission denied while trying to connect to the Docker daemon socket), add your user to the docker group so that you don't need to run the command with sudo .

```bash
sudo usermod -aG docker $USER
newgrp docker
```


## Step 2. Run draft-target speculative decoding

Execute the following command to set up and run traditional speculative decoding:

```bash
docker run \
-v $HOME/.cache/huggingface/:/root/.cache/huggingface/ \
--rm -it --ulimit memlock=-1 --ulimit stack=67108864 \
--gpus=all --ipc=host --network host nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev \
bash -c "
  # Download models
  hf download nvidia/Llama-3.3-70B-Instruct-FP4 && \
  hf download nvidia/Llama-3.1-8B-Instruct-FP4 \
  --local-dir /opt/Llama-3.1-8B-Instruct-FP4/ && \

  # Create configuration file
  cat <<EOF > extra-llm-api-config.yml
print_iter_log: false
disable_overlap_scheduler: true
speculative_config:
decoding_type: DraftTarget
max_draft_len: 4
speculative_model_dir: /opt/Llama-3.1-8B-Instruct-FP4/
kv_cache_config:
enable_block_reuse: false
EOF

  # Start TensorRT-LLM server
  trtllm-serve nvidia/Llama-3.3-70B-Instruct-FP4 \
    --backend pytorch --tp_size 1 \
    --max_batch_size 1 \
    --kv_cache_free_gpu_memory_fraction 0.9 \
    --extra_llm_api_options ./extra-llm-api-config.yml
"
```

## Step 3. Test the draft-target setup

Once the server is running, test it by making an API call from another terminal:

```bash
# Test completion endpoint
curl -X POST http://localhost:8000/v1/completions \
-H "Content-Type: application/json" \
-d '{
  "model": "nvidia/Llama-3.3-70B-Instruct-FP4",
  "prompt": "Explain the benefits of speculative decoding:",
  "max_tokens": 150,
  "temperature": 0.7
}'
```

**Key features of draft-target:**

- **Efficient resource usage**: 8B draft model accelerates 70B target model
- **Flexible configuration**: Adjustable draft token length for optimization
- **Memory efficient**: Uses FP4 quantized models for reduced memory footprint
- **Compatible models**: Uses Llama family models with consistent tokenization

## Step 5.  Cleanup

Stop the Docker container when finished:

```bash
# Find and stop the container
docker ps
docker stop <container_id>

# Optional: Clean up downloaded models from cache
# rm -rf $HOME/.cache/huggingface/hub/models--*gpt-oss*
```

## Step 6. Next Steps

- Experiment with different `max_draft_len` values (1, 2, 3, 4, 8)
- Monitor token acceptance rates and throughput improvements
- Test with different prompt lengths and generation parameters
- Read more on Speculative Decoding [here](https://nvidia.github.io/TensorRT-LLM/advanced/speculative-decoding.html).
