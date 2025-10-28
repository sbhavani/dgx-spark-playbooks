# Basic idea

This playbook guides you through setting up and using Pytorch for fine-tuning large language models on NVIDIA Spark devices.

# What you'll accomplish

You'll establish a complete fine-tuning environment for large language models (1-70B parameters) on your NVIDIA Spark device. 
By the end, you'll have a working installation that supports parameter-efficient fine-tuning (PEFT) and supervised fine-tuning (SFT).

# What to know before starting

- Previous experience with fine-tuning in Pytorch
- Working with Docker



# Prerequisites
Recipes are specifically for DIGITS SPARK. Please make sure that OS and drivers are latest.


# Ancillary files

ALl files required for fine-tuning are included in the folder in [the GitHub repository here](${GITLAB_ASSET_BASEURL}/${MODEL}).

# Time & risk

* **Time estimate:** 30-45 mins for setup and runing fine-tuning. Fine-tuning run time varies depending on model size 
* **Risks:** Model downloads can be large (several GB), ARM64 package compatibility issues may require troubleshooting.
