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

# Step 2. Clone the repository

In a terminal, clone the repository and navigate to the flux-finetuning directory.

```bash
git clone ${GITLAB_REPO_BASEURL}
```

# Step 3. Model download

You will have to be granted access to the FLUX.1-dev model since it is gated. Go to their [model card](https://huggingface.co/black-forest-labs/FLUX.1-dev) to accept the terms and gain access to the checkpoints.
If you do not have a `HF_TOKEN` already, follow the instructions [here](https://huggingface.co/docs/hub/en/security-tokens) to generate one. Authenticate your system by replacing your generated token in the following command.

```bash
export HF_TOKEN=<YOUR_HF_TOKEN>
cd dgx-spark-playbooks/nvidia/flux-finetuning/assets
sh download.sh
```
The download script can take about 30-45 minutes to complete based on your internet speed.

If you already have fine-tuned LoRAs, place them inside `models/loras`. If you do not have one yet, proceed to the `Step 6. Training` section for more details.

# Step 4. Base model inference

Let's begin by generating an image using the base FLUX.1 model on 2 concepts we are interested in, Toy Jensen and DGX Spark. 

```bash
# Build the inference docker image
docker build -f Dockerfile.inference -t flux-comfyui .

# Launch the ComfyUI container (ensure you are inside flux-finetuning/assets)
# You can ignore any import errors for `torchaudio`
sh launch_comfyui.sh
```
Access ComfyUI at `http://localhost:8188` to generate images with the base model. Do not select any pre-existing template.

Find the workflow section on the left-side panel of ComfyUI (or press `w`). Upon opening it, you should find two existing workflows loaded up. For the base Flux model, let's load the `base_flux.json` workflow. After loading the json, you should see ComfyUI load up the workflow.

Provide your prompt in the `CLIP Text Encode (Prompt)` block. For example, we will use `Toy Jensen holding a DGX Spark in a datacenter`. You can expect the generation to take ~3 mins since it is compute intesive to create high-resolution 1024px images.

After playing around with the base model, you have 2 possible next steps.
* If you already have fine-tuned LoRAs placed inside `models/loras/`, please skip to `Step 7. Fine-tuned model inference` section.
* If you wish to train a LoRA for your custom concepts, first make sure that the ComfyUI inference container is brought down before proceeding to train. You can bring it down by interrupting the terminal with `Ctrl+C` keystroke.

> [!NOTE]
>  To clear out any extra occupied memory from your system, execute the following command outside the container after interrupting the ComfyUI server.
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```

# Step 5. Dataset preparation

Let's prepare our dataset to perform Dreambooth LoRA fine-tuning on the FLUX.1-dev 12B model.

For this playbook, we have already prepared a dataset of 2 concepts - Toy Jensen and DGX Spark. This dataset is a collection of public assets accessible via Google Images. If you wish to generate images with these concepts, you do not need to modify the `data.toml` file.

**TJToy Concept**
- **Trigger phrase**: `tjtoy toy`
- **Training images**: 6 high-quality images of Toy Jensen figures available in the public domain
- **Use case**: Generate images featuring the specific toy character in various scenes

**SparkGPU Concept**
- **Trigger phrase**: `sparkgpu gpu`
- **Training images**: 7 images of DGX Spark GPU available in the public domain
- **Use case**: Generate images featuring the specific GPU design in different contexts

If you wish to generate images with custom concepts, you would need to prepare a dataset of all the concepts you would like to generate and about 5-10 images for each concept. 

Create a folder for each concept with its corresponding name and place it inside the `flux_data` directory. In our case, we have used `sparkgpu` and `tjtoy` as our concepts, and placed a few images inside each of them.

Now, let's modify the `flux_data/data.toml` file to reflect the concepts chosen. Ensure that you update/create entries for each of your concepts by modifying the `image_dir` and `class_tokens` fields under `[[datasets.subsets]]`. For better performance in fine-tuning, it is good practice to append a class token to your concept name (like `toy` or `gpu`).

# Step 6. Training

Launch training by executing the following command. The training script uses a default configuration that produces images that capture your DreamBooth concepts effectively after about 90 minutes of training. This train command will automatically store checkpoints in the `models/loras/` directory.

```bash
# Build the inference docker image
docker build -f Dockerfile.train -t flux-train .

# Trigger the training
sh launch_train.sh
```

# Step 7. Fine-tuned model inference

Now let's generate images using our fine-tuned LoRAs!

```bash
# Launch the ComfyUI container (ensure you are inside flux-finetuning/assets)
# You can ignore any import errors for `torchaudio`
sh launch_comfyui.sh
```
Access ComfyUI at `http://localhost:8188` to generate images with the fine-tuned model. Do not select any pre-existing template.

Find the workflow section on the left-side panel of ComfyUI (or press `w`). Upon opening it, you should find two existing workflows loaded up. For the fine-tuned Flux model, let's load the `finetuned_flux.json` workflow. After loading the json, you should see ComfyUI load up the workflow.

Provide your prompt in the `CLIP Text Encode (Prompt)` block. Now let's incorporate our custom concepts into our prompt for the fine-tuned model. For example, we will use `tjtoy toy holding sparkgpu gpu in a datacenter`. You can expect the generation to take ~3 mins since it is compute intesive to create high-resolution 1024px images.

Unlike the base model, we can see that the fine-tuned model can generate multiple concepts in a single image. Additionally, ComfyUI exposes several fields to tune and change the look and feel of the generated images. 
