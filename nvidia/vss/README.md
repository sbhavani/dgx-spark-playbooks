# Video Search and Summarization

> Run the VSS Blueprint on your Spark

## Table of Contents

- [Overview](#overview)
- [Instructions](#instructions)
  - [Navigate to Event Verification directory](#navigate-to-event-verification-directory)
  - [Configure NGC API Key](#configure-ngc-api-key)
  - [Start VSS Event Verification services](#start-vss-event-verification-services)
  - [Navigate to CV Event Detector directory](#navigate-to-cv-event-detector-directory)
  - [Start DeepStream CV pipeline](#start-deepstream-cv-pipeline)
  - [Wait for service initialization](#wait-for-service-initialization)
  - [Validate Event Reviewer deployment](#validate-event-reviewer-deployment)
  - [Navigate to remote LLM deployment directory](#navigate-to-remote-llm-deployment-directory)
  - [Configure environment variables](#configure-environment-variables)
  - [Review model configuration](#review-model-configuration)
  - [Launch Standard VSS deployment](#launch-standard-vss-deployment)
  - [Validate Standard VSS deployment](#validate-standard-vss-deployment)
  - [For Event Reviewer deployment](#for-event-reviewer-deployment)
  - [For Standard VSS deployment](#for-standard-vss-deployment)

---

## Overview

## Basic Idea

Deploy NVIDIA's Video Search and Summarization (VSS) AI Blueprint to build intelligent video analytics systems that combine vision language models, large language models, and retrieval-augmented generation. The system transforms raw video content into real-time actionable insights with video summarization, Q&A, and real-time alerts. You'll set up either a completely local Event Reviewer deployment or a hybrid deployment using remote model endpoints.

## What you'll accomplish

You will deploy NVIDIA's VSS AI Blueprint on NVIDIA Spark hardware with Blackwell architecture, choosing between two deployment scenarios: VSS Event Reviewer (completely local with VLM pipeline) or Standard VSS (hybrid deployment with remote LLM/embedding endpoints). This includes setting up Alert Bridge, VLM Pipeline, Alert Inspector UI, Video Storage Toolkit, and optional DeepStream CV pipeline for automated video analysis and event verification.

## What to know before starting

- Working with NVIDIA Docker containers and container registries
- Setting up Docker Compose environments with shared networks
- Managing environment variables and authentication tokens
- Working with NVIDIA DeepStream and computer vision pipelines
- Basic understanding of video processing and analysis workflows

## Prerequisites

- [ ] NVIDIA Spark device with ARM64 architecture and Blackwell GPU
- [ ] FastOS 1.81.38 or compatible ARM64 system
- [ ] Driver version 580.82.09 installed: `nvidia-smi | grep "Driver Version"`
- [ ] CUDA version 13.0 installed: `nvcc --version`
- [ ] Docker installed and running: `docker --version && docker compose version`
- [ ] Access to NVIDIA Container Registry with NGC API Key
- [ ] [Optional] NVIDIA API Key for remote model endpoints (hybrid deployment only)
- [ ] Sufficient storage space for video processing (>10GB recommended in `/tmp/`)

## Ancillary files

- [VSS Blueprint GitHub Repository](https://github.com/NVIDIA-AI-Blueprints/video-search-and-summarization) - Main codebase and Docker Compose configurations
- [Sample CV Detection Pipeline](https://github.com/NVIDIA-AI-Blueprints/video-search-and-summarization/tree/main/examples/cv-event-detector) - Reference CV pipeline for event reviewer workflow
- [VSS Official Documentation](https://docs.nvidia.com/vss/latest/index.html) - Complete system documentation

## Time & risk

**Duration:** 30-45 minutes for initial setup, additional time for video processing validation

**Risks:**
- Container startup can be resource-intensive and time-consuming with large model downloads
- Network configuration conflicts if shared network already exists
- Remote API endpoints may have rate limits or connectivity issues (hybrid deployment)

**Rollback:** Stop all containers with `docker compose down`, remove shared network with `docker network rm vss-shared-network`, and clean up temporary media directories.

## Instructions

## Step 1. Verify environment requirements

Check that your system meets the hardware and software prerequisites.

```bash
## Verify driver version
nvidia-smi | grep "Driver Version"
## Expected output: Driver Version: 580.82.09

## Verify CUDA version
nvcc --version
## Expected output: release 13.0

## Verify Docker is running
docker --version && docker compose version
```

## Step 2. Clone the VSS repository

Clone the Video Search and Summarization repository from NVIDIA's public GitHub.

```bash
## Clone the VSS AI Blueprint repository
git clone https://github.com/NVIDIA-AI-Blueprints/video-search-and-summarization.git
cd video-search-and-summarization
```

## Step 3. Run the cache cleaner script

Start the system cache cleaner to optimize memory usage during container operations.

```bash
## Start the cache cleaner script in background
sudo sh deploy/scripts/sys_cache_cleaner.sh &
```

## Step 4. Set up Docker shared network

Create a Docker network that will be shared between VSS services and CV pipeline containers.

```bash
## Create shared network (may require sudo depending on Docker configuration)
docker network create vss-shared-network
```

> **Warning:** If the network already exists, you may see an error. Remove it first with `docker network rm vss-shared-network` if needed.

## Step 5. Authenticate with NVIDIA Container Registry

Log in to NVIDIA's container registry using your NGC API Key.

```bash
## Log in to NVIDIA Container Registry
docker login nvcr.io
## Username: $oauthtoken
## Password: <PASTE_NGC_API_KEY_HERE>
```

## Step 6. Choose deployment scenario

Choose between two deployment options based on your requirements:

| Deployment Scenario  | VLM (Cosmos-Reason1-7B) | LLM (Llama 3.1 70B) | Embedding/Reranker | CV Pipeline |
|----------------------|--------------------------|---------------------|--------------------|-------------|
| VSS Event Reviewer   | Local                    | Not Used            | Not Used           | Local       |
| Standard VSS (Hybrid)| Local                   | Remote              | Remote             | Optional    |

Proceed with **Option A** for Event Reviewer or **Option B** for Standard VSS.

## Step 7. Option A - VSS Event Reviewer (Completely Local)

### Navigate to Event Verification directory

Change to the directory containing the Event Verification Docker Compose configuration.

```bash
cd deploy/docker/event_reviewer/
```

### Configure NGC API Key

Update the environment file with your NGC API Key.

```bash
## Edit the .env file and update NGC_API_KEY
echo "NGC_API_KEY=<YOUR_NGC_API_KEY>" >> .env
```

### Start VSS Event Verification services

Launch the complete VSS Event Verification stack including Alert Bridge, VLM Pipeline, Alert Inspector UI, and Video Storage Toolkit.

```bash
## Start VSS Event Verification with ARM64 and SBSA optimizations
IS_SBSA=1 IS_AARCH64=1 ALERT_REVIEW_MEDIA_BASE_DIR=/tmp/alert-media-dir docker compose up
```

> **Note:** This step will take several minutes as containers are pulled and services initialize. The VSS backend requires additional startup time.

### Navigate to CV Event Detector directory

In a new terminal session, navigate to the computer vision event detector configuration.

```bash
cd video-search-and-summarization/examples/cv-event-detector
```

### Start DeepStream CV pipeline

Launch the DeepStream computer vision pipeline and CV UI services.

```bash
## Start CV pipeline with ARM64 and SBSA optimizations
IS_SBSA=1 IS_AARCH64=1 ALERT_VERIFICATION_MEDIA_BASE_DIR=/tmp/alert-media-dir docker compose up
```

### Wait for service initialization

Allow time for all containers to fully initialize before accessing the user interfaces.

```bash
## Monitor container status
docker ps
## Verify all containers show "Up" status and VSS backend logs show ready state
```

### Validate Event Reviewer deployment

Access the web interfaces to confirm successful deployment and functionality.

```bash
## Test CV UI accessibility (replace <NODE_IP> with your system's IP)
curl -I http://<NODE_IP>:7862
## Expected: HTTP 200 response

## Test Alert Inspector UI accessibility
curl -I http://<NODE_IP>:7860
## Expected: HTTP 200 response
```

Open these URLs in your browser:
- `http://<NODE_IP>:7862` - CV UI to launch and monitor CV pipeline
- `http://<NODE_IP>:7860` - Alert Inspector UI to view clips and verification results

## Step 8. Option B - Standard VSS (Hybrid Deployment)

### Navigate to remote LLM deployment directory

```bash
cd deploy/docker/remote_llm_deployment/
```

### Configure environment variables

Update the environment file with your API keys and deployment preferences.

```bash
## Edit .env file with required keys
echo "NVIDIA_API_KEY=<YOUR_NVIDIA_API_KEY>" >> .env
echo "NGC_API_KEY=<YOUR_NGC_API_KEY>" >> .env
echo "DISABLE_CV_PIPELINE=true" >> .env  # Set to false to enable CV
echo "INSTALL_PROPRIETARY_CODECS=false" >> .env  # Set to true to enable CV
```

### Review model configuration

Verify that the config.yaml file contains the correct remote endpoints.

```bash
## Check model server endpoints in config.yaml
cat config.yaml | grep -A 10 "model_server"
```

### Launch Standard VSS deployment

```bash
## Start Standard VSS with hybrid deployment
docker compose up
```

### Validate Standard VSS deployment

Access the VSS UI to confirm successful deployment.

```bash
## Test VSS UI accessibility (replace <NODE_IP> with your system's IP)
curl -I http://<NODE_IP>:9100
## Expected: HTTP 200 response
```

Open `http://<NODE_IP>:9100` in your browser to access the VSS interface.

## Step 9. Test video processing workflow

Run a basic test to verify the video analysis pipeline is functioning based on your deployment.

### For Event Reviewer deployment
- Access CV UI at `http://<NODE_IP>:7862` to upload and process videos
- Monitor results in Alert Inspector UI at `http://<NODE_IP>:7860`

### For Standard VSS deployment
- Access VSS interface at `http://<NODE_IP>:9100`
- Upload videos and test summarization features

## Step 10. Troubleshooting

| Symptom | Cause | Fix |
|---------|--------|-----|
| Container fails to start with "pull access denied" | Missing or incorrect nvcr.io credentials | Re-run `docker login nvcr.io` with valid credentials |
| Network creation fails | Existing network with same name | Run `docker network rm vss-shared-network` then recreate |
| Services fail to communicate | Incorrect environment variables | Verify `IS_SBSA=1 IS_AARCH64=1` are set correctly |
| Web interfaces not accessible | Services still starting or port conflicts | Wait 2-3 minutes, check `docker ps` for container status |

## Step 11. Cleanup and rollback

To completely remove the VSS deployment and free up system resources.

> **Warning:** This will destroy all processed video data and analysis results.

```bash
## For Event Reviewer deployment
cd deploy/docker/event_reviewer/
docker compose down
cd ../../examples/cv-event-detector/
docker compose down

## For Standard VSS deployment
cd deploy/docker/remote_llm_deployment/
docker compose down

## Remove shared network (if using Event Reviewer)
docker network rm vss-shared-network

## Clean up temporary media files and stop cache cleaner
rm -rf /tmp/alert-media-dir
sudo pkill -f sys_cache_cleaner.sh
```

## Step 12. Next steps

With VSS deployed, you can now:

**Event Reviewer deployment:**
- Upload video files through the CV UI at port 7862
- Monitor automated event detection and verification
- Review analysis results in the Alert Inspector UI at port 7860
- Configure custom event detection rules and thresholds

**Standard VSS deployment:**
- Access full VSS capabilities at port 9100
- Test video summarization and Q&A features
- Configure knowledge graphs and graph databases
- Integrate with existing video processing workflows
