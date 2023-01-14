"""
Module for output (warning messages, etc.)
"""
from pathlib import Path
import os
import sys


def get_repo_name(path_str: str) -> str:
    """
    Returns the path to the given repo, relative to the current working
    directory. The path will always end with the repo name (e.g., "../repo"
    instead of just ".").
    """
    repo_path = Path(path_str).resolve()
    working_dir = Path(os.getcwd()).resolve()
    # Remove .git folder
    if repo_path.match(".git"):
        repo_path = repo_path.parent
    # Make sure the path ends with the repo name
    if repo_path == working_dir:
        relative_path = Path(f"../{repo_path.stem}")
    elif repo_path in working_dir.parents:
        relative_path = Path(os.path.relpath(repo_path, working_dir))
        relative_path = relative_path.joinpath(f"../{repo_path.stem}")
    else:
        relative_path = Path(os.path.relpath(repo_path, working_dir))
    return relative_path.as_posix()


def warn(msg: str) -> None:
    print(f"WARN: {msg}", file=sys.stderr)
