from test.base_test_case import BaseTestCase
import subprocess


class SetupTests(BaseTestCase):
    """
    Empty test case to check that setup works. This should only fail if there is a setup issue.
    """
    def _display_tree(self) -> None:
        result = subprocess.run(["tree", "/f", "/a"], capture_output=True, shell=True)
        result.check_returncode()
        print(result.stdout.decode(encoding="utf-8"))

    def test_setup(self) -> None:
        self._display_tree()
