import subprocess
import unittest

import test.common as common


class BaseTestCase(unittest.TestCase):
    # Ignore blank lines in the output (for some reason there are a lot of blank lines in GitHub Actions)
    ALLOW_BLANK_LINES = True

    def _display_tree(self) -> None:
        result = subprocess.run(["tree", "/f", "/a"], capture_output=True, shell=True)
        result.check_returncode()
        print(result.stdout.decode(encoding="utf-8"))

    def __init__(self, methodName: str):
        super(BaseTestCase, self).__init__(methodName)
        self.maxDiff = 0
        self._display_tree()

    def assert_gitsum_output(self, expected: str, actual: str) -> None:
        diff = common.actual_expected(actual, expected)

        result_lines = [line.rstrip() for line in actual.splitlines()]
        expected_lines = [line.rstrip() for line in expected.splitlines()]

        if self.ALLOW_BLANK_LINES:
            result_lines = [x for x in result_lines if x]

        # Check number of lines
        self.assertEqual(len(expected_lines), len(result_lines), diff)

        # Check line contents
        for (expected, actual) in zip(expected_lines, result_lines):
            self.assertEqual(expected, actual, diff)
