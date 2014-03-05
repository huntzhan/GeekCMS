from collections import defaultdict
from collections import UserDict
from functools import partial
from functools import wraps
from inspect import signature


_THEME = 'theme'
_PLUGIN = 'plugin'
_PLUGIN_RUN_METHOD_NAME = 'run'


class _UniqueKeyDict(UserDict):

    def __setitem__(self, key, val):
        if key in self:
            raise Exception('Key Already Existed!.')
        super().__setitem__(key, val)


class PluginIndex:

    def __init__(self, theme_name, plugin_name):
        self.theme_name = theme_name
        self.plugin_name = plugin_name
        self.unique_key = '{}.{}'.format(theme_name, plugin_name)

    def __hash__(self):
        return self.unique_key.__hash__()

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return 'PluginIndex({}, {})'.format(
            self.theme_name,
            self.plugin_name,
        )


class Manager:

    def __init__(self, target_cls):
        self._target_cls = target_cls
        self._container = defaultdict(list)

    def __get__(self, instance, cls):
        if instance:
            raise Exception('Manager Can Not Be Called From Instances')
        return self

    def __set__(self, instance, val):
        raise Exception('Manager Can Not Be Replaced.')

    def __delete__(self, instance):
        raise Exception('Manager Can Not Be Deleted.')

    def create(self, owner, *args, **kwargs):
        new_item = self._target_cls(owner, *args, **kwargs)
        self.add(new_item)
        return new_item

    def add(self, target):
        self._container[target.owner].append(target)

    def remove(self, target):
        self._container[target.owner].remove(target)
        if not self._container[target.owner]:
            del self._container[target.owner]

    def filter(self, owner):
        return self._container[owner]

    def keys(self):
        return list(self._container)


class ManagerProxyWithOwner:

    def __init__(self, owner, manager):

        for method_name in dir(manager):
            if method_name.startswith('_'):
                continue
            method = getattr(manager, method_name)
            sig = signature(method)
            if 'owner' in sig.parameters:
                partial_method = partial(method, owner=owner)
            else:
                partial_method = method
            setattr(self, method_name, partial_method)


class SetUpObjectManager(type):

    def __new__(cls, *args, **kwargs):
        result_cls = super().__new__(cls, *args, **kwargs)
        # set up manager.
        result_cls.objects = Manager(result_cls)
        return result_cls


class _BaseAsset(metaclass=SetUpObjectManager):

    def __init__(self, owner, *args, **kwargs):
        text = 'In Base Class: owner: {}, *args: {}; **kwargs: {}'
        raise Exception(
            text.format(owner, args, kwargs),
        )

    @classmethod
    def get_manager_with_fixed_owner(cls, owner):
        return ManagerProxyWithOwner(owner, cls.objects)


class BaseResource(_BaseAsset):
    pass


class BaseProduct(_BaseAsset):
    pass


class BaseMessage(_BaseAsset):
    pass


class SetUpPlugin(type):

    plugin_mapping = _UniqueKeyDict()

    @classmethod
    def _find_case_insensitive_name(cls, target_name, namespace):
        for name, val in namespace.items():
            if name.lower() == target_name:
                return val
        else:
            raise Exception(
                'Can Not Find {}.'.format(target_name),
            )

    @classmethod
    def _register_plugin(cls, theme_name, plugin_name, plugin_cls):
        plugin_index = PluginIndex(theme_name, plugin_name)
        cls.plugin_name[plugin_index.unique_key] = plugin_cls

    @classmethod
    def _data_filter(cls, func=None, owner=''):
        if func is None:
            return partial(cls._data_filter, owner=owner)

        # begin decorating
        def check_owner(owner):
            check_func = lambda item: item.owner == owner
            return check_func

        @wraps(func)
        def run(self, assets, messages, *args, **kwargs):
            check_func = check_owner(owner)
            processed_assets = filter(check_func, assets)
            processed_messages = filter(check_func, messages)
            return func(
                self,
                list(processed_assets),
                list(processed_messages),
                *args, **kwargs
            )
        return run

    @classmethod
    def _set_up_plugin(cls, plugin_cls):
        # find theme_name and plugin_name
        theme_name = cls._find_case_insensitive_name(_THEME, namespace)
        plugin_name = cls._find_case_insensitive_name(_PLUGIN, namespace)
        cls._register_plugin(theme_name, plugin_name, plugin_cls)
        # filter data for run method.
        process_func = getattr(plugin_cls, _PLUGIN_RUN_METHOD_NAME)
        setattr(
            plugin_cls,
            _PLUGIN_RUN_METHOD_NAME,
            cls._data_filter(owner=theme_name)(process_func),
        )

    def __new__(cls, cls_name, *args, **kargs):

        plugin_cls = super().__new__(cls, cls_name, *args, **kargs)
        if cls_name != 'BasePlugin':
            cls._set_up_plugin(plugin_cls)
        return plugin_cls


class BasePlugin(metaclass=SetUpPlugin):

    def __init__(*args, **kwargs):
        raise Exception('In BasePlugin')

    @classmethod
    def get_manager_bind_with_plugin(cls, other_cls):
        assert issubclass(other_cls, _BaseAsset)
        fixed_manager = other_cls.get_manager_with_fixed_owner(
            getattr(cls, _THEME),
        )
        return fixed_manager

    def run(self, assets, messages, *args, **kwargs):
        text = 'In Base Class: assets: {}, messages: {},'
        '*args: {}; **kwargs: {}'
        raise Exception(
            text.format(assets, messages, args, kwargs),
        )
