from test.base_test_case import BaseTestCase
import test.common as common


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


class OutsideFileTests(BaseTestCase):
    def _do_test_outside_files(self) -> None:
        result_str = common.run_gitsum(["--outside-files"])

        expected_output = _EXPECTED_COMBINED.replace("MODIFIED_REPO_COMMIT_HASH", common.modified_repo_commit_hash)

        actual_expected = common.actual_expected(result_str, expected_output)

        result_lines = [line.rstrip() for line in result_str.splitlines()]
        expected_lines = [line.rstrip() for line in expected_output.splitlines()]

        # Check number of lines
        self.assertEqual(len(expected_lines), len(result_lines), actual_expected)

        # Check line contents
        for (expected, actual) in zip(expected_lines, result_lines):
            self.assertEqual(expected, actual, actual_expected)

    def test_outside_files(self) -> None:
        common.run_test(self._do_test_outside_files)

    def _do_test_only_outside_files(self) -> None:
        result_str = common.run_gitsum(["--only-outside-files"])

        expected_output = _EXPECTED_FILES.replace("MODIFIED_REPO_COMMIT_HASH", common.modified_repo_commit_hash)

        actual_expected = common.actual_expected(result_str, expected_output)

        result_lines = [line.rstrip() for line in result_str.splitlines()]
        expected_lines = [line.rstrip() for line in expected_output.splitlines()]

        # Check number of lines
        self.assertEqual(len(expected_lines), len(result_lines), actual_expected)

        # Check line contents
        for (expected, actual) in zip(expected_lines, result_lines):
            self.assertEqual(expected, actual, actual_expected)

    def test_only_outside_files(self) -> None:
        common.run_test(self._do_test_only_outside_files)
