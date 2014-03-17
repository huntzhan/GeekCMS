
import os
import importlib
from collections import OrderedDict

from .utils import (SettingsLoader, ProjectSettings, ThemeSettings
                    ShareDate, PathResolver, SysPathContextManager)
from .protocal import SetUpPlugin
from .sequence_analyze import SequenceParser


class SettingsLoader:

    @classmethod
    def load_share_data(cls, loaders):
        ShareDate.load_data(loaders)

    @classmethod
    def load_project_settings(cls, path):
        project_settings_loader = SettingsLoader(path)
        ProjectSettings.load_data(project_settings_loader)
        cls.load_share_data(project_settings_loader)

    @classmethod
    def load_theme_settings(cls, path, name):
        theme_settings_loader = SettingsLoader(path, name)
        ThemeSettings.load_data(theme_settings_loader)
        cls.load_share_data(theme_settings_loader)

    @classmethod
    def load_settings(cls):
        pr = PathResolver

        # set up ProjectSettings
        project_settings_path = pr.project_settings()
        cls.load_project_settings(project_settings_path)

        # set up ThemeSettings
        theme_settings_set = []
        for theme_name in ProjectSettings.get_registered_theme_name():
            theme_settings_path = pr.theme_settings(theme_name)
            cls.load_theme_settings(theme_settings_path, theme_name)

    @classmethod
    def load_themes(cls):
        pr = PathResolver

        themes_path = pr.themes()
        with SysPathContextManager(themes_path):
            for theme_name in ProjectSettings.get_registered_theme_name():
                importlib.import_module(theme_name)

    @classmethod
    def run(cls):
        PathResolver.set_project_path(os.getcwd())
        cls.load_settings()
        cls.load_themes()


class PluginLoader:
    runtime_components = ['pre_load', 'in_load', 'post_load',
                          'pre_process', 'in_process', 'post_process',
                          'pre_write', 'in_write', 'post_write']

    @classmethod
    def get_execution_orders(cls):
        error_happend = False
        exec_orders = OrderedDict()

        for component in cls.runtime_components:
            parser = SequenceParser()
            for theme_name in ProjectSettings.get_registered_theme_name():
                # get plain text
                search_key = '{}.{}'.format(theme_name, component)
                plain_text = ThemeSettings.get(search_key)
                if plain_text is None:
                    continue
                # analyse
                parser.analyze(plain_text)

            if parser.error:
                parser.report_error()
                error_happend = True
            else:
                exec_orders[component] = parser.generate_sequence()

        return error_happend, exec_orders

    @classmethod
    def verify_plugins(cls, exec_orders):
        for plugin_index in exec_orders.values():
            plugin = SetUpPlugin.get_plugin(plugin_index)
            if plugin is None:
                # can not find such plugin
                return True
        return False

    @classmethod
    def run(cls):
        parse_error, exec_orders = cls.get_execution_orders()
        match_error = cls.verify_plugins(exec_orders)
        if parse_error or match_error:
            raise SyntaxError("Error happended, suspend program.')
        return exec_orders
