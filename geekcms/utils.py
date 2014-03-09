
"""
This package implements tools that can facilitates theme development.
"""


class _SettingsLoader:
    """
    Load settings and provide inquiry interface.
    """

    SHARE_FIELD = 'Share'
    THEME_FIELD = 'Theme'
    PLUGIN_REGISTRATION = 'Plugin'

    def __init__(self, path):
        self._path = path

    def _load_settings(self):
        pass

    def get(self, section, key):
        pass


class ShareData:
    """
    Interface to resolve shared data field.
    """

    _global_vars = {}
    _theme_vars = {}


class ThemeSettings:
    """
    Interface to get theme settings, including registered themes and plugin
    execution expressions.
    """
    pass
