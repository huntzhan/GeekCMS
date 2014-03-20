
import os
import importlib
from collections import OrderedDict

from .utils import (SettingsLoader, ProjectSettings, ThemeSettings,
                    ShareData, PathResolver, SysPathContextManager)
from .protocal import PluginRegister
from .sequence_analyze import SequenceParser


class SettingsProcedure:

    @classmethod
    def load_share_data(cls, loaders):
        ShareData.load_data(loaders)

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

        theme_dir = pr.themes()
        for theme_name in ProjectSettings.get_registered_theme_name():
            with SysPathContextManager(theme_name, theme_dir):
                importlib.import_module(theme_name)

    @classmethod
    def run(cls, project_path):
        PathResolver.set_project_path(project_path)
        cls.load_settings()
        cls.load_themes()


class PluginProcedure:
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
                # analyze
                parser.analyze(theme_name, plain_text)

            if parser.error:
                parser.report_error()
                error_happend = True
            else:
                exec_orders[component] = parser.generate_sequence()

        return error_happend, exec_orders

    @classmethod
    def linearize_exec_orders(cls, exec_orders):
        flat_orders = []
        for container in exec_orders.values():
            flat_orders.extend(container)
        return flat_orders

    @classmethod
    def verify_plugins(cls, flat_orders):
        for plugin_index in flat_orders:
            plugin = PluginRegister.get_plugin(plugin_index)
            if plugin is None:
                # can not find such plugin
                print('Can Not Find {}'.format(plugin_index))
                return True
        return False

    @classmethod
    def run(cls):
        parse_error, exec_orders = cls.get_execution_orders()
        flat_orders = cls.linearize_exec_orders(exec_orders)
        match_error = cls.verify_plugins(flat_orders)
        if parse_error or match_error:
            raise SyntaxError('Error happended, suspend program.')
        return flat_orders
