import unittest

import test.common as common


class BaseTestCase(unittest.TestCase):
    def __init__(self, methodName: str):
        super(BaseTestCase, self).__init__(methodName)
        self.maxDiff = 0

    def assert_gitsum_output(self, expected: str, actual: str) -> None:
        diff = common.actual_expected(actual, expected)

        result_lines = [line.rstrip() for line in actual.splitlines()]
        expected_lines = [line.rstrip() for line in expected.splitlines()]

        # Check number of lines
        self.assertEqual(len(expected_lines), len(result_lines), diff)

        # Check line contents
        for (expected, actual) in zip(expected_lines, result_lines):
            self.assertEqual(expected, actual, diff)
