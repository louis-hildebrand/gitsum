from typing import List
import os
import pygit2  # type: ignore
import subprocess
import unittest


class TestCase(unittest.TestCase):
    MODIFIED_REPO_COMMIT_HASH = "MODIFIED_REPO_COMMIT_HASH"

    _EMPTY_REPO_URL = "https://github.com/louis-hildebrand/empty.git"
    _NON_EMPTY_REPO_URL = "https://github.com/louis-hildebrand/test-repo.git"
    _GIT_USER_EMAIL = "gitsum tester"
    _GIT_USER_NAME = "gitsum tester"
    _GITSUM_REPO_ROOT: str

    _one_time_setup_done = False
    _modified_repo_commit_hash: str

    def __init__(self, methodName: str):
        super(TestCase, self).__init__(methodName)
        self.maxDiff = 0

        self._old_repo_path: str
        self._new_repo_path: str

    #region Shell commands

    def _run_shell_command(self, args: List[str], ignore_error: bool = False, shell: bool = False) -> str:
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

    def _git_init(self, dir: str, main_branch: str = "main") -> None:
        '''
        git init ``dir`` --initial-branch=``main_branch``
        '''
        # TODO: Rewrite this to support Git before 2.28?
        repo = pygit2.init_repository(dir, initial_head=main_branch)  # type: ignore
        repo.config["user.email"] = TestCase._GIT_USER_EMAIL  # type: ignore
        repo.config["user.name"] = TestCase._GIT_USER_NAME  # type: ignore

    def _git_add_all(self) -> None:
        '''
        git add .
        '''
        self._run_shell_command(["git", "add", "."])

    def _git_commit(self, msg: str) -> None:
        '''
        git commit -m ``msg``
        '''
        repo = pygit2.Repository(".")
        sig = pygit2.Signature(TestCase._GIT_USER_NAME, TestCase._GIT_USER_EMAIL)  # type: ignore
        parents = [repo.head.target] if not repo.head_is_unborn else []
        repo.create_commit("HEAD", sig, sig, msg, repo.index.write_tree(), parents)  # type: ignore

    def _git_checkout_detached(self, n: int) -> None:
        '''
        git checkout HEAD~``n``
        '''
        self._run_shell_command(["git", "checkout", f"HEAD~{n}"])

    def _git_checkout_branch(self, branch: str, new: bool = False) -> None:
        '''
        git checkout -b ``branch``
        '''
        args = ["git", "checkout"]
        if new:
            args.append("-b")
        args.append(branch)
        self._run_shell_command(args)

    def _git_merge(self, branch: str) -> None:
        '''
        git merge ``branch``
        '''
        self._run_shell_command(["git", "merge", branch], ignore_error=True)

    def _git_clone(self, url: str, dir: str) -> None:
        '''
        git clone ``url`` ``dir``
        '''
        self._run_shell_command(["git", "clone", url, dir])

    def _git_reset_hard(self, n: int) -> None:
        '''
        git reset --hard HEAD~``n``
        '''
        self._run_shell_command(["git", "reset", "--hard", f"HEAD~{n}"])

    def _create_file(self, filename: str) -> None:
        '''
        touch ``filename``
        '''
        with open(filename, "w"):
            pass

    def _delete_file(self, filename: str) -> None:
        '''
        rm ``filename``
        '''
        os.remove(filename)

    def _append_file(self, filename: str, text: str) -> None:
        '''
        echo ``text`` >> ``filename``
        '''
        with open(filename, "a") as f:
            f.write(text + "\n")

    def _overwrite_file(self, filename: str, text: str) -> None:
        '''
        echo ``text`` > ``filename``
        '''
        with open(filename, "w") as f:
            f.write(text + "\n")

    #endregion

    #region Helpers for setup

    def _set_up_directory_structure(self) -> None:
        print("Setting up directory structure")
        os.chdir("test")
        os.makedirs("test-repos")
        os.chdir("test-repos")
        os.makedirs("remote/not empty")

    def _set_up_untracked(self) -> None:
        print("Setting up repo 'untracked'")
        self._git_init("untracked")
        self._create_file("untracked/hello.txt")

    def _set_up_deleted(self) -> None:
        print("Setting up repo 'deleted'")
        self._git_init("deleted", "master")
        os.chdir("deleted")

        self._create_file("hello.txt")
        self._git_add_all()
        self._git_commit("Initial commit")

        self._delete_file("hello.txt")

        os.chdir("..")

    def _set_up_modified(self) -> None:
        print("Setting up repo 'modified'")
        self._git_init("modified")
        os.chdir("modified")

        self._create_file("hello.txt")
        self._git_add_all()
        self._git_commit("Initial commit")

        self._create_file("general-kenobi.txt")
        self._git_add_all()
        self._git_commit("Create new file")

        self._git_checkout_detached(1)

        self._append_file("hello.txt", "Hello there!")

        os.chdir("..")

    def _set_up_unmerged(self) -> None:
        print("Setting up repo 'unmerged'")
        self._git_init("unmerged", "main")
        os.chdir("unmerged")

        self._create_file("hello.txt")
        self._append_file("hello.txt", "Hello there!")
        self._git_add_all()
        self._git_commit("Initial commit")

        self._git_checkout_branch("feature", new=True)
        self._overwrite_file("hello.txt", "General Kenobi!")
        self._git_add_all()
        self._git_commit("Create feature branch")

        self._git_checkout_branch("main")
        self._overwrite_file("hello.txt", "Come here, my little friend.")
        self._git_add_all()
        self._git_commit("Extend main branch")

        self._git_merge("feature")

        os.chdir("..")

    def _set_up_remote_empty(self) -> None:
        print("Setting up repo 'remote/empty'")
        self._git_clone(TestCase._EMPTY_REPO_URL, "remote/empty")

    def _set_up_remote_staged(self) -> None:
        print("Setting up repo 'remote/not empty/staged'")
        self._git_clone(TestCase._NON_EMPTY_REPO_URL, "remote/not empty/staged")
        os.chdir("remote/not empty/staged")

        self._git_checkout_branch("feature")
        self._create_file("hello.txt")
        self._git_add_all()

        os.chdir("../../..")

    def _set_up_remote_ahead_behind(self) -> None:
        print("Setting up repo 'remote/not empty/ahead behind'")
        self._git_clone(TestCase._NON_EMPTY_REPO_URL, "remote/not empty/ahead behind")
        os.chdir("remote/not empty/ahead behind")

        self._git_reset_hard(3)
        self._create_file("hello.txt")
        self._git_add_all()
        self._git_commit("Add file")

        os.chdir("../../..")

    def _set_up_outside_files(self) -> None:
        print("Setting up outside files")
        os.makedirs("all-outside")
        self._create_file("all-outside/hello.txt")
        self._create_file("all-outside/general-kenobi.txt")
        self._create_file("outside.txt")
        os.makedirs("remote/all-outside")
        self._create_file("remote/all-outside/hello.txt")
        os.makedirs("remote/all-outside/nested-outside")
        self._create_file("remote/all-outside/nested-outside/general-kenobi.txt")
        os.makedirs("remote/empty-outside")
        self._create_file("remote/outside.txt")

    def _disable_outer_repo(self) -> None:
        outer_repo = pygit2.discover_repository(".")
        if outer_repo:
            print(f"Disabling the outer repo at '{outer_repo}'")
            ends_with_slash = outer_repo.endswith("/") or outer_repo.endswith("\\")
            self._old_repo_path = outer_repo[:-1] if ends_with_slash else outer_repo
            self._new_repo_path = self._old_repo_path + ".bak"
            os.rename(self._old_repo_path, self._new_repo_path)
        else:
            print("No outer repo found to disable")
            pass

    def _activate_outer_repo(self) -> None:
        if self._old_repo_path and self._new_repo_path:
            print(f"Re-activating the outer repo at '{self._new_repo_path}'")
            os.rename(self._new_repo_path, self._old_repo_path)
        else:
            print("No outer repo found to re-activate")
            pass

    def _do_one_time_setup(self) -> None:
        """
        Performs setup that only needs to be done once per test session (e.g., creating the test repos).

        This function assumes it starts in the root of the repository. If no exceptions are raised, it will return to that directory by the end.
        """
        TestCase._GITSUM_REPO_ROOT = os.getcwd()

        if os.path.exists("test/test-repos"):
            print("Skipping test repo creation: 'test/test-repos' already exists")
        else:
            self._set_up_directory_structure()

            self._set_up_untracked()
            self._set_up_deleted()
            self._set_up_modified()
            self._set_up_unmerged()
            self._set_up_remote_empty()
            self._set_up_remote_staged()
            self._set_up_remote_ahead_behind()

            self._set_up_outside_files()

        os.chdir(TestCase._GITSUM_REPO_ROOT)

        # Record the commit hash here so that it can be used to check the command output
        # This needs to be done whether or not the test repos already exist
        repo = pygit2.Repository("test/test-repos/modified")
        TestCase._modified_repo_commit_hash = repo.head.target.hex[:6]  # type: ignore

        # Clear previous coverage data
        self._run_shell_command(["coverage", "erase"], True)

    #endregion

    def run_gitsum(self, args: List[str], shell: bool = False) -> str:
        """
        If `shell` is `False`, runs `gitsum.py` and measures the test coverage.

        If `shell` is `True`, runs the platform-specific entry script (`gitsum` or `gitsum.bat`) in the shell without measuring its coverage.
        """
        slash = os.path.sep
        if shell:
            command = [f"..{slash}..{slash}gitsum"]
        else:
            gitsum_path = f"..{slash}..{slash}gitsum.py"
            command = ["coverage", "run", "--append", "--branch", "--data-file=../../.coverage", gitsum_path]
        return self._run_shell_command(command + args, shell=shell)

    def _make_assert_message(self, actual: str, expected: str) -> str:
        out = "\n" + ("~" * 31) + " OUTPUT " + ("~" * 31) + "\n"
        out += actual + "\n"

        out += ("~" * 30) + " EXPECTED " + ("~" * 30) + "\n"
        out += expected + "\n"
        out += ("~" * 70) + "\n"

        return out

    def assert_lines_equal(self, expected: str, actual: str) -> None:
        """
        Asserts that each line in each string is the same, ignoring trailing whitespace. Also adds a message with the expected and actual outputs.
        """
        diff = self._make_assert_message(actual, expected)

        result_lines = [line.rstrip() for line in actual.splitlines()]
        expected_lines = [line.rstrip() for line in expected.splitlines()]

        # Check number of lines
        self.assertEqual(len(expected_lines), len(result_lines), diff)

        # Check line contents
        for (expected, actual) in zip(expected_lines, result_lines):
            self.assertEqual(expected, actual, diff)

    def assert_gitsum_output(self, expected: str, actual: str) -> None:
        expected = expected.replace(TestCase.MODIFIED_REPO_COMMIT_HASH, TestCase._modified_repo_commit_hash)
        self.assert_lines_equal(expected, actual)

    def setUp(self) -> None:
        try:
            if not TestCase._one_time_setup_done:
                self._do_one_time_setup()
                TestCase._one_time_setup_done = True
            os.chdir("test/test-repos")
            self._disable_outer_repo()
        except:
            os.chdir(TestCase._GITSUM_REPO_ROOT)
            raise

    def tearDown(self) -> None:
        os.chdir(TestCase._GITSUM_REPO_ROOT)
        self._activate_outer_repo()
