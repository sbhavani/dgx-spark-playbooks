#!/usr/bin/env python3
"""
Tests for GitLab variable substitution in converge_playbooks.py
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from converge_playbooks import PlaybookConverter


class TestPlaybookConverterGitLabVariables(unittest.TestCase):
    """Test GitLab variable substitution in PlaybookConverter"""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test model
        self.temp_dir = tempfile.mkdtemp()
        self.model_path = Path(self.temp_dir) / "nvidia" / "test-model"
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # Create converter instance
        with patch.dict(os.environ, {
            'SRC_ASSETS_URL': 'https://example.com/assets',
            'GITLAB_MASTER_TOKEN_DGX_SPARK_PLAYBOOKS': 'test_token',
            'DST_REPOS_JSON': '[]'
        }):
            self.converter = PlaybookConverter(
                model_path=str(self.model_path),
                output_dir=str(Path(self.temp_dir) / "output"),
                push=False
            )

    def test_substitute_gitlab_variables_simple_string(self):
        """Test simple variable substitution in strings."""
        with patch.dict(
            os.environ,
            {
                "GITLAB_DOCS_URL": "https://docs.example.com",
                "GITLAB_MODEL_NAME": "test-model",
            },
        ):
            data = {
                "displayName": "${GITLAB_MODEL_NAME}",
                "description": "Documentation at ${GITLAB_DOCS_URL}",
            }

            result = self.converter._substitute_gitlab_variables(data)

            expected = {
                "displayName": "test-model",
                "description": "Documentation at https://docs.example.com",
            }

            self.assertEqual(result, expected)

    def test_substitute_gitlab_variables_tabs_content(self):
        """Test variable substitution in tabs content (markdown)."""
        with patch.dict(
            os.environ,
            {
                "GITLAB_DOCS_BASE": "https://docs.nvidia.com",
                "GITLAB_GITHUB_BASE": "https://github.com/NVIDIA",
            },
        ):
            data = {
                "tabs": [
                    {
                        "label": "Getting Started",
                        "content": """# Quick Start
                        
Visit [documentation](${GITLAB_DOCS_BASE}/guides) for more info.
Clone from [GitHub](${GITLAB_GITHUB_BASE}/my-repo).
"""
                    }
                ]
            }

            result = self.converter._substitute_gitlab_variables(data)

            expected = {
                "tabs": [
                    {
                        "label": "Getting Started",
                        "content": """# Quick Start
                        
