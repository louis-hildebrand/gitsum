from pathlib import Path
from typing import Any, List
import os
import pygit2  # type: ignore
import shutil
import stat
import subprocess
import unittest
import uuid


class TestCase(unittest.TestCase):
    MODIFIED_REPO_COMMIT_HASH = "MODIFIED_REPO_COMMIT_HASH"

    _EMPTY_REPO_URL = "https://louis-hildebrand@github.com/louis-hildebrand/empty.git"
    _NON_EMPTY_REPO_URL = "https://louis-hildebrand@github.com/louis-hildebrand/test.git"
    _GIT_USER_EMAIL = "gitsum tester"
    _GIT_USER_NAME = "gitsum tester"
    _GITSUM_REPO_ROOT = os.getcwd()

    _coverage_erased = False

    def __init__(self, methodName: str):
        super().__init__(methodName)
        self.maxDiff = 0
        self._old_repo_path = ""
        self._new_repo_path = ""
        self._changes_pushed = ""

    #region Shell commands

    def _run_shell_command(self, args: List[str], ignore_error: bool = False, shell: bool = False, working_dir: str = ".") -> str:
        if shell:
            args_str = " ".join(args)
            result = subprocess.run(args_str, capture_output=True, shell=True, cwd=working_dir)
        else:
            result = subprocess.run(args, capture_output=True, cwd=working_dir)
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

    def _git_push(self, force: bool = False) -> None:
        '''
        git push origin HEAD [--force]
        '''
        args = ["git", "push", "origin", "HEAD"]
        if force:
            args += ["--force"]
        self._run_shell_command(args)

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

    def _delete_all(self, dir: str) -> None:
        def handle_error(func: Any, path: str, info: Any) -> None:
            os.chmod(path, stat.S_IWRITE)
            os.unlink(path)
        shutil.rmtree(dir, onerror=handle_error)

    #endregion

    #region Helpers for setup

    def _create_repo_with_deleted_file(self, dir: str) -> None:
        if os.path.isdir(dir):
            print(f"Repo '{dir}' already exists")
            return
        print(f"Setting up repo '{dir}'")
        starting_dir = os.getcwd()
        os.makedirs(dir)
        self._git_init(dir, "master")
        os.chdir(dir)
        self._create_file("hello.txt")
        self._git_add_all()
        self._git_commit("Initial commit")
        self._delete_file("hello.txt")
        os.chdir(starting_dir)

    def _create_repo_with_modified_file(self, dir: str) -> None:
        if os.path.isdir(dir):
            print(f"Repo '{dir}' already exists")
            return
        print(f"Setting up repo '{dir}'")
        starting_dir = os.getcwd()
        os.makedirs(dir)
        self._git_init(dir)
        os.chdir(dir)
        self._create_file("hello.txt")
        self._git_add_all()
        self._git_commit("Initial commit")
        self._create_file("general-kenobi.txt")
        self._git_add_all()
        self._git_commit("Create new file")
        self._git_checkout_detached(1)
        self._append_file("hello.txt", "Hello there!")
        os.chdir(starting_dir)

    def _clone_empty_repo(self, dir: str) -> None:
        if os.path.isdir(dir):
            print(f"Repo '{dir}' already exists")
            return
        print(f"Cloning empty repo into '{dir}'")
        os.makedirs(dir)
        self._git_clone(TestCase._EMPTY_REPO_URL, dir)

    def _clone_non_empty_repo(self, dir: str, make_fresh: bool = False) -> None:
        already_exists = os.path.isdir(dir)
        if already_exists and not make_fresh:
            print(f"Repo '{dir}' already exists")
            return
        elif already_exists and make_fresh:
            self._delete_all(dir)
        print(f"Cloning empty repo into '{dir}'")
        os.makedirs(dir)
        self._git_clone(TestCase._NON_EMPTY_REPO_URL, dir)

    def _clone_repo_ahead_behind(self, dir: str) -> None:
        if os.path.isdir(dir):
            print(f"Repo '{dir}' already exists")
            return
        print(f"Cloning non-empty repo into '{dir}'")
        starting_dir = os.getcwd()
        os.makedirs(dir)
        self._git_clone(TestCase._NON_EMPTY_REPO_URL, dir)
        os.chdir(dir)
        self._git_reset_hard(3)
        self._create_file("hello.txt")
        self._git_add_all()
        self._git_commit("Add file locally")
        os.chdir(starting_dir)

    def _clone_repo_with_staged_changes(self, dir: str) -> None:
        if os.path.isdir(dir):
            print(f"Repo '{dir}' already exists")
            return
        print(f"Setting up repo '{dir}'")
        starting_dir = os.getcwd()
        os.makedirs(dir)
        self._git_clone(TestCase._NON_EMPTY_REPO_URL, dir)
        os.chdir(dir)
        self._git_checkout_branch("feature")
        self._create_file("hello.txt")
        self._git_add_all()
        os.chdir(starting_dir)

    def _create_repo_with_merge_conflicts(self, dir: str) -> None:
        if os.path.isdir(dir):
            print(f"Repo '{dir}' already exists")
            return
        print(f"Setting up repo '{dir}'")
        starting_dir = os.getcwd()
        os.makedirs(dir)
        self._git_init(dir, "main")
        os.chdir(dir)
        # Initial commit
        self._create_file("hello.txt")
        self._append_file("hello.txt", "Hello there!")
        self._git_add_all()
        self._git_commit("Initial commit")
        # Change on feature branch
        self._git_checkout_branch("feature", new=True)
        self._overwrite_file("hello.txt", "General Kenobi!")
        self._git_add_all()
        self._git_commit("Create feature branch")
        # Change on main branch
        self._git_checkout_branch("main")
        self._overwrite_file("hello.txt", "Come here, my little friend.")
        self._git_add_all()
        self._git_commit("Extend main branch")
        # Conflict
        self._git_merge("feature")
        os.chdir(starting_dir)

    def _create_repo_with_untracked_files(self, dir: str) -> None:
        if os.path.isdir(dir):
            print(f"Repo '{dir}' already exists")
            return
        print(f"Setting up repo '{dir}'")
        self._git_init(dir)
        self._create_file(os.path.join(dir, "hello.txt"))

    def _push_new_changes(self, dir: str) -> None:
        print(f"Pushing new changes from '{dir}'")
        starting_dir = os.getcwd()
        os.chdir(dir)
        filename = f"{uuid.uuid4()}.txt"
        self._create_file(filename)
        self._git_add_all()
        self._git_commit("New test commit")
        self._git_push()
        os.chdir(starting_dir)
        self._changes_pushed = dir

    def _undo_changes_in_remote(self) -> None:
        dir = self._changes_pushed
        if not dir:
            return
        print(f"Undoing changes in '{dir}'")
        starting_dir = os.getcwd()
        os.chdir(dir)
        self._git_reset_hard(1)
        self._git_push(force=True)
        os.chdir(starting_dir)
        self._changes_pushed = ""

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

    #endregion

    def run_gitsum(self, args: List[str], shell: bool = False, working_dir: str = ".") -> str:
        """
        If `shell` is `False`, runs `gitsum.py` and measures the test coverage.

        If `shell` is `True`, runs the platform-specific entry script (`gitsum` or `gitsum.bat`) in the shell without measuring its coverage.
        """
        root_path = Path(TestCase._GITSUM_REPO_ROOT)

        if shell:
            command = [str(root_path.joinpath("gitsum").absolute())]
        else:
            gitsum_path = str(root_path.joinpath("gitsum.py").absolute())
            coverage_path = str(root_path.joinpath(".coverage").absolute())
            command = ["coverage", "run", "--append", "--branch", f"--data-file={coverage_path}", gitsum_path]
        return self._run_shell_command(command + args, shell=shell, working_dir=working_dir)

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

    def _set_up_repos(self) -> None:
        """
        Override this method to set up the necessary repositories for your tests.
        """
        pass

    def setUp(self):
        """
        Moves to the test/test-repos directory, creates the required test repos, and disables the gitsum repo.
        """
        os.chdir(TestCase._GITSUM_REPO_ROOT)
        if not os.path.isdir("test/test-repos"):
            os.makedirs("test/test-repos")
        os.chdir("test/test-repos")
        try:
            self._set_up_repos()

            self._disable_outer_repo()
        except:
            self.tearDown()
            raise
        # Erase coverage data if this is the start of the test run
        if not TestCase._coverage_erased:
            self._run_shell_command(["coverage", "erase"])
            TestCase._coverage_erased = True

    def tearDown(self):
        """
        Moves back to the root of the gitsum repo and re-activates the gitsum repo.
        """
        self._activate_outer_repo()
        self._undo_changes_in_remote()
