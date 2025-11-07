#!/usr/bin/env python3
"""
Converge all playbooks and create MR to API Catalog repository

This script:
1. Converges all playbooks to generate conf.yaml and ux-conf.yaml files
2. Clones the API Catalog repository
3. Copies the generated YAML files to the correct model folders
4. Creates a merge request with the changes
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional
import requests


def run_command(cmd: List[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Execute shell command with error handling"""
    print(f"→ Running: {' '.join(cmd)}", flush=True)
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}", flush=True)
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        raise
    except subprocess.TimeoutExpired as e:
        print(f"❌ Command timed out: {' '.join(cmd)}", flush=True)
        raise


def get_all_models(project_root: Path, exclude: List[str] = None) -> List[str]:
    """
    Discover all model directories with metadata.yaml
    
    Args:
        project_root: Root directory to search
        exclude: List of model paths to exclude (e.g., ['nvidia/a-template-project'])
    
    Returns:
        Sorted list of model paths
    """
    if exclude is None:
        exclude = []
    
    models = []
    
    # Look for publisher directories (e.g., nvidia/)
    for publisher_dir in project_root.iterdir():
        if not publisher_dir.is_dir() or publisher_dir.name.startswith('.'):
            continue
        
        # Look for model directories within publisher
        for model_dir in publisher_dir.iterdir():
            if not model_dir.is_dir() or model_dir.name.startswith('.'):
                continue
            
            # Check if it has metadata.yaml (indicates it's a playbook)
            if (model_dir / 'metadata.yaml').exists():
                model_path = f"{publisher_dir.name}/{model_dir.name}"
                
                # Skip excluded models
                if model_path not in exclude:
                    models.append(model_path)
                else:
                    print(f"   ⏭️  Skipping excluded: {model_path}")
    
    return sorted(models)


def get_models_from_gitlab_ci(gitlab_ci_path: Path) -> List[str]:
    """
    Extract model list from .gitlab-ci.yml file
    
    Returns:
        List of model paths from the .models section
    """
    import yaml
    
    try:
        with open(gitlab_ci_path, 'r') as f:
            gitlab_ci = yaml.safe_load(f)
        
        # Extract models from .models section
        if '.models' in gitlab_ci:
            models_section = gitlab_ci['.models']
            if isinstance(models_section, list) and len(models_section) > 0:
                # The structure is: [{'MODEL': ['nvidia/model1', 'nvidia/model2', ...]}]
                first_item = models_section[0]
                if isinstance(first_item, dict) and 'MODEL' in first_item:
                    models = first_item['MODEL']
                    if isinstance(models, list):
                        print(f"Found {len(models)} models in .gitlab-ci.yml")
                        return models
        
        print("⚠️  Warning: Could not find models in .gitlab-ci.yml .models section")
        return []
    
    except FileNotFoundError:
        print(f"❌ Error: {gitlab_ci_path} not found")
        return []
    except yaml.YAMLError as e:
        print(f"❌ Error parsing {gitlab_ci_path}: {e}")
        return []
    except Exception as e:
        print(f"❌ Error reading models from .gitlab-ci.yml: {e}")
        return []


def converge_all_playbooks(models: List[str], output_dir: Path, allow_forbidden_refs: bool = False) -> int:
    """
    Converge all playbooks using converge_playbooks.py
    
    Returns:
        Number of successful conversions
    """
    print("=" * 80)
    print("📦 STEP 1: Converging all playbooks")
    print("=" * 80)
    
    successful = 0
    failed = []
    
    for model in models:
        print(f"\n🔄 Converging {model}...")
        try:
            cmd = [
                'python3', 'scripts/converge_playbooks.py',
                '--model', model,
                '--output-dir', str(output_dir),
                '--prepare-only'
            ]
            
            if allow_forbidden_refs:
                cmd.append('--allow-forbidden-refs')
            
            run_command(cmd)
            successful += 1
            print(f"✅ {model} converged successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to converge {model}")
            failed.append(model)
    
    print(f"\n📊 Summary: {successful}/{len(models)} playbooks converged successfully")
    if failed:
        print(f"⚠️  Failed playbooks: {', '.join(failed)}")
    
    return successful


def clone_api_catalog_repo(repo_url: str, dest_path: Path, token: str) -> bool:
    """Clone the API catalog repository"""
    print("\n" + "=" * 80)
    print("📥 STEP 2: Cloning API Catalog repository")
    print("=" * 80)
    
    # Inject token into URL
    if repo_url.startswith('https://'):
        url_no_proto = repo_url[8:]
        auth_url = f"https://oauth2:{token}@{url_no_proto}"
    else:
        print(f"❌ Error: Non-HTTPS URL not supported: {repo_url}")
        return False
    
    try:
        run_command(['git', 'clone', auth_url, str(dest_path)])
        print(f"✅ Cloned to {dest_path}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to clone {repo_url}")
        return False


