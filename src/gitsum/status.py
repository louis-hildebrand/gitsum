"""
Module for finding the status of a Git repository.
"""
from dataclasses import dataclass
from pathlib import Path
import os
import pygit2  # type: ignore

import gitsum.message as msg


@dataclass
class RepoStatus:
    name: str
    head: str
    is_local: bool
    has_changes: bool
    branch_has_upstream: bool
    local_ahead: int
    local_behind: int

    def __init__(self, repo: pygit2.Repository, fetch: bool) -> None:
        self.name = get_repo_name(repo.path)
        self.branch_has_upstream = False
        (self.local_ahead, self.local_behind) = (0, 0)
        if repo.head_is_unborn:
            self.head = "(no commits)"
        elif repo.head_is_detached:
            self.head = f"({repo.head.target.hex[:6]})"  # type: ignore
        else:
            self.head = repo.head.shorthand
            local_branch = repo.lookup_branch(self.head)
            if local_branch.upstream:
                self.branch_has_upstream = True
                if fetch:
                    remote = repo.remotes[local_branch.upstream.remote_name]
                    if not self._try_fetch(remote):
                        msg.warn(f"Failed to fetch repo '{self.name}'")
                (self.local_ahead, self.local_behind) = repo.ahead_behind(local_branch.target, local_branch.upstream.target) # type: ignore
        self.is_local = not len(repo.remotes) > 0
        self.has_changes = len(repo.status()) > 0

    @staticmethod
    def _try_fetch(remote: pygit2.Remote) -> bool:
        try:
            remote.fetch()  # type: ignore
            return True
        except pygit2.GitError:
            # TODO: Check credentials? Skip?
            return False

    def _is_up_to_date(self) -> bool:
        return not self.has_changes and (
            not self.branch_has_upstream or (
                self.local_ahead == 0 and self.local_behind == 0
            )
        )

    def to_string(self, name_width: int, head_width: int) -> str:
        flag = "!" if not self._is_up_to_date() else " "
        name = f"{self.name:<{name_width}}"
        head = f"{self.head:<{head_width}}"
        local_status = "*" if self.has_changes else " "
        if self.is_local:
            remote_status = "local repo"
        elif not self.branch_has_upstream:
            remote_status = "local branch"
        else:
            remote_status = ""
            if self.local_ahead > 0:
                remote_status += f">{self.local_ahead} "
            if self.local_behind > 0:
                remote_status += f"<{self.local_behind}"
        return f"{flag}  {name}  {head}  {local_status}  {remote_status}"

    def __str__(self) -> str:
        return self.to_string(0, 0)


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
