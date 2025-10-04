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

for SEED in $(seq 0 7); do
    python flux_minimal_inference.py \
        --ckpt_path="models/flux1-dev.safetensors" \
        --model_type="flux" \
        --clip_l="models/clip_l.safetensors" \
        --t5xxl="models/t5xxl_fp16.safetensors" \
        --ae="models/ae.safetensors" \
        --output_dir="outputs" \
        --lora_weights="saved_models/flux_dreambooth.safetensors" \
        --merge_lora_weights \
        --prompt="tjtoy toy holding sparkgpu gpu in a datacenter" \
        --width=1024 \
        --height=1024 \
        --steps=50 \
        --guidance=1.0 \
        --cfg_scale=1.0 \
        --seed=$SEED \
        --dtype="bfloat16"
done