from shutil import rmtree
import os
import pygit2  # type: ignore
import subprocess
import unittest


EMPTY_REPO_URL = "https://github.com/louis-hildebrand/empty.git"
NON_EMPTY_REPO_URL = "https://github.com/louis-hildebrand/test-repo.git"
EXPECTED_OUTPUT = """Found 7 Git repositories.
!  deleted                        [LR]  master        *
!  modified                       [LR]  (MODIFIED_REPO_COMMIT_HASH)      *
   remote/empty                   [LB]  (no commits)
!  remote/not empty/ahead behind        main            >1 <3
!  remote/not empty/staged              feature       *
!  unmerged                       [LR]  main          *
!  untracked                      [LR]  (no commits)  *"""


def _run_shell_command(args: list[str]) -> None:
    subprocess.run(args, capture_output=True)


def _git_init(dir: str, main_branch: str = "main") -> None:
    '''
    git init ``dir`` --initial-branch=``main_branch``
    '''
    # TODO: Rewrite this to support Git before 2.28?
    _run_shell_command(["git", "init", dir, "-b", main_branch])


def _git_add_all() -> None:
    '''
    git add .
    '''
    _run_shell_command(["git", "add", "."])


def _git_commit(msg: str) -> None:
    '''
    git commit -m ``msg``
    '''
    _run_shell_command(["git", "commit", "-m", msg])


def _git_checkout_detached(n: int) -> None:
    '''
    git checkout HEAD~``n``
    '''
    _run_shell_command(["git", "checkout", f"HEAD~{n}"])


def _git_checkout_branch(branch: str, new: bool = False) -> None:
    '''
    git checkout -b ``branch``
    '''
    args = ["git", "checkout"]
    if new:
        args.append("-b")
    args.append(branch)
    _run_shell_command(args)


def _git_merge(branch: str) -> None:
    '''
    git merge ``branch``
    '''
    _run_shell_command(["git", "merge", branch])


def _git_clone(url: str, dir: str) -> None:
    '''
    git clone ``url`` ``dir``
    '''
    _run_shell_command(["git", "clone", url, dir])


def _git_reset_hard(n: int) -> None:
    '''
    git reset --hard HEAD~``n``
    '''
    _run_shell_command(["git", "reset", "--hard", f"HEAD~{n}"])


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


class GitSumTests(unittest.TestCase):
    modified_repo_commit_hash = "MODIFIED_REPO_COMMIT_HASH"

    def _set_up_directory_structure(self) -> None:
        print("Setting up directory structure...")
        os.chdir("test")
        if os.path.exists("test-repos"):
            try:
                rmtree("test-repos")
            except:
                raise RuntimeError("Please delete 'test/test-repos/' before running the integration tests")
        os.makedirs("test-repos", exist_ok=True)
        os.chdir("test-repos")
        os.makedirs("remote/not empty", exist_ok=True)

    def _disable_outer_repo(self):
        self.old_repo_path = None
        self.new_repo_path = None
        outer_repo = pygit2.discover_repository(".")
        if outer_repo:
            print(f"Disabling the outer repo at '{outer_repo}'")
            old_repo_path = outer_repo[:-1] if outer_repo.endswith("/") else outer_repo
            new_repo_path = old_repo_path + ".bak"
            os.rename(old_repo_path, new_repo_path)
            self.old_repo_path = old_repo_path
            self.new_repo_path = new_repo_path
        else:
            print("No outer repo to disable")

    def _activate_outer_repo(self):
        if self.old_repo_path and self.new_repo_path:
            print(f"Re-activating the outer repo at '{self.new_repo_path}'")
            os.rename(self.new_repo_path, self.old_repo_path)
        else:
            print("No outer repo to re-activate")

    def _set_up_untracked(self) -> None:
        print("Setting up repo 'untracked'")
        _git_init("untracked")
        _create_file("untracked/hello.txt")

    def _set_up_deleted(self) -> None:
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

    def _set_up_modified(self) -> None:
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

            # Get current commit hash?
            repo = pygit2.Repository(".")
            self.modified_repo_commit_hash: str = repo.head.target.hex[:6]  # type: ignore
        finally:
            os.chdir("..")

    def _set_up_unmerged(self) -> None:
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

    def _set_up_remote_empty(self) -> None:
        print("Setting up repo 'remote/empty'")
        _git_clone(EMPTY_REPO_URL, "remote/empty")

    def _set_up_remote_staged(self) -> None:
        print("Setting up repo 'remote/not empty/staged'")
        _git_clone(NON_EMPTY_REPO_URL, "remote/not empty/staged")
        os.chdir("remote/not empty/staged")
        try:
            _git_checkout_branch("feature")
            _create_file("hello.txt")
            _git_add_all()
        finally:
            os.chdir("../../..")

    def _set_up_remote_ahead_behind(self) -> None:
        print("Setting up repo 'remote/not empty/ahead behind'")
        _git_clone(NON_EMPTY_REPO_URL, "remote/not empty/ahead behind")
        os.chdir("remote/not empty/ahead behind")
        try:
            _git_reset_hard(3)
            _create_file("hello.txt")
            _git_add_all()
            _git_commit("Add file")
        finally:
            os.chdir("../../..")

    def set_up(self) -> None:
        # TODO: Clean out existing repos?
        # TODO: Check that user is running tests from the root of the repo?
        self.maxDiff = 0

        self._disable_outer_repo()

        self._set_up_directory_structure()

        self._set_up_untracked()
        self._set_up_deleted()
        self._set_up_modified()
        self._set_up_unmerged()
        self._set_up_remote_empty()
        self._set_up_remote_staged()
        self._set_up_remote_ahead_behind()

    def tear_down(self) -> None:
        # TODO: Activate current repo
        # TODO: Disable inner repos?
        os.chdir("../..")
        self._activate_outer_repo()

    def _run_gitsum(self) -> str:
        # TODO: Make this platform-independent?
        result = subprocess.run(["gitsum.bat"], stdout=subprocess.PIPE)
        result_str = result.stdout.decode()
        return result_str

    def run_test(self):
        result_str = self._run_gitsum()

        # Print actual results
        print("\n" + ("=" * 31) + " OUTPUT " + ("=" * 31))
        print(result_str)

        # Print expected results
        expected_output = EXPECTED_OUTPUT.replace("MODIFIED_REPO_COMMIT_HASH", self.modified_repo_commit_hash)
        print(("=" * 30) + " EXPECTED " + ("=" * 30))
        print(expected_output)
        print(("=" * 70) + "\n")

        # Check number of lines
        result_lines = [line.rstrip() for line in result_str.splitlines()]
        expected_lines = [line.rstrip() for line in expected_output.splitlines()]
        self.assertEqual(len(expected_lines), len(result_lines))

        # Check metadata (first line)
        result_metadata = result_lines[0]
        expected_metadata = expected_lines[0]
        self.assertEqual(expected_metadata, result_metadata)

        # Check list of repos
        result_lines = result_lines[1:]
        result_lines.sort(key = lambda x: x[2:])
        expected_lines = expected_lines[1:]
        for (expected, actual) in zip(expected_lines, result_lines):
            self.assertEqual(expected, actual)
        # TODO: Assert order of lines?

    def test(self) -> None:
        # Manually run setup and teardown methods so that teardown happens even if setup fails
        try:
            self.set_up()
            self.run_test()
        finally:
            self.tear_down()
