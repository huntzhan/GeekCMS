import unittest
from geekcms import protocal


class _BaseAssetTest(unittest.TestCase):

    def setUp(self):
        class TestClass(protocal._BaseAsset):
            def __init__(self, owner):
                self.owner = owner

        self.TestClass = TestClass

    def test_init(self):
        owner = 'testowner'
        attr = 'testattr'

        item = self.TestClass(owner)
        self.assertEqual(item.owner, owner)

        item.attr = attr
        self.assertEqual(item.attr, attr)

        self.assertIsInstance(item, self.TestClass)


if __name__ == '__main__':
    unittest.main()
