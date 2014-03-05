import unittest
from collections import defaultdict
from geekcms import protocal


class ManagerTest(unittest.TestCase):

    def setUp(self):
        class TestClass:
            def __init__(self, owner):
                self.owner = owner

        self.TestClass = TestClass
        self.owner = 'testowner'
        self.manager = protocal.Manager(TestClass)

    def test_create(self):
        item = self.manager.create(self.owner)
        self.assertEqual(item.owner, self.owner)
        self.assertIsInstance(item, self.TestClass)

    def test_add_remove(self):
        item = self.TestClass(self.owner)
        self.assertEqual(self.manager._container, defaultdict(list))

        self.manager.add(item)
        self.assertDictEqual(
            self.manager._container,
            {self.owner: [item]},
        )

        self.manager.remove(item)
        self.assertEqual(self.manager._container, defaultdict(list))

    def test_filter_keys(self):
        owner_1 = 'owner_1'
        owner_2 = 'owner_2'
        item_1 = self.manager.create(owner_1)
        item_2 = self.manager.create(owner_2)

        self.assertListEqual(self.manager.filter(owner_1), [item_1])
        self.assertListEqual(self.manager.filter(owner_2), [item_2])
        self.assertSetEqual(
            set(self.manager.keys()),
            {owner_1, owner_2},
        )


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

    def test_manager(self):
        owner = 'testowner'
        manager = self.TestClass.get_manager_with_fixed_owner(owner)
        item = manager.create()
        self.assertEqual(item.owner, owner)
        self.assertIsInstance(item, self.TestClass)


if __name__ == '__main__':
    unittest.main()