Visit [documentation](https://docs.nvidia.com/guides) for more info.
Clone from [GitHub](https://github.com/NVIDIA/my-repo).
"""
                    }
                ]
            }

            self.assertEqual(result, expected)

    def test_substitute_gitlab_variables_nested_structures(self):
        """Test variable substitution in nested dictionaries and lists."""
        with patch.dict(
            os.environ,
            {
                "GITLAB_PROJECT_URL": "https://example.com/project",
                "GITLAB_PROJECT_NAME": "My Project",
            },
        ):
            data = {
                "displayName": "${GITLAB_PROJECT_NAME}",
                "tabs": [
                    {
                        "label": "Overview",
                        "content": "Visit ${GITLAB_PROJECT_URL}",
                    },
                    {
                        "label": "Setup",
                        "content": "Project: ${GITLAB_PROJECT_NAME}",
                    }
                ],
                "metadata": {
                    "url": "${GITLAB_PROJECT_URL}",
                }
            }

            result = self.converter._substitute_gitlab_variables(data)

            expected = {
                "displayName": "My Project",
                "tabs": [
                    {
                        "label": "Overview",
                        "content": "Visit https://example.com/project",
                    },
                    {
                        "label": "Setup",
                        "content": "Project: My Project",
                    }
                ],
                "metadata": {
                    "url": "https://example.com/project",
                }
            }

            self.assertEqual(result, expected)

    def test_substitute_gitlab_variables_missing_var(self):
        """Test handling of missing environment variables."""
        with patch.dict(os.environ, {"GITLAB_EXISTING": "exists"}, clear=True):
            data = {
                "existing": "${GITLAB_EXISTING}",
                "missing": "${GITLAB_MISSING}",
                "mixed": "${GITLAB_EXISTING} and ${GITLAB_MISSING}",
            }

            result = self.converter._substitute_gitlab_variables(data)

            expected = {
                "existing": "exists",
                "missing": "${GITLAB_MISSING}",  # Should remain unchanged
                "mixed": "exists and ${GITLAB_MISSING}",  # Partial substitution
            }

            self.assertEqual(result, expected)

    def test_substitute_gitlab_variables_prefix_filter(self):
        """Test that only GITLAB_ prefixed variables are substituted."""
        with patch.dict(
            os.environ,
            {
                "GITLAB_SUBSTITUTE_ME": "substituted",
                "DONT_SUBSTITUTE": "should_not_appear",
                "OTHER_VAR": "also_ignored",
            },
        ):
            data = {
                "gitlab_var": "${GITLAB_SUBSTITUTE_ME}",
                "non_gitlab_var": "${DONT_SUBSTITUTE}",
                "other": "${OTHER_VAR}",
                "content": """
Use ${GITLAB_SUBSTITUTE_ME} for substitution.
But ${TEMPLATE_VAR} and ${CONFIG_VAR} remain unchanged.
"""
            }

            result = self.converter._substitute_gitlab_variables(data)

            expected = {
                "gitlab_var": "substituted",
                "non_gitlab_var": "${DONT_SUBSTITUTE}",  # NOT substituted
                "other": "${OTHER_VAR}",  # NOT substituted
                "content": """
Use substituted for substitution.
But ${TEMPLATE_VAR} and ${CONFIG_VAR} remain unchanged.
"""
            }

            self.assertEqual(result, expected)

    def test_substitute_gitlab_variables_no_substitution(self):
        """Test that data without variables remains unchanged."""
        data = {
            "displayName": "My Model",
            "tabs": [
                {"label": "Overview", "content": "Simple content"}
            ],
            "number": 42,
            "boolean": True,
        }

        result = self.converter._substitute_gitlab_variables(data)

        # Should be exactly the same
        self.assertEqual(result, data)

    def test_substitute_gitlab_variables_empty_structures(self):
        """Test that empty structures are handled correctly."""
        data = {
            "empty_dict": {},
            "empty_list": [],
            "empty_string": "",
            "tabs": []
        }

        result = self.converter._substitute_gitlab_variables(data)

        self.assertEqual(result, data)

    def test_substitute_gitlab_variables_realistic_ux_conf(self):
        """Test realistic ux-conf.yaml structure with tabs."""
        with patch.dict(
            os.environ,
            {
                "GITLAB_DOCS_BASE": "https://docs.nvidia.com",
                "GITLAB_GITHUB_BASE": "https://github.com/NVIDIA",
                "GITLAB_MODEL_NAME": "jax",
                "GITLAB_MODEL_DISPLAY": "NVIDIA JAX",
            },
        ):
            data = {
                "displayName": "${GITLAB_MODEL_DISPLAY}",
                "short_description": "High-performance ${GITLAB_MODEL_NAME} framework",
                "tabs": [
                    {
                        "label": "Overview",
                        "content": """# ${GITLAB_MODEL_DISPLAY}

Visit [documentation](${GITLAB_DOCS_BASE}/${GITLAB_MODEL_NAME}) for details.
"""
                    },
                    {
                        "label": "Installation",
                        "content": """## Install ${GITLAB_MODEL_NAME}

Clone from [GitHub](${GITLAB_GITHUB_BASE}/${GITLAB_MODEL_NAME}).
"""
                    }
                ]
            }

            result = self.converter._substitute_gitlab_variables(data)

            expected = {
                "displayName": "NVIDIA JAX",
                "short_description": "High-performance jax framework",
                "tabs": [
                    {
                        "label": "Overview",
                        "content": """# NVIDIA JAX

Visit [documentation](https://docs.nvidia.com/jax) for details.
"""
                    },
                    {
                        "label": "Installation",
                        "content": """## Install jax

Clone from [GitHub](https://github.com/NVIDIA/jax).
"""
                    }
                ]
            }

            self.assertEqual(result, expected)

    def test_substitute_gitlab_variables_multiple_vars_in_string(self):
        """Test multiple variable substitutions in a single string."""
        with patch.dict(
            os.environ,
            {
                "GITLAB_ORG": "NVIDIA",
                "GITLAB_TEAM": "AI",
                "GITLAB_PROJECT": "jax",
                "GITLAB_VERSION": "v1.0",
            },
        ):
            data = {
                "url": "${GITLAB_ORG}/${GITLAB_TEAM}/${GITLAB_PROJECT}/${GITLAB_VERSION}",
            }

            result = self.converter._substitute_gitlab_variables(data)

            expected = {
                "url": "NVIDIA/AI/jax/v1.0",
            }

            self.assertEqual(result, expected)

    def test_substitute_model_variable(self):
        """Test that ${MODEL} variable is substituted (special allowed variable)."""
        with patch.dict(
            os.environ,
            {
                "MODEL": "nvidia/jax",
                "GITLAB_DOCS_BASE": "https://docs.nvidia.com",
            },
        ):
            data = {
                "displayName": "Playbook for ${MODEL}",
                "tabs": [
                    {
                        "label": "Overview",
                        "content": "# ${MODEL}\n\nVisit ${GITLAB_DOCS_BASE}/${MODEL}",
                    }
                ],
            }

            result = self.converter._substitute_gitlab_variables(data)

            expected = {
                "displayName": "Playbook for nvidia/jax",
                "tabs": [
                    {
                        "label": "Overview",
                        "content": "# nvidia/jax\n\nVisit https://docs.nvidia.com/nvidia/jax",
                    }
                ],
            }

            self.assertEqual(result, expected)

    def test_substitute_mixed_gitlab_and_model_variables(self):
        """Test that both GITLAB_ and MODEL variables work together."""
        with patch.dict(
            os.environ,
            {
                "MODEL": "nvidia/jax",
                "GITLAB_ASSET_BASE": "https://assets.example.com",
                "GITLAB_DOCS_BASE": "https://docs.example.com",
                "NON_ALLOWED_VAR": "should_not_appear",
            },
        ):
            data = {
                "path": "${GITLAB_ASSET_BASE}/${MODEL}/assets",
                "docs": "${GITLAB_DOCS_BASE}/${MODEL}/guide",
                "other": "${NON_ALLOWED_VAR}",  # Should NOT be substituted
                "tabs": [
                    {
                        "label": "Setup",
                        "content": "Install ${MODEL} from ${GITLAB_ASSET_BASE}/${MODEL}",
                    }
                ],
            }

            result = self.converter._substitute_gitlab_variables(data)

            expected = {
                "path": "https://assets.example.com/nvidia/jax/assets",
                "docs": "https://docs.example.com/nvidia/jax/guide",
                "other": "${NON_ALLOWED_VAR}",  # Remains unchanged
                "tabs": [
                    {
                        "label": "Setup",
                        "content": "Install nvidia/jax from https://assets.example.com/nvidia/jax",
                    }
                ],
            }

            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()