def copy_yaml_files(models: List[str], source_dir: Path, dest_dir: Path) -> int:
    """
    Copy generated YAML files to API catalog repository
    
    Returns:
        Number of files copied
    """
    print("\n" + "=" * 80)
    print("📋 STEP 3: Copying YAML files to API Catalog repository")
    print("=" * 80)
    
    copied_count = 0
    
    for model in models:
        source_model_dir = source_dir / model
        dest_model_dir = dest_dir / model
        
        # Ensure destination directory exists
        dest_model_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy conf.yaml
        conf_source = source_model_dir / 'conf.yaml'
        conf_dest = dest_model_dir / 'conf.yaml'
        if conf_source.exists():
            import shutil
            shutil.copy2(conf_source, conf_dest)
            print(f"✅ Copied {model}/conf.yaml")
            copied_count += 1
        else:
            print(f"⚠️  {model}/conf.yaml not found, skipping")
        
        # Copy ux-conf.yaml
        ux_conf_source = source_model_dir / 'ux-conf.yaml'
        ux_conf_dest = dest_model_dir / 'ux-conf.yaml'
        if ux_conf_source.exists():
            import shutil
            shutil.copy2(ux_conf_source, ux_conf_dest)
            print(f"✅ Copied {model}/ux-conf.yaml")
            copied_count += 1
        else:
            print(f"⚠️  {model}/ux-conf.yaml not found, skipping")
    
    print(f"\n📊 Copied {copied_count} YAML files")
    return copied_count


def create_branch_and_commit(repo_path: Path, branch_name: str) -> bool:
    """Create a new branch and commit changes"""
    print("\n" + "=" * 80)
    print("🔀 STEP 4: Creating branch and committing changes")
    print("=" * 80)
    
    try:
        # Create and checkout new branch
        run_command(['git', 'checkout', '-b', branch_name], cwd=repo_path)
        print(f"✅ Created branch: {branch_name}")
        
        # Stage all changes
        run_command(['git', 'add', '.'], cwd=repo_path)
        
        # Check if there are changes to commit
        result = run_command(
            ['git', 'diff', '--staged', '--quiet'],
            cwd=repo_path,
            check=False
        )
        
        if result.returncode == 0:
            print("ℹ️  No changes to commit")
            return False
        
        # Commit changes
        commit_msg = f"Update playbook YAML files - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        run_command(['git', 'commit', '-m', commit_msg], cwd=repo_path)
        print(f"✅ Committed changes: {commit_msg}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create branch and commit: {e}")
        return False


def push_branch(repo_path: Path, branch_name: str, token: str) -> bool:
    """Push branch to remote"""
    print("\n" + "=" * 80)
    print("⬆️  STEP 5: Pushing branch to remote")
    print("=" * 80)
    
    try:
        # Set up remote with token (in case it's not already configured)
        result = run_command(['git', 'remote', 'get-url', 'origin'], cwd=repo_path)
        origin_url = result.stdout.strip()
        
        # Push branch
        run_command(['git', 'push', '-u', 'origin', branch_name], cwd=repo_path)
        print(f"✅ Pushed branch: {branch_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to push branch: {e}")
        return False


