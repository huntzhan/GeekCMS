from collections import defaultdict
from collections import UserDict
from functools import partial
from functools import wraps
from inspect import signature
from inspect import Parameter


RESOURCES = 'resources'
PRODUCTS = 'products'
MESSAGES = 'messages'
OWNER = 'owner'


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

    def values(self):
        result = []
        for objs in self._container.values():
            result.extend(objs)
        return result


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

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, self.owner)


class BaseResource(_BaseAsset):
    pass


class BaseProduct(_BaseAsset):
    pass


class BaseMessage(_BaseAsset):
    pass


# Control owner
def accept_owner(*owners):
    def decorator(func):
        func.__accept_owners__ = owners
    return func


# Control incoming parameter.
def accept_parameters(*params):
    if not set(params) <= set([RESOURCES, PRODUCTS, MESSAGES]):
        raise SyntaxError('Arguments should be any among'
                          ' [RESOURCES, PRODUCTS, MESSAGES]')

    # just add __accept_params__ and __signature__.
    def decorator(func):
        func.__accept_params__ = params
        func.__signature__ = signature(func)
        return func
    return decorator


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
        cls.plugin_mapping[plugin_index.unique_key] = plugin_cls

    @classmethod
    def _get_owner(cls, func, cls_defined_owner):
        decorator_defined_owners = getattr(func, '__accept_owners__', None)
        if not cls_defined_owner\
                and not decorator_defined_owners:
            raise Exception("Can Not Find Owner.")
        # final_owners should be a container
        final_owners = decorator_defined_owners or list(cls_defined_owner)
        return final_owners

    @classmethod
    def _check_owner(cls, owners):
        check_func = lambda item: item.owner in owners
        return check_func

    @classmethod
    def _count_params(cls, func, expect_num=None):
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

    @classmethod
    def _data_filter(cls, func=None, owner=''):
        # support decorator
        if func is None:
            return partial(cls._data_filter, owner=owner)

        # begin decorating
        @wraps(func)
        def run(self, resources, products, messages):

            owners = cls._get_owner(func, owner)
            check_func = cls._check_owner(owners)

            params = {
                RESOURCES: resources,
                PRODUCTS: products,
                MESSAGES: messages,
            }

            params_order = getattr(func, '__accept_params__', None)
            if params_order:
                cls._count_params(func, len(params_order))
            else:
                count = cls._count_params(func)
                params_order = [RESOURCES, PRODUCTS, MESSAGES][:count]

            iter_params = [filter(check_func, params[name])
                           for name in params_order]

            processed_params = [list(iter_param) for iter_param in iter_params]
            return func(self, *processed_params)
        return run

    @classmethod
    def _set_up_plugin(cls, plugin_cls, namespace):
        # find theme_name and plugin_name
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

    def __init__(*args, **kwargs):
        raise Exception('In BasePlugin')

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
