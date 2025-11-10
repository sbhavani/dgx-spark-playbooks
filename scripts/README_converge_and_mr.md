# Converge and MR Script

This script automates the process of converging all playbooks and creating a merge request to the API Catalog repository.

## Overview

The `converge_and_mr.py` script performs the following steps:

1. **Auto-discovers all playbooks** (excluding `nvidia/a-template-project` by default)
2. **Converges each playbook** to generate `conf.yaml` and `ux-conf.yaml` files
3. **Clones the API Catalog repository** from GitLab
4. **Copies the generated YAML files** to the correct model folders
5. **Creates a new branch** with the changes
6. **Commits and pushes** the changes
7. **Creates a merge request** using GitLab API

**By default**, the script auto-discovers all playbooks with `metadata.yaml` and excludes the template project (`nvidia/a-template-project`).

## CI/CD Setup

### Required Environment Variables

The following environment variables must be set in GitLab CI/CD Settings > Variables:

#### Required
- `GITLAB_MASTER_TOKEN_API_CATALOG` - GitLab token with these permissions:
  - `api` - Create merge requests
  - `read_repository` - Clone the repository
  - `write_repository` - Push changes

#### Optional
- `MR_REVIEWER_USERNAME` - GitLab username to add as reviewer on created MRs
  - Example: `margaretz`
  - The script will look up the user ID and add them as a reviewer
  - Can add multiple reviewers using `--reviewer` flag multiple times

#### Used by converge_playbooks.py
- `GITLAB_ASSET_BASEURL` - Base URL for GitHub assets
- `GITLAB_REPO_BASEURL` - Base URL for GitHub repository
- `GITLAB_RAW_CONTENT_BASEURL` - Base URL for raw GitHub content
- `SRC_ASSETS_URL` - Source assets repository URL

### GitLab CI Job

The job is defined in `.gitlab-ci.yml`:

```yaml
generate-convergence-output:
  stage: generate
  image: python:3.9-slim
  before_script:
    - apt-get update && apt-get install -y git
    - pip install requests
    - git config --global user.email "automaton@nvidia.com"
    - git config --global user.name "GitLab CI"
  script:
    - python3 -u scripts/converge_and_mr.py
        --output-dir convergence-output
        --api-catalog-repo "https://gitlab-master.nvidia.com/api-catalog/dgx-spark-playbooks"
        --api-catalog-token "$GITLAB_MASTER_TOKEN_API_CATALOG"
        --gitlab-url "https://gitlab-master.nvidia.com"
        --project-id "api-catalog%2Fdgx-spark-playbooks"
        --target-branch "main"
        --allow-forbidden-refs
  artifacts:
    paths:
      - convergence-output/
    expire_in: 7 days
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      when: manual
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
```

### Triggering the Job

The job is configured as `manual` and will appear in the pipeline. To run it:

1. Go to CI/CD > Pipelines in GitLab
2. Find your pipeline
3. Click the play button (▶️) on the `generate-convergence-output` job

## Local Testing

You can test the script locally before running in CI/CD:

### Setup

```bash
# Export required environment variables
export GITLAB_ASSET_BASEURL="https://github.com/NVIDIA/dgx-spark-playbooks/blob/main"
export GITLAB_REPO_BASEURL="https://github.com/NVIDIA/dgx-spark-playbooks"
export GITLAB_RAW_CONTENT_BASEURL="https://raw.githubusercontent.com/NVIDIA/dgx-spark-playbooks/refs/heads/main"
export SRC_ASSETS_URL="dummy"
export DST_REPOS_JSON='[]'
export GITLAB_MASTER_TOKEN_API_CATALOG="your-token-here"
```

### Run the Script

```bash
python3 scripts/converge_and_mr.py \
  --output-dir test-output \
  --api-catalog-repo "https://gitlab-master.nvidia.com/api-catalog/dgx-spark-playbooks" \
  --api-catalog-token "$GITLAB_MASTER_TOKEN_API_CATALOG" \
  --gitlab-url "https://gitlab-master.nvidia.com" \
  --project-id "api-catalog%2Fdgx-spark-playbooks" \
  --target-branch "main" \
  --allow-forbidden-refs
```

