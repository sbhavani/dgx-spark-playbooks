#!/usr/bin/env python3
"""
Purpose: Publish all converged playbooks to public repos (complete regeneration)
Inputs: Artifacts from all converge jobs in convergence-output/
Outputs: Fresh destination repo with all models
Assumptions: Artifacts from parallel jobs are aggregated by GitLab
Edge cases: Missing artifacts, empty repo
Notes: Deletes all destination content first, ensures exact match with source
"""

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path


def run_git(cmd, cwd=None, stream=True, timeout=600):
    """Execute git command with streaming output"""
    print(f"   → {' '.join(cmd)}", flush=True)
    sys.stdout.flush()
    
    result = subprocess.run(
        cmd, cwd=cwd, timeout=timeout,
        stdout=None if stream else subprocess.PIPE,
        stderr=None if stream else subprocess.PIPE
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result


def publish_all(artifacts_dir: str = 'convergence-output', push: bool = False, allow_forbidden_refs: bool = False, censor_forbidden_refs: bool = False, skip_models: list = None) -> int:
    """
    Publish all playbooks with complete regeneration
    
    Args:
        artifacts_dir: Directory containing aggregated artifacts from converge jobs
        push: Whether to push changes to remote
        allow_forbidden_refs: Allow forbidden references (testing only)
        censor_forbidden_refs: Replace forbidden references with ****** in output
        skip_models: List of model paths to exclude (format: "publisher/model")
        
    Returns:
        Exit code (0 for success, 1 for errors)
        
    Note:
        If artifacts don't exist, generates them by running converge for all models
    """
    skip_models = skip_models or []
    artifacts_path = Path(artifacts_dir)
    
    print("=" * 70, flush=True)
    print("📦 Publishing All Playbooks (Complete Regeneration)", flush=True)
    print(f"   Artifacts: {artifacts_path}", flush=True)
    print(f"   Push: {push}", flush=True)
    print("=" * 70, flush=True)
    sys.stdout.flush()
    
    # Clean artifacts directory to start fresh (remove accumulated content from previous runs)
    if artifacts_path.exists():
        print(f"\n🧹 Cleaning old artifacts directory", flush=True)
        shutil.rmtree(artifacts_path)
        print(f"   ✅ Old artifacts removed", flush=True)
    
    artifacts_path.mkdir(exist_ok=True)
    
    # Discover all models that SHOULD exist
    from converge_playbooks import PlaybookConverter
    
    project_root = Path('.')
    all_models = []
    
    for publisher_dir in project_root.iterdir():
        if not publisher_dir.is_dir() or publisher_dir.name.startswith('.'):
            continue
        for model_dir in publisher_dir.iterdir():
            if not model_dir.is_dir() or model_dir.name.startswith('.'):
                continue
            if (model_dir / 'ux-conf.yaml').exists():
                all_models.append(f"{publisher_dir.name}/{model_dir.name}")
    
    all_models = sorted(all_models)
    print(f"\n📊 Total models in source: {len(all_models)}", flush=True)
    
    # Filter out skipped models
    if skip_models:
        skip_set = set(skip_models)
        original_count = len(all_models)
        all_models = [m for m in all_models if m not in skip_set]
        skipped_count = original_count - len(all_models)
        if skipped_count > 0:
            print(f"   ⏭️  Skipping {skipped_count} model(s): {', '.join(sorted(skip_set))}", flush=True)
            print(f"   📊 Models to publish: {len(all_models)}", flush=True)
    
    # Check which models are missing from artifacts
    missing_models = []
    artifacts_path.mkdir(exist_ok=True)
    
    for model in all_models:
        # Check if model has artifacts (look for the model dir in any destination alias)
        has_artifacts = False
        for item in artifacts_path.iterdir():
            if item.is_dir():
                model_path = item / model
                if model_path.exists():
                    has_artifacts = True
                    break
        
        if not has_artifacts:
            missing_models.append(model)
    
    # Generate missing models
    if missing_models:
        print(f"\n🔄 Generating {len(missing_models)} missing model(s)", flush=True)
        print("=" * 70, flush=True)
        
        for i, model in enumerate(missing_models, 1):
            print(f"\n[{i}/{len(missing_models)}] {model}", flush=True)
            sys.stdout.flush()
            
            converter = PlaybookConverter(
                model,
                output_dir=str(artifacts_path),
                push=False,
                allow_forbidden_refs=allow_forbidden_refs,
                prepare_only=True,  # Just generate markdown, no git ops
                censor_forbidden_refs=censor_forbidden_refs
            )
            
            if converter.run() != 0:
                print(f"❌ Failed: {model}")
                return 1
        
        print(f"\n✅ Generated missing content", flush=True)
    else:
        print(f"\n✅ All {len(all_models)} models have artifacts", flush=True)
    
    # Step: Clone destination and source repos (ONCE)
    print(f"\n📥 Cloning repositories (once for all models)", flush=True)
    sys.stdout.flush()
    
    dst_repos = json.loads(os.environ.get('DST_REPOS_JSON', '[]'))
    src_assets_url = os.environ.get('SRC_ASSETS_URL')
    src_assets_token = os.environ.get('GITLAB_MASTER_TOKEN_DGX_SPARK_PLAYBOOKS')
    
    # Clone source assets repo
    print(f"   📥 Cloning source assets repo...")
    src_auth_url = f"https://oauth2:{src_assets_token}@{src_assets_url.replace('https://', '')}"
    src_path = Path('source-assets')
    if src_path.exists():
        shutil.rmtree(src_path)
    run_git(['git', 'clone', '--progress', src_auth_url, str(src_path)], stream=True)
    print(f"   ✅ Source cloned", flush=True)
    
    # Process each destination repo
    for repo in dst_repos:
        alias = repo['alias']
        url = repo['url']
        token = os.environ.get(repo['token_var'])
        
        print(f"\n   📥 Cloning destination: {alias}")
        
        # Handle SSH vs HTTPS URLs differently
        if url.startswith('git@') or url.startswith('ssh://'):
            # SSH URL - use as-is (deploy key configured in before_script)
            dest_auth_url = url
            print(f"      Using SSH authentication", flush=True)
        else:
            # HTTPS URL - inject OAuth token
            dest_auth_url = f"https://oauth2:{token}@{url.replace('https://', '')}"
            print(f"      Using HTTPS OAuth authentication", flush=True)
        
        dest_path = Path(f"publish-{alias}")
        
        if dest_path.exists():
            shutil.rmtree(dest_path)
        
        run_git(['git', 'clone', '--progress', dest_auth_url, str(dest_path)], stream=True)
        print(f"   ✅ Destination cloned", flush=True)
        
        # Clear destination (except .git)
        print(f"\n🧹 Clearing destination {alias}", flush=True)
        for item in dest_path.iterdir():
            if item.name == '.git':
                continue
            if item.is_dir():
                shutil.rmtree(item)
                print(f"   🗑️  {item.name}/")
            else:
                item.unlink()
                print(f"   🗑️  {item.name}")
        print(f"   ✅ Cleared", flush=True)
        
        # Assemble content for each model
        print(f"\n📋 Assembling content for {len(all_models)} model(s)", flush=True)
        for model in all_models:
            model_basename = model.split('/')[-1]
            
            # Copy README from artifacts
            src_readme = artifacts_path / model / 'README.md'
            dest_model_dir = dest_path / model
            dest_model_dir.mkdir(parents=True, exist_ok=True)
            
            if src_readme.exists():
                shutil.copy2(src_readme, dest_model_dir / 'README.md')
            
            # Copy assets from source repo
            src_assets_dir = src_path / model_basename / 'assets'
            if src_assets_dir.exists():
                dest_assets_dir = dest_model_dir / 'assets'
                if dest_assets_dir.exists():
                    shutil.rmtree(dest_assets_dir)
                shutil.copytree(src_assets_dir, dest_assets_dir)
        
        print(f"   ✅ Model content assembled", flush=True)
        
        # Copy root files from source assets repo
        print(f"\n📄 Copying root files from source", flush=True)
        root_globs = json.loads(os.environ.get('ROOT_FILE_GLOBS_JSON', '["LICENSE*"]'))
        import glob as glob_module
        for pattern in root_globs:
            for src_file in glob_module.glob(str(src_path / pattern)):
                shutil.copy2(src_file, dest_path / Path(src_file).name)
                print(f"   📄 {Path(src_file).name}")
        
        # Copy root directories from project
        print(f"\n📂 Copying root directories from project", flush=True)
        root_dirs = json.loads(os.environ.get('ROOT_DIRS_JSON', '["src"]'))
        for dir_name in root_dirs:
            src_dir = Path(dir_name)
            if src_dir.exists():
                dest_dir = dest_path / dir_name
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(src_dir, dest_dir)
                print(f"   📂 {dir_name}/")
        
        # Generate main README
        print(f"\n📝 Generating main README.md", flush=True)
        template_path = Path('README-Public.md')
        if template_path.exists():
            with open(template_path) as f:
                template = f.read()
            
            # Generate TOC
            toc_lines = ["### NVIDIA", ""]
            for model in sorted(all_models):
                # Read displayName
                ux_path = Path(model) / 'ux-conf.yaml'
                display_name = model.split('/')[-1].replace('-', ' ').title()
                if ux_path.exists():
                    import yaml
                    with open(ux_path) as f:
                        conf = yaml.safe_load(f)
                        if conf and 'displayName' in conf:
                            display_name = conf['displayName']
                
                toc_lines.append(f"- [{display_name}]({model}/)")
            
            toc = '\n'.join(toc_lines)
            readme = template.replace('<!-- TABLE OF CONTENTS GENERATED BELOW -->', toc)
            
            with open(dest_path / 'README.md', 'w') as f:
                f.write(readme)
            print(f"   ✅ Main README generated", flush=True)
        
        if push:
            print(f"\n📤 Step 4: Push to {alias}", flush=True)
            
            # Random delay for safety
            delay = random.randint(1, 10)
            print(f"   ⏱️  Delay: {delay}s", flush=True)
            time.sleep(delay)
            
            run_git(['git', 'add', '-A'], cwd=dest_path, stream=False)
            
            # Check for changes
            result = subprocess.run(
                ['git', 'diff', '--staged', '--quiet'],
                cwd=dest_path
            )
            
            if result.returncode != 0:
                run_git(['git', 'commit', '-m', 'chore: Regenerate all playbooks'], cwd=dest_path, stream=False)
                
                # Retry push with backoff
                for attempt in range(1, 4):
                    try:
                        if attempt > 1:
                            print(f"   🔄 Retry {attempt}/3")
                            run_git(['git', 'pull', '--rebase'], cwd=dest_path, stream=True)
                        
                        run_git(['git', 'push'], cwd=dest_path, stream=True)
                        print(f"   ✅ Pushed", flush=True)
                        break
                    except subprocess.CalledProcessError:
                        if attempt < 3:
                            delay = random.randint(10, 30) * attempt
                            print(f"   ⚠️  Failed, waiting {delay}s...", flush=True)
                            time.sleep(delay)
                        else:
                            raise
            else:
                print(f"   ℹ️  No changes")
    
    # Print violations summary if any were found
    from converge_playbooks import PlaybookConverter
    PlaybookConverter.print_violations_summary()
    
    print("\n" + "=" * 70)
    print("✅ Complete!")
    print("=" * 70)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Publish all playbooks to public repos')
    parser.add_argument(
        '--artifacts-dir',
        default='convergence-output',
        help='Directory containing aggregated artifacts (default: convergence-output)'
    )
    parser.add_argument(
        '--push',
        action='store_true',
        help='Push changes to remote repositories'
    )
    parser.add_argument(
        '--allow-forbidden-refs',
        action='store_true',
        help='Allow forbidden references (for testing only)'
    )
    parser.add_argument(
        '--censor-forbidden-refs',
        action='store_true',
        help='Replace forbidden references with ****** in published content'
    )
    parser.add_argument(
        '--skip-models',
        help='Comma-separated list of models to skip (e.g., "nvidia/sglang,nvidia/vibe-coding")'
    )
    args = parser.parse_args()
    
    # Parse skip models from CLI or env var (priority: CLI > SKIP_MODELS > SKIP_MODELS_JSON)
    skip_models = []
    if args.skip_models:
        skip_models = [m.strip() for m in args.skip_models.split(',') if m.strip()]
    elif os.environ.get('SKIP_MODELS'):
        # Comma-separated string env var
        skip_models = [m.strip() for m in os.environ['SKIP_MODELS'].split(',') if m.strip()]
    elif os.environ.get('SKIP_MODELS_JSON'):
        # JSON array env var
        skip_models = json.loads(os.environ['SKIP_MODELS_JSON'])
    
    sys.exit(publish_all(args.artifacts_dir, args.push, args.allow_forbidden_refs, args.censor_forbidden_refs, skip_models))

