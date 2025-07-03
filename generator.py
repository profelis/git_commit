"""
Git Commit Generator core functionality
"""

import logging
import re
from typing import List, Optional

from providers import ProviderType, create_provider
from git_utils import get_recent_commit_messages_for_files

logger = logging.getLogger('git-commit-generator')


class GitCommitGenerator:
    def __init__(
        self,
        model: Optional[str],
        provider: ProviderType = ProviderType.OLLAMA,
        ollama_base_url: str = "http://localhost:11434",
        lm_studio_base_url: str = "http://localhost:1234/v1",
        max_tokens: int = 150,
        temperature: float = 0.7,
        commit_template: Optional[str] = None,
        use_history: bool = False
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
            use_history: Whether to include recent commit messages for changed files as samples
        """
        base_url = ollama_base_url if provider == ProviderType.OLLAMA else lm_studio_base_url
        self.provider = create_provider(provider, base_url, model) if model else None
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.commit_template = commit_template
        self.use_history = use_history

    def get_available_models(self) -> List[str]:
        """
        Get available models for the configured provider
        
        Returns:
            List of available model names
        """
        if self.provider:
            return self.provider.get_available_models()
        return []

    def generate_commit_message(self) -> str:
        """
        Generate a commit message based on staged changes.
        
        Returns:
            Generated commit message or error message
        """
        import subprocess
        # Limits
        MAX_FILES = 50
        MAX_DIFF_LINES_PER_FILE = 200
        MAX_DIFF_LINES_EXCLUDE = 10000

        # Get staged files
        try:
            staged_files_command = ["git", "diff", "--staged", "--name-only"]
            staged_files_output = subprocess.check_output(staged_files_command, universal_newlines=True)
            staged_files = [f.strip() for f in staged_files_output.splitlines() if f.strip()]
        except Exception as e:
            logger.error(f"Error getting staged files: {e}")
            return "Error: Could not get staged files."

        if not staged_files:
            return "Error: No staged changes found. Use 'git add' to stage changes first."

        # Limit number of files
        limited_files = staged_files[:MAX_FILES]
        diff_contexts : List[str] = []
        for file in limited_files:
            try:
                diff_cmd = ["git", "diff", "--staged", "--", file]
                diff_output = subprocess.check_output(diff_cmd, universal_newlines=True)
                diff_lines = diff_output.splitlines()
                if len(diff_lines) > MAX_DIFF_LINES_EXCLUDE:
                    logger.info(f"Excluding file {file} from diff context (diff too large: {len(diff_lines)} lines)")
                    continue
                # Limit lines per file
                limited_diff = "\n".join(diff_lines[:MAX_DIFF_LINES_PER_FILE])
                diff_contexts.append(f"File: {file}\n{limited_diff}")
            except Exception as e:
                logger.error(f"Error getting diff for {file}: {e}")
                continue

        if not diff_contexts:
            return "Error: No suitable staged changes to generate a commit message."

        diff_output = "\n\n".join(diff_contexts)

        # History context (unchanged)
        history_context = ""
        if self.use_history:
            try:
                file_histories = get_recent_commit_messages_for_files(limited_files, n=5)
                history_lines : List[str] = []
                for fname, messages in file_histories.items():
                    if messages:
                        history_lines.append(f"Recent commit messages for {fname}:")
                        for msg in messages:
                            history_lines.append(f"  - {msg}")
                        history_lines.append("")
                if history_lines:
                    history_context = "\n".join(history_lines)
            except Exception as e:
                logger.error(f"Error getting commit history context: {e}")

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
0. Don't write anything about commit message, just output the commit message
1. Start with a type (feat, fix, docs, style, refactor, test, chore)
2. Keep the message under 80 characters for the first line
3. Be specific about what changed and why
4. Use imperative mood (e.g., "Add feature" not "Added feature")
5. Write one commit for all related changes
6. After first line, add a blank line before the long description
7. Use long description to explain the context, motivation, and any relevant details
"""

        prompt = f"""
Generate a concise and descriptive Git commit message based on the following changes.
{template_instructions}
"""
        if history_context:
            prompt += f"\nHere are recent commit messages for the changed files (use these as style and content samples):\n\n{history_context}\n"
        prompt += f"\nHere are the staged changes (showing up to {MAX_FILES} files, {MAX_DIFF_LINES_PER_FILE} lines per file):\n\n{diff_output}\n\nCommit message:\n"

        if not self.provider:
            return "Error: No model/provider configured."

        # Generate commit message using the provider and clean up the response
        message = self.provider.generate(
            prompt=prompt, max_tokens=self.max_tokens, temperature=self.temperature
        )

        raw_message = message

        # Remove any content inside <think>...</think> tags, including the tags themselves
        message = re.sub(r'<think>.*?</think>', '', message, flags=re.DOTALL)
        # Remove any remaining standalone <think> or </think> tags
        message = re.sub(r'</?think>', '', message)
        message = message.strip('`').strip()

        if message == "":
            if raw_message != "":
                logger.warning("Empty commit message generated. Raw message: %s", raw_message)
            logger.warning("Empty commit message generated. Retrying with a different prompt.")
            return "Error: Empty commit message generated. Please try again."

        return message
