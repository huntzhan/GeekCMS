import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
from collections import OrderedDict

from jinja2 import Environment
from jinja2 import FileSystemLoader

from process_layer import Product
from utils import get_module_path
from .html2text import html2text

from .settings import ARTICLE
from .settings import ABOUT
from .settings import HOME
from .settings import ARCHIVE


def _title2url(title):
    return title + '.html'


def _article_handler(fragment, env):
    template = env.get_template('article.html')
    html = template.render(title=fragment.meta['title'],
                           article_html=fragment.data)
    url = _title2url(fragment.meta['title'])
    return url, html


def _about_handler(fragment, env):
    template = env.get_template('article.html')
    html = template.render(article_html=fragment.data)
    return 'about.html', html


def _get_env():
    template_path = os.path.join(os.getcwd(), 'cms/plugins/default/templates')
    loader = FileSystemLoader(template_path)
    env = Environment(loader=loader)
    return env


def article_processor(data_set):
    env = _get_env()

    article_urls = []
    for fragment in data_set.fragments:
        if fragment.mark == ARTICLE:
            url, html = _article_handler(fragment, env)
        elif fragment.mark == ABOUT:
            url, html = _about_handler(fragment, env)
        else:
            continue

        # assure url to be unique
        while url in article_urls:
            url = re.sub('.html', '', url) + '_again.html'
        article_urls.append(url)

        # add new page to data_set
        html_page = Product(fragment.mark, html)
        html_page.url = url
        # make one-to-one relations
        html_page.fragment = fragment
        data_set.products.append(html_page)


def _article_filter(func):
    """
    filter out non-article items.
    """
    def _wrap(items, *args, **kwargs):
        article_items = items[:]
        for item in items:
            if item.mark != ARTICLE:
                article_items.remove(item)
        return func(article_items, *args, **kwargs)
    return _wrap


def _genenrate_text_from_html(html):
    MAX_LINES = 10
    MAX_WORDS = 300

    raw_text = html2text(html)
    text_list = []
    for line in filter(lambda x: bool(x),
                       raw_text.split(os.linesep)):
        text_list.append(line)

    text = os.linesep.join(text_list[:MAX_LINES])
    return text[:MAX_WORDS]


@_article_filter
def _home_handler(pages, env):
    pages = sorted(
        pages,
        key=lambda x: x.fragment.meta['post_time'],
        reverse=True,
    )

    formated_pages = []
    for page in pages:
        formated_page = {}
        formated_page['url'] = page.url
        formated_page['title'] = page.fragment.meta['title']
        formated_page['post_time'] = page.fragment.meta['post_time']

        brief_content = _genenrate_text_from_html(page.fragment.data)
        formated_page['brief_content'] = brief_content

        formated_pages.append(formated_page)

    template = env.get_template('home.html')
    html = template.render(pages=formated_pages)
    return 'index.html', html


def home_processor(data_set):
    env = _get_env()
    url, html = _home_handler(data_set.products, env)
    home_page = Product(HOME, html)
    home_page.url = url
    data_set.products.append(home_page)


ROOT = 'root'
TOPIC = 'topic'
PAGE = 'page'


def _expand_article_tree(article_tree, dirs):
    cur_node = article_tree
    for dir in dirs:
        if dir in cur_node:
            cur_node = cur_node[dir]
        else:
            cur_node[dir] = {}
            cur_node = cur_node[dir]

    return cur_node


def _construct_article_tree(path_page_mapping,
                            ordered_paths,
                            common_prefix):
    article_tree = OrderedDict()
    for path in ordered_paths:
        rel_path = re.sub(common_prefix, '', path)
        head, _ = os.path.split(rel_path)
        dirs = head.split('/')

        cur_node = _expand_article_tree(article_tree, dirs)
        if None not in cur_node:
            cur_node[None] = []

        cur_node[None].append({
            'path': path,
            'url': path_page_mapping[path].url,
            'title': path_page_mapping[path].fragment.meta['title'],
        })
    return article_tree


def _construct_xml_tree(xml_parent, article_parent):
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
            _construct_xml_tree(topic, sub_article_parent)


def _construct_raw_paths_and_path_page_mapping(pages):
    path_page_mapping = {}
    raw_paths = []
    for page in pages:
        file = page.fragment.file
        path_page_mapping[file.abs_path] = page
        raw_paths.append(file.abs_path)

    return path_page_mapping, raw_paths


def _load_xml(module_path):
    xml_name = 'xml_archive'

    xml_path = os.path.join(module_path, xml_name)
    try:
        with open(xml_path) as f:
            archive_xml_str = f.read()
        old_xml = ET.fromstring(archive_xml_str)
    except:
        old_xml = ET.Element(ROOT)

    return xml_path, old_xml


def _generate_xml(article_tree, xml_path):
    new_xml = ET.Element(ROOT)
    _construct_xml_tree(new_xml, article_tree)

    raw_xml = ET.tostring(new_xml, encoding='UTF-8')
    reparse = minidom.parseString(raw_xml)
    xml_str = reparse.toprettyxml(' ' * 4, os.linesep, 'UTF-8')
    with open(xml_path, 'wb') as f:
        f.write(xml_str)


def _construct_ordered_paths(raw_paths, old_xml):
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
    return ordered_paths


def _get_common_prefix(ordered_paths):
    dir_paths = []
    for head, tail in map(os.path.split, ordered_paths):
        dir_paths.append(head)

    # all aritcles should shoulde be placed in a single dir,
    # which is the root of the article tree.
    # leaf of the article tree represents article, while dir
    # represents topic.
    common_prefix = os.path.commonprefix(dir_paths)
    if not common_prefix.endswith('/'):
        common_prefix += '/'
    if '/' not in re.sub(common_prefix, '', ordered_paths[0]):
        # there is only a single topic.
        # go to an upper layer
        common_prefix, _ = os.path.split(common_prefix.rstrip('/'))
        common_prefix += '/'

    return common_prefix


@_article_filter
def _archives_handler(pages, env):
    pages = sorted(
        pages,
        key=lambda x: x.fragment.meta['post_time'],
        reverse=False,
    )

    # using abs_path to identify an item.
    path_page_mapping, raw_paths = \
        _construct_raw_paths_and_path_page_mapping(pages)

    # load xml
    module_path = get_module_path(_archives_handler)
    xml_path, old_xml = _load_xml(module_path)

    # generate a ordered_paths for generating archives.
    ordered_paths = _construct_ordered_paths(raw_paths, old_xml)

    # using ordered paths to generate archive page
    common_prefix = _get_common_prefix(ordered_paths)

    # build article tree
    article_tree = _construct_article_tree(
        path_page_mapping,
        ordered_paths,
        common_prefix,
    )

    # using ordered paths to generate xml
    _generate_xml(article_tree, xml_path)
    # render to html and return
    template = env.get_template('archives.html')
    html = template.render(article_tree=article_tree)
    return 'archive.html', html


def archive_processor(data_set):
    env = _get_env()
    url, html = _archives_handler(data_set.products, env)
    archive_page = Product(ARCHIVE, html)
    archive_page.url = url
    data_set.products.append(archive_page)
