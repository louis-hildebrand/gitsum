from test.base_test_case import TestCase
import test.base_test_case as base_test_case


_EXPECTED_OUTPUT = """Found 7 Git repositories.
!  deleted                        [LR]  master        *
!  modified                       [LR]  (MODIFIED_REPO_COMMIT_HASH)      *
   remote/empty                   [LB]  (no commits)
!  remote/not empty/ahead behind        main            >1 <3
!  remote/not empty/staged              feature       *
!  unmerged                       [LR]  main          *
!  untracked                      [LR]  (no commits)  *"""


class NoArgsTests(TestCase):
    def test_no_args(self):
        result_str = base_test_case.run_gitsum([])
        expected_output = _EXPECTED_OUTPUT.replace("MODIFIED_REPO_COMMIT_HASH", base_test_case.modified_repo_commit_hash)
        self.assert_gitsum_output(expected_output, result_str)
