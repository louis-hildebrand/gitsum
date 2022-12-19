from inspect import cleandoc
import os

from test.base_test_case import TestCase


class OutsideFileTests(TestCase):
    def _set_up_repos(self) -> None:
        self._create_repo_with_deleted_file("test_outside_files/deleted")
        self._create_repo_with_untracked_files("test_outside_files/foo/untracked")

        os.makedirs("test_outside_files/all-outside", exist_ok=True)
        self._create_file("test_outside_files/all-outside/hello.txt")
        self._create_file("test_outside_files/all-outside/general-kenobi.txt")
        self._create_file("test_outside_files/outside.txt")
        os.makedirs("test_outside_files/foo/all-outside", exist_ok=True)
        self._create_file("test_outside_files/foo/all-outside/hello.txt")
        os.makedirs("test_outside_files/foo/all-outside/nested-outside", exist_ok=True)
        self._create_file("test_outside_files/foo/all-outside/nested-outside/general-kenobi.txt")
        os.makedirs("test_outside_files/foo/empty-outside", exist_ok=True)
        self._create_file("test_outside_files/foo/outside.txt")

    _EXPECTED_FILES = cleandoc("""
        OUTSIDE: all-outside/
        OUTSIDE: foo/all-outside/
        OUTSIDE: foo/empty-outside/
        OUTSIDE: foo/outside.txt
        OUTSIDE: outside.txt
    """)

    _EXPECTED_REPOS = cleandoc("""
        Found 2 Git repositories.
        !  deleted        master        *  local repo
        !  foo/untracked  (no commits)  *  local repo
    """)

    _EXPECTED_COMBINED = _EXPECTED_FILES + "\n" + _EXPECTED_REPOS

    def test_outside_files(self) -> None:
        actual = self.run_gitsum(["--outside-files"], working_dir="test_outside_files")
        self.assert_lines_equal(self._EXPECTED_COMBINED, actual)

    def test_only_outside_files(self) -> None:
        actual = self.run_gitsum(["--only-outside-files"], working_dir="test_outside_files")
        self.assert_lines_equal(self._EXPECTED_FILES, actual)

    def test_no_outside_files(self) -> None:
        actual = self.run_gitsum(["--only-outside-files"], working_dir="test_outside_files/deleted")
        self.assertEqual("", actual)
