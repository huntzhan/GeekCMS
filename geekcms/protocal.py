from collections import defaultdict
from collections import UserDict
from functools import partial
from functools import wraps
from inspect import signature


_THEME = 'theme'
_PLUGIN = 'plugin'
_PLUGIN_RUN_METHOD_NAME = 'run'
_OWNER = 'owner'


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


class _ManagerProxyWithOwner:

    def __init__(self, owner, manager):

        for method_name in dir(manager):
            if method_name.startswith('_'):
                continue
            method = getattr(manager, method_name)
            sig = signature(method)
            if _OWNER in sig.parameters:
                partial_method = partial(method, owner=owner)
            else:
                partial_method = method
            setattr(self, method_name, partial_method)


class _SetUpObjectManager(type):

    def __new__(cls, *args, **kwargs):
        result_cls = type.__new__(cls, *args, **kwargs)
        # set up manager.
        result_cls.objects = _Manager(result_cls)
        return result_cls


class _Base(metaclass=_SetUpObjectManager):

    def __init__(self, owner, *args, **kwargs):
        text = 'In Base Class: owner: {}, *args: {}; **kwargs: {}'
        raise Exception(
            text.format(owner, args, kwargs),
        )

    @classmethod
    def get_manager_with_fixed_owner(cls, owner):
        return _ManagerProxyWithOwner(owner, cls.objects)


class Resource(_Base):
    pass


class Product(_Base):
    pass


class Message(_Base):
    pass


class _UniqueKeyDict(UserDict):

    def __setitem__(self, key, val):
        if key in self:
            raise Exception('Key Already Existed!.')
        super().__setitem__(key, val)


class _PluginIndex:

    def __init__(self, theme_name, plugin_name):
        self.theme_name = theme_name
        self.plugin_name = plugin_name
        self.unique_key = '{}.{}'.format(theme_name, plugin_name)

    def __hash__(self):
        return self.unique_key.__hash__()

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return '_PluginIndex({}, {})'.format(
            self.theme_name,
            self.plugin_name,
        )


class _SetUpPlugin(type):

    plugin_mapping = _UniqueKeyDict()

    @classmethod
    def _find_case_insensitive_name(cls, target_name, namespace):
        for name, val in namespace.items():
            if name.lower() == target_name:
                return name
        else:
            raise Exception(
                'Can Not Find {}.'.format(target_name),
            )

    @classmethod
    def _register_plugin(cls, theme_name, plugin_name, plugin_cls):
        plugin_index = _PluginIndex(theme_name, plugin_name)
        cls.plugin_name[plugin_index.unique_key] = plugin_cls

    @classmethod
    def _data_filter(cls, func=None, owner=''):
        if func is None:
            return partial(cls._data_filter, owner=owner)

        # begin decorating
        @wraps(func)
        def run(self, data, *args, **kwargs):
            processed_data = [item for item in data if data.owner == owner]
            return func(self, processed_data, *args, **kwargs)
        return run

    def __new__(cls, cls_name, bases, namespace, **kargs):
        # find theme_name and plugin_name
        theme_name = cls._find_case_insensitive_name(_THEME, namespace)
        plugin_name = cls._find_case_insensitive_name(_PLUGIN, namespace)
        plugin_cls = type.__new__(cls, cls_name, bases, namespace, **kargs)
        cls._register_plugin(theme_name, plugin_name, plugin_cls)
        # filter data for run method.
        process_func = getattr(plugin_cls, _PLUGIN_RUN_METHOD_NAME)
        setattr(
            plugin_cls,
            _PLUGIN_RUN_METHOD_NAME,
            cls._data_filter(owner=theme_name)(process_func),
        )
