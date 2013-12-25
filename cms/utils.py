import os
import importlib
import inspect
import configuration


plugins_func_name_mapping = (
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

    ('writers',
     configuration.WRITERS,
     'register_writer'),
)


class Settings:

    def __init__(self):
        for attr, plugins, func_name in plugins_func_name_mapping:
            loaded_plugins = self._load_plugins(plugins, func_name)
            setattr(self, attr, loaded_plugins)

    def _load_plugins(self, plugin_names, func_name):
        plugins = []
        for plugin_name in plugin_names:
            if isinstance(plugin_name, str):
                module = importlib.import_module('plugins.' + plugin_name)
                plugin = getattr(module, func_name)()
            # check callable
            elif hasattr(plugin_name, '__call__'):
                plugin = plugin_name

            # ensure iterable
            if not hasattr(plugin, '__iter__'):
                plugin = [plugin]

            plugins.extend(plugin)

        return plugins


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
