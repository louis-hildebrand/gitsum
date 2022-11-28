from test.base_test_case import BaseTestCase
import test.common as common


_EXPECTED_OUTPUT = """Found 7 Git repositories.
!  deleted                        [LR]  master        *
!  modified                       [LR]  (MODIFIED_REPO_COMMIT_HASH)      *
   remote/empty                   [LB]  (no commits)
!  remote/not empty/ahead behind        main            >1 <3
!  remote/not empty/staged              feature       *
!  unmerged                       [LR]  main          *
!  untracked                      [LR]  (no commits)  *"""


class NoArgsTests(BaseTestCase):
    def _do_test_no_args(self):
        result_str = common.run_gitsum([])

        expected_output = _EXPECTED_OUTPUT.replace("MODIFIED_REPO_COMMIT_HASH", common.MODIFIED_REPO_COMMIT_HASH)

        print(common.actual_expected(result_str, expected_output))

        result_lines = [line.rstrip() for line in result_str.splitlines()]
        expected_lines = [line.rstrip() for line in expected_output.splitlines()]

        # Check number of lines
        self.assertEqual(len(expected_lines), len(result_lines))

        # Check line contents
        for (expected, actual) in zip(expected_lines, result_lines):
            self.assertEqual(expected, actual)

    def test_no_args(self) -> None:
        common.run_test(self._do_test_no_args)
