from inspect import cleandoc

from test.base_test_case import TestCase


class NoArgsTests(TestCase):
    _EXPECTED_OUTPUT = cleandoc(f"""Found 7 Git repositories.
        !  deleted                        [LR]  master        *
        !  modified                       [LR]  ({TestCase.MODIFIED_REPO_COMMIT_HASH})      *
           remote/empty                   [LB]  (no commits)
        !  remote/not empty/ahead behind        main            >1 <3
        !  remote/not empty/staged              feature       *
        !  unmerged                       [LR]  main          *
        !  untracked                      [LR]  (no commits)  *"""
    )

    def test_no_args(self):
        result_str = self.run_gitsum([])
        self.assert_gitsum_output(self._EXPECTED_OUTPUT, result_str)
