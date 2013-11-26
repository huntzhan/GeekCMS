"""Usage: cms.py [git-push | auto]

Explanation:
    git-push  Commit and push git repo pointed by OUTPUT_DIR
    auto      Generate HTML and git-push

"""

import os
from datetime import datetime
from docopt import docopt
from jinja2 import Environment
from jinja2 import FileSystemLoader

from load import ArticleLoader
from load import ArticleSetGenerator
from process import ArticleSetPreprocessor
from process import PageSetGenerator
from printer import PageSetProcessor

from settings import TEMPLATE_DIR
from settings import OUTPUT_DIR

def default():
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

def git_commit_and_push():
    os.chdir(OUTPUT_DIR)    

    command = """git add --all *
                 git commit -m 'GeekCMS Update, {}'
                 git push
              """.format(datetime.now().strftime('%c'))

    os.system(command)

if __name__ == '__main__':
    args = docopt(__doc__, version='0.2')
    if not args['git-push'] and not args['auto']:
        # default
        default()

    elif args['git-push']:
        # commit and push git
        git_commit_and_push()

    elif args['auto']:
        # default + git-push
        default()
        git_commit_and_push()
