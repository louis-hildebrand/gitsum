from inspect import cleandoc
import os
import pygit2  # type: ignore

from test.base_test_case import TestCase


class NoArgsTests(TestCase):
    def __init__(self, methodName: str):
        super().__init__(methodName)
        self._modified_repo_commit_hash: str

    def _set_up_repos(self) -> None:
        self._create_repo_with_deleted_file("test_no_args/deleted")
        self._create_repo_with_modified_file("test_no_args/modified")
        self._clone_empty_repo("test_no_args/remote/empty")
        os.makedirs("test_no_args/remote/empty/subfolder", exist_ok=True)
        self._clone_repo_ahead_behind("test_no_args/remote/not empty/ahead behind")
        self._clone_repo_with_staged_changes("test_no_args/remote/not empty/staged")
        self._create_repo_with_merge_conflicts("test_no_args/unmerged")
        self._create_repo_with_untracked_files("test_no_args/untracked")
        os.makedirs("test_no_args/not a repo", exist_ok=True)

        # Get modified repo commit hash
        repo = pygit2.Repository("test_no_args/modified")
        self._modified_repo_commit_hash = repo.head.target.hex[:6]  # type: ignore

    def test_no_args(self):
        expected = cleandoc(f"""
            Found 7 Git repositories.
            !  deleted                        master        *  local repo
            !  modified                       ({self._modified_repo_commit_hash})      *  local repo
               remote/empty                   (no commits)     local branch
            !  remote/not empty/ahead behind  main             >1 <3
            !  remote/not empty/staged        feature       *
            !  unmerged                       main          *  local repo
            !  untracked                      (no commits)  *  local repo
        """)
        actual = self.run_gitsum([], working_dir="test_no_args")
        self.assert_lines_equal(expected, actual)

    def test_no_repos(self):
        expected = "Found 0 Git repositories."
        actual = self.run_gitsum([], working_dir="test_no_args/not a repo")
        self.assert_lines_equal(expected, actual)

    def test_inside_repo_root(self):
        expected = cleandoc("""
            Found 1 Git repository.
            !  ../deleted  master  *  local repo
        """)
        actual = self.run_gitsum([], working_dir="test_no_args/deleted")
        self.assert_lines_equal(expected, actual)

    def test_inside_repo_subfolder(self):
        expected = cleandoc("""
            Found 1 Git repository.
            !  ../../empty  (no commits)     local branch
        """)
        actual = self.run_gitsum([], working_dir="test_no_args/remote/empty/subfolder")
        self.assert_lines_equal(expected, actual)
