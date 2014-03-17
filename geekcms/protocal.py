from collections import UserDict
from collections import abc
from functools import partial
from functools import wraps
from inspect import signature
from inspect import Parameter


_THEME = 'theme'
_PLUGIN = 'plugin'
_PLUGIN_RUN_METHOD_NAME = 'run'


class _UniqueKeyDict(dict):

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


class Manager(UserDict):

    def __get__(self, instance, cls):
        if instance:
            raise Exception('Manager Can Not Be Called From Instances')
        return self

    def __set__(self, instance, val):
        raise Exception('Manager Can Not Be Replaced.')

    def __delete__(self, instance):
        raise Exception('Manager Can Not Be Deleted.')

    def __init__(self, target_cls, data=None):
        super().__init__()
        # share data area
        if data:
            self.data = data
        # class to init items
        self._target_cls = target_cls

    def __getitem__(self, key):
        if key not in self:
            self[key] = []
        return super().__getitem__(key)

    def create(self, owner, *args, **kwargs):
        item = self._target_cls(owner, *args, **kwargs)
        self[owner].append(item)
        return item

    def add(self, item):
        self[item.owner].append(item)

    def remove(self, item):
        self[item.owner].remove(item)
        if not self[item.owner]:
            del self[item.owner]

    def filter(self, owner):
        if isinstance(owner, str):
            return self[owner]
        elif isinstance(owner, abc.Iterable):
            result = []
            owners = owner
            for owner in owners:
                result.extend(self[owner])
            return reuslt

    def keys(self):
        return list(self)

    def values(self):
        result = []
        for items in super().values():
            result.extend(items)
        return result


class ManagerProxyWithOwner:

    def __init__(self, owner, manager):

        # search type(manager).__dict__
        for method_name in vars(type(manager)):
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

    MANAGER_NAME = 'objects'

    @classmethod
    def _get_manager_data(cls, result_cls):
        pre_manager = getattr(result_cls, cls.MANAGER_NAME, None)
        if pre_manager:
            return pre_manager.data
        else:
            return None

    def __new__(cls, cls_name, *args, **kwargs):
        result_cls = super().__new__(cls, cls_name, *args, **kwargs)
        data = cls._get_manager_data(result_cls)
        setattr(result_cls, cls.MANAGER_NAME, Manager(result_cls, data))
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

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, self.owner)


class BaseResource(_BaseAsset):
    pass


class BaseProduct(_BaseAsset):
    pass


class BaseMessage(_BaseAsset):
    pass


class PluginController:
    """
    Data fields and operations related to plugin 'run' method's customization.
    """

    ACCEPT_OWNERS_ATTR = '__accept_owners__'
    ACCEPT_PARAMS_ATTR = '__accept_params__'
    OWNER = 'owner'
    RESOURCES = 'resources'
    PRODUCTS = 'products'
    MESSAGES = 'messages'
    AVALIABLE_PARA_NAMES = [RESOURCES, PRODUCTS, MESSAGES]

    # Control owner
    @classmethod
    def accept_owners(cls, *owners):
        def decorator(func):
            setattr(func, cls.ACCEPT_OWNERS_ATTR, owners)
        return func

    # Control incoming parameter.
    @classmethod
    def accept_parameters(cls, *params):
        if not set(params) <= set(cls.AVALIABLE_PARA_NAMES):
            raise SyntaxError('Arguments should be any among'
                              ' [RESOURCES, PRODUCTS, MESSAGES]')

        # just add __accept_params__ and __signature__.
        def decorator(func):
            setattr(func, cls.ACCEPT_PARAMS_ATTR, params)
            # protocal of inspect.signature
            func.__signature__ = signature(func)
            return func
        return decorator

    @classmethod
    def get_owner(cls, func, cls_defined_owner):
        # get owners definded by accept_owners.
        decorator_defined_owners = getattr(func, cls.ACCEPT_OWNERS_ATTR, None)
        # ensure developer definded owner.
        if not any((cls_defined_owner, decorator_defined_owners)):
            raise Exception("Can Not Find Owner.")
        # make class defined owner iterable
        if isinstance(cls_defined_owner, str):
            cls_defined_owner = [cls_defined_owner]

        # final_owners should be a container.
        final_owners = decorator_defined_owners or cls_defined_owner
        return final_owners

    @classmethod
    def asset_owner_filter(cls, owners):
        check_func = lambda item: item.owner in owners
        return check_func

    @classmethod
    def get_parameters(cls, func):
        return getattr(func, cls.ACCEPT_PARAMS_ATTR, None)

    @classmethod
    def count_parameters(cls, func, expect_num=None):
        # get __signature__ of func, or generate a new signature of func.
        sig = signature(func)

        count = 0
        for name, para in sig.parameters.items():
            if para.kind is Parameter.POSITIONAL_OR_KEYWORD\
                    and para.default is Parameter.empty:
                count += 1
        if count > 3:
            raise SyntaxError('Require only 0~3 positional parameters.')
        # self is counted
        if expect_num and count != (expect_num + 1):
            raise SyntaxError(
                'Require {} positional parameters'.format(expect_num),
            )
        return count