def create_merge_request(
    gitlab_url: str,
    project_id: str,
    source_branch: str,
    target_branch: str,
    token: str,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Optional[str]:
    """
    Create a merge request using GitLab API
    
    Returns:
        MR URL if successful, None otherwise
    """
    print("\n" + "=" * 80)
    print("🔀 STEP 6: Creating Merge Request")
    print("=" * 80)
    
    if not title:
        title = f"Update playbook YAML files - {time.strftime('%Y-%m-%d')}"
    
    if not description:
        description = "Automated update of playbook configuration files (conf.yaml and ux-conf.yaml)"
    
    api_url = f"{gitlab_url}/api/v4/projects/{project_id}/merge_requests"
    
    headers = {
        'PRIVATE-TOKEN': token,
        'Content-Type': 'application/json'
    }
    
    data = {
        'source_branch': source_branch,
        'target_branch': target_branch,
        'title': title,
        'description': description,
        'remove_source_branch': True
    }
    
    try:
        print(f"Creating MR from {source_branch} to {target_branch}...")
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        
        mr_data = response.json()
        mr_url = mr_data.get('web_url')
        print(f"✅ Merge Request created: {mr_url}")
        return mr_url
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to create merge request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Converge all playbooks and create MR to API Catalog'
    )
    parser.add_argument(
        '--output-dir',
        default='convergence-output',
        help='Output directory for converged files'
    )
    parser.add_argument(
        '--api-catalog-repo',
        required=True,
        help='API Catalog repository URL'
    )
    parser.add_argument(
        '--api-catalog-token',
        required=True,
        help='GitLab token for API Catalog repository'
    )
    parser.add_argument(
        '--gitlab-url',
        default='https://gitlab-master.nvidia.com',
        help='GitLab instance URL'
    )
    parser.add_argument(
        '--project-id',
        required=True,
        help='GitLab project ID for API Catalog'
    )
    parser.add_argument(
        '--target-branch',
        default='main',
        help='Target branch for merge request'
    )
    parser.add_argument(
        '--allow-forbidden-refs',
        action='store_true',
        help='Allow forbidden references during convergence'
    )
    parser.add_argument(
        '--skip-mr',
        action='store_true',
        help='Skip MR creation (for testing)'
    )
    parser.add_argument(
        '--exclude',
        action='append',
        default=None,
        help='Exclude specific models (can be used multiple times, default: nvidia/a-template-project)'
    )
    parser.add_argument(
        '--use-gitlab-ci',
        action='store_true',
        help='Use MODEL list from .gitlab-ci.yml instead of auto-discovering'
    )
    parser.add_argument(
        '--gitlab-ci-file',
        default='.gitlab-ci.yml',
        help='Path to .gitlab-ci.yml file when using --use-gitlab-ci (default: .gitlab-ci.yml)'
    )
    
    args = parser.parse_args()
    
    # Paths
    project_root = Path('.')
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    api_catalog_dir = output_dir / 'api-catalog-repo'
    
    # Set default exclusions
    if args.exclude is None:
        exclude_models = ['nvidia/a-template-project']
    else:
        exclude_models = args.exclude
    
    # Step 1: Get model list
    if args.use_gitlab_ci:
        print(f"🔍 Reading model list from {args.gitlab_ci_file}...")
        gitlab_ci_path = Path(args.gitlab_ci_file)
        models = get_models_from_gitlab_ci(gitlab_ci_path)
        if not models:
            print("❌ No models found in .gitlab-ci.yml, exiting")
            print("💡 Remove --use-gitlab-ci to auto-discover all playbooks")
            sys.exit(1)
        print(f"📋 Processing {len(models)} playbooks from .gitlab-ci.yml")
    else:
        print("🔍 Auto-discovering all playbooks...")
        if exclude_models:
            print(f"   Excluding: {', '.join(exclude_models)}")
        models = get_all_models(project_root, exclude=exclude_models)
        print(f"📋 Found {len(models)} playbooks to process")
    
    # Step 2: Converge all playbooks
    successful = converge_all_playbooks(models, output_dir, args.allow_forbidden_refs)
    if successful == 0:
        print("❌ No playbooks converged successfully, exiting")
        sys.exit(1)
    
    # Step 3: Clone API catalog repo
    if not clone_api_catalog_repo(args.api_catalog_repo, api_catalog_dir, args.api_catalog_token):
        sys.exit(1)
    
    # Step 4: Copy YAML files
    copied = copy_yaml_files(models, output_dir, api_catalog_dir)
    if copied == 0:
        print("⚠️  No files copied, nothing to commit")
        sys.exit(0)
    
    # Step 5: Create branch and commit
    branch_name = f"update-playbooks-{time.strftime('%Y%m%d-%H%M%S')}"
    if not create_branch_and_commit(api_catalog_dir, branch_name):
        print("ℹ️  No changes to push")
        sys.exit(0)
    
    # Step 6: Push branch
    if not push_branch(api_catalog_dir, branch_name, args.api_catalog_token):
        sys.exit(1)
    
    # Step 7: Create merge request
    if not args.skip_mr:
        mr_url = create_merge_request(
            args.gitlab_url,
            args.project_id,
            branch_name,
            args.target_branch,
            args.api_catalog_token
        )
        
        if mr_url:
            print("\n" + "=" * 80)
            print("✅ SUCCESS!")
            print(f"📋 Merge Request: {mr_url}")
            print("=" * 80)
        else:
            print("\n⚠️  Branch pushed but MR creation failed")
            print("You may need to create the MR manually")
            sys.exit(1)
    else:
        print("\n✅ Branch pushed (MR creation skipped)")
    
    sys.exit(0)


if __name__ == '__main__':
    main()

