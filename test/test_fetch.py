from inspect import cleandoc

from test.base_test_case import TestCase


class FetchTests(TestCase):
    def _set_up_repos(self) -> None:
        self._clone_empty_repo("test_fetch/remote/empty")
        self._clone_non_empty_repo("test_fetch/remote/not empty", make_fresh=True)
        self._make_changes_in_remote("test_fetch/remote/not empty")
        self._create_repo_with_untracked_files("test_fetch/untracked")

    def test_fetch(self):
        expected = cleandoc(f"""
            Found 3 Git repositories.
               remote/empty      [LB]  (no commits)
            !  remote/not empty        main               <4
            !  untracked         [LR]  (no commits)  *
        """)
        actual = self.run_gitsum(["--fetch"], working_dir="test_fetch")
        self.assert_lines_equal(expected, actual)
