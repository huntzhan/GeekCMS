import os
import importlib
import inspect
import configuration


class Settings:

    def __init__(self):
        self.command_processors = self._load_plugins(
            configuration.COMMAND_PROCESSORS,
            'register_command_processor',
        )

        self.loaders = self._load_plugins(
            configuration.LOADERS,
            'register_loader',
        )

        self.preprocessors = self._load_plugins(
            configuration.PREPROCESSORS,
            'register_preprocessor',
        )

        self.processors = self._load_plugins(
            configuration.PROCESSORS,
            'register_processor',
        )

        self.writers = self._load_plugins(
            configuration.WRITERS,
            'register_writer',
        )

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
            if hasattr(plugin, '__iter__'):
                pass
            else:
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