### Test Without Creating MR

To test the convergence and file copying without creating an actual merge request:

```bash
python3 scripts/converge_and_mr.py \
  --output-dir test-output \
  --api-catalog-repo "https://gitlab-master.nvidia.com/api-catalog/dgx-spark-playbooks" \
  --api-catalog-token "$GITLAB_MASTER_TOKEN_API_CATALOG" \
  --gitlab-url "https://gitlab-master.nvidia.com" \
  --project-id "api-catalog%2Fdgx-spark-playbooks" \
  --skip-mr
```

## Command Line Options

```
--output-dir TEXT           Output directory for converged files (default: convergence-output)
--api-catalog-repo TEXT     API Catalog repository URL (required)
--api-catalog-token TEXT    GitLab token for API Catalog repository (required)
--gitlab-url TEXT           GitLab instance URL (default: https://gitlab-master.nvidia.com)
--project-id TEXT           GitLab project ID for API Catalog (required)
--target-branch TEXT        Target branch for merge request (default: main)
--reviewer USERNAME         GitLab username to add as reviewer (can be used multiple times)
--exclude MODEL             Exclude specific models (can be used multiple times, default: nvidia/a-template-project)
--use-gitlab-ci             Use MODEL list from .gitlab-ci.yml instead of auto-discovering
--gitlab-ci-file TEXT       Path to .gitlab-ci.yml file when using --use-gitlab-ci (default: .gitlab-ci.yml)
--allow-forbidden-refs      Allow forbidden references during convergence
--skip-mr                   Skip MR creation (for testing)
```

### Model Selection

**Default behavior (recommended):**
- Auto-discovers all playbooks with `metadata.yaml`
- Excludes `nvidia/a-template-project` by default
- Processes all other playbooks automatically

**Excluding additional models:**
```bash
# Exclude multiple models
python3 scripts/converge_and_mr.py \
  --exclude nvidia/a-template-project \
  --exclude nvidia/another-project \
  ...
```

**Using .gitlab-ci.yml MODEL list:**
- Use `--use-gitlab-ci` flag to read from `.gitlab-ci.yml` file's `.models` section
- Only processes playbooks explicitly listed in the MODEL array
- Useful if you need strict control over which playbooks are processed

### Adding Reviewers to MRs

**Add single reviewer:**
```bash
python3 scripts/converge_and_mr.py \
  --reviewer margaretz \
  ...
```

**Add multiple reviewers:**
```bash
python3 scripts/converge_and_mr.py \
  --reviewer margaretz \
  --reviewer johndoe \
  --reviewer janedoe \
  ...
```

The script will automatically look up each username and add them as reviewers to the created MR.

## Project ID Format

The `--project-id` parameter should be URL-encoded. For example:
- Repository path: `api-catalog/dgx-spark-playbooks`
- Encoded project ID: `api-catalog%2Fdgx-spark-playbooks`

Alternatively, you can use the numeric project ID which can be found on the repository's settings page.

## Troubleshooting

### Authentication Failed

If you get authentication errors:
1. Verify the token has the correct permissions (`api`, `read_repository`, `write_repository`)
2. Check that the token hasn't expired
3. Ensure the token is properly set in GitLab CI/CD variables

### MR Creation Failed

If the branch pushes successfully but MR creation fails:
1. Check that the project ID is correct and properly URL-encoded
2. Verify the target branch exists
3. Check that there isn't already an open MR from the same branch
4. Manually create the MR from the GitLab UI using the pushed branch

### No Changes to Commit

If you see "No changes to commit":
1. Verify that playbooks were converged successfully
2. Check that YAML files were generated in the output directory
3. Ensure the API Catalog repo was cloned successfully

## Output

The script will create:
- `convergence-output/<model-name>/conf.yaml` - Configuration files
- `convergence-output/<model-name>/ux-conf.yaml` - UX configuration files with readable markdown
- `convergence-output/api-catalog-repo/` - Cloned API Catalog repository with changes

## Artifacts

In CI/CD, the `convergence-output/` directory is saved as an artifact for 7 days, allowing you to:
- Download and inspect the generated files
- Debug issues with convergence
- Review changes before they're merged

