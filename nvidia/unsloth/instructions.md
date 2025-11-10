# Step 1. Verify prerequisites

Confirm your NVIDIA Spark device has the required CUDA toolkit and GPU resources available.

```bash
nvcc --version
```
The output should show CUDA 13.0.

```bash
nvidia-smi
```
The output should show a summary of GPU information.

# Step 2. Get the container image
```bash
docker pull nvcr.io/nvidia/pytorch:25.09-py3
```

# Step 3. Launch Docker
```bash
docker run --gpus all --ulimit memlock=-1 -it --ulimit stack=67108864 --entrypoint /usr/bin/bash --rm nvcr.io/nvidia/pytorch:25.09-py3
```

# Step 4. Install dependencies inside Docker

```bash
pip install transformers peft "datasets==4.3.0" "trl==0.19.1"
pip install --no-deps unsloth unsloth_zoo
pip install hf_transfer
```

# Step 5. Build and install bitsandbytes inside Docker
```bash
pip install --no-deps bitsandbytes
```

# Step 6. Create Python test script

Curl the test script [here](${GITLAB_ASSET_BASEURL}/${MODEL}/assets/test_unsloth.py) into the container.

```bash
curl -O https://raw.githubusercontent.com/NVIDIA/dgx-spark-playbooks/refs/heads/main/nvidia/unsloth/assets/test_unsloth.py
```

We will use this test script to validate the installation with a simple fine-tuning task.


# Step 7. Run the validation test

Execute the test script to verify Unsloth is working correctly.

```bash
python test_unsloth.py
```

Expected output in the terminal window:
- "Unsloth: Will patch your computer to enable 2x faster free finetuning"
- Training progress bars showing loss decreasing over 60 steps
- Final training metrics showing completion

# Step 8. Next steps

Test with your own model and dataset by updating the `test_unsloth.py` file:

```python
# Replace line 32 with your model choice
model_name = "unsloth/Meta-Llama-3.1-8B-bnb-4bit"

# Load your custom dataset in line 8
dataset = load_dataset("your_dataset_name")

# Adjust training parameter args at line 61
per_device_train_batch_size = 4
max_steps = 1000
```

Visit https://github.com/unslothai/unsloth/wiki
for advanced usage instructions, including:
- [Saving models in GGUF format for vLLM](https://github.com/unslothai/unsloth/wiki#saving-to-gguf)
- [Continued training from checkpoints](https://github.com/unslothai/unsloth/wiki#loading-lora-adapters-for-continued-finetuning)
- [Using custom chat templates](https://github.com/unslothai/unsloth/wiki#chat-templates)
- [Running evaluation loops](https://github.com/unslothai/unsloth/wiki#evaluation-loop---also-fixes-oom-or-crashing)
