#!/bin/bash
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

accelerate launch \
    --num_processes=1 --num_machines=1 --mixed_precision=bf16 \
    --main_process_ip=127.0.0.1 --main_process_port=29500 \
    --num_cpu_threads_per_process=2 \
    flux_train_network.py \
    --pretrained_model_name_or_path="models/flux1-dev.safetensors" \
    --clip_l="models/clip_l.safetensors" \
    --t5xxl="models/t5xxl_fp16.safetensors" \
    --ae="models/ae.safetensors" \
    --dataset_config="flux_data/data.toml" \
    --output_dir="saved_models" \
    --prior_loss_weight=1.0 \
    --output_name="flux_dreambooth" \
    --save_model_as=safetensors \
    --network_module=networks.lora_flux \
    --network_dim=256 \
    --network_alpha=256 \
    --learning_rate=1.0 \
    --optimizer_type="Prodigy" \
    --lr_scheduler="cosine_with_restarts" \
    --sdpa \
    --max_train_epochs=100 \
    --save_every_n_epochs=25 \
    --mixed_precision="bf16" \
    --guidance_scale=1.0 \
    --timestep_sampling="flux_shift" \
    --model_prediction_type="raw" \
    --torch_compile \
    --persistent_data_loader_workers \
    --cache_latents \
    --cache_latents_to_disk \
    --cache_text_encoder_outputs \
    --cache_text_encoder_outputs_to_disk \
    --gradient_checkpointing