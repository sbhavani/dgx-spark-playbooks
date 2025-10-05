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
hf download black-forest-labs/FLUX.1-dev ae.safetensors --local-dir models/vae
hf download black-forest-labs/FLUX.1-dev flux1-dev.safetensors --local-dir  models/checkpoints
hf download comfyanonymous/flux_text_encoders clip_l.safetensors --local-dir models/text_encoders
hf download comfyanonymous/flux_text_encoders t5xxl_fp16.safetensors --local-dir models/text_encoders