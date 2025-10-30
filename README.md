# DGX Spark Playbooks

This repository contains step-by-step tutorials for NVIDIA DGX Spark devices. Each playbook walks users through installing and configuring specific tools or workflows.

## Quick Start

Want to create a new playbook? Here's the simple process:

1. **Copy the template**
   ```bash
   cp -r nvidia/a-template-project nvidia/my-new-playbook
   ```

2. **Fill playbook content**
   - Each .md file corresponds to a tab on the build site. E.g. [Overview](https://build.nvidia.com/spark/comfy-ui/overview) or [Troubleshooting](https://build.nvidia.com/spark/comfy-ui/troubleshooting) tab
   - Replace all the `{placeholder}` text with your actual content
   - Focus on `metadata.yaml`, `overview.md`, `instructions.md`, and `troubleshooting.md`
   - Rename or add new .md files if needed. E.g. add `run-two-spark.md` for instructions to run on two Sparks. Make sure to add new/renamed files to the `metadata.yaml` file. Otherwise the content won't be published on build site.
   - Add any code/assets to an `assets/` folder if needed

3. **Create a merge request and go through review**
   - Resolve test failures and reviewer comments
   - The CI/CD pipeline will handle validation and publishing

## Getting help

- Join #dgx-spark-playbooks slack channel and raise a question there.
