
import re
import os
import urllib.parse
import subprocess

from .utils import PathResolver, PathResolverContextManager


_SVN_URL = 'https://github.com/haoxun/GeekCMS-Themes/trunk/'


def download_theme(theme_name, path):
    svn_url = urllib.parse.urljoin(
        _SVN_URL,
        re.sub(r'\s', '', theme_name),
    )
    target_path = os.path.join(path, theme_name)
    subprocess.check_call(
        ['svn', 'checkout', svn_url, target_path],
    )

    with PathResolverContextManager(target_path):
        PathResolver.inputs(ensure_exist=True)
        PathResolver.outputs(ensure_exist=True)
        PathResolver.themes(ensure_exist=True)
        PathResolver.states(ensure_exist=True)
        PathResolver.project_settings(ensure_exist=True)
