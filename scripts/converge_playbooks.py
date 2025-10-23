#!/usr/bin/env python3
"""
Purpose: Converge DGX Spark playbook content to external GitHub repositories AND API Catalog repositories
Inputs: 
  - Model directory path (e.g., nvidia/jax)
  - Source files directory
  - Destination github repositories (JSON config)
  - Destination API Catalog repositories (JSON config)
Outputs: 
  - conf.yaml and ux-conf.yaml files generated from source files
  - Markdown files generated from source files
  - Assets copied to destination repos
  - All changes stored as artifacts in convergence-output/
Assumptions: 
  - Assets repo has subdirs matching model basename
  - Git credentials are provided via environment variables
Edge cases: 
  - Missing metadata.yaml, overview.md and instructions.md (skip gracefully)
  - Missing troubleshooting.md or assets directory (warning only)
  - Git clone failures (error and exit)
Notes: Files are prepared but NOT pushed - review artifacts first
"""

import argparse
import glob as glob_module
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import yaml
from pathlib import Path
from typing import Dict, List, Optional


class PlaybookConverter:
    """Handles convergence of playbook content to external repositories"""
    
    # Default forbidden patterns (internal references that shouldn't be public)
    DEFAULT_FORBIDDEN_PATTERNS = [
        r'gitlab-master\.nvidia\.com',           # Internal GitLab
        r'gitlab-master\.nvidia\.com:5005',      # Internal registry
        r'urm\.nvidia\.com',                     # Internal URM registry
        r'nvcr\.io.*-internal',                  # Internal NGC containers
        r'@nvidia\.com',                         # NVIDIA email addresses
    ]
    
    # Default root file globs to copy to destination repos
    DEFAULT_ROOT_FILE_GLOBS = [
        'LICENSE*',
        'CONTRIBUTING.md',
        'CODE_OF_CONDUCT.md',
    ]
    
    # Default root directories to copy to destination repos
    DEFAULT_ROOT_DIRS = [
        'src',  # Images and assets for README-Public.md
    ]
    
    def __init__(self, model_path: str, output_dir: str = "convergence-output", 
                 push: bool = False, allow_forbidden_refs: bool = False,
                 project_root: str = ".", prepare_only: bool = False,
                 censor_forbidden_refs: bool = False):
        self.model_path = Path(model_path)
        self.model_name = model_path  # e.g., "nvidia/jax"
        self.model_basename = self.model_path.name  # e.g., "jax"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.push = push
        self.allow_forbidden_refs = allow_forbidden_refs
        self.project_root = Path(project_root)
        self.prepare_only = prepare_only  # If True, skip git operations
        self.censor_forbidden_refs = censor_forbidden_refs  # If True, replace violations with ******
        
        # Read configuration from environment
        self.src_assets_url = os.environ.get('SRC_ASSETS_URL')
        self.src_assets_token = os.environ.get('GITLAB_MASTER_TOKEN_DGX_SPARK_PLAYBOOKS')
        
         # Parse destination repos from JSON
        dst_repos_json = os.environ.get('DST_REPOS_JSON', '[]')
        try:
            self.dst_repos = json.loads(dst_repos_json)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing DST_REPOS_JSON: {e}")
            sys.exit(1)

        # Load forbidden patterns (allow override from env)
        forbidden_patterns_json = os.environ.get('FORBIDDEN_PATTERNS_JSON')
        if forbidden_patterns_json:
            try:
                self.forbidden_patterns = json.loads(forbidden_patterns_json)
            except json.JSONDecodeError as e:
                print(f"⚠️  Warning: Invalid FORBIDDEN_PATTERNS_JSON, using defaults: {e}")
                self.forbidden_patterns = self.DEFAULT_FORBIDDEN_PATTERNS
        else:
            self.forbidden_patterns = self.DEFAULT_FORBIDDEN_PATTERNS
        
        # Get all models list for main README generation
        # This comes from scanning the project or from environment
        self.all_models = self._discover_all_models()
    
    def _discover_all_models(self) -> List[str]:
        """
        Discover all model directories in the project
        
        Returns:
            List of model paths (e.g., ["nvidia/jax", "nvidia/ollama", ...])
            
        Note:
            Scans for directories with ux-conf.yaml files
        """
        all_models = []
        
        # Look for publisher directories (e.g., nvidia/)
        for publisher_dir in self.project_root.iterdir():
            if not publisher_dir.is_dir() or publisher_dir.name.startswith('.'):
                continue
            
            # Look for model directories within publisher
            for model_dir in publisher_dir.iterdir():
                if not model_dir.is_dir() or model_dir.name.startswith('.'):
                    continue
                
                # Check if it has ux-conf.yaml (indicates it's a playbook)
                if (model_dir / 'ux-conf.yaml').exists():
                    model_path = f"{publisher_dir.name}/{model_dir.name}"
                    all_models.append(model_path)
        
        return sorted(all_models)
            
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, 
                   check: bool = True, timeout: int = 300, stream_output: bool = False) -> subprocess.CompletedProcess:
        """
        Execute shell command with error handling and timeout
        
        Args:
            cmd: Command and arguments as list
            cwd: Working directory for command
            check: Whether to raise on non-zero exit
            timeout: Command timeout in seconds (default: 300s/5min)
            stream_output: If True, stream output to console (for long operations like push)
            
        Returns:
            CompletedProcess instance
            
        Raises:
            subprocess.CalledProcessError if command fails and check=True
            subprocess.TimeoutExpired if command times out
        """
        # Log command for debugging (mask tokens)
        cmd_str = ' '.join(cmd)
        if 'oauth2' in cmd_str or 'token' in cmd_str.lower():
            # Mask sensitive parts
            masked_cmd = re.sub(r'oauth2:[^@]+@', 'oauth2:[MASKED]@', cmd_str)
            print(f"      → Running: {masked_cmd}", flush=True)
        else:
            print(f"      → Running: {cmd_str}", flush=True)
        sys.stdout.flush()
        
        try:
            if stream_output:
                # For long operations, stream output directly to console
                result = subprocess.run(
                    cmd,
                    cwd=cwd,
                    check=check,
                    timeout=timeout,
                    # Don't capture - let output stream to console
                    stdout=None,
                    stderr=None
                )
            else:
                # For quick operations, capture output
                result = subprocess.run(
                    cmd,
                    cwd=cwd,
                    check=check,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            return result
        except subprocess.TimeoutExpired as e:
            print(f"❌ Command timed out after {timeout}s: {' '.join(cmd)}", flush=True)
            print(f"   Working directory: {cwd}", flush=True)
            raise
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(cmd)}", flush=True)
            if hasattr(e, 'stdout') and e.stdout:
                print(f"   stdout: {e.stdout}", flush=True)
            if hasattr(e, 'stderr') and e.stderr:
                print(f"   stderr: {e.stderr}", flush=True)
            raise
            
    def git_clone_with_token(self, url: str, dest: Path, token: str) -> bool:
        """
        Clone git repository using OAuth token
        
        Args:
            url: Repository URL (without credentials)
            dest: Local destination path
            token: OAuth token for authentication
            
        Returns:
            True if successful, False otherwise
        """
        # Extract URL components for OAuth injection
        if url.startswith('https://'):
            url_no_proto = url[8:]  # Remove https://
            auth_url = f"https://oauth2:{token}@{url_no_proto}"
        else:
            print(f"⚠️  Warning: Non-HTTPS URL, using as-is: {url}", flush=True)
            auth_url = url
            
        print(f"   Cloning to {dest}...", flush=True)
        sys.stdout.flush()
        
        try:
            # Use longer timeout for clones (10 min) and stream progress output
            self.run_command(
                ['git', 'clone', '--progress', auth_url, str(dest)], 
                timeout=600,
                stream_output=True
            )
            print(f"   ✅ Clone successful", flush=True)
            return True
        except subprocess.TimeoutExpired:
            print(f"❌ Clone timed out after 10 minutes: {url}", flush=True)
            return False
        except subprocess.CalledProcessError:
            print(f"❌ Failed to clone {url}", flush=True)
            return False
            
    def _substitute_gitlab_variables(self, data, mask_secrets: bool = True, prefix: str = "GITLAB_", allowed_vars=None, _track_subs=None):
        """
        Recursively substitute GitLab CI variables in configuration.
        Variables should be specified as ${GITLAB_VAR_NAME} or ${MODEL} in the configuration.
        
        Args:
            data: The data structure to process
            mask_secrets: Whether to mask sensitive values in logs
            prefix: Only substitute variables with this prefix (default: "GITLAB_")
            allowed_vars: Additional variable names allowed without prefix (default: ["MODEL"])
            _track_subs: Internal - tracks substitutions for summary logging
        
        Returns:
            The processed data with variables substituted
        """
        if allowed_vars is None:
            allowed_vars = ["MODEL"]
        
        # Initialize substitution tracker on first call
        if _track_subs is None:
            _track_subs = {}
            is_root_call = True
        else:
            is_root_call = False
            
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                result[key] = self._substitute_gitlab_variables(value, mask_secrets, prefix, allowed_vars, _track_subs)
            return result
        elif isinstance(data, list):
            return [self._substitute_gitlab_variables(item, mask_secrets, prefix, allowed_vars, _track_subs) for item in data]
        elif isinstance(data, str):
            # Pattern to match ${VAR_NAME}
            pattern = r"\$\{([^}]+)\}"
            matches = re.findall(pattern, data)

            if matches:
                result = data
                for var_name in matches:
                    # Only substitute variables with the specified prefix or in allowed list
                    if not var_name.startswith(prefix) and var_name not in allowed_vars:
                        continue
                    
                    # Special handling for MODEL - use instance attribute
                    if var_name == "MODEL":
                        env_value = str(self.model_path)  # e.g., "nvidia/pytorch-fine-tune"
                    else:
                        env_value = os.getenv(var_name)
                    
                    if env_value is not None:
                        placeholder = f"${{{var_name}}}"
                        result = result.replace(placeholder, env_value)
                        
                        # Track unique substitutions
                        if var_name not in _track_subs:
                            _track_subs[var_name] = {
                                'value': env_value,
                                'is_secret': mask_secrets and any(
                                    secret_keyword in var_name.lower()
                                    for secret_keyword in [
                                        "password", "secret", "key", "token", "auth", "credential"
                                    ]
                                )
                            }

                # Print summary only on root call completion
                if is_root_call and _track_subs:
                    for var_name, info in _track_subs.items():
                        if info['is_secret']:
                            print(f"   🔐 Substituted {var_name}: [MASKED]")
                        else:
                            print(f"   ✅ Substituted {var_name}: {info['value']}")
                
                return result
            else:
                return data
        else:
            return data

    def parse_metadata(self) -> Optional[Dict]:
        """
        Parse metadata.yaml for the model
        
        Returns:
            Parsed YAML content with GitLab variables substituted, or None if file not found
        """
        metadata_path = self.model_path / 'metadata.yaml'
        
        if not metadata_path.exists():
            print(f"⚠️  Warning: {metadata_path} not found, skipping")
            return None
            
        try:
            with open(metadata_path, 'r') as f:
                data = yaml.safe_load(f)
                
            # Apply GitLab variable substitution
            print("   🔄 Applying GitLab variable substitution...")
            data = self._substitute_gitlab_variables(data)
            
            return data
        except yaml.YAMLError as e:
            print(f"❌ Error parsing {ux_conf_path}: {e}")
            return None

    def _read_md_file(self, file_path) -> Optional[str]:
        """
        Read markdown file and return content
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            Content of markdown file, or None if file not found
        """
        if not file_path.exists():
            print(f"⚠️  Warning: {file_path} not found, skipping")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            print(f"File path: {file_path}. File content:")
            print(content)
            return content
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def parse_markdown_content(self, metadata) -> Optional[Dict]:
        """
        Parse *.md files in the model

        Args:
            metadata: Metadata of the model
        
        Returns:
            Parsed markdown content with GitLab variables substituted, or None if file not found
        """
        data = {}


        if not metadata or not metadata.get('tabs'):
            print("⚠️  Warning: No tabs found in metadata")
            return None

        for tab in metadata['tabs']:
            if not tab.get('id'):
                print("⚠️  Warning: No id found in tab")
                continue
            if not tab.get('filename'):
                print("⚠️  Warning: No filename found in tab")
                continue

            data[tab['id']] = self._read_md_file(self.model_path / tab['filename'])

        # Apply GitLab variable substitution
        print("   🔄 Applying GitLab variable substitution...")
        data = self._substitute_gitlab_variables(data)
        
        return data

            
    def shift_headings_down(self, content: str) -> str:
        """
        Shift all markdown headings down one level
        
        Args:
            content: Markdown content with headings
            
        Returns:
            Content with headings shifted down one level
        """
        lines = content.split('\n')
        shifted_lines = []
        
        for line in lines:
            # Check if line is a heading (starts with #)
            if line.strip().startswith('#') and not line.strip().startswith('#!'):
                # Add one more # to shift down
                shifted_lines.append('#' + line)
            else:
                shifted_lines.append(line)
                
        return '\n'.join(shifted_lines)
    
    def extract_h2_headings(self, content: str) -> List[str]:
        """
        Extract H2 headings from markdown content (before shifting)
        
        Args:
            content: Markdown content
            
        Returns:
            List of H2 heading texts (without the ## prefix)
        """
        h2_headings = []
        lines = content.split('\n')
        
        for line in lines:
            stripped = line.strip()
            # Match lines starting with ## but not ###
            if stripped.startswith('## ') and not stripped.startswith('### '):
                # Remove the ## prefix and whitespace
                heading_text = stripped[3:].strip()
                h2_headings.append(heading_text)
                
        return h2_headings
    
    def create_anchor(self, text: str) -> str:
        """
        Create markdown anchor from heading text
        
        Args:
            text: Heading text
            
        Returns:
            Anchor string (lowercase, spaces to hyphens, special chars removed)
        """
        # Lowercase and replace spaces with hyphens
        anchor = text.lower().replace(' ', '-')
        # Remove special characters except hyphens and numbers
        anchor = ''.join(c for c in anchor if c.isalnum() or c == '-')
        # Remove multiple consecutive hyphens
        anchor = re.sub(r'-+', '-', anchor)
        # Remove leading/trailing hyphens
        anchor = anchor.strip('-')
        return anchor
    
    def generate_table_of_contents(self, tabs: List[Dict], markdown_content: Dict) -> str:
        """
        Generate table of contents from tabs with 2-level depth
        
        Args:
            tabs: List of tab dictionaries with 'label' and 'filename' keys
            markdown_content: All parsed markdown content
        Returns:
            Markdown table of contents with tab sections (H2) and subsections (H3)
        """
        toc_lines = ["## Table of Contents", ""]
        
        for tab in tabs:
            if not isinstance(tab, dict):
                continue
                
            tab_id = tab.get('id', 'unlabeled')
            label = tab.get('label', 'Unlabeled')
            content = markdown_content.get(tab_id, None)
            if content is None:
                continue
            
            # Create anchor for tab (will be H2 in final doc)
            tab_anchor = self.create_anchor(label)
            
            # Add main tab link to TOC
            toc_lines.append(f"- [{label}](#{tab_anchor})")
            
            # Extract H2 headings from content (will become H3 after shifting)
            if content:
                h2_headings = self.extract_h2_headings(content)
                for h2_text in h2_headings:
                    h3_anchor = self.create_anchor(h2_text)
                    # Indent subsections
                    toc_lines.append(f"  - [{h2_text}](#{h3_anchor})")
            
        toc_lines.append("")
        return '\n'.join(toc_lines)
        
    def validate_forbidden_references_in_source(self, source_content) -> bool:
        """
        Check source YAML content for forbidden internal references
        
        Args:
            source_content: Source YAML content to check
            
        Returns:
            True if validation passes (no forbidden refs or allowed), False otherwise
            
        Side effects:
            Prints warnings/errors for each forbidden reference found
            Stores violations with SOURCE file locations for summary table
        """      
        violations = []
        
        # Check each forbidden pattern in SOURCE file
        for pattern in self.forbidden_patterns:
            matches = re.finditer(pattern, source_content, re.IGNORECASE)
            for match in matches:
                # Get line number in SOURCE file
                line_num = source_content[:match.start()].count('\n') + 1
                
                # Extract context
                start = max(0, match.start() - 40)
                end = min(len(source_content), match.end() + 40)
                context = source_content[start:end].replace('\n', ' ')
                
                violations.append({
                    'model': self.model_name,
                    'file': 'ux-conf.yaml',  # SOURCE file
                    'pattern': pattern,
                    'match': match.group(),
                    'line': line_num,
                    'context': context
                })
        
        # Store violations for summary table (class-level for aggregation)
        if not hasattr(self.__class__, '_all_violations'):
            self.__class__._all_violations = []
        self.__class__._all_violations.extend(violations)
        
        # Report for this model
        if violations:
            print(f"\n⚠️  Found {len(violations)} forbidden reference(s) in {self.model_name}/ux-conf.yaml")
            for violation in violations:
                print(f"      Line {violation['line']}: {violation['match']}")
            
            if self.allow_forbidden_refs:
                print("   ⚠️  ALLOWED (--allow-forbidden-refs enabled)")
                return True
            else:
                print("   ❌ BLOCKED")
                return False
        else:
            print("   ✅ No forbidden references detected")
            return True
    
    def censor_forbidden_references(self, readme_content: str) -> str:
        """
        Replace forbidden references with ****** in README content
        
        Args:
            readme_content: README content to censor
            
        Returns:
            Censored README content
        """
        censored = readme_content
        censor_count = 0
        
        for pattern in self.forbidden_patterns:
            matches = list(re.finditer(pattern, censored, re.IGNORECASE))
            for match in reversed(matches):  # Reverse to maintain positions
                censored = censored[:match.start()] + '******' + censored[match.end():]
                censor_count += 1
        
        if censor_count > 0:
            print(f"   🔒 Censored {censor_count} forbidden reference(s)", flush=True)
        
        return censored
    
    @classmethod
    def print_violations_summary(cls):
        """Print summary table of all violations across all models"""
        if not hasattr(cls, '_all_violations') or not cls._all_violations:
            return
        
        print("\n" + "=" * 80)
        print("📊 FORBIDDEN REFERENCE VIOLATIONS SUMMARY")
        print("=" * 80)
        print(f"\n{'Model':<30} {'File':<15} {'Line':<6} {'Match':<30}")
        print("-" * 80)
        
        for v in cls._all_violations:
            model_short = v['model'].split('/')[-1][:28]
            match_short = v['match'][:28]
            print(f"{model_short:<30} {v['file']:<15} {v['line']:<6} {match_short:<30}")
        
        print("-" * 80)
        print(f"Total violations: {len(cls._all_violations)}")
        print("=" * 80)
    
    def generate_readme_from_markdown(self, metadata, markdown_content: Dict) -> str:
        """
        Generate README from markdown content
        
        Args:
            metadata: Parsed metadata.yaml content
            markdown_content: All parsed markdown content
            
        Returns:
            Generated README with TOC and shifted headings
        """
        if markdown_content is None:
            print("⚠️  Warning: No markdown_content to generate README from")
            return ""
            
        markdown_lines = []
        
        # Add front matter with metadata
        markdown_lines.append(f"# {metadata.get('displayName', self.model_basename)}")
        markdown_lines.append("")
        
        if 'short_description' in metadata:
            markdown_lines.append(f"> {metadata['short_description']}")
            markdown_lines.append("")
            
        # Add table of contents
        tabs = metadata.get('tabs', [])
        toc = self.generate_table_of_contents(tabs, markdown_content)
        markdown_lines.append(toc)
        markdown_lines.append("---")
        markdown_lines.append("")
            
        # Process each tab
        for tab in tabs:
            if not isinstance(tab, dict):
                continue
                
            tab_id = tab.get('id', 'unlabeled')
            label = tab.get('label', 'Unlabeled')
            content = markdown_content.get(tab_id, None)
            if content is None:
                continue
            
            # Add tab as second-level heading (was first-level, now shifted)
            markdown_lines.append(f"## {label}")
            markdown_lines.append("")
            
            # Add content with shifted headings
            if content:
                # Remove leading/trailing whitespace but preserve internal formatting
                content = content.strip()
                # Shift all headings in content down one level
                shifted_content = self.shift_headings_down(content)
                markdown_lines.append(shifted_content)
                markdown_lines.append("")
                
        return '\n'.join(markdown_lines)
        
    def generate_conf_yaml(self, metadata) -> Optional[Dict]:
        """
        Generate conf.yaml from metadata
        
        Args:
            metadata: Parsed metadata.yaml content
            
        Returns:
            Generated conf.yaml for build site publishing
        """
        if metadata is None:
            print("⚠️  Warning: No metadata to generate conf.yaml from")
            return None
            
        conf_yaml_lines = {}
        conf_yaml_lines['kind'] = metadata.get('kind', 'PLAYBOOK')
        conf_yaml_lines['catalog_name'] = metadata.get('catalog_name', self.model_name)
        conf_yaml_lines['name'] = metadata.get('name', self.model_basename)
                
        return conf_yaml_lines

    def _attach_build_site_metadata(self, ux_conf_lines: Dict) -> None:
        """
        Attach build site metadata to ux-conf.yaml
        These attached fields are required by the build site.
        
        Args:
            ux_conf_lines: List of lines to attach build site metadata to
        """
        ux_conf_lines['env_specific_attributes'] = {
            'test': [{
                'attributes_env': 'test',
                'showUnavailableBanner': 'false'
            }],
            'production': [{
                'attributes_env': 'production',
                'showUnavailableBanner': 'false'
            }]
        }
        ux_conf_lines['artifactName'] = self.model_basename
        ux_conf_lines['namespace'] = 'qc69jvmznzxy'

    def generate_ux_conf_yaml(self, metadata, markdown_content) -> Optional[Dict]:
        """
        Generate ux-conf.yaml from markdown content
        
        Args:
            metadata: Parsed metadata.yaml content
            markdown_content: All parsed markdown content
        Returns:
            Generated ux-conf.yaml for build site publishing
        """
            
        ux_conf_lines = {}
        ux_conf_lines['kind'] = metadata.get('kind', 'PLAYBOOK')
        ux_conf_lines['name'] = metadata.get('name', self.model_basename)
        ux_conf_lines['displayName'] = metadata.get('displayName', self.model_basename)
        ux_conf_lines['short_description'] = metadata.get('short_description', '')
        ux_conf_lines['publisher'] = metadata.get('publisher', 'nvidia')
        ux_conf_lines['labels'] = metadata.get('labels', [])
        ux_conf_lines['duration'] = metadata.get('duration', 'UNKNOWN')

        self._attach_build_site_metadata(ux_conf_lines)

        # Add tabs
        tabs = metadata.get('tabs', [])
        ux_conf_lines['tabs'] = []
        # Process each tab
        for tab in tabs:
            if not isinstance(tab, dict):
                continue
                
            tab_id = tab.get('id', 'unlabeled')
            label = tab.get('label', 'Unlabeled')
            content = markdown_content.get(tab_id, None)
            if content is None:
                continue
            
            # Add indentation to each line of content
            if content:
                lines = content.split('\n')
                # Add 2-space indent to each non-empty line
                indented_lines = ['  ' + line if line.strip() else line for line in lines]
                content = '\n'.join(indented_lines)
            
            # Ensure content ends with newline for consistent YAML formatting
            if content and not content.endswith('\n'):
                content = content + '\n'
            
            ux_conf_lines['tabs'].append({
                'id': tab_id,
                'label': label,
                'content': content
            })
        
        ux_conf_lines['resources'] = metadata.get('resources', [])
        
        # Add cta (Call To Action) if present in metadata
        cta = metadata.get('cta')
        if cta:
            ux_conf_lines['cta'] = cta

        return ux_conf_lines

    def clone_destination_repos(self) -> Dict[str, Path]:
        """
        Clone all destination repositories
        
        Returns:
            Dictionary mapping alias to local path
        """
        dest_paths = {}
        
        for repo in self.dst_repos:
            alias = repo['alias']
            url = repo['url']
            token_var = repo['token_var']
            
            # Get token from environment
            token = os.environ.get(token_var)
            if not token:
                print(f"❌ Error: Token variable {token_var} not set")
                sys.exit(1)
                
            dest_path = self.output_dir / alias
            
            print(f"📥 Cloning destination repo: {alias}")
            if self.git_clone_with_token(url, dest_path, token):
                dest_paths[alias] = dest_path
            else:
                sys.exit(1)
                
        return dest_paths
        
    def clone_source_assets(self) -> Optional[Path]:
        """
        Clone source assets repository
        
        Returns:
            Path to cloned repo or None if failed
        """
        if not self.src_assets_url:
            print("❌ Error: SRC_ASSETS_URL not set")
            sys.exit(1)
            
        if not self.src_assets_token:
            print("❌ Error: GITLAB_MASTER_TOKEN_DGX_SPARK_PLAYBOOKS not set")
            sys.exit(1)
            
        src_path = self.output_dir / 'source_assets'
        
        print(f"📥 Cloning source assets repo...")
        if self.git_clone_with_token(self.src_assets_url, src_path, self.src_assets_token):
            return src_path
        else:
            sys.exit(1)
            
    def copy_assets(self, src_assets_path: Path, dest_paths: Dict[str, Path]) -> None:
        """
        Copy assets from source to all destination repos
        
        Args:
            src_assets_path: Path to cloned source assets repo
            dest_paths: Dictionary of destination repo paths
            
        Note:
            Destination directories are already cleaned by clean_destination_directory()
            Gracefully handles models without assets (warning only, not an error)
        """
        # Source assets are in {src_assets_path}/{model_basename}/assets/
        model_dir_in_assets = src_assets_path / self.model_basename
        src_assets_dir = model_dir_in_assets / 'assets'
        
        # Check if model directory exists in source assets repo
        if not model_dir_in_assets.exists():
            print(f"   ℹ️  Model '{self.model_basename}' has no directory in source assets repo")
            print(f"      (This is OK - not all models have assets)")
            return
        
        # Check if assets subdirectory exists
        if not src_assets_dir.exists():
            print(f"   ℹ️  Model '{self.model_basename}' has no assets/ subdirectory")
            print(f"      (This is OK - not all models have assets)")
            return
            
        print(f"📋 Copying assets from {src_assets_dir}", flush=True)
        sys.stdout.flush()
        
        for alias, dest_base_path in dest_paths.items():
            # Destination is {dest_repo}/{model_name}/assets/
            dest_model_dir = dest_base_path / self.model_name
            dest_assets_dir = dest_model_dir / 'assets'
            
            print(f"   → {alias}/{self.model_name}/assets/", flush=True)
                
            # Copy assets directory (directory was already cleaned)
            try:
                shutil.copytree(src_assets_dir, dest_assets_dir)
                print(f"   ✅ Assets copied successfully ({len(list(src_assets_dir.iterdir()))} items)", flush=True)
            except Exception as e:
                print(f"   ❌ Error copying assets: {e}", flush=True)
                sys.exit(1)
                
    def clean_destination_directory(self, dest_paths: Dict[str, Path]) -> None:
        """
        Clean (remove and recreate) destination model directories
        
        Args:
            dest_paths: Dictionary of destination repo paths
            
        Side effects:
            Removes entire {dest_repo}/{model_name}/ directory tree
        """
        for alias, dest_base_path in dest_paths.items():
            dest_model_dir = dest_base_path / self.model_name
            
            if dest_model_dir.exists():
                print(f"🧹 Cleaning {alias}/{self.model_name}/ (removing stale content)")
                try:
                    shutil.rmtree(dest_model_dir)
                    print(f"   ✅ Directory cleaned")
                except Exception as e:
                    print(f"   ❌ Error cleaning directory: {e}")
                    sys.exit(1)
            
            # Recreate empty directory
            dest_model_dir.mkdir(parents=True, exist_ok=True)
            
    def push_to_destinations(self, dest_paths: Dict[str, Path], max_retries: int = 3) -> None:
        """
        Commit and push changes to destination repositories with conflict handling
        
        Args:
            dest_paths: Dictionary of destination repo paths
            max_retries: Maximum number of retry attempts for push conflicts
            
        Side effects:
            Commits and pushes to remote git repositories
            
        Note:
            Includes random delay (1-30s) to avoid simultaneous push conflicts
            from parallel jobs. Automatically pulls/rebases if remote has changed.
        """
        for alias, dest_base_path in dest_paths.items():
            print(f"📤 Pushing changes to {alias}")
            
            # Add random delay to stagger parallel pushes (1-30 seconds)
            delay = random.randint(1, 30)
            print(f"   ⏱️  Waiting {delay}s to stagger parallel pushes...")
            time.sleep(delay)
            
            try:
                # Stage all changes
                self.run_command(['git', 'add', '-A'], cwd=dest_base_path)
                
                # Check if there are changes to commit
                result = self.run_command(
                    ['git', 'diff', '--staged', '--quiet'],
                    cwd=dest_base_path,
                    check=False
                )
                
                if result.returncode == 0:
                    print(f"   ℹ️  No changes to commit for {alias}")
                    continue
                
                # Commit changes
                commit_msg = f"[{self.model_name}] Update playbook content"
                self.run_command(
                    ['git', 'commit', '-m', commit_msg],
                    cwd=dest_base_path
                )
                print(f"   ✅ Changes committed: {commit_msg}")
                
                # Push with retry logic for handling conflicts
                # Pull before EVERY attempt to minimize race window
                push_success = False
                for attempt in range(1, max_retries + 1):
                    try:
                        if attempt > 1:
                            print(f"   🔄 Retry attempt {attempt}/{max_retries}")
                        
                        # ALWAYS pull before pushing to minimize race condition window
                        print(f"   ⬇️  Pulling latest changes from remote...", flush=True)
                        sys.stdout.flush()
                        self.run_command(
                            ['git', 'pull', '--rebase', '--progress'],
                            cwd=dest_base_path,
                            stream_output=True
                        )
                        print(f"   ✅ Rebase successful", flush=True)
                        
                        # Attempt push immediately after pull with extended timeout
                        # Use longer timeout for push (10 min) and stream progress
                        print(f"   ⬆️  Pushing to remote...", flush=True)
                        sys.stdout.flush()
                        self.run_command(
                            ['git', 'push', '--progress'], 
                            cwd=dest_base_path, 
                            timeout=600,
                            stream_output=True
                        )
                        print(f"   ✅ Changes pushed to remote", flush=True)
                        push_success = True
                        break
                        
                    except subprocess.CalledProcessError as e:
                        if attempt < max_retries:
                            # Wait longer with exponential backoff
                            retry_delay = random.randint(10, 30) * attempt
                            print(f"   ⚠️  Push failed, waiting {retry_delay}s before retry...")
                            time.sleep(retry_delay)
                        else:
                            print(f"   ❌ Push failed after {max_retries} attempts")
                            raise
                
                if not push_success:
                    print(f"   ❌ Failed to push to {alias} after {max_retries} attempts")
                    sys.exit(1)
                
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Error pushing to {alias}: {e}")
                sys.exit(1)
    
    def copy_root_files(self, src_assets_path: Path, dest_paths: Dict[str, Path]) -> None:
        """
        Copy root-level files (LICENSE, CONTRIBUTING, etc.) from source assets repo to destination repos
        
        Args:
            src_assets_path: Path to cloned source assets repository
            dest_paths: Dictionary of destination repo paths
            
        Side effects:
            Copies files from source assets repo root to destination repo roots
            
        Note:
            Uses DEFAULT_ROOT_FILE_GLOBS and ROOT_FILE_GLOBS_JSON env var
        """
        # Get file globs from environment or use defaults
        root_globs_json = os.environ.get('ROOT_FILE_GLOBS_JSON')
        if root_globs_json:
            try:
                file_globs = json.loads(root_globs_json)
            except json.JSONDecodeError as e:
                print(f"⚠️  Warning: Invalid ROOT_FILE_GLOBS_JSON, using defaults: {e}")
                file_globs = self.DEFAULT_ROOT_FILE_GLOBS
        else:
            file_globs = self.DEFAULT_ROOT_FILE_GLOBS
        
        # Find matching files in SOURCE ASSETS repo root
        files_to_copy = []
        for pattern in file_globs:
            matches = glob_module.glob(str(src_assets_path / pattern))
            files_to_copy.extend([Path(m) for m in matches])
        
        if not files_to_copy:
            print(f"   ℹ️  No root files found in source assets repo matching: {', '.join(file_globs)}")
            return
        
        print(f"📋 Copying {len(files_to_copy)} root file(s) from source assets repo")
        
        for src_file in files_to_copy:
            filename = src_file.name
            print(f"   📄 {filename}")
            
            for alias, dest_base_path in dest_paths.items():
                dest_file = dest_base_path / filename
                
                try:
                    shutil.copy2(src_file, dest_file)
                    print(f"      → {alias}/")
                except Exception as e:
                    print(f"      ❌ Error copying to {alias}: {e}")
                    sys.exit(1)
        
        print(f"   ✅ Root files copied successfully")
    
    def copy_root_directories(self, dest_paths: Dict[str, Path]) -> None:
        """
        Copy root-level directories (src, etc.) from project root to destination repos
        
        Args:
            dest_paths: Dictionary of destination repo paths
            
        Side effects:
            Copies directories from project root to destination repo roots
            
        Note:
            Uses DEFAULT_ROOT_DIRS and ROOT_DIRS_JSON env var
        """
        # Get directory list from environment or use defaults
        root_dirs_json = os.environ.get('ROOT_DIRS_JSON')
        if root_dirs_json:
            try:
                dir_names = json.loads(root_dirs_json)
            except json.JSONDecodeError as e:
                print(f"⚠️  Warning: Invalid ROOT_DIRS_JSON, using defaults: {e}")
                dir_names = self.DEFAULT_ROOT_DIRS
            else:
                dir_names = self.DEFAULT_ROOT_DIRS
        
        # Find matching directories
        dirs_to_copy = []
        for dir_name in dir_names:
            src_dir = self.project_root / dir_name
            if src_dir.exists() and src_dir.is_dir():
                dirs_to_copy.append(src_dir)
        
        if not dirs_to_copy:
            print(f"   ℹ️  No root directories found matching: {', '.join(dir_names)}")
            return
        
        print(f"📂 Copying {len(dirs_to_copy)} root director(y/ies) from project root")
        
        for src_dir in dirs_to_copy:
            dir_name = src_dir.name
            print(f"   📂 {dir_name}/")
            
            for alias, dest_base_path in dest_paths.items():
                dest_dir = dest_base_path / dir_name
                
                try:
                    # Remove existing directory if present
                    if dest_dir.exists():
                        shutil.rmtree(dest_dir)
                    
                    # Copy directory
                    shutil.copytree(src_dir, dest_dir)
                    print(f"      → {alias}/{dir_name}/")
                except Exception as e:
                    print(f"      ❌ Error copying to {alias}: {e}")
                    sys.exit(1)
        
        print(f"   ✅ Root directories copied successfully")
    
    def get_model_display_name(self, model_path: str) -> str:
        """
        Get displayName from model's ux-conf.yaml
        
        Args:
            model_path: Model path (e.g., "nvidia/jax")
            
        Returns:
            displayName from ux-conf.yaml, or formatted model name if not found
        """
        ux_conf_path = self.project_root / model_path / 'ux-conf.yaml'
        
        try:
            with open(ux_conf_path, 'r') as f:
                config = yaml.safe_load(f)
                if config and 'displayName' in config:
                    return config['displayName']
        except Exception:
            # If we can't read the file, fall back to formatted name
            pass
        
        # Fallback: format from model name
        model_name = model_path.split('/')[-1]
        return model_name.replace('-', ' ').title()
    
    def generate_main_readme(self, dest_paths: Dict[str, Path], 
                            all_models: List[str]) -> None:
        """
        Generate main README.md from README-Public.md template with model TOC
        
        Args:
            dest_paths: Dictionary of destination repo paths
            all_models: List of all model paths to include in TOC
            
        Side effects:
            Replaces README.md in each destination repo root
            
        Note:
            Uses README-Public.md as template, adds generated TOC
            Reads displayName from each model's ux-conf.yaml
        """
        # Read template
        template_path = self.project_root / 'README-Public.md'
        
        if not template_path.exists():
            print(f"⚠️  Warning: {template_path} not found, skipping main README generation")
            return
        
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
        except Exception as e:
            print(f"❌ Error reading {template_path}: {e}")
            sys.exit(1)
        
        # Generate TOC for models
        toc_lines = []
        
        # Group models by publisher (e.g., "nvidia")
        models_by_publisher = {}
        for model in sorted(all_models):
            parts = model.split('/')
            if len(parts) == 2:
                publisher, model_name = parts
                if publisher not in models_by_publisher:
                    models_by_publisher[publisher] = []
                
                # Get display name from ux-conf.yaml
                display_name = self.get_model_display_name(model)
                models_by_publisher[publisher].append((display_name, model))
        
        # Generate TOC grouped by publisher
        for publisher in sorted(models_by_publisher.keys()):
            toc_lines.append(f"### {publisher.upper()}")
            toc_lines.append("")
            
            # Sort by display name for better readability
            for display_name, model_path in sorted(models_by_publisher[publisher]):
                toc_lines.append(f"- [{display_name}]({model_path}/)")
            
            toc_lines.append("")
        
        toc_content = '\n'.join(toc_lines)
        
        # Insert TOC after "## Available Playbooks" heading or comment marker
        lines = template_content.split('\n')
        result_lines = []
        inserted = False
        
        for i, line in enumerate(lines):
            result_lines.append(line)
            
            # Look for insertion point (either heading or comment marker)
            if not inserted and (
                line.strip().startswith('## Available Playbooks') or
                line.strip() == '<!-- TABLE OF CONTENTS GENERATED BELOW -->'
            ):
                # Skip the comment marker line if present
                if line.strip() == '<!-- TABLE OF CONTENTS GENERATED BELOW -->':
                    result_lines.pop()  # Remove the comment marker
                
                result_lines.append("")
                result_lines.append(toc_content)
                inserted = True
        
        if not inserted:
            print("⚠️  Warning: Could not find insertion point in README-Public.md, appending TOC")
            result_lines.append("")
            result_lines.append("## Available Playbooks")
            result_lines.append("")
            result_lines.append(toc_content)
        
        readme_content = '\n'.join(result_lines)
        
        # Write to each destination
        print(f"📝 Generating main README.md for destination repos")
        for alias, dest_base_path in dest_paths.items():
            readme_path = dest_base_path / 'README.md'
            
            try:
                with open(readme_path, 'w') as f:
                    f.write(readme_content)
                print(f"   ✅ README.md written to {alias}/")
            except Exception as e:
                print(f"   ❌ Error writing README.md to {alias}: {e}")
                sys.exit(1)
                
    # def write_markdown(self, markdown_content: str, dest_paths: Dict[str, Path]) -> None:
    #     """
    #     Write generated markdown to all destination repos
        
    #     Args:
    #         markdown_content: Generated markdown content
    #         dest_paths: Dictionary of destination repo paths
    #     """
    #     for alias, dest_base_path in dest_paths.items():
    #         # Write to {dest_repo}/{model_name}/README.md
    #         dest_model_dir = dest_base_path / self.model_name
    #         readme_path = dest_model_dir / 'README.md'
            
    #         print(f"📝 Writing README.md to {alias}/{self.model_name}/")
            
    #         try:
    #             with open(readme_path, 'w') as f:
    #                 f.write(markdown_content)
    #             print(f"   ✅ README.md written successfully")
    #         except Exception as e:
    #             print(f"   ❌ Error writing README.md: {e}")
    #             sys.exit(1)
    
    def run(self) -> int:
        """
        Execute the convergence process
        
        Returns:
            Exit code (0 for success, 1 for errors)
        """
        print("=" * 70, flush=True)
        print(f"🔄 Converging playbook: {self.model_name}", flush=True)
        print(f"   Push enabled: {self.push}", flush=True)
        print(f"   Allow forbidden refs: {self.allow_forbidden_refs}", flush=True)
        print(f"   Destination repos: {len(self.dst_repos)}", flush=True)
        print("=" * 70, flush=True)
        sys.stdout.flush()
        
        # Step 1: Parse metadata.yaml
        print("\n📖 Step 1: Parsing metadata.yaml", flush=True)
        print(f"   Looking for: {self.model_path / 'ux-conf.yaml'}", flush=True)
        sys.stdout.flush()
        metadata = self.parse_metadata()
        if not metadata:
            print("⚠️  Skipping convergence (no ux-conf.yaml)")
            return 0
            
        # Step 1.1: Parse markdown files
        print("\n📖 Step 1.1: Parsing markdown files", flush=True)
        print(f"   Looking for: {self.model_path / '*.md'}", flush=True)
        sys.stdout.flush()
        markdown_content = self.parse_markdown_content(metadata)
        if not markdown_content:
            print("⚠️  Skipping convergence (no markdown content)")
            return 0

        # Step 2: Generate README.md file
        print("\n📝 Step 2: Generating README.md file from markdown content", flush=True)
        sys.stdout.flush()
        readme_content = self.generate_readme_from_markdown(metadata, markdown_content)
        
        if not readme_content:
            print("⚠️  No content generated, skipping", flush=True)
            return 0
            
        print(f"   ✅ Generated {len(readme_content)} characters of README", flush=True)
        sys.stdout.flush()

        # Step 2.1: Generate conf.yaml and ux-conf.yaml files from markdown and metadata.yaml
        print("\n📝 Step 2.1: Generating conf.yaml and ux-conf.yaml from metadata and markdown content", flush=True)
        sys.stdout.flush()

        conf_yaml = self.generate_conf_yaml(metadata)
        if not conf_yaml:
            print("⚠️  No conf.yaml generated, skipping", flush=True)
            return 0
        print(f"   ✅ Generated {len(conf_yaml)} characters of conf.yaml", flush=True)
        sys.stdout.flush()

        ux_conf_yaml = self.generate_ux_conf_yaml(metadata, markdown_content)
        if not ux_conf_yaml:
            print("⚠️  No ux-conf.yaml generated, skipping", flush=True)
            return 0
        print(f"   ✅ Generated {len(ux_conf_yaml)} characters of ux-conf.yaml", flush=True)
        sys.stdout.flush()

        
        # Step 2.5: Validate for forbidden references in SOURCE file
        print("\n🔍 Step 2.5: Validating for forbidden references in source", flush=True)
        print(f"   Checking {len(self.forbidden_patterns)} pattern(s) in ux-conf.yaml...", flush=True)
        sys.stdout.flush()
        ux_conf_yaml_str = yaml.dump(ux_conf_yaml, default_flow_style=False, sort_keys=False, allow_unicode=True)
        if not self.validate_forbidden_references_in_source(ux_conf_yaml_str):
            # Validation failed and not allowed to proceed
            return 1
        
        # Step 2.6: Censor forbidden references if enabled
        if self.censor_forbidden_refs:
            print("\n🔒 Step 2.6: Censoring forbidden references", flush=True)
            readme_content = self.censor_forbidden_references(readme_content)
        
        # PREPARE-ONLY MODE: Just write markdown to filesystem, skip git operations
        if self.prepare_only:
            print("\n📝 Step 3: Writing README content to filesystem (prepare-only mode)", flush=True)
            # Write to simple directory structure: output_dir/model_path/README.md
            model_output_dir = self.output_dir / self.model_name
            model_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Write README.md
            readme_path = model_output_dir / 'README.md'
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            print(f"   ✅ Wrote: {readme_path}", flush=True)

            # Write conf.yaml
            conf_path = model_output_dir / 'conf.yaml'
            with open(conf_path, 'w') as f:
                yaml.dump(conf_yaml, f)
            print(f"   ✅ Wrote: {conf_path}", flush=True)

            # Write ux-conf.yaml
            ux_conf_path = model_output_dir / 'ux-conf.yaml'
            
            # Convert multiline strings to use literal scalars
            try:
                from ruamel.yaml import YAML
                from ruamel.yaml.scalarstring import LiteralScalarString
                
                # Recursively convert multiline strings to LiteralScalarString
                def convert_multiline_strings(data):
                    if isinstance(data, dict):
                        return {k: convert_multiline_strings(v) for k, v in data.items()}
                    elif isinstance(data, list):
                        return [convert_multiline_strings(item) for item in data]
                    elif isinstance(data, str) and '\n' in data:
                        # Strip trailing whitespace/newlines, then add exactly one newline
                        # This gives us clean | without +/- indicators
                        cleaned = data.rstrip() + '\n'
                        return LiteralScalarString(cleaned)
                    else:
                        return data
                
                converted_yaml = convert_multiline_strings(ux_conf_yaml)
                
                yaml_writer = YAML()
                yaml_writer.default_flow_style = False
                yaml_writer.width = 4096
                
                with open(ux_conf_path, 'w') as f:
                    yaml_writer.dump(converted_yaml, f)
                    
            except ImportError:
                # Fallback to PyYAML with custom dumper
                with open(ux_conf_path, 'w') as f:
                    class LiteralDumper(yaml.Dumper):
                        pass
                    
                    def str_representer(dumper, data):
                        if isinstance(data, str) and '\n' in data:
                            # Use literal block scalar (|) for multiline strings
                            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
                        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
                    
                    LiteralDumper.add_representer(str, str_representer)
                    
                    yaml.dump(
                        ux_conf_yaml, 
                        f, 
                        Dumper=LiteralDumper, 
                        default_flow_style=False, 
                        sort_keys=False, 
                        allow_unicode=True,
                        width=4096
                    )
            
            print(f"   ✅ Wrote: {ux_conf_path}", flush=True)

            print("\n⏸️  Skipping git operations (prepare-only mode)", flush=True)
            return 0
        
        # FULL MODE: Clone, copy, push (original behavior)
        # Step 3: Clone destination repositories
        print("\n📥 Step 3: Cloning destination repositories", flush=True)
        sys.stdout.flush()
        dest_paths = self.clone_destination_repos()
        print(f"   ✅ Cloned {len(dest_paths)} destination repo(s)", flush=True)
        sys.stdout.flush()
        
        # Step 4: Clone source assets repository
        print("\n📥 Step 4: Cloning source assets repository", flush=True)
        sys.stdout.flush()
        src_assets_path = self.clone_source_assets()
        print(f"   ✅ Source assets cloned", flush=True)
        sys.stdout.flush()
        
        # Step 5: Clean destination directories (remove stale content)
        print("\n🧹 Step 5: Cleaning destination directories", flush=True)
        sys.stdout.flush()
        self.clean_destination_directory(dest_paths)
        print(f"   ✅ Directories cleaned and ready for fresh content", flush=True)
        sys.stdout.flush()
        
        # Step 6: Write markdown to destinations
        print("\n📝 Step 6: Writing markdown files", flush=True)
        sys.stdout.flush()
        self.write_markdown(markdown_content, dest_paths)
        
        # Step 7: Copy assets to destinations
        print("\n📋 Step 7: Copying assets", flush=True)
        sys.stdout.flush()
        self.copy_assets(src_assets_path, dest_paths)
        
        # Step 8: Copy root files (LICENSE, etc.) from source assets repo to destinations
        print("\n📋 Step 8: Copying root files from source assets repo", flush=True)
        sys.stdout.flush()
        self.copy_root_files(src_assets_path, dest_paths)
        
        # Step 8.5: Copy root directories (src, etc.) from project root to destinations
        print("\n📂 Step 8.5: Copying root directories from project root", flush=True)
        sys.stdout.flush()
        self.copy_root_directories(dest_paths)
        
        # Step 9: Generate main README.md with model TOC
        print("\n📝 Step 9: Generating main README.md with model directory", flush=True)
        print(f"   Found {len(self.all_models)} total model(s)", flush=True)
        sys.stdout.flush()
        self.generate_main_readme(dest_paths, self.all_models)
        
        # Step 10: Push to destinations (if --push flag set)
        if self.push:
            print("\n📤 Step 10: Pushing changes to remote repositories", flush=True)
            sys.stdout.flush()
            self.push_to_destinations(dest_paths)
        else:
            print("\n⏸️  Step 10: Skipping push (use --push to enable)", flush=True)
            sys.stdout.flush()
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ Convergence complete!")
        print(f"   Model: {self.model_name}")
        print(f"   Destinations: {', '.join(dest_paths.keys())}")
        print(f"   Output directory: {self.output_dir}")
        if not self.push:
            print("\n💡 Review artifacts before pushing to remote repositories")
        print("=" * 70)
        
        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Converge DGX Spark playbook content to external repositories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Forbidden References:
  By default, the script checks for internal references that should not
  appear in public documentation (e.g., gitlab-master.nvidia.com).
  
  Default patterns checked:
    - gitlab-master.nvidia.com (internal GitLab)
    - urm.nvidia.com (internal URM registry)
    - nvcr.io.*-internal (internal containers)
    - @nvidia.com (email addresses)
  
  Use --allow-forbidden-refs to bypass validation during testing.
  Customize patterns with FORBIDDEN_PATTERNS_JSON environment variable.
        """
    )
    parser.add_argument(
        '--model',
        required=True,
        help='Model path (e.g., nvidia/jax)'
    )
    parser.add_argument(
        '--output-dir',
        default='convergence-output',
        help='Output directory for artifacts (default: convergence-output)'
    )
    parser.add_argument(
        '--push',
        action='store_true',
        help='Push changes to remote repositories (default: False, only prepare artifacts)'
    )
    parser.add_argument(
        '--allow-forbidden-refs',
        action='store_true',
        help='Allow forbidden references in markdown (for testing only, will still report detections)'
    )
    parser.add_argument(
        '--prepare-only',
        action='store_true',
        help='Only prepare markdown files, skip all git operations (for parallel stage 1)'
    )
    parser.add_argument(
        '--censor-forbidden-refs',
        action='store_true',
        help='Replace forbidden references with ****** in output (recommended for publishing)'
    )
    
    args = parser.parse_args()
    
    # Validate environment
    required_env_vars = ['SRC_ASSETS_URL', 'DST_REPOS_JSON']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Run convergence
    converter = PlaybookConverter(
        args.model, 
        args.output_dir, 
        push=args.push,
        allow_forbidden_refs=args.allow_forbidden_refs,
        prepare_only=args.prepare_only,
        censor_forbidden_refs=args.censor_forbidden_refs
    )
    exit_code = converter.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
