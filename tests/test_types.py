import unittest
import protoconf

class TestTypes(unittest.TestCase):

    def test_test(self):
        self.assertTrue(protoconf.valid())
