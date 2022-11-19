from pygit2 import Repository
from typing import TypeVar
import os
import pygit2


T = TypeVar("T")


class RepoStatus:
    def __init__(self, name: str, branch: str, is_local: bool, has_changes: bool, branch_has_upstream: bool, local_ahead: int, local_behind: int):
        self._name = name
        self._branch = branch
        self._has_changes = has_changes
        self._is_local = is_local
        self._branch_has_upstream = branch_has_upstream
        self._local_ahead = local_ahead
        self._local_behind = local_behind

    def to_string(self, name_width: int, head_width: int) -> str:
        is_up_to_date = not self._has_changes
        return f"{' ' if is_up_to_date else '!'}  {self._name:<{name_width}}  {'[LR]' if self._is_local else '[LB]' if not self._branch_has_upstream else '    '}  {self._branch:<{head_width}} {' *' if self._has_changes else '  '}{f' >{self._local_ahead}' if self._local_ahead > 0 else '   '}{f' <{self._local_behind}' if self._local_behind > 0 else '   '}"


def _flatten(l: list[list[T]]) -> list[T]:
    return [x for sublist in l for x in sublist]


def _get_git_repos(dir: str) -> list[Repository]:
    """
    Recursively searches for git repos starting in (and including) the given directory.
    """
    # TODO: Why???
    if "Special Characters" in dir:
        return []
    if not os.path.isdir(dir):
        return []
    repo_path = pygit2.discover_repository(dir)
    if repo_path:
        return [Repository(repo_path)]
    return _flatten([_get_git_repos(os.path.join(dir, subdir)) for subdir in os.listdir(dir)])


def _get_short_name(repo: Repository) -> str:
    name = repo.path[len(os.getcwd())+1:-6]
    if not name:
        name = "."
    return name


def _get_status(repo: Repository, name: str) -> RepoStatus:
    branch_has_upstream = False
    (local_ahead, local_behind) = (0, 0)
    if repo.head_is_unborn:
        # TODO: What to do here? Use repo.head.name?
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
    # TODO: Test this
    has_changes = len(repo.status()) > 0
    return RepoStatus(name, branch_name, is_local, has_changes, branch_has_upstream, local_ahead, local_behind)


def main():
    cwd = os.getcwd()
    repos = _get_git_repos(cwd)
    statuses = [_get_status(r, _get_short_name(r)) for r in repos]
    name_width = max([len(s._name) for s in statuses])
    head_width = max([len(s._branch) for s in statuses])
    [print(s.to_string(name_width, head_width)) for s in statuses]


if __name__ == "__main__":
    main()
