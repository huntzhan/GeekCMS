from __future__ import unicode_literals
import markdown
import re
import os
from datetime import datetime
import urllib

from settings import ARTICLE_DIR
from settings import NORMAL_DIR

class Article(object):

    def __init__(self, relative_path, content):
        self.relative_path = relative_path
        self.content = content
        
        self._extract_info()
        self._remove_info_pattern()

    def _extract_info(self):
        """
        Infomation of article should be stored as following format:
        <!-- Key[Value] -->
        
        Avaliable Key/Value pairs is as follow:
        
        1. Key: Title, The title of article.
        2. Time: Article posted time, should be parsed by 
        datetime.strptime(Time, '%d/%m/%Y'), i.e. 1/11/2013
        """

        def title_parser(info):
            return info

        def time_parser(info):
            return datetime.strptime(info, '%d/%m/%Y')

        avaliable_keys = [
            ('Title', 'title', title_parser),
            ('Time', 'post_time', time_parser),
        ]

        info_pattern = '<!--\s+{}\[((\w|\W)+?)\]\s+-->'

        for key, cls_attr, parser in avaliable_keys:
            pattern = re.compile(info_pattern.format(key))
            match = pattern.search(self.content)
            try:
                info = match.group(1)
                info = parser(info)
                setattr(self, cls_attr, info)                
            except Exception as e:
                # implement it later
                raise e

    def _remove_info_pattern(self):
        info_pattern = '<!--\s+(\w|\W)+?\[(\w|\W)+?\]\s+-->'
        pattern = re.compile(info_pattern)
        self.content = pattern.sub('', self.content)

    def _get_url(self):
        head, tail = os.path.split(self.relative_path)
        tail = tail.replace('.md', '.html')
        url = '/' + os.path.join(head, tail)
        url = url.encode('utf-8')
        return url
    url = property(_get_url)


class ArticleLoader(object):

    def __call__(self, relative_path):
        absolute_path = os.path.join(ARTICLE_DIR, relative_path)

        try:
            with open(absolute_path) as f:
                content = f.read()
                content = content.decode('utf-8')
        except Exception as e:
            # implement it later
            raise e

        return Article(relative_path, content)


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
                relative_path = relative_path.decode('utf-8')
                article = loader(relative_path)
                self._article_set.append(article)

    def _get_article_set(self):
        return self._article_set
    article_set = property(_get_article_set)
