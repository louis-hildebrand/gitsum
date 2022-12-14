"""
Simple test case to check that the platform-specific entry scripts (gitsum and gitsum.bat) are working.
"""
import os

from test.base_test_case import BaseTestCase
import test.common as common


_EXPECTED_HELP_MSG = """usage: gitsum [-h] [-f] [-o] [-O]

View a summary of statuses for multiple Git repositories.

optional arguments:
  -h, --help            show this help message and exit
  -f, --fetch           fetch before getting status
  -o, --outside-files   list files and directories that are not inside a Git
                        repository
  -O, --only-outside-files
                        list files and directories that are not inside a Git
                        repository and exit"""


class HelpTests(BaseTestCase):
    def _do_test_help(self):
        sep = os.path.sep
        result = common.run_shell_command([f"..{sep}..{sep}gitsum", "--help"], shell=True)
        self.assert_gitsum_output(_EXPECTED_HELP_MSG, result)

    def test_help(self):
        common.run_test(self._do_test_help)
