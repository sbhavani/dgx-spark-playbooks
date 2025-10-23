# Step 1. Verify system prerequisites

Check that your NVIDIA Spark device meets the requirements before proceeding with installation.

```bash
python3 --version
pip3 --version
nvcc --version
nvidia-smi
```

Expected output should show Python 3.8+, pip available, CUDA toolkit and GPU detection.

# Step 2. Create Python virtual environment

You will install ComfyUI on your host system, so you should create an isolated environment to avoid conflicts with system packages.

```bash
python3 -m venv comfyui-env
source comfyui-env/bin/activate
```

Verify the virtual environment is active by checking the command prompt shows `(comfyui-env)`.

# Step 3. Install PyTorch with CUDA support

Install PyTorch with CUDA 12.9 support.

```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu129
```

This installation targets CUDA 12.9 compatibility with Blackwell architecture GPUs.

# Step 4. Clone ComfyUI repository

Download the ComfyUI source code from the official repository.

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI/
```

# Step 5. Install ComfyUI dependencies

Install the required Python packages for ComfyUI operation.

```bash
pip install -r requirements.txt
```

This installs all necessary dependencies including web interface components and model handling libraries.

# Step 6. Download Stable Diffusion checkpoint

Navigate to the checkpoints directory and download the Stable Diffusion 1.5 model.

```bash
cd models/checkpoints/
wget https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive/resolve/main/v1-5-pruned-emaonly-fp16.safetensors
cd ../../
```

The download will be approximately 2GB and may take several minutes depending on network speed.

# Step 7. Launch ComfyUI server

Start the ComfyUI web server with network access enabled.

```bash
python main.py --listen 0.0.0.0
```

The server will bind to all network interfaces on port 8188, making it accessible from other devices.

# Step 8. Validate installation

Check that ComfyUI is running correctly and accessible via web browser.

```bash
curl -I http://localhost:8188
```

Expected output should show HTTP 200 response indicating the web server is operational.

Open a web browser and navigate to `http://<SPARK_IP>:8188` where `<SPARK_IP>` is your device's IP address.

# Step 9. Optional - Cleanup and rollback

If you need to remove the installation completely, follow these steps:

> [!WARNING]
> This will delete all installed packages and downloaded models.

```bash
deactivate
rm -rf comfyui-env/
rm -rf ComfyUI/
```

To rollback during installation, press `Ctrl+C` to stop the server and remove the virtual environment.

# Step 10. Optional - Next steps

Test the installation with a basic image generation workflow:

1. Access the web interface at `http://<SPARK_IP>:8188`
2. Load the default workflow (should appear automatically)
3. Click "Run" to generate your first image
4. Monitor GPU usage with `nvidia-smi` in a separate terminal

The image generation should complete within 30-60 seconds depending on your hardware configuration.
