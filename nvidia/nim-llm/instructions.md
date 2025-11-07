# Step 1. Verify environment prerequisites

Check that your system meets the basic requirements for running GPU-enabled containers.

```bash
nvidia-smi
docker --version
docker run --rm --gpus all nvidia/cuda:12.0-base-ubuntu20.04 nvidia-smi
```

## Step 2. Configure NGC authentication

Set up access to NVIDIA's container registry using your NGC API key.

```bash
export NGC_API_KEY="<YOUR_NGC_API_KEY>"
echo "$NGC_API_KEY" | docker login nvcr.io --username '$oauthtoken' --password-stdin
```

# Step 3. Select and configure NIM container

Choose a specific LLM NIM from NGC and set up local caching for model assets.

```bash
export CONTAINER_NAME="nim-llm-demo"
export IMG_NAME="nvcr.io/nim/meta/llama-3.1-8b-instruct-dgx-spark:latest"
export LOCAL_NIM_CACHE=~/.cache/nim
mkdir -p "$LOCAL_NIM_CACHE"
chmod -R a+w "$LOCAL_NIM_CACHE"
```

# Step 4. Launch NIM container

Start the containerized LLM service with GPU acceleration and proper resource allocation.

```bash
docker run -it --rm --name=$CONTAINER_NAME \
--runtime=nvidia \
--gpus all \
--shm-size=16GB \
-e NGC_API_KEY=$NGC_API_KEY \
-v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
-u $(id -u) \
-p 8000:8000 \
$IMG_NAME
```

The container will download the model on first run and may take several minutes to start. Look for
startup messages indicating the service is ready.

# Step 5. Validate inference endpoint

Test the deployed service with a basic completion request to verify functionality. Run the following curl command in a new terminal.


```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/v1/chat/completions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "meta/llama-3.1-8b-instruct",
    "messages": [
      {
        "role":"system",
        "content":"detailed thinking on"
      },
      {
        "role":"user",
        "content":"Can you write me a song?"
      }
    ],
    "top_p": 1,
    "n": 1,
    "max_tokens": 15,
    "frequency_penalty": 1.0,
    "stop": ["hello"]

  }'
  
```

Expected output should be a JSON response containing a completion field with generated text.

# Step 6. Cleanup and rollback

Remove the running container and optionally clean up cached model files.

> [!WARNING]
> Removing cached models will require re-downloading on next run.

```bash
docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME
```

To remove cached models and free disk space:
```bash
rm -rf "$LOCAL_NIM_CACHE"
```

# Step 7. Next steps

With a working NIM deployment, you can:

- Integrate the API endpoint into your applications using the OpenAI-compatible interface
- Experiment with different models available in the NGC catalog
- Scale the deployment using container orchestration tools
- Monitor resource usage and optimize container resource allocation

Test the integration with your preferred HTTP client or SDK to begin building applications.
