"""
Module for finding Git repositories.
"""
from pathlib import Path
from typing import List, Tuple, TypeVar
import os
import pygit2  # type: ignore


T = TypeVar("T")


def _flatten(l: List[List[T]]) -> List[T]:
    return [x for sublist in l for x in sublist]


def _do_get_git_repos(dir: Path) -> Tuple[List[pygit2.Repository], List[Path]]:
    # TODO: for this specific folder, pygit2.discover_repository() returns a path but the Repository constructor rejects that same path. Why???
    if "Special Characters" in str(dir):
        return ([], [])
    if not os.path.isdir(dir):
        return ([], [dir])

    repo_path = pygit2.discover_repository(str(dir))
    if repo_path:
        return ([pygit2.Repository(repo_path)], [])

    results = [_do_get_git_repos(subdir) for subdir in dir.iterdir()]
    # If there are no Git repos within this directory, just say that this entire directory is an outside file
    repos = _flatten([repos for (repos, _) in results])
    outside_files = _flatten([outside_files for (_, outside_files) in results])
    if len(repos) != 0:
        return (repos, outside_files)
    else:
        return (repos, [dir])


def find_git_repos(dir: Path, list_outside_files: bool) -> List[pygit2.Repository]:
    """
    Recursively searches for git repos starting in (and including) the given directory.
    """
    (repos, outside_files) = _do_get_git_repos(dir)

    if list_outside_files:
        outside_files.sort()
        for f in outside_files:
            relative_path = f.relative_to(dir).as_posix()
            path_str = relative_path + "/" if f.is_dir() else relative_path
            print(f"OUTSIDE: {path_str}")

    return repos
