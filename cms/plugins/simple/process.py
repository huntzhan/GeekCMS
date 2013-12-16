import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
from html.parser import HTMLParser
from collections import OrderedDict

from jinja2 import Environment
from jinja2 import FileSystemLoader
from process_layer import Page
from utils import get_module_path

from .settings import ARTICLE
from .settings import ABOUT
from .settings import HOME


def title2url(title):
    return title + '.html'


def article_handler(fragment, env):
    template = env.get_template('article.html')
    html = template.render(title=fragment.meta['title'],
                           article_html=fragment.html)
    url = title2url(fragment.meta['title'])
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

    article_urls = []
    for fragment in fragments:
        if fragment.kind == ARTICLE:
            url, html = article_handler(fragment, env)
        elif fragment.kind == ABOUT:
            url, html = about_handler(fragment, env)
        else:
            continue

        while url in article_urls:
            url = re.sub('.html', '', url) + '_again.html'
        article_urls.append(url)

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


class _DeHTMLParser(HTMLParser):
    UNAVALIABLE_TAGS = ['script', 'style', 'link', 'div', 'h1', 'h2']

    def __init__(self):
        HTMLParser.__init__(self)
        self.ok = True
        self.__text = []

    def handle_data(self, data):
        text = data.strip()
        if len(text) > 0 and self.ok:
            text = re.sub('[ \t\r\n]+', ' ', text)
            self.__text.append(text + ' ')

    def handle_starttag(self, tag, attrs):
        if tag in self.UNAVALIABLE_TAGS:
            self.ok = False
            return

        if tag == 'p':
            self.__text.append('\n\n')
        elif tag == 'br':
            self.__text.append('\n')

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.__text.append('\n\n')

    def handle_endtag(self, tag):
        if tag in self.UNAVALIABLE_TAGS:
            self.ok = True

    def text(self):
        return ''.join(self.__text).strip()


def dehtml(text):
    try:
        parser = _DeHTMLParser()
        parser.feed(text)
        parser.close()
        return parser.text()
    except:
        return text


@article_filter
def home_handler(pages, env):
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

        # extract brief content
        MAX_WORDS_NUM = 500
        brief_content = dehtml(page.fragment.html)[:MAX_WORDS_NUM]
        brief_content = re.sub('\s+', ' ', brief_content)
        formated_page['brief_content'] = brief_content + '......'

        formated_pages.append(formated_page)

    template = env.get_template('home.html')
    html = template.render(pages=formated_pages)
    return 'index.html', html


def home_processor(fragments, pages):
    env = _get_env()
    url, html = home_handler(pages, env)
    pages.append(
        Page(html, url, HOME),
    )


ROOT = 'root'
TOPIC = 'topic'
PAGE = 'page'


def expand_article_tree(article_tree, dirs):
    cur_node = article_tree
    for dir in dirs:
        if dir in cur_node:
            cur_node = cur_node[dir]
        else:
            cur_node[dir] = {}
            cur_node = cur_node[dir]

    return cur_node


def construct_article_tree(path_page_mapping,
                           ordered_paths,
                           common_prefix):
    article_tree = OrderedDict()
    for path in ordered_paths:
        rel_path = re.sub(common_prefix, '', path)
        head, _ = os.path.split(rel_path)
        dirs = head.split('/')

        cur_node = expand_article_tree(article_tree, dirs)
        if None not in cur_node:
            cur_node[None] = []

        cur_node[None].append({
            'path': path,
            'url': path_page_mapping[path].url,
            'title': path_page_mapping[path].fragment.meta['title'],
        })
    return article_tree


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


def construct_raw_paths_and_path_page_mapping(pages):
    path_page_mapping = {}
    raw_paths = []
    for page in pages:
        file = page.fragment.file
        path_page_mapping[file.abs_path] = page
        raw_paths.append(file.abs_path)

    return path_page_mapping, raw_paths


def load_xml(module_path):
    xml_name = 'xml_archive'

    xml_path = os.path.join(module_path, xml_name)
    try:
        with open(xml_path) as f:
            archive_xml_str = f.read()
        old_xml = ET.fromstring(archive_xml_str)
    except:
        old_xml = ET.Element(ROOT)

    return xml_path, old_xml


def generate_xml(article_tree, xml_path):
    new_xml = ET.Element(ROOT)
    construct_xml_tree(new_xml, article_tree)

    raw_xml = ET.tostring(new_xml, encoding='UTF-8')
    reparse = minidom.parseString(raw_xml)
    xml_str = reparse.toprettyxml(' ' * 4, os.linesep, 'UTF-8')
    with open(xml_path, 'wb') as f:
        f.write(xml_str)


def construct_ordered_paths(raw_paths, old_xml):
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


def get_common_prefix(ordered_paths):
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


@article_filter
def archives_handler(pages, env):
    pages = sorted(
        pages,
        key=lambda x: x.fragment.meta['post_time'],
        reverse=False,
    )

    # using abs_path to identify an item.
    path_page_mapping, raw_paths = \
        construct_raw_paths_and_path_page_mapping(pages)

    # load xml
    module_path = get_module_path(archives_handler)
    xml_path, old_xml = load_xml(module_path)

    # generate a ordered_paths for generating archives.
    ordered_paths = construct_ordered_paths(raw_paths, old_xml)

    # using ordered paths to generate archive page
    common_prefix = get_common_prefix(ordered_paths)

    # build article tree
    article_tree = construct_article_tree(
        path_page_mapping,
        ordered_paths,
        common_prefix,
    )

    # using ordered paths to generate xml
    generate_xml(article_tree, xml_path)
    # render to html and return
    template = env.get_template('archives.html')
    html = template.render(article_tree=article_tree)
    return 'archive.html', html


def archive_processor(fragments, pages):
    env = _get_env()
    url, html = archives_handler(pages, env)
    pages.append(
        Page(html, url, HOME),
    )
