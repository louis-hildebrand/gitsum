from subprocess import PIPE
from typing import List, Union
import os
import subprocess


class RepoStatus:
    BRANCH_WIDTH = 10

    def __init__(self, full_path: str, name: str, branch: str, has_changes: bool, has_remote: bool, local_commits: Union[int, None], remote_commits: Union[int, None]):
        self.full_path = full_path
        self.name = name
        self.branch = branch
        self.has_changes = has_changes
        self.has_remote = has_remote
        self.local_commits = local_commits
        self.remote_commits = remote_commits

    def to_string(self, name_width: int) -> str:
        is_up_to_date = not self.has_changes and (not self.has_remote or (self.local_commits == 0 and self.remote_commits == 0))
        return f"{' ' if is_up_to_date else '!'}  {self.name:<{name_width}}  {self.branch:<{RepoStatus.BRANCH_WIDTH}} {' *' if self.has_changes else '  '}{f' >{self.local_commits}' if self.local_commits else '   '}{f' <{self.remote_commits}' if self.remote_commits else '   '}"


def _flatten(l: List[List[str]]) -> List[str]:
    return [x for sublist in l for x in sublist]


def _invoke_git(args: List[str], full_path: str) -> str:
    result = subprocess.run(["git", "--git-dir", os.path.join(full_path, ".git"), "--work-tree", full_path] + args, stdout=PIPE)
    return result.stdout.decode().strip()


def _is_git_repo(dir: str) -> bool:
    # TODO: This seems hacky
    return os.path.isdir(dir + "/.git")


def _get_git_repos(dir: str) -> List[str]:
    """
    Recursively searches for git repos starting in (and including) the given directory.

    Returns the full path of each git repo.
    """
    if not os.path.isdir(dir):
        return []
    if _is_git_repo(dir):
        return [dir]
    return _flatten([_get_git_repos(os.path.join(dir, subdir)) for subdir in os.listdir(dir)])


def _check_changes(full_path: str) -> bool:
    return bool(
        _invoke_git(
            ["ls-files", "--others", "--deleted", "--modified", "--unmerged", "--exclude-standard"],
            full_path
        )
    )


def _get_branch(full_path: str) -> str:
    branch_name = _invoke_git(["branch", "--show-current"], full_path)
    if branch_name:
        return branch_name
    else:
        commit_hash = _invoke_git(["rev-parse", "--short", "HEAD"], full_path)
        return f"({commit_hash})"


def _get_remote_branch(full_path: str) -> str:
    ref = _invoke_git(["symbolic-ref", "--quiet", "HEAD"], full_path)
    return _invoke_git(["for-each-ref", f"{ref}", "--format", "%(upstream:short)"], full_path)


def _count_local_commits(full_path: str, remote_branch: str) -> Union[int, None]:
    output = _invoke_git(["rev-list", "--count", f"{remote_branch}..HEAD"], full_path)
    return int(output) if output else None


def _count_remote_commits(full_path: str, remote_branch: str) -> Union[int, None]:
    output = _invoke_git(["rev-list", "--count", f"HEAD..{remote_branch}"], full_path)
    return int(output) if output else None


def _get_status(full_path: str, name: str) -> RepoStatus:
    branch_name = _get_branch(full_path)
    has_changes = _check_changes(full_path)
    remote_branch_name = _get_remote_branch(full_path)
    if remote_branch_name:
        has_remote = True
        local_commits = _count_local_commits(full_path, remote_branch_name)
        remote_commits = _count_remote_commits(full_path, remote_branch_name)
    else:
        has_remote = False
        local_commits = None
        remote_commits = None
    return RepoStatus(full_path, name, branch_name, has_changes, has_remote, local_commits, remote_commits)


def main():
    cwd = os.getcwd()
    repo_paths = _get_git_repos(cwd)
    repo_names = [(x, x[len(cwd)+1:]) for x in repo_paths]
    max_name_width = max([len(name) for (_, name) in repo_names])
    for (full_path, name) in repo_names:
        status = _get_status(full_path, name)
        print(status.to_string(max_name_width))


if __name__ == "__main__":
    main()
