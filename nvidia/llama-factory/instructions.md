# Step 1. Verify system prerequisites

Check that your NVIDIA Spark system has the required components installed and accessible.

```bash
nvcc --version
docker --version
nvidia-smi
python --version
git --version
```

# Step 2. Launch PyTorch container with GPU support

Start the NVIDIA PyTorch container with GPU access and mount your workspace directory.
> [!NOTE]
> This NVIDIA PyTorch container supports CUDA 13

```bash
docker run --gpus all --ipc=host --ulimit memlock=-1 -it --ulimit stack=67108864 --rm -v "$PWD":/workspace nvcr.io/nvidia/pytorch:25.09-py3 bash
```

# Step 3. Clone LLaMA Factory repository

Download the LLaMA Factory source code from the official repository.

```bash
git clone --depth 1 https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
```

## Step 4. Install LLaMA Factory with dependencies

Install the package in editable mode with metrics support for training evaluation.

```bash
pip install -e ".[metrics]"
```

# Step 5. Verify Pytorch CUDA support. 

PyTorch is pre-installed with CUDA support.

To verify installation:

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}')"
```

# Step 6. Prepare training configuration

Examine the provided LoRA fine-tuning configuration for Llama-3.

```bash
cat examples/train_lora/llama3_lora_sft.yaml
```

# Step 7. Launch fine-tuning training

> [!NOTE]
> Login to your hugging face hub to download the model if the model is gated.

Execute the training process using the pre-configured LoRA setup.

```bash
huggingface-cli login # if the model is gated
llamafactory-cli train examples/train_lora/llama3_lora_sft.yaml
```

Example output:
```bash
***** train metrics *****
epoch                    =        3.0
total_flos               = 22851591GF
train_loss               =     0.9113
train_runtime            = 0:22:21.99
train_samples_per_second =      2.437
train_steps_per_second   =      0.306
Figure saved at: saves/llama3-8b/lora/sft/training_loss.png
```

# Step 8. Validate training completion

Verify that training completed successfully and checkpoints were saved.

```bash
ls -la saves/llama3-8b/lora/sft/
```


Expected output should show:
- Final checkpoint directory (`checkpoint-21` or similar)
- Model configuration files (`config.json`, `adapter_config.json`) 
- Training metrics showing decreasing loss values
- Training loss plot saved as PNG file

# Step 9. Test inference with fine-tuned model

Test your fine-tuned model with custom prompts:

```bash
llamafactory-cli chat examples/inference/llama3_lora_sft.yaml
# Type: "Hello, how can you help me today?"
# Expect: Response showing fine-tuned behavior
```

# Step 10. For production deployment, export your model
```bash
llamafactory-cli export examples/merge_lora/llama3_lora_sft.yaml
```

# Step 11. Cleanup and rollback

> [!WARNING]
> This will delete all training progress and checkpoints.

To remove all generated files and free up storage space:

```bash
cd /workspace
rm -rf LLaMA-Factory/
docker system prune -f
```

To rollback Docker container changes:
```bash
exit  # Exit container
docker container prune -f
```
