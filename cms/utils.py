import os
import importlib
import inspect
import configuration


# this ternary tuple is built for class Settings, with the format (attr,
# plugins, func_name). attr defines the attribute name of Settings, which is a
# list storing some sort of plugins. plugins handles the names or callables of
# plugins. func_name holds for the name of function in __init__.py of plugin
# package, which return callable plugins.
_plugins_func_name_mapping = (
    ('command_processors',
     configuration.COMMAND_PROCESSORS,
     'register_command_processor'),

    ('loaders',
     configuration.LOADERS,
     'register_loader'),

    ('preprocessors',
     configuration.PREPROCESSORS,
     'register_preprocessor'),

    ('processors',
     configuration.PROCESSORS,
     'register_processor'),

    ('postprocessors',
     configuration.POSTPROCESSORS,
     'register_postprocessor'),

    ('writers',
     configuration.WRITERS,
     'register_writer'),
)


class Settings:
    def __init__(self):
        for attr, plugins, func_name in _plugins_func_name_mapping:
            loaded_plugins = self._load_plugins(plugins, func_name)
            # plugins would be stored in a list named by attr.
            # list named attr would be empty if there is no corresponed
            # plugins.
            setattr(self, attr, loaded_plugins)

    def _load_plugins(self, plugin_names, func_name):
        plugins = []
        for plugin_name in plugin_names:
            if isinstance(plugin_name, str):
                try:
                    module = importlib.import_module('plugins.' + plugin_name)
                    plugin = getattr(module, func_name)()
                except Exception as e:
                    # module might not exist
                    # function might not exist
                    raise e

            # check callable
            elif hasattr(plugin_name, '__call__'):
                plugin = plugin_name

            # ensure iterable
            if not hasattr(plugin, '__iter__'):
                plugin = [plugin]

            plugins.extend(plugin)
        return plugins

    def _get_classified_plugins(self):
        # list of list.
        classified_plugins = []
        for attr, _, _ in _plugins_func_name_mapping:
            if attr == 'command_processors':
                continue
            classified_plugins.append(
                getattr(self, attr)
            )
        return classified_plugins

    classified_plugins = property(_get_classified_plugins)


class BaseData:
    """
    Base class for storing data.
    """
    def __init__(self, mark, data):
        # be used to classification, with each being handled by different
        # plugin(s).
        self.mark = mark
        # store the data, such as content of file, html of page.
        # data should always store decoded string.
        self.data = data


def url2rel_path(url):
    rel_path = url.lstrip('/')
    return rel_path


def url2abs_path(root, url):
    rel_path = url2rel_path(url)
    return os.path.join(root, rel_path)


def get_module_path(obj):
    module = inspect.getmodule(obj)
    path = module.__file__
    module_path, _ = os.path.split(path)
    return module_path
