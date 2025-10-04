#
# SPDX-FileCopyrightText: Copyright (c) 1993-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from unsloth import FastVisionModel

import os
import re
import gc
import yaml
import glob
import random
import subprocess

import wandb
import torch
from PIL import Image
import streamlit as st


REASONING_START = "<REASONING>"
REASONING_END = "</REASONING>"
SOLUTION_START = "<SOLUTION>"
SOLUTION_END = "</SOLUTION>"


def initialize_session_state(resources):
    # Initialize page-specific session state
    st.session_state["base"] = st.session_state.get("base", resources["base"])
    st.session_state["finetuned"] = st.session_state.get("finetuned", resources["finetuned"])
    st.session_state["current_image"] = st.session_state.get("current_image", glob.glob("assets/image_vlm/images/*/*")[0])
    st.session_state["train_process"] = st.session_state.get("train_process", None)


def load_config():
    config_key = "config"
    if getattr(st.session_state, config_key, None) is None:
        with open("src/image_vlm_config.yaml", "r") as f:
            config = yaml.safe_load(f)
        setattr(st.session_state, config_key, config)
    else:
        config = getattr(st.session_state, config_key)

    return config


@st.cache_resource
def initialize_resources(inference_config):
    base_model, base_tokenizer = load_model_for_inference(inference_config, "base")
    finetuned_model, finetuned_tokenizer = load_model_for_inference(inference_config, "finetuned")

    return {
        "base": {"model": base_model, "tokenizer": base_tokenizer},
        "finetuned": {"model": finetuned_model, "tokenizer": finetuned_tokenizer},
    }


