import os
import hashlib
from jinja2 import Environment
from jinja2 import FileSystemLoader
import xml.etree.ElementTree as ET
from xml.dom import minidom

from process_layer import Page
from utils import get_module_path

from .settings import ARTICLE
from .settings import ABOUT
from .settings import HOME
from .settings import ARCHIVE



def md5_url(html):
    m = hashlib.md5()
    m.update(html.encode('utf-8'))
    return m.hexdigest() + '.html'


def article_handler(fragment, env):
    template = env.get_template('article.html')
    html = template.render(title=fragment.meta['title'],
                           article_html=fragment.html)
    url = md5_url(html)
    return url, html


def about_handler(fragment, env):
    template = env.get_template('article.html')
    html = template.render(article_html=fragment.html)
    return 'about.html', html


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


def article_filter(func):
    def _wrap(items, *args, **kwargs):
        article_items = items[:]
        for item in items:
            if item.kind != ARTICLE:
                article_items.remove(item)
        return func(article_items, *args, **kwargs)
    return _wrap


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


def construct_article_tree(article_tree, dirs):
    cur_node = article_tree
    for dir in dirs:
        if dir in cur_node:
            cur_node = cur_node[dir]
        else:
            cur_node[dir] = {}
            cur_node = cur_node[dir]

    return cur_node


ROOT = 'root'
TOPIC = 'topic'
PAGE = 'page'


def construct_xml_tree(xml_parent, article_parent):
    if None in article_parent:
        # leaf
        for item in article_parent[None]:
            page = ET.SubElement(xml_parent, PAGE)
            page.attrib['title'] = item['title']
            page.attrib['path'] = item['path']
            page.attrib['url'] = item['url']
    else:
        # recursive build
        for topic_name, sub_article_parent in article_parent.items():
            topic = ET.SubElement(xml_parent, TOPIC)
            topic.attrib['name'] = topic_name
            construct_xml_tree(topic, sub_article_parent)


@article_filter
def archives_handler(pages, env):
    pages = sorted(
        pages,
        key=lambda x: x.fragment.meta['post_time'],
        reverse=False,
    )

    # using abs_path to identify an item.
    path_page_mapping = {}
    raw_paths = []
    for page in pages:
        file = page.fragment.file
        path_page_mapping[file.abs_path] = page
        raw_paths.append(file.abs_path)

    # load xml
    module_path = get_module_path(archives_handler)
    xml_name = 'xml_archive'
    xml_path = os.path.join(module_path, xml_name)
    try:
        with open(xml_path) as f:
            archive_xml_str = f.read()
        old_xml = ET.fromstring(archive_xml_str)
    except:
        old_xml = ET.Element(ROOT)

    # generate a ordered_paths for generating archives.
    ordered_paths = []
    for node in old_xml.iter():
        if node.tag != PAGE:
            continue
        path = node.attrib['path']
        if path in raw_paths:
            # avaliable path
            ordered_paths.append(path)
            raw_paths.remove(path)
    # extend new pages.
    ordered_paths.extend(raw_paths)

    # using ordered paths to generate archive page
    # remove common prefix
    
    # first remove the tail of paths.
    dir_paths = []
    for head, tail in map(os.path.split, ordered_paths):
        dir_paths.append(head)

    common_prefix = os.path.commonprefix(dir_paths)
    if not common_prefix.endswith('/'):
        common_prefix += '/' 
    if '/' not in ordered_paths[0].lstrip(common_prefix):
        # there is only a single topic.
        # go to an upper layer
        common_prefix, _ = os.path.split(common_prefix.rstrip('/'))
        common_prefix += '/'

    # build article tree
    article_tree = {}
    for path in ordered_paths:
        rel_path = path.lstrip(common_prefix)
        head, _ = os.path.split(rel_path)
        dirs = head.split('/')

        cur_node = construct_article_tree(article_tree, dirs)
        if None not in cur_node:
            cur_node[None] = []

        cur_node[None].append({
            'path': path,
            'url': path_page_mapping[path].url,
            'title': path_page_mapping[path].fragment.meta['title'],
        })
    # render to html
    template = env.get_template('archives.html')
    html = template.render(article_tree=article_tree)

    # using ordered paths to generate xml
    new_xml = ET.Element(ROOT)
    construct_xml_tree(new_xml, article_tree)

    raw_xml = ET.tostring(new_xml, encoding='UTF-8')
    reparse = minidom.parseString(raw_xml)
    xml_str = reparse.toprettyxml(' '*4, os.linesep, 'UTF-8')
    with open(xml_path, 'wb') as f:
        f.write(xml_str)

    # DONE
    return 'archive.html', html


def archive_processor(fragments, pages):
    env = _get_env()
    url, html = archives_handler(pages, env)
    pages.append(
        Page(html, url, HOME),
    )
