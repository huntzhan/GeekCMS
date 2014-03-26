from collections import UserDict
from collections import OrderedDict
from collections import abc
from functools import partial
from functools import wraps
from inspect import signature
from inspect import Parameter
import types


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
        # share data area.
        if isinstance(data, dict):
            self.data = data
        # class to init items
        self._target_cls = target_cls

    def __getitem__(self, key):
        if key not in self:
            self[key] = []
        return super().__getitem__(key)

    # operations covers all types.
    def add(self, item):
        self[item.owner].append(item)

    def remove(self, item):
        self[item.owner].remove(item)
        if not self[item.owner]:
            del self[item.owner]

    def keys(self):
        return list(self)

    # operations related to _target_cls.
    def _filter_isinstance(self, items):
        for item in items[:]:
            if not isinstance(item, self._target_cls):
                items.remove(item)
        return items

    # Be Careful! owner is keyword-only parameter.
    def create(self, *args, owner, **kwargs):
        item = self._target_cls(*args, **kwargs)
        item.set_owner(owner)
        self[owner].append(item)
        return item

    def filter(self, owner):
        if isinstance(owner, str):
            result = self[owner]
        elif isinstance(owner, abc.Iterable):
            result = []
            owners = owner
            for owner in owners:
                result.extend(self[owner])
        return self._filter_isinstance(result)

    def values(self):
        result = []
        for items in super().values():
            result.extend(items)
        return self._filter_isinstance(result)

    def clear(self):
        owners_to_be_remove = []
        for owner, items in self.items():
            for item in items[:]:
                if isinstance(item, self._target_cls):
                    items.remove(item)
            if not items:
                owners_to_be_remove.append(owner)
        for owner in owners_to_be_remove:
            del self[owner]


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
        # _BaseAsset would create the first manager, and all derived class
        # would operated a shared data field.
        if isinstance(pre_manager, Manager):
            return pre_manager.data
        else:
            return None

    def __new__(cls, *args, **kwargs):
        result_cls = super().__new__(cls, *args, **kwargs)
        # init share data for BaseResource, BaseProduct and BaseMessage.
        if result_cls.__name__ != '_BaseAsset':
            data = cls._get_manager_data(result_cls)
            setattr(
                result_cls,
                cls.MANAGER_NAME,
                Manager(result_cls, data),
            )
        return result_cls


class _BaseAsset(metaclass=SetUpObjectManager):

    def __init__(self, *args, **kwargs):
        text = 'In Base Class: *args: {}; **kwargs: {}'
        raise Exception(
            text.format(owner, args, kwargs),
        )

    def set_owner(self, owner):
        self.owner = owner

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
        return decorator

    # Control incoming parameter.
    @classmethod
    def accept_parameters(cls, *fixed_params, **typed_params):

        """
        1. typed_params is empty and params is not empty.
        2. params is empty and typed_params is not empty.
        3. both params and typed_params are not empty.(conflict might occur)
        4. params might cantains items of str or tuple.
        """

        # preprocess of params and typed_params.
        params = []
        for index, item in enumerate(fixed_params[:]):
            if isinstance(item, str):
                params.append(item)
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                para_name, para_type = item
                # add name to params.
                params.append(para_name)
                # update restriction of types.
                typed_params.update({para_name: para_type})
            else:
                raise SyntaxError('Error In *params.')

        # check parameters name.
        name_set = set(params) | set(typed_params)
        if not name_set:
            raise SyntaxError('Argument Can Not Be Empty.')
        if not (name_set <= set(cls.AVALIABLE_PARA_NAMES)):
            raise SyntaxError(
                'Arguments should be any among'
                ' [RESOURCES, PRODUCTS, MESSAGES]'
            )

        # set up order dict to keep the restriction.
        customized_params = OrderedDict()
        # keep the order defined by params
        for key in params:
            customized_params[key] = None
        # set the type of params.
        for key in cls.AVALIABLE_PARA_NAMES:
            if key not in typed_params:
                continue
            elif key not in params and params:
                raise SyntaxError('Parameters Conflicts.')
            else:
                customized_params[key] = typed_params[key]

        def decorator(func):
            setattr(func, cls.ACCEPT_PARAMS_ATTR, customized_params)
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

        # final_owners should be a container, and owners definded by
        # accept_owners is in higher priority.
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
        bound_func = types.MethodType(func, object)
        sig = signature(bound_func)

        count = 0
        for name, para in sig.parameters.items():
            if para.kind is Parameter.POSITIONAL_OR_KEYWORD\
                    and para.default is Parameter.empty:
                count += 1
        if count > 3:
            raise SyntaxError('Require only 0~3 positional parameters.')
        if expect_num and count != expect_num:
            raise SyntaxError(
                'Require {} positional parameters'.format(expect_num),
            )
        return count


