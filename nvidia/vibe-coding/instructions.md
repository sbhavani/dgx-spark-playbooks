# Step 1. Install Ollama

Install the latest version of Ollama using the following command:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```
Once the service is running, pull the desired model:

```bash
ollama pull gpt-oss:120b
```

# Step 2. (Optional) Enable Remote Access

To allow remote connections (e.g., from a workstation using VSCode and Continue), modify the Ollama systemd service:

```bash
sudo systemctl edit ollama
```

Add the following lines beneath the commented section:

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_ORIGINS=*"
```

Reload and restart the service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

If using a firewall, open port 11434:

```bash
sudo ufw allow 11434/tcp
```

Verify that the workstation can connect to your DGX Spark's Ollama server:

```bash
curl -v http://YOUR_SPARK_IP:11434/api/version
```
 Replace **YOUR_SPARK_IP** with your DGX Spark's IP address.
 If the connection fails please see the Troubleshooting tab.

# Step 3. Install VSCode

For DGX Spark (ARM-based), download and install VSCode:
Navigate to https://code.visualstudio.com/download and download the Linux ARM64 version of VSCode. After
the download completes note the downloaded package name. Use it in the next command in place of DOWNLOADED_PACKAGE_NAME.
```bash
sudo dpkg -i DOWNLOADED_PACKAGE_NAME
```

If using a remote workstation, **install VSCode appropriate for your system architecture**.

# Step 4. Install Continue.dev Extension

Open VSCode and install **Continue.dev** from the Marketplace:
- Go to **Extensions view** in VSCode
- Search for **Continue** published by [Continue.dev](https://www.continue.dev/) and install the extension.
After installation, click the Continue icon on the right-hand bar.

# Step 5. Local Inference Setup
- Click `Or, configure your own models`
- Click `Click here to view more providers`
- Choose `Ollama` as the Provider
- For Model, select `Autodetect`
- Test inference by sending a test prompt.

Your downloaded model will now be the default (e.g., `gpt-oss:120b`) for inference.

# Step 6. Setting up a Workstation to Connect to the DGX Spark' Ollama Server

To connect a workstation running VSCode to a remote DGX Spark instance the following must be completed on that workstation:
- Install Continue as instructed in Step 4
- Click on the `Continue` icon on the left pane
- Click `Or, configure your own models`
- Click `Click here to view more providers`
- Select `Ollama` as the Provider
- Select `Autodetect` as the Model.

Continue **will** fail to detect the model as it is attempting to connect to a locally hosted Ollama server.
- Find the `gear` icon in the upper right corner of the Continue window and click on it.
- On the left pane, click **Models**
- Next to the first dropdown menu under **Chat** click the gear icon.
- Continue's `config.yaml` will open. Take note of your DGX Spark's IP address.
- Replace the configuration with the following. **YOUR_SPARK_IP** should be replaced with your DGX Spark's IP.


```yaml
name: Config
version: 1.0.0
schema: v1

assistants:
- name: default
  model: OllamaSpark

models:
- name: OllamaSpark
  provider: ollama
  model: gpt-oss:120b
  apiBase: http://YOUR_SPARK_IP:11434
  title: gpt-oss:120b
  roles:
    - chat
    - edit
    - autocomplete
```

Replace `YOUR_SPARK_IP` with the IP address of your DGX Spark.  
Add additional model entries for any other Ollama models you wish to host remotely.
