# Vibe Coding in VS Code

> Use DGX Spark as a local or remote Vibe Coding assistant with Ollama and Continue.dev

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
While NVIDIA NIMs are not yet widely supported, this guide uses **Ollama** with **GPT-OSS 120B** to provide a high-performance local LLM environment.

### What You'll Accomplish

You'll have a fully configured DGX Spark system capable of:
- Running local code assistance through Ollama.
- Serving models remotely for Continue.dev and VSCode integration.
- Hosting large LLMs like GPT-OSS 120B using unified memory.

### Prerequisites

- DGX Spark (128GB unified memory recommended)
- Internet access for model downloads
- Basic familiarity with the terminal
- Optional: firewall control for remote access configuration

### Requirements

- **Ollama** and an LLM of your choice (e.g., `gpt-oss:120b`)
- **VSCode**
- **Continue.dev** VSCode extension

## Instructions

## Step 1. Install Ollama

Install the latest version of Ollama using the following command:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Start the Ollama service:

```bash
ollama serve
```

Once the service is running, pull the desired model:

```bash
ollama pull gpt-oss:120b
```

## Step 2. (Optional) Enable Remote Access

To allow remote connections (e.g., from a workstation using VSCode and Continue.dev), modify the Ollama systemd service:

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

## Step 3. Install VSCode

For DGX Spark (ARM-based), download and install VSCode:

```bash
wget https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-arm64 -O vscode-arm64.deb
sudo apt install ./vscode-arm64.deb
```

If using a remote workstation, install VSCode appropriate for your system architecture.

## Step 4. Install Continue.dev Extension

Open VSCode and install **Continue.dev** from the Marketplace.  
After installation, click the Continue icon on the right-hand bar.

Skip login and open the manual configuration via the **gear (⚙️)** icon.  
This opens `config.yaml`, which controls model settings.

## Step 5. Local Inference Setup

- In the Continue chat window, use `Ctrl/Cmd + L` to focus the chat.
- Click **Select Model → + Add Chat Model**
- Choose **Ollama** as the provider.
- Set **Install Provider** to default.
- For **Model**, select **Autodetect**.
- Click **Connect**.

You can now select your downloaded model (e.g., `gpt-oss:120b`) for local inference.

## Step 6. Remote Setup for DGX Spark

To connect Continue.dev to a remote DGX Spark instance, edit `config.yaml` in Continue and add:

```yaml
models:
  - model: gpt-oss:120b
    title: gpt-oss:120b
    apiBase: http://YOUR_SPARK_IP:11434/
    provider: ollama
```

Replace `YOUR_SPARK_IP` with the IP address of your DGX Spark.  
Add additional model entries for any other Ollama models you wish to host remotely.

## Troubleshooting

## Common Issues

**1. Ollama not starting**
- Verify Docker and GPU drivers are installed correctly.
- Run `ollama serve` manually to view errors.

**2. VSCode can't connect**
- Ensure port 11434 is open and accessible from your workstation.
- Check `OLLAMA_HOST` and `OLLAMA_ORIGINS` in `/etc/systemd/system/ollama.service.d/override.conf`.

**3. High memory usage**
- Use smaller models such as `gpt-oss:20b` for lightweight usage.
- Confirm no other large models or containers are running with `nvidia-smi`.
