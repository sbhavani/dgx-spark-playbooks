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

# Step 2. Verify Docker setup and pull container

Pull the Open WebUI container image with integrated Ollama:

```bash
docker pull ghcr.io/open-webui/open-webui:ollama
```

# Step 3. Start the Open WebUI container

Start the Open WebUI container by running:

```bash
docker run -d -p 8080:8080 --gpus=all \
-v open-webui:/app/backend/data \
-v open-webui-ollama:/root/.ollama \
--name open-webui ghcr.io/open-webui/open-webui:ollama
```

This will start the Open WebUI container and make it accessible at `http://localhost:8080`. You can access the Open WebUI interface from your local web browser.

Application data will be stored in the `open-webui` volume and model data will be stored in the `open-webui-ollama` volume.

# Step 4. Create administrator account

This step sets up the initial administrator account for Open WebUI. This is a local account that you will use to access the Open WebUI interface.

In the Open WebUI interface, click the "Get Started" button at the bottom of the screen.

Fill out the administrator account creation form with your preferred credentials.

Click the registration button to create your account and access the main interface.

# Step 5. Download and configure a model

This step downloads a language model through Ollama and configures it for use in
Open WebUI. The download happens on your DGX Spark device and may take several minutes.

Click on the "Select a model" dropdown in the top left corner of the Open WebUI interface.

Type `gpt-oss:20b` in the search field.

Click the "Pull 'gpt-oss:20b' from Ollama.com" button that appears.

Wait for the model download to complete. You can monitor progress in the interface.

Once complete, select "gpt-oss:20b" from the model dropdown.

# Step 6. Test the model

This step verifies that the complete setup is working properly by testing model
inference through the web interface.

In the chat text area at the bottom of the Open WebUI interface, enter: **Write me a haiku about GPUs**

Press Enter to send the message and wait for the model's response.

# Step 8. Cleanup and rollback

Steps to completely remove the Open WebUI installation and free up resources:

> [!WARNING]
> These commands will permanently delete all Open WebUI data and downloaded models.

Stop and remove the Open WebUI container:

```bash
docker stop open-webui
docker rm open-webui
```

Remove the downloaded images:

```bash
docker rmi ghcr.io/open-webui/open-webui:ollama
```

Remove persistent data volumes:

```bash
docker volume rm open-webui open-webui-ollama
```

# Step 9. Next steps

Try downloading different models from the Ollama library at https://ollama.com/library.

You can monitor GPU and memory usage through the DGX Dashboard available in NVIDIA Sync as you try different models.

If Open WebUI reports an update is available, you can update the container image by running:

```bash
docker pull ghcr.io/open-webui/open-webui:ollama
```
