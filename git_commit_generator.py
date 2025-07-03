#!/usr/bin/env python3
"""
Git Commit Message Generator

This script generates meaningful commit messages based on staged changes in a Git repository.
It can be configured to use either Ollama or LM-Studio.
"""

import argparse
import sys
import logging

# Fix relative imports by using absolute imports instead
from providers import ProviderType
from generator import GitCommitGenerator
from git_utils import commit_changes

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("git-commit-generator")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Git commit messages based on staged changes"
    )
    parser.add_argument(
        "model_name",
        type=str,
        nargs="?",  # Make positional argument optional
        default=None,
        help="Model name to use with the provider",
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["ollama", "lm-studio"],
        default="ollama",
        help="LLM provider to use (ollama or lm-studio) (lm-studio by default)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name to use with the provider (alternative to positional argument)",
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default="http://localhost:11434",
        help="Base URL for Ollama API",
    )
    parser.add_argument(
        "--lm-studio-url",
        type=str,
        default="http://localhost:1234/v1",
        help="Base URL for LM-Studio API",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=400,
        help="Maximum number of tokens for response",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature parameter for generation",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Automatically commit changes with the generated message",
    )
    parser.add_argument(
        "--template",
        type=str,
        default=None,
        help='Template for commit message format (e.g. "project: <short description>\n\n<long description>")',
    )
    parser.add_argument(
        "--use-history",
        action="store_true",
        help="Include recent commit messages for changed files as samples for the LLM",
    )

    args = parser.parse_args()

    # Use the model name from either the positional argument or --model flag
    model_name = args.model if args.model is not None else args.model_name

    provider = (
        ProviderType.OLLAMA if args.provider == "ollama" else ProviderType.LM_STUDIO
    )

    # If provider is specified but model is not provided through command line arguments
    if model_name is None:
        # Initialize generator without model to get available models
        generator = GitCommitGenerator(
            model=None,
            provider=provider,
            ollama_base_url=args.ollama_url,
            lm_studio_base_url=args.lm_studio_url,
        )

        available_models = generator.get_available_models()

        if available_models:
            print(f"Available models for {args.provider}:")
            for model in available_models:
                print(f"- {model}")
            print(
                "\nPlease specify a model either as a positional argument or with --model parameter."
            )
            print(
                "Example: git-commit-gen <modelname> OR git-commit-gen --model <modelname>"
            )
        else:
            print(
                f"Failed to retrieve models for {args.provider}. Please check if the service is running."
            )
        sys.exit(1)

    generator = GitCommitGenerator(
        model=model_name,
        provider=provider,
        ollama_base_url=args.ollama_url,
        lm_studio_base_url=args.lm_studio_url,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        commit_template=args.template,
        use_history=args.use_history,
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
        success = commit_changes(commit_message)
        if success:
            print("\nChanges committed successfully!")
        else:
            print("\nError committing changes.")
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
