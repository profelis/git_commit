#!/usr/bin/env python3
"""
Git Commit Message Generator

This script generates meaningful commit messages based on staged changes in a Git repository.
It can be configured to use either Ollama or LM-Studio.
"""

import argparse
import subprocess
import sys
import json
import requests
import os
from enum import Enum
import logging
from typing import List, Dict, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('git-commit-generator')

class LLMProvider(Enum):
    OLLAMA = "ollama"
    LM_STUDIO = "lm-studio"

class GitCommitGenerator:
    def __init__(
        self,
        provider: LLMProvider = LLMProvider.OLLAMA,
        model: str = "llama3",
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
                             (e.g. "project: <short description>\n\n<long description>")
        """
        self.provider = provider
        self.model = model
        self.ollama_base_url = ollama_base_url
        self.lm_studio_base_url = lm_studio_base_url
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.commit_template = commit_template

    def _check_staged_changes(self) -> Tuple[bool, str]:
        """
        Check if there are staged changes in the Git repository.
        
        Returns:
            Tuple of (has_changes: bool, diff_output: str)
        """
        try:
            # Get staged changes
            diff_command = ["git", "diff", "--staged"]
            diff_output = subprocess.check_output(diff_command, universal_newlines=True)
            
            # Check if there are any staged changes
            if not diff_output:
                return False, ""
            
            # Also get the file names that are staged
            staged_files_command = ["git", "diff", "--staged", "--name-only"]
            staged_files = subprocess.check_output(staged_files_command, universal_newlines=True)
            
            # Combine the information
            summary = f"Staged files:\n{staged_files}\n\nChanges:\n{diff_output}"
            return True, summary
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing Git command: {e}")
            return False, f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False, f"Error: {str(e)}"

    def _generate_with_ollama(self, prompt: str) -> str:
        """
        Generate text using Ollama API.
        
        Args:
            prompt: The prompt to send to Ollama
            
        Returns:
            Generated text response
        """
        try:
            url = f"{self.ollama_base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data.get("response", "")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error with Ollama API: {e}")
            return f"Error: Could not generate with Ollama: {str(e)}"

    def _generate_with_lm_studio(self, prompt: str) -> str:
        """
        Generate text using LM-Studio API.
        
        Args:
            prompt: The prompt to send to LM-Studio
            
        Returns:
            Generated text response
        """
        try:
            url = f"{self.lm_studio_base_url}/completions"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stream": False
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            choices = data.get("choices", [])
            if choices and len(choices) > 0:
                return choices[0].get("text", "")
            return ""
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error with LM-Studio API: {e}")
            return f"Error: Could not generate with LM-Studio: {str(e)}"

    def _get_available_ollama_models(self) -> List[str]:
        """
        Get a list of available models from Ollama
        
        Returns:
            List of model names or empty list if failed
        """
        try:
            url = f"{self.ollama_base_url}/api/tags"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            models = [model.get("name") for model in data.get("models", [])]
            return models
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Ollama models: {e}")
            return []

    def _get_available_lm_studio_models(self) -> List[str]:
        """
        Get a list of available models from LM-Studio
        
        Returns:
            List of model names or empty list if failed
        """
        try:
            url = f"{self.lm_studio_base_url}/models"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            models = [model.get("id") for model in data.get("data", [])]
            return models
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching LM-Studio models: {e}")
            return []
    
    def get_available_models(self) -> List[str]:
        """
        Get available models for the configured provider
        
        Returns:
            List of available model names
        """
        if self.provider == LLMProvider.OLLAMA:
            return self._get_available_ollama_models()
        else:
            return self._get_available_lm_studio_models()

    def generate_commit_message(self) -> str:
        """
        Generate a commit message based on staged changes.
        
        Returns:
            Generated commit message or error message
        """
        # Check for staged changes
        has_changes, diff_output = self._check_staged_changes()
        
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
        
        # Generate commit message based on selected provider
        if self.provider == LLMProvider.OLLAMA:
            message = self._generate_with_ollama(prompt)
        else:
            message = self._generate_with_lm_studio(prompt)
            
        # Clean up the message
        message = message.strip()
        
        return message

def main():
    parser = argparse.ArgumentParser(description='Generate Git commit messages based on staged changes')
    parser.add_argument(
        '--provider', 
        type=str, 
        choices=['ollama', 'lm-studio'], 
        default='ollama',
        help='LLM provider to use (ollama or lm-studio)'
    )
    parser.add_argument(
        '--model', 
        type=str, 
        default=None,
        help='Model name to use with the provider'
    )
    parser.add_argument(
        '--ollama-url', 
        type=str, 
        default='http://localhost:11434',
        help='Base URL for Ollama API'
    )
    parser.add_argument(
        '--lm-studio-url', 
        type=str, 
        default='http://localhost:1234/v1',
        help='Base URL for LM-Studio API'
    )
    parser.add_argument(
        '--max-tokens', 
        type=int, 
        default=150,
        help='Maximum number of tokens for response'
    )
    parser.add_argument(
        '--temperature', 
        type=float, 
        default=0.7,
        help='Temperature parameter for generation'
    )
    parser.add_argument(
        '--commit', 
        action='store_true',
        help='Automatically commit changes with the generated message'
    )
    parser.add_argument(
        '--template', 
        type=str, 
        default=None,
        help='Template for commit message format (e.g. "project: <short description>\\n\\n<long description>")'
    )
    
    args = parser.parse_args()
    
    provider = LLMProvider.OLLAMA if args.provider == 'ollama' else LLMProvider.LM_STUDIO
    
    # If provider is specified but model is not provided through command line arguments
    if args.model is None:
        # Initialize generator without model to get available models
        generator = GitCommitGenerator(
            provider=provider,
            model=None,
            ollama_base_url=args.ollama_url,
            lm_studio_base_url=args.lm_studio_url
        )
        
        available_models = generator.get_available_models()
        
        if available_models:
            print(f"Available models for {args.provider}:")
            for model in available_models:
                print(f"- {model}")
            print("\nPlease specify a model with --model parameter.")
        else:
            print(f"Failed to retrieve models for {args.provider}. Please check if the service is running.")
        sys.exit(1)
    
    generator = GitCommitGenerator(
        provider=provider,
        model=args.model,
        ollama_base_url=args.ollama_url,
        lm_studio_base_url=args.lm_studio_url,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        commit_template=args.template
    )
    
    commit_message = generator.generate_commit_message()
    
    if commit_message.startswith("Error:"):
        print(commit_message)
        sys.exit(1)
    
    print("\nGenerated commit message:")
    print("-" * 50)
    print(commit_message)
    print("-" * 50)
    
    if args.commit:
        try:
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            print("\nChanges committed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"\nError committing changes: {e}")
            sys.exit(1)
    else:
        print("\nTo use this message for your commit, run:")
        print(f"git commit -m \"{commit_message.replace('"', '\\"')}\"")
        
        # Offer to copy to clipboard if available
        try:
            import pyperclip
            pyperclip.copy(commit_message)
            print("\nCommit message has been copied to clipboard.")
        except ImportError:
            print("\nTip: Install 'pyperclip' to enable clipboard support.")

if __name__ == "__main__":
    main()
