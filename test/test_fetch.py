from inspect import cleandoc

from test.base_test_case import TestCase


class FetchTests(TestCase):
    def _set_up_repos(self) -> None:
        self._clone_empty_repo("test_fetch/remote/empty")
        self._clone_non_empty_repo("test_fetch/remote/not empty", make_fresh=True)
        self._clone_non_empty_repo("test_fetch/remote/copy for pushing", make_fresh=True)
        self._push_new_changes("test_fetch/remote/copy for pushing")
        self._create_repo_with_untracked_files("test_fetch/untracked")

    # TODO: Somehow, I need to undo the new commit pushed to the remote repo

    def test_fetch(self):
        expected = cleandoc(f"""
            Found 4 Git repositories.
               remote/copy for pushing        main
               remote/empty             [LB]  (no commits)
            !  remote/not empty               main            <1
            !  untracked                [LR]  (no commits)  *
        """)
        actual = self.run_gitsum(["--fetch"], working_dir="test_fetch")
        self.assert_lines_equal(expected, actual)
