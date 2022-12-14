from typing import Callable, List
import os
import pygit2  # type: ignore
import subprocess


_EMPTY_REPO_URL = "https://github.com/louis-hildebrand/empty.git"
_NON_EMPTY_REPO_URL = "https://github.com/louis-hildebrand/test-repo.git"
_GIT_USER_EMAIL = "gitsum tester"
_GIT_USER_NAME = "gitsum tester"

_working_dir = ""
_setup_complete = False
_old_repo_path = None
_new_repo_path = None

modified_repo_commit_hash: str = "MODIFIED_REPO_COMMIT_HASH"


# ----------------------------------------------------------------------------------------------------------------------
# Shell commands
# ----------------------------------------------------------------------------------------------------------------------
def run_shell_command(args: List[str], ignore_error: bool = False, shell: bool = False) -> str:
    if shell:
        args_str = " ".join(args)
        result = subprocess.run(args_str, capture_output=True, shell=True)
    else:
        result = subprocess.run(args, capture_output=True)
    if not ignore_error:
        error_msg = result.stderr.decode()
        if error_msg:
            print(error_msg)
        result.check_returncode()
    return result.stdout.decode()


def _git_init(dir: str, main_branch: str = "main") -> None:
    '''
    git init ``dir`` --initial-branch=``main_branch``
    '''
    # TODO: Rewrite this to support Git before 2.28?
    repo = pygit2.init_repository(dir, initial_head=main_branch)  # type: ignore
    repo.config["user.email"] = _GIT_USER_EMAIL  # type: ignore
    repo.config["user.name"] = _GIT_USER_NAME  # type: ignore


def _git_add_all() -> None:
    '''
    git add .
    '''
    run_shell_command(["git", "add", "."])


def _git_commit(msg: str) -> None:
    '''
    git commit -m ``msg``
    '''
    repo = pygit2.Repository(".")
    sig = pygit2.Signature(_GIT_USER_NAME, _GIT_USER_EMAIL)  # type: ignore
    parents = [repo.head.target] if not repo.head_is_unborn else []
    repo.create_commit("HEAD", sig, sig, msg, repo.index.write_tree(), parents)  # type: ignore


def _git_checkout_detached(n: int) -> None:
    '''
    git checkout HEAD~``n``
    '''
    run_shell_command(["git", "checkout", f"HEAD~{n}"])


def _git_checkout_branch(branch: str, new: bool = False) -> None:
    '''
    git checkout -b ``branch``
    '''
    args = ["git", "checkout"]
    if new:
        args.append("-b")
    args.append(branch)
    run_shell_command(args)


def _git_merge(branch: str) -> None:
    '''
    git merge ``branch``
    '''
    run_shell_command(["git", "merge", branch], ignore_error=True)


def _git_clone(url: str, dir: str) -> None:
    '''
    git clone ``url`` ``dir``
    '''
    run_shell_command(["git", "clone", url, dir])


def _git_reset_hard(n: int) -> None:
    '''
    git reset --hard HEAD~``n``
    '''
    run_shell_command(["git", "reset", "--hard", f"HEAD~{n}"])


def _create_file(filename: str) -> None:
    '''
    touch ``filename``
    '''
    with open(filename, "w"):
        pass


def _delete_file(filename: str) -> None:
    '''
    rm ``filename``
    '''
    os.remove(filename)


def _append_file(filename: str, text: str) -> None:
    '''
    echo ``text`` >> ``filename``
    '''
    with open(filename, "a") as f:
        f.write(text + "\n")


def _overwrite_file(filename: str, text: str) -> None:
    '''
    echo ``text`` > ``filename``
    '''
    with open(filename, "w") as f:
        f.write(text + "\n")


# ----------------------------------------------------------------------------------------------------------------------
# Set up: repo creation
# ----------------------------------------------------------------------------------------------------------------------
def _set_up_directory_structure() -> None:
    print("Setting up directory structure")
    os.chdir("test")
    os.makedirs("test-repos")
    os.chdir("test-repos")
    os.makedirs("remote/not empty")


def _set_up_untracked() -> None:
    print("Setting up repo 'untracked'")
    _git_init("untracked")
    _create_file("untracked/hello.txt")


def _set_up_deleted() -> None:
    print("Setting up repo 'deleted'")
    _git_init("deleted", "master")
    os.chdir("deleted")
    try:
        _create_file("hello.txt")
        _git_add_all()
        _git_commit("Initial commit")

        _delete_file("hello.txt")
    finally:
        os.chdir("..")


def _set_up_modified() -> None:
    print("Setting up repo 'modified'")
    _git_init("modified")
    os.chdir("modified")
    try:
        _create_file("hello.txt")
        _git_add_all()
        _git_commit("Initial commit")

        _create_file("general-kenobi.txt")
        _git_add_all()
        _git_commit("Create new file")

        _git_checkout_detached(1)
        _append_file("hello.txt", "Hello there!")
    finally:
        os.chdir("..")


