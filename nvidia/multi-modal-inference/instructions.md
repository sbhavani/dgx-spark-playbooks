# Step 1. Launch the TensorRT container environment

Start the NVIDIA PyTorch container with GPU access and HuggingFace cache mounting. This provides 
the TensorRT development environment with all required dependencies pre-installed.

```bash
docker run --gpus all --ipc=host --ulimit memlock=-1 \
--ulimit stack=67108864 -it --rm --ipc=host \
-v $HOME/.cache/huggingface:/root/.cache/huggingface \
nvcr.io/nvidia/pytorch:25.09-py3
```

# Step 2. Clone and set up TensorRT repository

Download the TensorRT repository and configure the environment for diffusion model demos.

```bash
git clone https://github.com/NVIDIA/TensorRT.git -b main --single-branch && cd TensorRT
export TRT_OSSPATH=/workspace/TensorRT/
cd $TRT_OSSPATH/demo/Diffusion
```

# Step 3. Install required dependencies

Install NVIDIA ModelOpt and other dependencies for model quantization and optimization.

```bash
# Install OpenGL libraries
apt update
apt install -y libgl1 libglu1-mesa libglib2.0-0t64 libxrender1 libxext6 libx11-6 libxrandr2 libxss1 libxcomposite1 libxdamage1 libxfixes3 libxcb1

pip install nvidia-modelopt[torch,onnx]
sed -i '/^nvidia-modelopt\[.*\]=.*/d' requirements.txt
pip3 install -r requirements.txt
```

# Step 4. Run Flux.1 Dev model inference

Test multi-modal inference using the Flux.1 Dev model with different precision formats.

**Substep A. BF16 quantized precision**

```bash
python3 demo_txt2img_flux.py "a beautiful photograph of Mt. Fuji during cherry blossom" \
  --hf-token=$HF_TOKEN --download-onnx-models --bf16
```

**Substep B. FP8 quantized precision**

```bash
python3 demo_txt2img_flux.py "a beautiful photograph of Mt. Fuji during cherry blossom" \
  --hf-token=$HF_TOKEN --quantization-level 4 --fp8 --download-onnx-models
```

**Substep C. FP4 quantized precision**

```bash
python3 demo_txt2img_flux.py "a beautiful photograph of Mt. Fuji during cherry blossom" \
  --hf-token=$HF_TOKEN --fp4 --download-onnx-models
```

# Step 5. Run Flux.1 Schnell model inference

Test the faster Flux.1 Schnell variant with different precision formats.

> [!WARNING]
> FP16 Flux.1 Schnell requires >48GB VRAM for native export

**Substep A. FP16 precision (high VRAM requirement)**

```bash
python3 demo_txt2img_flux.py "a beautiful photograph of Mt. Fuji during cherry blossom" \
  --hf-token=$HF_TOKEN --version="flux.1-schnell"
```

**Substep B. FP8 quantized precision**

```bash
python3 demo_txt2img_flux.py "a beautiful photograph of Mt. Fuji during cherry blossom" \
  --hf-token=$HF_TOKEN --version="flux.1-schnell" \
  --quantization-level 4 --fp8 --download-onnx-models
```

**Substep C. FP4 quantized precision**

```bash
python3 demo_txt2img_flux.py "a beautiful photograph of Mt. Fuji during cherry blossom" \
  --hf-token=$HF_TOKEN --version="flux.1-schnell" \
  --fp4 --download-onnx-models
```

# Step 6. Run SDXL model inference

Test the SDXL model for comparison with different precision formats.

**Substep A. BF16 precision**

```bash
python3 demo_txt2img_xl.py "a beautiful photograph of Mt. Fuji during cherry blossom" \
  --hf-token=$HF_TOKEN --version xl-1.0 --download-onnx-models
```

**Substep B. FP8 quantized precision**

```bash
python3 demo_txt2img_xl.py "a beautiful photograph of Mt. Fuji during cherry blossom" \
  --hf-token=$HF_TOKEN --version xl-1.0 --download-onnx-models --fp8
```

# Step 7. Validate inference outputs

Check that the models generated images successfully and measure performance differences.

```bash
# Check for generated images in output directory
ls -la *.png *.jpg 2>/dev/null || echo "No image files found"

# Verify CUDA is accessible
nvidia-smi

# Check TensorRT version
python3 -c "import tensorrt as trt; print(f'TensorRT version: {trt.__version__}')"
```

# Step 8. Cleanup and rollback

Remove downloaded models and exit container environment to free disk space.

> [!WARNING]
> This will delete all cached models and generated images

```bash
# Exit container
exit

# Remove HuggingFace cache (optional)
rm -rf $HOME/.cache/huggingface/
```

# Step 9. Next steps

Use the validated setup to generate custom images or integrate multi-modal inference into your 
applications. Try different prompts or explore model fine-tuning with the established TensorRT 
environment.
