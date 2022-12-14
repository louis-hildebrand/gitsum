from inspect import cleandoc

from test.base_test_case import TestCase


class OutsideFileTests(TestCase):
    _EXPECTED_FILES = cleandoc("""
        OUTSIDE: all-outside/
        OUTSIDE: outside.txt
        OUTSIDE: remote/all-outside/
        OUTSIDE: remote/empty-outside/
        OUTSIDE: remote/outside.txt"""
    )

    _EXPECTED_REPOS = cleandoc(f"""
        Found 7 Git repositories.
        !  deleted                        [LR]  master        *
        !  modified                       [LR]  ({TestCase.MODIFIED_REPO_COMMIT_HASH})      *
           remote/empty                   [LB]  (no commits)
        !  remote/not empty/ahead behind        main            >1 <3
        !  remote/not empty/staged              feature       *
        !  unmerged                       [LR]  main          *
        !  untracked                      [LR]  (no commits)  *"""
    )

    _EXPECTED_COMBINED = _EXPECTED_FILES + "\n" + _EXPECTED_REPOS

    def test_outside_files(self) -> None:
        result_str = self.run_gitsum(["--outside-files"])
        self.assert_gitsum_output(self._EXPECTED_COMBINED, result_str)

    def test_only_outside_files(self) -> None:
        result_str = self.run_gitsum(["--only-outside-files"])
        self.assert_gitsum_output(self._EXPECTED_FILES, result_str)
