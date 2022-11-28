import unittest


class BaseTestCase(unittest.TestCase):
    def __init__(self, methodName: str):
        self.maxDiff = 0
        super(BaseTestCase, self).__init__(methodName)
