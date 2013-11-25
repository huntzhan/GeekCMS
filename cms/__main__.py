from __future__ import unicode_literals

from jinja2 import Environment
from jinja2 import FileSystemLoader

from load import ArticleLoader
from load import ArticleSetGenerator
from process import ArticleSetPreprocessor
from process import PageSetGenerator
from printer import PageSetProcessor

from settings import TEMPLATE_DIR

article_loader = ArticleLoader()
preprocessor = ArticleSetPreprocessor()
page_set_processor = PageSetProcessor()

# load file
article_set_generator = ArticleSetGenerator(article_loader)
article_set = article_set_generator.article_set

# process content
loader = FileSystemLoader(TEMPLATE_DIR)
env = Environment(loader=loader)
page_set_generator = PageSetGenerator(
    article_set,
    env,
    article_loader,
    preprocessor
)
page_set = page_set_generator.page_set

# print 
page_set_processor(page_set)