def main():
    # set page ui
    st.title("Image VLM Finetuning")
    st.caption("A DGX Spark showcase for on-device VLM finetuning")
    # st.page_link("https://github.com/your-username/your-repo", label="GitHub", icon=":material/github:")

    # load css
    with open("src/styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # load resources
    config = load_config()
    if st.session_state.get("base", None) is None:
        st.toast("Loading model", icon="⏳", duration="short")
    resource = initialize_resources(config["inference"])
    if st.session_state.get("base", None) is None:
        st.toast("Model loaded", icon="✅", duration="short")
    initialize_session_state(resource)

    # train section
    st.markdown("---")
    train_section()

    # inference Section
    st.markdown("---")
    inference_section()


def train_section():
    st.header("GRPO Training")

    column_1, column_2, column_3 = st.columns(3, gap="large")
    with column_1:
        finetuning_method = st.selectbox(
        "Finetuning Method:",
            ["LoRA", "QLoRA", "Full Fine-tuning"],
        )
    
    # update lora config
    if finetuning_method in ("QLoRA", "LoRA"):
        lora_config = st.session_state["config"]["train"]["model"]["lora_config"]

        with column_2:
            lora_rank = st.slider(
                "LoRA Rank", 
                min_value=8,
                max_value=64, 
                value=lora_config["rank"], 
                step=8,
            )

        with column_3:
            lora_alpha = st.slider(
                "LoRA Alpha", 
                min_value=8,
                max_value=64, 
                value=lora_config["alpha"], 
                step=8,
            )

        st.session_state["config"]["train"]["model"]["lora_config"].update({
            'rank': lora_rank,
            'alpha': lora_alpha,
        })

    # update model config based on selection
    st.session_state["config"]["train"]["model"]["use_lora"] = finetuning_method == "LoRA"
    st.session_state["config"]["train"]["model"]["use_qlora"] = finetuning_method == "QLoRA"

    # update train config
    st.write("")
    column_1, column_2, column_3, column_4 = st.columns(4, gap="large")
    with column_1:
        finetune_vision_layers = st.toggle(
            "Finetune Vision Layers",
            value=st.session_state["config"]["train"]["model"]["finetune_vision_layers"])

    with column_2:
        finetune_language_layers = st.toggle(
            "Finetune Language Layers",
            value=st.session_state["config"]["train"]["model"]["finetune_language_layers"])
    
    with column_3:
        finetune_attention_modules = st.toggle(
            "Finetune Attention Modules",
            value=st.session_state["config"]["train"]["model"]["finetune_attention_modules"])
    
    with column_4:
        finetune_mlp_modules = st.toggle(
            "Finetune MLP Modules",
            value=st.session_state["config"]["train"]["model"]["finetune_mlp_modules"])

    st.write("")
    column_1, column_2, column_3, column_4 = st.columns(4, gap="large")
    with column_1:
        epochs = st.slider(
            "Epochs", 
            min_value=1,
            max_value=100, 
            value=st.session_state["config"]["train"]["hyperparameters"]["epochs"])

    with column_2:
        batch_size = st.select_slider(
            "Batch Size",
            options=[1, 2, 4, 8, 16],
            value=st.session_state["config"]["train"]["hyperparameters"]["batch_size"])

    with column_3:
        learning_rate = st.number_input(
            "Learning Rate",
            min_value=1e-6,
            max_value=1e-2,
            value=float(st.session_state["config"]["train"]["hyperparameters"]["learning_rate"]),
            format="%.2e")

    with column_4:
        optimizer = st.selectbox(
            "Optimizer",
            options=["adamw_torch", "adafactor"])

    st.session_state["config"]["train"]["hyperparameters"].update({
        'epochs': epochs,
        'batch_size': batch_size,
        'learning_rate': learning_rate,
        'optimizer': optimizer,
    })

    st.session_state["config"]["train"]["model"].update({
        'finetune_vision_layers': finetune_vision_layers,
        'finetune_language_layers': finetune_language_layers,
        'finetune_attention_modules': finetune_attention_modules,
        'finetune_mlp_modules': finetune_mlp_modules,
    })

    st.write("")
    column_1, column_2, column_3, column_4 = st.columns(4, gap="large")
    with column_1:
        enable_grpo = st.toggle(
            "Enable GRPO",
            value=st.session_state["config"]["train"]["hyperparameters"]["enable_grpo"],
            disabled=True)

    with column_2:
        format_reward = st.number_input(
            "Reward for reasoning format",
            min_value=0.0,
            max_value=5.0,
            value=float(st.session_state["config"]["train"]["hyperparameters"]["format_reward"]),
            format="%.2e")

    with column_3:
        correctness_reward = st.number_input(
            "Reward for correct response",
            min_value=0.0,
            max_value=5.0,
            value=float(st.session_state["config"]["train"]["hyperparameters"]["correctness_reward"]),
            format="%.2e")

    with column_4:
        num_generations = st.number_input(
            "Number of generations",
            min_value=1,
            max_value=16,
            value=st.session_state["config"]["train"]["hyperparameters"]["num_generations"],
            format="%.2e")

    # Training control
    st.write("")
    column_1, column_2, column_3 = st.columns([4, 4, 1])

    with column_1:
        button_type = "secondary" if st.session_state["train_process"] else "primary"
        if st.button("▶️ Start Finetuning", type=button_type, width="stretch", disabled=bool(st.session_state["train_process"])):
            if st.session_state["train_process"] is None:
                # store config
                with open("src/train.yaml", "w") as f:
                    yaml.dump(st.session_state["config"]["train"], f, default_flow_style=False)

                # start training
                st.session_state["train_process"] = subprocess.Popen(
                    ["python", "src/train_image_vlm.py"],
                    stdout=None, stderr=None
                )
            else:
                st.toast("Training already in progress", icon="❌", duration="short")

    with column_2:
        button_type = "primary" if st.session_state["train_process"] else "secondary"
        if st.button("⏹️ Stop Finetuning", type=button_type, width="stretch", disabled=not bool(st.session_state["train_process"])):
            if st.session_state["train_process"] is not None:
                st.session_state["train_process"].terminate()
                st.session_state["train_process"] = None
                st.toast("Training stopped", icon="✅", duration="short")
                st.toast("Re-deploy the app with updated finetuned model", icon=":material/info:", duration="short")
            else:
                st.toast("No training to stop", icon="❌", duration="short")
    
    with column_3:
        if st.session_state["train_process"]:
            st.badge("Running", icon=":material/hourglass_arrow_up:", color="green", width="stretch")
        else:
            st.badge("Idle", icon=":material/hourglass_disabled:", color="red", width="stretch")

    # display wandb
    runs = wandb.Api().runs(f"{os.environ.get('WANDB_ENTITY')}/{os.environ.get('WANDB_PROJECT')}")
    if runs:
        base_url = runs[0].url
        loss_url = f"{base_url}?panelDisplayName=train%2Floss&panelSectionName=train"
        memory_url = f"{base_url}?panelDisplayName=GPU+Memory+Allocated+%28%25%29&panelSectionName=System"

    column_1, column_2 = st.columns(2)
    with column_1:
        st.markdown(f"""
        <div class="wandb-wrapper">
            <iframe src="{loss_url}" class="wandb-iframe"></iframe>
        </div>
        """, unsafe_allow_html=True)
    with column_2:
        st.markdown(f"""
        <div class="wandb-wrapper">
            <iframe src="{memory_url}" class="wandb-iframe"></iframe>
        </div>
        """, unsafe_allow_html=True)


def inference_section():
    st.header("Image Inference")

    columns = st.columns([3, 3, 1, 2])
    with columns[1]:
        with st.container(border=True, horizontal_alignment="center", vertical_alignment="center"):
            image_holder = st.empty()
            image_holder.image(st.session_state["current_image"])

    with columns[3]:
        if st.button("🎲 Test another sample"):
            while True:
                current_image = random.choice(glob.glob("assets/image_vlm/images/*/*"))
                if current_image != st.session_state["current_image"]:
                    break
            st.session_state["current_image"] = current_image
            image_holder.image(st.session_state["current_image"])

    columns = st.columns(2, gap="small")
    with columns[0]:
        with st.container(border=True):
            st.write("##### :green[Base Qwen2.5-VL-7B]")
            base_generation = st.empty()
            base_generation.write("...")

    with columns[1]:
        with st.container(border=True):
            st.write("##### :green[Finetuned Qwen2.5-VL-7B]")
            finetuned_generation = st.empty()
            finetuned_generation.write("...")

    columns = st.columns([9, 1], gap="small")
    with columns[0]:
        prompt = st.text_input(
            "Prompt Input",
            label_visibility="collapsed",
            key="prompt_input",
            on_change=lambda: st.session_state.update(prompt=st.session_state["prompt_input"])
        )

    with columns[1]:
        if st.button("Generate", width="stretch"):
            if st.session_state.get("prompt", None):
                st.session_state["prompt"] = prompt

                with st.spinner("Running..."):
                    response = start_inference("base")
                base_generation.markdown(response)

                with st.spinner("Running..."):
                    response = start_inference("finetuned")
                finetuned_generation.markdown(response)


def load_model_for_inference(config, model_type):
    if model_type == "finetuned":
        model_name = config["finetuned_model_id"]
    elif model_type == "base":
        model_name = config["model_id"]
    else:
        raise ValueError(f"Invalid model type: {model_type}")

    model, tokenizer = FastVisionModel.from_pretrained(
        model_name=model_name,
        max_seq_length=config["max_seq_length"],
        load_in_4bit=False,
    )

    FastVisionModel.for_inference(model)

    return model, tokenizer


@torch.no_grad()
def start_inference(model_type):
    # define prompt
    prompt = st.session_state["prompt"]
    if model_type == "finetuned":
        prompt = (
            f"{prompt}. Also first provide your reasoning or working out"\
            f" on how you would go about identifying the presence of wildfire affected regions between {REASONING_START} and {REASONING_END}"
            f" and then your final answer between {SOLUTION_START} and (put a simple Yes or No here) {SOLUTION_END}"
        )

    # load image
    image = Image.open(st.session_state["current_image"])
    if image.mode != "RGB":
        image = image.convert("RGB")

    # construct instruction prompt
    prompt = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": prompt},
            ],
        },
    ]

    # apply chat template
    prompt = st.session_state[f"{model_type}_image_vlm"]["tokenizer"].apply_chat_template(
        prompt,
        tokenize=False,
        add_generation_prompt=True,
    )

    # tokenize inputs
    inputs = st.session_state[f"{model_type}_image_vlm"]["tokenizer"](
        image,
        prompt,
        add_special_tokens=False,
        return_tensors="pt",
    ).to("cuda")

    # perform inference
    response = st.session_state[f"{model_type}_image_vlm"]["model"].generate(
        **inputs,
        max_new_tokens=1024,
        use_cache=True,
        do_sample=False
    )[0][inputs["input_ids"].shape[1]: ]

    # decode tokens
    response = st.session_state[f"{model_type}_image_vlm"]["tokenizer"].decode(response, skip_special_tokens=True)

    # format response
    if model_type == "finetuned":
        response = response.replace(REASONING_START, "```")
        response = response.replace(REASONING_END, "```")
        
        # Handle solution formatting with proper newline handling
        solution_pattern = f'{re.escape(SOLUTION_START)}(.*?){re.escape(SOLUTION_END)}'
        solution_match = re.search(solution_pattern, response, re.DOTALL)
        if solution_match:
            solution_content = solution_match.group(1).strip()
            response = re.sub(solution_pattern, f"**{solution_content}**", response, flags=re.DOTALL)

    return response


if __name__ == "__main__":
    main()
