# Step 1. Configure Docker permissions

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

# Step 2. Clone the repository

```bash
git clone ${GITLAB_REPO_BASEURL}
cd dgx-spark-playbooks/${MODEL}/assets
```

# Step 3. Run the model download script

```bash
chmod +x model_download.sh
./model_download.sh
```

The setup script will take care of pulling model GGUF files from HuggingFace. 
The model files being pulled include gpt-oss-120B (~63GB), Deepseek-Coder:6.7B-Instruct (~7GB) and Qwen3-Embedding-4B (~4GB). 
This may take between 30 minutes to 2 hours depending on network speed.


# Step 4. Start the docker containers for the application

```bash
  docker compose -f docker-compose.yml -f docker-compose-models.yml up -d --build
```
This step builds the base llama.cpp server image and starts all the required docker services to serve models, the backend API server as well as the frontend UI. 
This step can take 10 to 20 minutes depending on network speed.
Wait for all the containers to become ready and healthy.

```bash
watch 'docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"'
```

# Step 5. Access the frontend UI

Open your browser and go to: http://localhost:3000

> [!NOTE]
> If you are running this on a remote GPU via an SSH connection, in a new terminal window, you need to run the following command to be able to access the UI at localhost:3000 and for the UI to be able to communicate to the backend at localhost:8000.

>```ssh -L 3000:localhost:3000 -L 8000:localhost:8000  username@IP-address```

# Step 6. Try out the sample prompts

Click on any of the tiles on the frontend to try out the supervisor and the other agents.

**RAG Agent**:
Before trying out the example prompt for the RAG agent, upload the example PDF document [NVIDIA Blackwell Whitepaper](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) 
as context by going to the link, downloading the PDF to the local filesystem, clicking on the green "Upload Documents" button in the left sidebar under "Context", and then make sure to check the box in the "Select Sources" section.

# Step 8. Cleanup and rollback

Steps to completely remove the containers and free up resources.

From the root directory of the multi-agent-chatbot project, run the following commands:

```bash
docker compose -f docker-compose.yml -f docker-compose-models.yml down

docker volume rm "$(basename "$PWD")_postgres_data"
```

# Step 9. Next steps

- Try different prompts with the multi-agent chatbot system.
- Try different models by following the instructions in the repository.
- Try adding new MCP (Model Context Protocol) servers as tools for the supervisor agent.
