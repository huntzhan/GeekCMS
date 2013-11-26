import markdown
import re
import os
from datetime import datetime
import urllib

from settings import ARTICLE_DIR
from settings import NORMAL_DIR

import markdown
from settings import MD_EXTENSIONS


meta_processor = [
    ('title', 'title', lambda x: x[0]),
    ('date', 'post_time', lambda x: datetime.strptime(x[0], '%d/%m/%Y')),
]


class Article(object):

    def __init__(self, relative_path, html, meta):
        self.relative_path = relative_path
        self.html = html

        # process meta data
        self._process_meta(meta)

    def _process_meta(self, meta):
        for key, cls_attr, processor in meta_processor:
            try:
                val = processor(meta.get(key))
                setattr(self, cls_attr, val)
            except Exception as e:
                raise e

    def _get_url(self):
        head, tail = os.path.split(self.relative_path)
        tail = tail.replace('.md', '.html')
        url = '/' + os.path.join(head, tail)
        return url
    url = property(_get_url)


class ArticleLoader(object):

    def __call__(self, relative_path):
        absolute_path = os.path.join(ARTICLE_DIR, relative_path)

        try:
            with open(absolute_path) as f:
                content = f.read()
                # generate html
                md = markdown.Markdown(extensions=MD_EXTENSIONS)
                html = md.convert(content)
        except Exception as e:
            # implement it later
            raise e

        return Article(relative_path, html, md.Meta)


class ArticleSetGenerator(object):

    def __init__(self, loader):
        self._article_set = []

        self._load_article_set(loader)

    def _load_article_set(self, loader):
        article_dir_root = os.path.join(ARTICLE_DIR, NORMAL_DIR)

        for dirpath, dirnames, filenames in os.walk(article_dir_root):
            if dirnames:
                continue
            for name in filenames:
                if not name.endswith('.md'):
                    continue

                absolute_path = os.path.join(dirpath, name)
                relative_path = os.path.relpath(absolute_path,
                                                ARTICLE_DIR)
                article = loader(relative_path)
                self._article_set.append(article)

    def _get_article_set(self):
        return self._article_set
    article_set = property(_get_article_set)