class PluginRegister(type):

    THEME = 'theme'
    PLUGIN = 'plugin'

    plugin_mapping = _UniqueKeyDict()
    context_theme = None

    @classmethod
    def unset_context_theme(cls):
        cls.context_theme = None

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
    def get_plugin(cls, plugin_index):
        return cls.plugin_mapping.get(plugin_index, None)

    @classmethod
    def get_registered_plugins(cls):
        return dict(cls.plugin_mapping)

    @classmethod
    def _get_theme_name(cls, namespace):
        find_name = cls._find_case_insensitive_name
        # class-level attribute 'theme' could be omitted, in such case the name
        # of theme's top-level directory would be adapt.
        theme_name = find_name(cls.THEME, namespace) or cls.context_theme
        # class-level attribute 'plugin' could be omitted, in such case the
        return theme_name

    @classmethod
    def _get_plugin_name(cls, plugin_cls, namespace):
        find_name = cls._find_case_insensitive_name
        # name of plugin class would be adapt.
        plugin_name = find_name(cls.PLUGIN, namespace) or plugin_cls.__name__
        return plugin_name

    @classmethod
    def _register_plugin(cls, plugin_cls, namespace):

        # get attributes.
        theme_name = cls._get_theme_name(namespace)
        plugin_name = cls._get_plugin_name(plugin_cls, namespace)

        # set attrbutes of theme and plugin to class.
        setattr(plugin_cls, cls.THEME, theme_name)
        setattr(plugin_cls, cls.PLUGIN, plugin_name)

        # register plugin
        plugin_index = PluginIndex(theme_name, plugin_name)
        cls.plugin_mapping[plugin_index] = plugin_cls

    @classmethod
    def _should_process(cls, cls_name):
        return cls_name not in ['BasePlugin', 'BaseExtendedProcedure']

    def __new__(cls, cls_name, bases, namespace, **kargs):

        plugin_cls = super().__new__(cls,
                                     cls_name, bases, namespace,
                                     **kargs)
        if cls._should_process(cls_name):
            cls._register_plugin(plugin_cls, namespace)
        return plugin_cls


class PluginRegisterAndRunFilter(PluginRegister):

    PLUGIN_RUN_METHOD_NAME = 'run'

    @classmethod
    def _data_filter(cls, func=None, owner=''):
        # support decorator
        if func is None:
            return partial(cls._data_filter, owner=owner)

        # begin decorating
        @wraps(func)
        def run(self):
            # contains all assets index by AVALIABLE_PARA_NAMES
            params = {
                PluginController.RESOURCES: BaseResource,
                PluginController.PRODUCTS: BaseProduct,
                PluginController.MESSAGES: BaseMessage,
            }

            owners = PluginController.get_owner(func, owner)
            check_owner_func = PluginController.asset_owner_filter(owners)

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

                # adjust params with user defined types.
                for key, val in params_order.items():
                    if val is None:
                        continue
                    params[key] = val

            # filter assets.
            processed_params = []
            for key in params_order:
                filtered_items = filter(
                    check_owner_func,
                    params[key].objects.values(),
                )
                processed_params.append(list(filtered_items))

            # here we go.
            return func(self, *processed_params)
        return run

    def __new__(cls, cls_name, bases, namespace, **kargs):

        plugin_cls = super().__new__(cls,
                                     cls_name, bases, namespace,
                                     **kargs)

        if cls._should_process(cls_name):
            theme_name = cls._get_theme_name(namespace)
            # filter data for run method.
            process_func = getattr(plugin_cls, cls.PLUGIN_RUN_METHOD_NAME)
            setattr(
                plugin_cls,
                cls.PLUGIN_RUN_METHOD_NAME,
                cls._data_filter(process_func, theme_name),
            )

        return plugin_cls


class BasePlugin(metaclass=PluginRegisterAndRunFilter):

    @classmethod
    def get_manager_bind_with_plugin(cls, other_cls):
        fixed_manager = other_cls.get_manager_with_fixed_owner(
            getattr(cls, PluginRegister.THEME),
        )
        return fixed_manager

    # all plugins should define a 'run' function with 'self' as its first
    # parameter, and with other zero/one/two/three positional parameter(s),
    # one for resources, one for products, and the last one is for messages.
    # Otherwise, use 'accept_parameters' to control parameters.
    def run(self, resources=None, products=None, messages=None):
        raise Exception('In BasePlugin.')


class BaseExtendedProcedure(metaclass=PluginRegister):

    """
    1. call get_command_and_explanation(self), in order to construct main doc.
    2. when user enter 'geekcms <command> [args...]', GeekCMS would call
    get_doc(self) to construct an new instance of docopt, such instance would
    be passed to run(self, args).
    """

    def get_command_and_explanation(self):
        # return (<command>, explanation).
        raise Exception('In BaseExtendedProcedure.')

    def get_doc(self):
        raise Exception('In BaseExtendedProcedure.')

    def run(self, args):
        raise Exception('In BaseExtendedProcedure.')
