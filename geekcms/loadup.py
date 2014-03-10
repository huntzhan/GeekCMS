
import os
from .utils import PathResolver


def load_project_settings(project_path):
    pass


def load_theme_settings(theme_path):
    pass


def load_settings():
    pr = PathResolver

    themes, project_settings = load_project_settings(pr.project_settings())
    theme_settings_set = []
    for theme_name in themes:
        theme_settings = load_theme_settings(pr.theme_settings(theme_name))
        theme_settings_set.append(theme_settings)
    return project_settings, theme_settings_set


def load_themes():
    pass


def prepare():
    PathResolver.set_project_path(os.getcwd())
