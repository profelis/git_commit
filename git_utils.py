"""
Git utilities for Git Commit Generator
"""

import logging
import subprocess

logger = logging.getLogger("git-commit-generator")


def commit_changes(message: str) -> bool:
    """
    Commit staged changes with the given message.

    Args:
        message: The commit message to use

    Returns:
        True if successful, False otherwise
    """
    try:
        subprocess.run(["git", "commit", "-m", message], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error committing changes: {e}")
        return False


from typing import List, Dict


def get_recent_commit_messages_for_files(
    files: List[str], n: int = 5
) -> Dict[str, List[str]]:
    """
    For each file in files, fetch the last n commit messages that affected it.
    Returns a dict: {filename: [commit messages]}
    """
    result: Dict[str, List[str]] = {}
    for file in files:
        try:
            log_command: List[str] = [
                "git",
                "log",
                f"-n{n}",
                "--pretty=format:%s",
                "--",
                file,
            ]
            output: str = subprocess.check_output(log_command, universal_newlines=True)
            messages: List[str] = [
                line.strip() for line in output.splitlines() if line.strip()
            ]
            result[file] = messages
        except subprocess.CalledProcessError as e:
            logger.error(f"Error fetching git log for {file}: {e}")
            result[file] = []
    return result