def _set_up_unmerged() -> None:
    print("Setting up repo 'unmerged'")
    _git_init("unmerged", "main")
    os.chdir("unmerged")
    try:
        _create_file("hello.txt")
        _append_file("hello.txt", "Hello there!")
        _git_add_all()
        _git_commit("Initial commit")

        _git_checkout_branch("feature", new=True)
        _overwrite_file("hello.txt", "General Kenobi!")
        _git_add_all()
        _git_commit("Create feature branch")

        _git_checkout_branch("main")
        _overwrite_file("hello.txt", "Come here, my little friend.")
        _git_add_all()
        _git_commit("Extend main branch")

        _git_merge("feature")
    finally:
        os.chdir("..")


def _set_up_remote_empty() -> None:
    print("Setting up repo 'remote/empty'")
    _git_clone(_EMPTY_REPO_URL, "remote/empty")


def _set_up_remote_staged() -> None:
    print("Setting up repo 'remote/not empty/staged'")
    _git_clone(_NON_EMPTY_REPO_URL, "remote/not empty/staged")
    os.chdir("remote/not empty/staged")
    try:
        _git_checkout_branch("feature")
        _create_file("hello.txt")
        _git_add_all()
    finally:
        os.chdir("../../..")


def _set_up_remote_ahead_behind() -> None:
    print("Setting up repo 'remote/not empty/ahead behind'")
    _git_clone(_NON_EMPTY_REPO_URL, "remote/not empty/ahead behind")
    os.chdir("remote/not empty/ahead behind")
    try:
        _git_reset_hard(3)
        _create_file("hello.txt")
        _git_add_all()
        _git_commit("Add file")
    finally:
        os.chdir("../../..")


def _set_up_outside_files() -> None:
    print("Setting up outside files")
    os.makedirs("all-outside")
    _create_file("all-outside/hello.txt")
    _create_file("all-outside/general-kenobi.txt")
    _create_file("outside.txt")
    os.makedirs("remote/all-outside")
    _create_file("remote/all-outside/hello.txt")
    os.makedirs("remote/all-outside/nested-outside")
    _create_file("remote/all-outside/nested-outside/general-kenobi.txt")
    os.makedirs("remote/empty-outside")
    _create_file("remote/outside.txt")


# ----------------------------------------------------------------------------------------------------------------------
# Setup and teardown
# ----------------------------------------------------------------------------------------------------------------------
def _disable_outer_repo() -> None:
    global _old_repo_path
    global _new_repo_path
    outer_repo = pygit2.discover_repository(".")
    if outer_repo:
        #print(f"Disabling the outer repo at '{outer_repo}'")
        old_repo_path = outer_repo[:-1] if outer_repo.endswith("/") else outer_repo
        new_repo_path = old_repo_path + ".bak"
        os.rename(old_repo_path, new_repo_path)
        _old_repo_path = old_repo_path
        _new_repo_path = new_repo_path
    else:
        #print("No outer repo to disable")
        pass


def _activate_outer_repo() -> None:
    if _old_repo_path and _new_repo_path:
        #print(f"Re-activating the outer repo at '{_new_repo_path}'")
        os.rename(_new_repo_path, _old_repo_path)
    else:
        #print("No outer repo to re-activate")
        pass


def _get_modified_repo_commit_hash() -> str:
    repo = pygit2.Repository("test/test-repos/modified")
    return repo.head.target.hex[:6]  # type: ignore


def _shared_setup() -> None:
    # TODO: Clean out existing repos?
    # TODO: Check that user is running tests from the root of the repo?
    global _working_dir
    global modified_repo_commit_hash
    _working_dir = os.getcwd()

    if os.path.exists("test/test-repos"):
        print("Skipping setup: 'test/test-repos' already exists")
    else:
        _set_up_directory_structure()

        _set_up_untracked()
        _set_up_deleted()
        _set_up_modified()
        _set_up_unmerged()
        _set_up_remote_empty()
        _set_up_remote_staged()
        _set_up_remote_ahead_behind()

        _set_up_outside_files()

    os.chdir(_working_dir)

    modified_repo_commit_hash = _get_modified_repo_commit_hash()

    run_shell_command(["coverage", "erase"], True)

    print()


def _individual_setup() -> None:
    os.chdir("test/test-repos")
    _disable_outer_repo()


def _tear_down() -> None:
    # TODO: Activate current repo
    # TODO: Disable inner repos?
    os.chdir(_working_dir)
    _activate_outer_repo()


# ----------------------------------------------------------------------------------------------------------------------
# General utility
# ----------------------------------------------------------------------------------------------------------------------
def run_test(test: Callable[[], None]) -> None:
    global _setup_complete
    try:
        if not _setup_complete:
            _shared_setup()
            _setup_complete = True
        _individual_setup()
        test()
    finally:
        _tear_down()


def run_gitsum(args: List[str]) -> str:
    gitsum_command = [f"..{os.path.sep}..{os.path.sep}lib{os.path.sep}gitsum.py"]
    coverage_command = ["coverage", "run", "--append", "--branch", "--data-file=../../.coverage"]
    return run_shell_command(coverage_command + gitsum_command + args)

def actual_expected(actual: str, expected: str) -> str:
    out = "\n" + ("=" * 31) + " OUTPUT " + ("=" * 31) + "\n"
    out += actual + "\n"

    out += ("=" * 30) + " EXPECTED " + ("=" * 30) + "\n"
    out += expected + "\n"
    out += ("=" * 70) + "\n"

    return out
