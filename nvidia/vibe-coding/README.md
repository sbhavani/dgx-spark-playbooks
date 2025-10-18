# Vibe Coding in VS Code

> Use DGX Spark as a local or remote Vibe Coding assistant with Ollama and Continue

## Table of Contents

- [Overview](#overview)
  - [What You'll Accomplish](#what-youll-accomplish)
  - [Prerequisites](#prerequisites)
  - [Requirements](#requirements)
- [Instructions](#instructions)
- [Troubleshooting](#troubleshooting)

---

## Overview

## DGX Spark Vibe Coding

This playbook walks you through setting up DGX Spark as a **Vibe Coding assistant** — locally or as a remote coding companion for VSCode with Continue.dev.  
This guide uses **Ollama** with **GPT-OSS 120B** to provide easy deployment of a coding assistant to VSCode. Included is advanced instructions to allow DGX Spark and Ollama to provide the coding assistant to be available over your local network. This guide is also written on a **fresh installation* of the OS. If your OS is not freshly installed and you have issues, see the troubleshooting section at the bottom of the document.

### What You'll Accomplish

You'll have a fully configured DGX Spark system capable of:
- Running local code assistance through Ollama.
- Serving models remotely for Continue and VSCode integration.
- Hosting large LLMs like GPT-OSS 120B using unified memory.

### Prerequisites

- DGX Spark (128GB unified memory recommended)
- Internet access for model downloads
- Basic familiarity with the terminal
- Optional: firewall control for remote access configuration

### Requirements

- **Ollama** and an LLM of your choice (e.g., `gpt-oss:120b`)
- **VSCode**
- **Continue** VSCode extension
- Basic familiarity with opening the Linux terminal, copying and pasting commands.
- Having sudo access.

## Instructions

## Step 1. Install Ollama

Install the latest version of Ollama using the following command:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```
Once the service is running, pull the desired model:

```bash
ollama pull gpt-oss:120b
```

## Step 2. (Optional) Enable Remote Access

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
 Replace YOUR_SPARK_IP with your DGX Spark's IP address.
 If the connection fails please see the troubleshooting section at the bottom of this document.

## Step 3. Install VSCode

For DGX Spark (ARM-based), download and install VSCode:
  Navigate to https://code.visualstudio.com/download and download the Linux ARM64 version of VSCode. After
  the download completes note the downloaded package name. Use it in the next command in place of DOWNLOADED_PACKAGE_NAME.
```bash
sudo dpkg -i DOWNLOADED_PACKAGE_NAME
```

If using a remote workstation, **install VSCode appropriate for your system architecture**.

## Step 4. Install Continue.dev Extension

Open VSCode and install **Continue.dev** from the Marketplace.  
After installation, click the Continue icon on the right-hand bar.


## Step 5. Local Inference Setup
- Click Select **Or, configure your own models**
- Click **Click here to view more providers**
- Choose **Ollama** as the provider.
- For **Model**, select **Autodetect**.
- Test inference by sending a test prompt.

Your downloaded model will now be the default (e.g., `gpt-oss:120b`) for inference.

## Step 6. Setting up a Workstation to Connect to the DGX Spark' Ollama Server

To connect a workstation running VSCode to a remote DGX Spark instance the following must be completed on that workstation:
  - Install Continue from the marketplace.
  - Click on the Continue icon on the left pane.
  - Click ***Or, configure your own models***
  - Click **Click here to view more providers.
  - Select ***Ollama*** from the provider list.
  - Select ***Autodetect*** as the model.

Continue **wil** fail to detect the model as it is attempting to connect to a locally hosted Ollama server.
  - Find the **gear** icon in the upper right corner of the chat window and click on it.
  - On the left pane, click **Models**
  - Next to the first dropdown menu under **Chat** click the gear icon.
  - Continue's config.yaml will open. Take note of your DGX Spark's IP address.
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

## Troubleshooting

## Common Issues

**1. Ollama not starting**
- Verify GPU drivers are installed correctly.
  Run `nvidia-smi` in the terminal. If the command fails check DGX Dashboard for updates to your DGX Spark.
  If there are no updates or updates do not correct the issue, create a thread on the DGX Spark/GB10 User forum here :
    https://forums.developer.nvidia.com/c/accelerated-computing/dgx-spark-gb10/dgx-spark-gb10/
- Run `ollama serve` on the DGX Spark to view Ollama logs.

**2. Continue can't connect over the network**
- Ensure port 11434 is open and accessible from your workstation. 
    ```bash
    ss -tuln | grep 11434
    ```
      If the output does not reflect " tcp   LISTEN 0      4096               *:11434            *:*  "
      go back to step 2 and run the ufw command.

**3. Continue can't detect a locally running Ollama model
- Check `OLLAMA_HOST` and `OLLAMA_ORIGINS` in `/etc/systemd/system/ollama.service.d/override.conf`.
- If `OLLAMA_HOST` and `OLLAMA_ORIGINS` are set correctly you should add these lines to your .bashrc.

**4. High memory usage**
- Use smaller models such as `gpt-oss:20b` for lightweight usage.
- Confirm no other large models or containers are running with `nvidia-smi`.
