"""
Simple test case to check that the platform-specific entry scripts (gitsum and gitsum.bat) are working.
"""
from inspect import cleandoc

from test.base_test_case import TestCase


class HelpTests(TestCase):
    _EXPECTED_HELP_MSG = cleandoc("""
        usage: gitsum [-h] [-f] [-o] [-O]

        View a summary of statuses for multiple Git repositories.

        optional arguments:
          -h, --help            show this help message and exit
          -f, --fetch           fetch before getting status
          -o, --outside-files   list files and directories that are not inside a Git
                                repository
          -O, --only-outside-files
                                list files and directories that are not inside a Git
                                repository and exit"""
    )

    def test_help(self):
        result = self.run_gitsum(["--help"], shell=True)
        self.assert_lines_equal(self._EXPECTED_HELP_MSG, result)
