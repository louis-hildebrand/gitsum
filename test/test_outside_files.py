from test.base_test_case import TestCase
import test.base_test_case as base_test_case


_EXPECTED_FILES = """OUTSIDE: all-outside/
OUTSIDE: outside.txt
OUTSIDE: remote/all-outside/
OUTSIDE: remote/empty-outside/
OUTSIDE: remote/outside.txt"""

_EXPECTED_REPOS = """Found 7 Git repositories.
!  deleted                        [LR]  master        *
!  modified                       [LR]  (MODIFIED_REPO_COMMIT_HASH)      *
   remote/empty                   [LB]  (no commits)
!  remote/not empty/ahead behind        main            >1 <3
!  remote/not empty/staged              feature       *
!  unmerged                       [LR]  main          *
!  untracked                      [LR]  (no commits)  *"""

_EXPECTED_COMBINED = _EXPECTED_FILES + "\n" + _EXPECTED_REPOS


class OutsideFileTests(TestCase):
    def test_outside_files(self) -> None:
        result_str = base_test_case.run_gitsum(["--outside-files"])
        expected_output = _EXPECTED_COMBINED.replace("MODIFIED_REPO_COMMIT_HASH", base_test_case.modified_repo_commit_hash)
        self.assert_gitsum_output(expected_output, result_str)

    def test_only_outside_files(self) -> None:
        result_str = base_test_case.run_gitsum(["--only-outside-files"])
        expected_output = _EXPECTED_FILES.replace("MODIFIED_REPO_COMMIT_HASH", base_test_case.modified_repo_commit_hash)
        self.assert_gitsum_output(expected_output, result_str)
