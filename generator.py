"""
Git Commit Generator core functionality
"""

import logging
import re
from typing import List, Optional

from providers import ProviderType, create_provider
from git_utils import check_staged_changes

logger = logging.getLogger('git-commit-generator')

class GitCommitGenerator:
    def __init__(
        self,
        model: str,
        provider: ProviderType = ProviderType.OLLAMA,
        ollama_base_url: str = "http://localhost:11434",
        lm_studio_base_url: str = "http://localhost:1234/v1",
        max_tokens: int = 150,
        temperature: float = 0.7,
        commit_template: Optional[str] = None
    ):
        """
        Initialize the GitCommitGenerator with specified LLM provider and settings.
        
        Args:
            provider: Which LLM provider to use (Ollama or LM-Studio)
            model: Model name to use with the provider
            ollama_base_url: Base URL for Ollama API
            lm_studio_base_url: Base URL for LM-Studio API
            max_tokens: Maximum number of tokens in the generated response
            temperature: Temperature parameter for generation (higher = more creative)
            commit_template: Optional template string for commit message format
                             (e.g. "project: <short description>\\n\\n<long description>")
        """
        base_url = ollama_base_url if provider == ProviderType.OLLAMA else lm_studio_base_url
        self.provider = create_provider(provider, base_url, model)
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.commit_template = commit_template

    def get_available_models(self) -> List[str]:
        """
        Get available models for the configured provider
        
        Returns:
            List of available model names
        """
        return self.provider.get_available_models()

    def generate_commit_message(self) -> str:
        """
        Generate a commit message based on staged changes.
        
        Returns:
            Generated commit message or error message
        """
        # Check for staged changes
        has_changes, diff_output = check_staged_changes()
        
        if not has_changes:
            return "Error: No staged changes found. Use 'git add' to stage changes first."
        
        # Create a prompt for the language model
        if self.commit_template:
            template_instructions = f"""
Use the following template for your commit message:
{self.commit_template}

Where:
- <short description> should be a brief summary of changes
- <long description> should provide more context and details
"""
        else:
            template_instructions = """
Follow these guidelines:
1. Start with a type (feat, fix, docs, style, refactor, test, chore)
2. Keep the message under 50 characters for the first line
3. Be specific about what changed and why
4. Use imperative mood (e.g., "Add feature" not "Added feature")
"""
            
        prompt = f"""
Generate a concise and descriptive Git commit message based on the following changes.
{template_instructions}

Here are the staged changes:

{diff_output}

Commit message:
"""
        
        # Generate commit message using the provider and clean up the response
        message = self.provider.generate(
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        print("Generated message:\n///////\n", message)
        print("////")
        
        # Remove any content inside <think></think> tags
        # This handles:
        # 1. Complete <think>...</think> blocks
        # 2. Orphaned </think> tags when opening tag is missing
        # 3. Orphaned <think> tags when closing tag is missing
        
        # First remove complete <think>...</think> blocks
        message = re.sub(r'<think>.*?</think>', '', message, flags=re.DOTALL)
        
        # Remove orphaned </think> tags and any text before them
        message = re.sub(r'.*</think>', '', message, flags=re.DOTALL)
        
        # Clean up the message by removing any backticks and extra whitespace
        message = message.strip('`').strip()
        
        return message
