#!/usr/bin/env python3


from dataclasses import dataclass
from pygit2 import Repository
from typing import TypeVar
import os
import pygit2


T = TypeVar("T")


@dataclass
class RepoStatus:
    name: str
    head: str
    is_local: bool
    has_changes: bool
    branch_has_upstream: bool
    local_ahead: int
    local_behind: int

    def is_up_to_date(self) -> bool:
        return not self.has_changes and (
            not self.branch_has_upstream or (
                self.local_ahead == 0 and self.local_behind == 0
            )
        )

    def to_string(self, name_width: int, head_width: int) -> str:
        return f"{'!' if not self.is_up_to_date() else ' '}  {self.name:<{name_width}}  {'[LR]' if self.is_local else '[LB]' if not self.branch_has_upstream else '    '}  {self.head:<{head_width}} {' *' if self.has_changes else '  '}{f' >{self.local_ahead}' if self.local_ahead > 0 else '   '}{f' <{self.local_behind}' if self.local_behind > 0 else '   '}"

    def __str__(self) -> str:
        return self.to_string(0, 0)


def _truncate_path(path: str) -> str:
    name = path[len(os.getcwd())+1:-6]
    if not name:
        name = "."
    return name


def _do_get_git_repos(dir: str, max_path_len: int) -> tuple[list[Repository], int]:
    """
    Recursively searches for git repos starting in (and including) the given directory.
    """
    trunc_dir = _truncate_path(dir)
    max_path_len = max(len(trunc_dir), max_path_len)
    print(f"Scanning {trunc_dir + '.':<{max_path_len+1}}", end="\r")
    # TODO: for this specific folder, pygit2.discover_repository() returns a path but the Repository constructor rejects that same path. Why???
    if "Special Characters" in dir:
        return ([], max_path_len)
    if not os.path.isdir(dir):
        return ([], max_path_len)
    repo_path = pygit2.discover_repository(dir)
    if repo_path:
        return ([Repository(repo_path)], max_path_len)
    repos: list[Repository] = []
    for subdir in os.listdir(dir):
        (new_repos, max_path_len) = _do_get_git_repos(os.path.join(dir, subdir), max_path_len)
        repos += new_repos
    return (repos, max_path_len)


def _get_git_repos(dir: str) -> list[Repository]:
    (repos, max_path_len) = _do_get_git_repos(dir, 0)
    print(" " * (len("Scanning .") + max_path_len), end="\r")
    return repos


def get_status(repo: Repository, name: str) -> RepoStatus:
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
            (local_ahead, local_behind) = repo.ahead_behind(local_branch.target, upstream_branch.target) # type: ignore
    is_local = not len(repo.remotes) > 0
    has_changes = len(repo.status()) > 0
    return RepoStatus(name, branch_name, is_local, has_changes, branch_has_upstream, local_ahead, local_behind)


def main():
    cwd = os.getcwd()
    repos = _get_git_repos(cwd)
    print(" " * 100, end="\r")
    print(f"Found {len(repos)} Git repositories.")
    statuses = [get_status(r, _truncate_path(r.path)) for r in repos]
    name_width = max([len(s.name) for s in statuses])
    head_width = max([len(s.head) for s in statuses])
    [print(s.to_string(name_width, head_width)) for s in statuses]


if __name__ == "__main__":
    main()
