# Step 1. Create the Project Directory

First, create a dedicated directory to store your model weights and configuration files. This 
keeps the project organized and provides a clean workspace.

```bash
# Create the main directory
mkdir -p ~/monai-reasoning-spark
cd ~/monai-reasoning-spark

# Create a subdirectory for the model
mkdir -p models
```

# Step 2. Download the MONAI-Reasoning-CXR-3B Model

Use the Hugging Face CLI to download the model weights into the directory you just created. 
The model is approximately 6GB and will take several minutes to download depending on your 
internet connection.

```bash
huggingface-cli download monai/monai-reasoning-cxr-3b \
--local-dir ./models/monai-reasoning-cxr-3b \
--local-dir-use-symlinks False
```

**Verification Step:**
```bash
ls -la ./models/monai-reasoning-cxr-3b
# You should see model files including config.json and model weights
```

> [!IMPORTANT]
> Currently, a custom internal VLLM container is required until the sm121 support is available in the public image. The instructions below use the internal container `gitlab-master.nvidia.com:5005/dl/dgx/vllm:main-py3.31165712-devel`.

# Step 3. Verify System Architecture

Before proceeding, confirm your system architecture is ARM64 for proper container selection 
on your NVIDIA Spark device:

```bash
# Check your system architecture
uname -m
# Should output: aarch64 for ARM64 systems like NVIDIA Spark
```

# Step 4. Create a Docker Network

Create a dedicated Docker bridge network to allow the VLLM and Open WebUI containers to 
communicate with each other easily and reliably.

```bash
docker network create monai-net
```

# Step 5. Deploy the VLLM Server

Launch the VLLM container with ARM64 architecture support, attaching it to the network you 
created and mounting your local model directory. This step configures the server for optimal 
performance on NVIDIA Spark hardware.

```bash
# Stop and remove existing container if running
docker stop vllm-server 2>/dev/null || true
docker rm vllm-server 2>/dev/null || true

# Run the VLLM server with internal container
docker run --rm -d \
--name vllm-server \
--gpus all \
--ipc=host \
--ulimit memlock=-1 \
--ulimit stack=67108864 \
--network monai-net \
--platform linux/arm64 \
-v ./models/monai-reasoning-cxr-3b:/model \
-p 8000:8000 \
gitlab-master.nvidia.com:5005/dl/dgx/vllm:main-py3.31165712-devel \
vllm serve /model \
--host 0.0.0.0 \
--port 8000 \
--dtype bfloat16 \
--trust-remote-code \
--gpu-memory-utilization 0.5 \
--enforce-eager \
--served-model-name monai-reasoning-cxr-3b
```

**Wait for startup and verify:**
```bash
# Wait for the model to load (can take 1-2 minutes on Spark hardware)
sleep 90

# Check if container is running
docker ps

# Test the VLLM API
curl http://localhost:8000/v1/models
```

You should see JSON output showing the model is loaded and available.

# Step 6. Deploy Open WebUI

Launch the Open WebUI container with ARM64 architecture support for your NVIDIA Spark device.

```bash
# Define custom prompt suggestions for medical X-ray analysis
PROMPT_SUGGESTIONS='[
{
  "title": ["Analyze X-Ray Image", "Find abnormalities and support devices"],
  "content": "Find abnormalities and support devices in the image."
}
]'

# Stop and remove existing container if running
docker stop open-webui 2>/dev/null || true
docker rm open-webui 2>/dev/null || true
sleep 5

# Run Open WebUI with custom configuration
docker run -d --rm \
--name open-webui \
--network monai-net \
--platform linux/arm64 \
-p 3000:8080 \
-e WEBUI_AUTH=0 \
-e WEBUI_NAME=monai-reasoning \
-e ENABLE_SIGNUP=0 \
-e ENABLE_ADMIN_CHAT_ACCESS=0 \
-e ENABLE_VERSION_UPDATE_CHECK=0 \
-e OPENAI_API_BASE_URL="http://vllm-server:8000/v1" \
-e DEFAULT_PROMPT_SUGGESTIONS="$PROMPT_SUGGESTIONS" \
ghcr.io/open-webui/open-webui:main
```

**Verify deployment:**
```bash
# Wait for startup
sleep 15

# Check both containers are running
docker ps

# Test Open WebUI accessibility
curl -f http://localhost:3000 || echo "Still starting up"
```

# Step 7. Validate the Complete Deployment

Check that both containers are running properly and all endpoints are accessible:

```bash
# Check container status
docker ps
# You should see both vllm-server and open-webui containers running

# Test the VLLM API
curl http://localhost:8000/v1/models
# Should return JSON with model information

# Test Open WebUI accessibility
curl -f http://localhost:3000
# Should return HTTP 200 response
```

# Step 8. Configure Open WebUI

Configure the front-end interface to connect to your VLLM backend:

1. Open your web browser and navigate to **http://<YOUR_SPARK_DEVICE_IP>:3000**
2. Since authentication is disabled, you'll have direct access to the interface
3. The OpenAI API connection is pre-configured through environment variables
4. Go to the main chat screen, click **"Select a model"**, and choose **monai-reasoning-cxr-3b**
5. **Important:** Navigate to **Chat Controls** → **Advanced Params** and disable **"Reasoning Tags"** to get the full reasoning output from the model

You can now upload a chest X-ray image and ask questions directly in the chat interface. The custom prompt suggestion "Find abnormalities and support devices in the image" will be available for quick access.

# Step 9. Cleanup and Rollback

To stop and remove the containers and network, run the following commands. This will not 
delete your downloaded model weights.

> [!WARNING]
> This will stop all running containers and remove the network.

```bash
# Stop containers
docker stop vllm-server open-webui

# Remove network
docker network rm monai-net

# Optional: Remove model directory to free disk space
# rm -rf ~/monai-reasoning-spark/models
```

# Step 10. Next Steps

Your MONAI reasoning system is now ready for use. Upload chest X-ray images through the web 
interface at http://<YOUR_SPARK_DEVICE_IP>:3000 and interact with the MONAI-Reasoning-CXR-3B model 
for medical image analysis and reasoning tasks.
