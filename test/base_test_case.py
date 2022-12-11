import unittest

import test.common as common


class BaseTestCase(unittest.TestCase):
    # Ignore blank lines in the output (for some reason there are a lot of blank lines in GitHub Actions)
    # TODO: Is this really necessary?
    ALLOW_BLANK_LINES = True

    def __init__(self, methodName: str):
        super(BaseTestCase, self).__init__(methodName)
        self.maxDiff = 0

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
