# Basic Idea

This playbook demonstrates how to set up remote access to an Ollama server running on your NVIDIA
Spark device using NVIDIA Sync's Custom Apps feature. You'll install Ollama on your Spark device,
configure NVIDIA Sync to create an SSH tunnel, and access the Ollama API from your local machine.
This eliminates the need to expose ports on your network while enabling AI inference from your
laptop through a secure SSH tunnel.

# What you'll accomplish

You will have Ollama running on your NVIDIA Spark with Blackwell architecture and accessible via
API calls from your local laptop. This setup allows you to build applications or use tools on your
local machine that communicate with the Ollama API for large language model inference, leveraging
the powerful GPU capabilities of your Spark device without complex network configuration.

# What to know before starting

- Working with SSH connections and system tray applications
- Basic familiarity with terminal commands and cURL for API testing
- Understanding of REST API concepts and JSON formatting
- Experience with container environments and GPU-accelerated workloads

# Prerequisites

- DGX Spark device set up and connected to your network
- NVIDIA Sync installed and connected to your Spark
- Terminal access to your local machine for testing API calls

# Time & risk

**Duration**: 10-15 minutes for initial setup, 2-3 minutes for model download (varies by model size)

**Risk level**: Low - No system-level changes, easily reversible by stopping the custom app

**Rollback**: Stop the custom app in NVIDIA Sync and uninstall Ollama with standard package
removal if needed.
