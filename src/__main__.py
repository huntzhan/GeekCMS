from __future__ import unicode_literals

from jinja2 import Environment
from jinja2 import FileSystemLoader

from load import ArticleLoader
from load import ArticleSetGenerator
from process import ArticleSetPreprocessor
from process import PageSetGenerator
from printer import PagePrinter

from settings import TEMPLATE_DIR

# load file
article_loader = ArticleLoader()
article_set_generator = ArticleSetGenerator(article_loader)
article_set = article_set_generator.article_set
# process content
preprocessor = ArticleSetPreprocessor()
loader = FileSystemLoader(TEMPLATE_DIR)
env = Environment(loader=loader)
page_set_generator = PageSetGenerator(
    article_set,
    env,
    article_loader,
    preprocessor
)
page_set = page_set_generator.page_set
# output
printer = PagePrinter()
for page in page_set:
    printer(page)
