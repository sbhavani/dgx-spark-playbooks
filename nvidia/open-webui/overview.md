# Basic idea

Open WebUI is an extensible, self-hosted AI interface that operates entirely offline.
This playbook shows you how to deploy Open WebUI with an integrated Ollama server on your DGX Spark device that lets you access the web interface from your local browser while the models run on Spark's GPU.

# What you'll accomplish

You will have a fully functional Open WebUI installation running on your DGX Spark. This will be accessible through your local web browser either via **NVIDIA Sync's managed SSH tunneling (recommended)** or via manual setup. The setup includes integrated Ollama for model management, persistent data storage, and GPU acceleration for model inference.

# What to know before starting

- How to [Set Up Local Network Access](/spark/connect-to-your-spark) to your DGX Spark device

# Prerequisites

-  DGX Spark [device is set up](https://docs.nvidia.com/dgx/dgx-spark/first-boot.html) and accessible
-  [Local Network Access](/spark/connect-to-your-spark) to your DGX Spark
-  Enough disk space for the Open WebUI container image and model downloads

# Time & risk

* **Duration**: 15-20 minutes for initial setup, plus model download time (varies by model size)
* **Risks**:
  * Docker permission issues may require user group changes and session restart
  * Large model downloads may take significant time depending on network speed
