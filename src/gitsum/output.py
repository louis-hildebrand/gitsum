"""
Module for output (warning messages, etc.)
"""
from pathlib import Path
import os
import sys


def get_repo_name(path_str: str) -> str:
    """
    Returns the path to the given repo, relative to the current working directory.
    """
    repo_path = Path(path_str)
    working_dir = Path(os.getcwd())
    # Remove .git folder
    if repo_path.match(".git"):
        repo_path = repo_path.parent
    return repo_path.relative_to(working_dir).as_posix()


def warn(msg: str) -> None:
    print(f"WARN: {msg}", file=sys.stderr)
