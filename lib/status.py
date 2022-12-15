"""
Module for finding the status of a Git repository.
"""
from dataclasses import dataclass
from pathlib import Path
import os
import pygit2  # type: ignore

import lib.message as msg


@dataclass
class RepoStatus:
    name: str
    head: str
    is_local: bool
    has_changes: bool
    branch_has_upstream: bool
    local_ahead: int
    local_behind: int

    def _is_up_to_date(self) -> bool:
        return not self.has_changes and (
            not self.branch_has_upstream or (
                self.local_ahead == 0 and self.local_behind == 0
            )
        )

    def to_string(self, name_width: int, head_width: int) -> str:
        return f"{'!' if not self._is_up_to_date() else ' '}  {self.name:<{name_width}}  {'[LR]' if self.is_local else '[LB]' if not self.branch_has_upstream else '    '}  {self.head:<{head_width}} {' *' if self.has_changes else '  '}{f' >{self.local_ahead}' if self.local_ahead > 0 else '   '}{f' <{self.local_behind}' if self.local_behind > 0 else '   '}"

    def __str__(self) -> str:
        return self.to_string(0, 0)


def get_repo_name(path_str: str) -> str:
    repo_path = Path(path_str)
    working_dir = Path(os.getcwd())
    # Remove .git folder
    if repo_path.match(".git"):
        repo_path = repo_path.parent
    return repo_path.relative_to(working_dir).as_posix()


def _try_fetch(remote: pygit2.Remote, repo_name: str) -> None:
    try:
        remote.fetch()  # type: ignore
    except pygit2.GitError:
        # TODO: Check credentials? Skip?
        msg.warn(f"Failed to fetch repo '{repo_name}'")


def get_repo_status(repo: pygit2.Repository, fetch: bool) -> RepoStatus:
    name = get_repo_name(repo.path)
    branch_has_upstream = False
    (local_ahead, local_behind) = (0, 0)
    if repo.head_is_unborn:
        branch_name = "(no commits)"
    elif repo.head_is_detached:
        branch_name = f"({repo.head.target.hex[:6]})"  # type: ignore
    else:
        branch_name = repo.head.shorthand
        local_branch = repo.lookup_branch(branch_name)
        upstream_branch = local_branch.upstream
        if upstream_branch:
            branch_has_upstream = True
            if fetch:
                remote = repo.remotes[upstream_branch.remote_name]
                _try_fetch(remote, name)
            (local_ahead, local_behind) = repo.ahead_behind(local_branch.target, upstream_branch.target) # type: ignore
    is_local = not len(repo.remotes) > 0
    has_changes = len(repo.status()) > 0
    return RepoStatus(name, branch_name, is_local, has_changes, branch_has_upstream, local_ahead, local_behind)
