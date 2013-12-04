import os
from datetime import datetime
from docopt import docopt

import configuration
from load_layer import load
from process_layer import preprocess
from process_layer import process
from write_layer import write
from command_layer import process_docopt_doc
from command_layer import process_args

import importlib
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

            # make iterable
            if hasattr(plugin, '__iter__'):
                pass
            else:
                plugin = [plugin]

            plugins.extend(plugin)

        return plugins



def default(settings):
    files = load(settings)
    fragments = preprocess(settings, files)
    pages = process(settings, fragments)
    write(settings, pages)


if __name__ == '__main__':
    settings = Settings()
    doc = process_docopt_doc(settings)
    args = docopt(doc, version='0.2.1')

    if process_args(settings, args):
        default(settings)
