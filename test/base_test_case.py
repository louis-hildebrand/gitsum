import subprocess
import unittest


class BaseTestCase(unittest.TestCase):
    def _display_tree(self) -> None:
        result = subprocess.run(["tree", "/f", "/a"], capture_output=True, shell=True)
        result.check_returncode()
        print(result.stdout.decode(encoding="utf-8"))

    def __init__(self, methodName: str):
        super(BaseTestCase, self).__init__(methodName)
        self.maxDiff = 0
        self._display_tree()
