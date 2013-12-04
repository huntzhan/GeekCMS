import os
import hashlib
from jinja2 import Environment
from jinja2 import FileSystemLoader
from process_layer import Page

from .settings import ARTICLE
from .settings import ABOUT
from .settings import HOME
from .settings import ARCHIVE



def md5_url(html):
    m = hashlib.md5()
    m.update(html.encode('utf-8'))
    return m.hexdigest()


def article_handler(fragment, env):
    template = env.get_template('article.html')
    html = template.render(title=fragment.meta['title'],
                           article_html=fragment.html)
    url = md5_url(html)
    return url, html


def about_handler(fragment, env):
    template = env.get_template('article.html')
    html = template.render(title=fragment.meta['title'],
                           article_html=fragment.html)
    return 'about.html', html


def article_filter(func):
    def _wrap(items, *args, **kwargs):
        article_items = items[:]
        for item in article_items:
            if item.kind != ARTICLE:
                article_items.remove(item)
        return func(article_items, *args, **kwargs)
    return _wrap


def _get_env():
    template_path = os.path.join(os.getcwd(), 'cms/plugins/simple/templates')
    loader = FileSystemLoader(template_path)
    env = Environment(loader=loader)
    return env


def article_processor(fragments, pages):
    env = _get_env()

    for fragment in fragments:
        if fragment.kind == ARTICLE:
            url, html = article_handler(fragment, env)
        elif fragment.kind == ABOUT:
            url, html = about_handler(fragment, env)
        else:
            continue
        
        pages.append(
            Page(html, url, fragment.kind, fragment),
        )


@article_filter
def home_handler(pages, env):
    pages = sorted(
        pages,
        key=lambda x: x.fragment.meta['post_time'],
        reverse=True,
    )
    template = env.get_template('home.html')
    html = template.render(pages=pages)
    return 'index.html', html


def home_processor(fragments, pages):
    env = _get_env()
    url, html = home_handler(pages, env)
    pages.append(
        Page(html, url, HOME),
    )
