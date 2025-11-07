## Step 1. Set up the prerequisites to use Open WebUI with TRT-LLM

After setting up TensorRT-LLM inference server in either single-node or multi-node configuration, 
you can deploy Open WebUI to interact with your models through Open WebUI. To get setup, just make sure the following 
is in order

- TensorRT-LLM inference server running and accessible at http://localhost:8355
- Docker installed and configured (see earlier steps)
- Port 3000 available on your DGX Spark

## Step 2. Launch Open WebUI container

Run the following command on the DGX Spark node where you have the TensorRT-LLM inference server running.
For multi-node setup, this would be the primary node.

> [!NOTE]
> If you used a different port for your OpenAI-compatible API server, adjust the `OPENAI_API_BASE_URL="http://localhost:8355/v1"` to match the IP and port of your TensorRT-LLM inference server.

```bash
docker run \
  -d \
  -e OPENAI_API_BASE_URL="http://localhost:8355/v1" \
  -v open-webui:/app/backend/data \
  --network host \
  --add-host=host.docker.internal:host-gateway \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

This command:
- Connects to your OpenAI-compatible API server for TensorRT-LLM at http://localhost:8355
- Provides access to the Open WebUI interface at http://localhost:8080
- Persists chat data in a Docker volume
- Enables automatic container restart
- Uses the latest Open WebUI image

## Step 3. Access the Open WebUI interface

Open your web browser and navigate to:

```
http://localhost:8080
```

You should see the Open WebUI interface at http://localhost:8080 where you can:
- Chat with your deployed models
- Adjust model parameters
- View chat history
- Manage model configurations

You can select your model(s) from the dropdown menu on the top left corner. That's all you need to do to start using Open WebUI with your deployed models.

> [!NOTE]
> If accessing from a remote machine, replace localhost with your DGX Spark's IP address.

## Step 4. Cleanup and rollback
> [!WARNING]
> This removes all chat data and may require re-uploading for future runs.

Remove the container by using the following command:
```bash
docker stop open-webui
docker rm open-webui
docker volume rm open-webui
docker rmi ghcr.io/open-webui/open-webui:main
```
