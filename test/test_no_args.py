from inspect import cleandoc

from test.base_test_case import TestCase


class NoArgsTests(TestCase):
    def test_no_args(self):
        expected = cleandoc(f"""Found 7 Git repositories.
            !  deleted                        [LR]  master        *
            !  modified                       [LR]  ({TestCase.MODIFIED_REPO_COMMIT_HASH})      *
               remote/empty                   [LB]  (no commits)
            !  remote/not empty/ahead behind        main            >1 <3
            !  remote/not empty/staged              feature       *
            !  unmerged                       [LR]  main          *
            !  untracked                      [LR]  (no commits)  *"""
        )
        actual = self.run_gitsum([])
        self.assert_gitsum_output(expected, actual)

    def test_no_repos(self):
        expected = "Found 0 Git repositories."
        actual = self.run_gitsum([], working_dir="all-outside")
        self.assert_gitsum_output(expected, actual)

    def test_inside_repo(self):
        expected = cleandoc("""Found 1 Git repository.
            !  .  [LR]  master  *"""
        )
        actual = self.run_gitsum([], working_dir="deleted")
        self.assert_gitsum_output(expected, actual)