class SetUpPlugin(type):

    plugin_mapping = _UniqueKeyDict()

    @classmethod
    def clean_up_registered_plugins(cls):
        cls.plugin_mapping = _UniqueKeyDict()

    @classmethod
    def _find_case_insensitive_name(cls, target_name, namespace):
        for name, val in namespace.items():
            if name.lower() == target_name:
                return val
        return None

    @classmethod
    def _register_plugin(cls, theme_name, plugin_name, plugin_cls):
        plugin_index = PluginIndex(theme_name, plugin_name)
        cls.plugin_mapping[plugin_index] = plugin_cls

    @classmethod
    def get_plugin(cls, plugin_index):
        return cls.plugin_mapping.get(plugin_index, None)

    @classmethod
    def _data_filter(cls, func=None, owner=''):
        # support decorator
        if func is None:
            return partial(cls._data_filter, owner=owner)

        # begin decorating
        @wraps(func)
        def run(self, resources, products, messages):
            # contains all assets index by AVALIABLE_PARA_NAMES
            params = {
                PluginController.RESOURCES: resources,
                PluginController.PRODUCTS: products,
                PluginController.MESSAGES: messages,
            }

            owners = PluginController.get_owner(func, owner)
            check_func = PluginController.asset_owner_filter(owners)

            # get parameters order defined by accept_parameters
            params_order = PluginController.get_parameters(func)

            if params_order is None:
                # make sure the number of functino's POSITIONAL_OR_KEYWORD
                # parameters <= 3.
                count = PluginController.count_parameters(func)
                # defualt
                params_order = PluginController.AVALIABLE_PARA_NAMES[:count]
            else:
                # call count_parameters to check function's signature and make
                # sure that the number of POSITIONAL_OR_KEYWORD parameters is
                # exactly the same as the length of params_order
                PluginController.count_parameters(func, len(params_order))

            # filter assets.
            iter_params = [filter(check_func, params[name])
                           for name in params_order]
            processed_params = [list(iter_param) for iter_param in iter_params]
            # here we go.
            return func(self, *processed_params)
        return run

    @classmethod
    def _set_up_plugin(cls, plugin_cls, namespace):
        # find theme_name and plugin_name, should both be string.
        find_name = cls._find_case_insensitive_name
        theme_name = find_name(_THEME, namespace)
        plugin_name = find_name(_PLUGIN, namespace) or plugin_cls.__name__

        # register plugin
        cls._register_plugin(theme_name, plugin_name, plugin_cls)

        # filter data for run method.
        process_func = getattr(plugin_cls, _PLUGIN_RUN_METHOD_NAME)
        setattr(
            plugin_cls,
            _PLUGIN_RUN_METHOD_NAME,
            cls._data_filter(process_func, theme_name),
        )

    def __new__(cls, cls_name, bases, namespace, **kargs):

        plugin_cls = super().__new__(cls,
                                     cls_name, bases, namespace,
                                     **kargs)
        if cls_name != 'BasePlugin':
            cls._set_up_plugin(plugin_cls, namespace)
        return plugin_cls


class BasePlugin(metaclass=SetUpPlugin):

    @classmethod
    def get_manager_bind_with_plugin(cls, other_cls):
        assert issubclass(other_cls, _BaseAsset)
        fixed_manager = other_cls.get_manager_with_fixed_owner(
            getattr(cls, _THEME),
        )
        return fixed_manager

    # all plugins should define a 'run' function with 'self' as its first
    # parameter, and with other zero/one/two/three positional parameter(s),
    # one for resources, one for products, and the last one is for messages.
    # Otherwise, use 'accept_parameters' to control parameters.
    def run(self, resources=None, products=None, messages=None):
        raise Exception('In BasePlugin.')


def get_registered_plugins():
    return dict(SetUpPlugin.plugin_mapping)
