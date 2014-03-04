from collections import defaultdict


class _Manager:

    def __init__(self, target_cls):
        self._target_cls = target_cls
        self._container = defaultdict(list)

    def create(self, owner, *args, **kwargs):
        new_item = self._target_cls(owner, *args, **kwargs)
        self.add(new_item)
        return new_item

    def add(self, target):
        self._container[target.owner].append(target)

    def remove(self, target):
        self._container[target.owner].remove(target)

    def filter(self, owner):
        return self._container[owner]


class _SetUpObjectManager(type):

    def __new__(cls, *args, **kwargs):
        result_cls = type.__new__(cls, *args, **kwargs)
        # set up manager.
        result_cls.objects = _Manager(result_cls)
        return result_cls


class _Base(metaclass=_SetUpObjectManager):

    def __init__(self, owner, *args, **kwargs):
        text = 'In Base Class: *args: {}, {}; **kwargs: {}'
        raise Exception(
            text.format(owner, args, kwargs),
        )


class Resource(_Base):
    pass


class Product(_Base):
    pass


class Message(_Base):
    pass
