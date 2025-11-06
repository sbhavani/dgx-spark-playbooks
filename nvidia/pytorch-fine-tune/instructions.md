# Step 1. Configure Docker permissions

To easily manage containers without sudo, you must be in the `docker` group. If you choose to skip this step, you will need to run Docker commands with sudo.

Open a new terminal and test Docker access. In the terminal, run:

```bash
docker ps
```

If you see a permission denied error (something like permission denied while trying to connect to the Docker daemon socket), add your user to the docker group so that you don't need to run the command with sudo .

```bash
sudo usermod -aG docker $USER
newgrp docker
```

# Step 2.  Pull the latest Pytorch container

```bash
docker pull nvcr.io/nvidia/pytorch:25.09-py3
```

# Step 3. Launch Docker

```bash
docker run --gpus all -it --rm --ipc=host \
-v $HOME/.cache/huggingface:/root/.cache/huggingface \
-v ${PWD}:/workspace -w /workspace \
nvcr.io/nvidia/pytorch:25.09-py3
```

# Step 4. Install dependencies inside the container

```bash
pip install transformers peft datasets "trl==0.19.1" "bitsandbytes==0.48"
```

# Step 5: Authenticate with Huggingface

```bash
huggingface-cli login
#<input your huggingface token.
#<Enter n for git credential>
```

# Step 6:  Clone the git repo with fine-tuning recipes

```bash
git clone ${GITLAB_REPO_BASEURL}
cd dgx-spark-playbooks/${MODEL}/assets
```

# Step7: Run the fine-tuning recipes

To run LoRA on Llama3-8B use the following command:
```bash
python Llama3_8B_LoRA_finetuning.py
```

To run qLoRA fine-tuning on llama3-70B use the following command:
```bash
python Llama3_70B_qLoRA_finetuning.py
```

To run full fine-tuning on llama3-3B use the following command:
```bash
python Llama3_3B_full_finetuning.py
```
