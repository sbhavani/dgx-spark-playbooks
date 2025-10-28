# Basic idea

This playbook walks you through setting up DGX Spark as a **Vibe Coding assistant** — locally or as a remote coding companion for VSCode with Continue.dev.  
This guide uses **Ollama** with **GPT-OSS 120B** to provide easy deployment of a coding assistant to VSCode. Included is advanced instructions to allow DGX Spark and Ollama to provide the coding assistant to be available over your local network. This guide is also written on a **fresh installation** of the OS. If your OS is not freshly installed and you have issues, see the troubleshooting tab.

## What You'll Accomplish

You'll have a fully configured DGX Spark system capable of:
- Running local code assistance through Ollama.
- Serving models remotely for Continue and VSCode integration.
- Hosting large LLMs like GPT-OSS 120B using unified memory.

## Prerequisites

- DGX Spark (128GB unified memory recommended)
- **Ollama** and an LLM of your choice (e.g., `gpt-oss:120b`)
- **VSCode**
- **Continue** VSCode extension
- Internet access for model downloads
- Basic familiarity with opening the Linux terminal, copying and pasting commands.
- Having sudo access.
- Optional: firewall control for remote access configuration

## Time & risk
* **Duration:** About 30 minutes 
* **Risks:** Data download slowness or failure due to network issues
* **Rollback:** No permanent system changes made during normal usage.
