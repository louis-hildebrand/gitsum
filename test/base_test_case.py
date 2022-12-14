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

    _working_dir = ""
    _setup_complete = False
    _old_repo_path = None
    _new_repo_path = None
    _modified_repo_commit_hash: str = MODIFIED_REPO_COMMIT_HASH

    def __init__(self, methodName: str):
        super(TestCase, self).__init__(methodName)
        self.maxDiff = 0

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
        repo.config["user.email"] = _GIT_USER_EMAIL  # type: ignore
        repo.config["user.name"] = _GIT_USER_NAME  # type: ignore

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
        sig = pygit2.Signature(_GIT_USER_NAME, _GIT_USER_EMAIL)  # type: ignore
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

    #region Setup helpers

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
        try:
            self._create_file("hello.txt")
            self._git_add_all()
            self._git_commit("Initial commit")

            self._delete_file("hello.txt")
        finally:
            os.chdir("..")

    def _set_up_modified(self) -> None:
        print("Setting up repo 'modified'")
        self._git_init("modified")
        os.chdir("modified")
        try:
            self._create_file("hello.txt")
            self._git_add_all()
            self._git_commit("Initial commit")

            self._create_file("general-kenobi.txt")
            self._git_add_all()
            self._git_commit("Create new file")

            self._git_checkout_detached(1)
            self._append_file("hello.txt", "Hello there!")
        finally:
            os.chdir("..")

    def _set_up_unmerged(self) -> None:
        print("Setting up repo 'unmerged'")
        self._git_init("unmerged", "main")
        os.chdir("unmerged")
        try:
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
        finally:
            os.chdir("..")

    def _set_up_remote_empty(self) -> None:
        print("Setting up repo 'remote/empty'")
        self._git_clone(self._EMPTY_REPO_URL, "remote/empty")

    def _set_up_remote_staged(self) -> None:
        print("Setting up repo 'remote/not empty/staged'")
        self._git_clone(self._NON_EMPTY_REPO_URL, "remote/not empty/staged")
        os.chdir("remote/not empty/staged")
        try:
            self._git_checkout_branch("feature")
            self._create_file("hello.txt")
            self._git_add_all()
        finally:
            os.chdir("../../..")

    def _set_up_remote_ahead_behind(self) -> None:
        print("Setting up repo 'remote/not empty/ahead behind'")
        self._git_clone(self._NON_EMPTY_REPO_URL, "remote/not empty/ahead behind")
        os.chdir("remote/not empty/ahead behind")
        try:
            self._git_reset_hard(3)
            self._create_file("hello.txt")
            self._git_add_all()
            self._git_commit("Add file")
        finally:
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

    def _activate_outer_repo(self) -> None:
        if _old_repo_path and _new_repo_path:
            #print(f"Re-activating the outer repo at '{_new_repo_path}'")
            os.rename(_new_repo_path, _old_repo_path)
        else:
            #print("No outer repo to re-activate")
            pass

    def _get_modified_repo_commit_hash(self) -> str:
        repo = pygit2.Repository("test/test-repos/modified")
        return repo.head.target.hex[:6]  # type: ignore

    def _shared_setup(self) -> None:
        # TODO: Clean out existing repos?
        # TODO: Check that user is running tests from the root of the repo?
        global _working_dir
        global modified_repo_commit_hash
        _working_dir = os.getcwd()

        if os.path.exists("test/test-repos"):
            print("Skipping setup: 'test/test-repos' already exists")
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

        os.chdir(_working_dir)

        self._modified_repo_commit_hash = self._get_modified_repo_commit_hash()

        self._run_shell_command(["coverage", "erase"], True)

        print()

    def _individual_setup(self) -> None:
        os.chdir("test/test-repos")
        self._disable_outer_repo()

    #endregion

    def run_gitsum(self, args: List[str], shell: bool = False) -> str:
        slash = os.path.sep
        if shell:
            gitsum_path = f"..{slash}..{slash}gitsum"
        else:
            gitsum_path = f"..{slash}..{slash}lib{slash}gitsum.py"
        coverage_command = ["coverage", "run", "--append", "--branch", "--data-file=../../.coverage"]
        return self._run_shell_command(coverage_command + [gitsum_path] + args, shell=shell)

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
        expected = expected.replace(self.MODIFIED_REPO_COMMIT_HASH, self._modified_repo_commit_hash)
        self.assert_lines_equal(expected, actual)

    def setUp(self) -> None:
        global _setup_complete
        try:
            if not self._setup_complete:
                self._shared_setup()
                _setup_complete = True
            self._individual_setup()
        except:
            os.chdir(_working_dir)
            raise

    def tearDown(self) -> None:
        os.chdir(_working_dir)
        self._activate_outer_repo()
