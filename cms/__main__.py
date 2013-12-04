"""Usage: cms.py [git-push | auto | server]

Explanation:
    git-push  Commit and push git repo pointed by OUTPUT_DIR
    auto      Generate HTML and git-push
    server    Run Python SimpleHTTPServer in output working directory

"""

import os
from datetime import datetime
from docopt import docopt
from jinja2 import Environment
from jinja2 import FileSystemLoader

#from load import ArticleLoader
#from load import ArticleSetGenerator
#from process import ArticleSetPreprocessor
#from process import PageSetGenerator
#from printer import PageSetProcessor

#from settings import TEMPLATE_DIR
#from settings import OUTPUT_DIR

import configuration
import importlib
class Settings:

    def __init__(self):
        self.loaders = self._load_plugins(
            configuration.LOADERS,
            'register_loader',
        )

        self.preprocessors = self._load_plugins(
            configuration.PREPROCESSORS,
            'register_preprocessor',
        )

        self.processors = self._load_plugins(
            configuration.PROCESSORS,
            'register_processor',
        )

        self.writers = self._load_plugins(
            configuration.WRITERS,
            'register_writer',
        )

    def _load_plugins(self, plugin_names, func_name):
        plugins = []
        for plugin_name in plugin_names:
            if isinstance(plugin_name, str):
                module = importlib.import_module('plugins.' + plugin_name)
                plugin = getattr(module, func_name)()

            # check callable
            elif hasattr(plugin_name, '__call__'):
                plugin = plugin_name

            # make iterable
            if hasattr(plugin, '__iter__'):
                pass
            else:
                plugin = [plugin]

            plugins.extend(plugin)

        return plugins


from load_layer import load
from process_layer import preprocess
from process_layer import process
from write_layer import write

def test():
    settings = Settings()
    files = load(settings)
    fragments = preprocess(settings, files)
    pages = process(settings, fragments)
    write(settings, pages)


#def default():
#    article_loader = ArticleLoader()
#    preprocessor = ArticleSetPreprocessor()
#    page_set_processor = PageSetProcessor()
#
#    # load file
#    article_set_generator = ArticleSetGenerator(article_loader)
#    article_set = article_set_generator.article_set
#
#    # process content
#    loader = FileSystemLoader(TEMPLATE_DIR)
#    env = Environment(loader=loader)
#    page_set_generator = PageSetGenerator(
#        article_set,
#        env,
#        article_loader,
#        preprocessor
#    )
#    page_set = page_set_generator.page_set
#
#    # print
#    page_set_processor(page_set)
#
#
#def git_commit_and_push():
#    os.chdir(OUTPUT_DIR)
#
#    command = """git add --all *
#                 git commit -m 'GeekCMS Update, {}'
#                 git push
#              """.format(datetime.now().strftime('%c'))
#
#    os.system(command)
#
#
#def run_server():
#    os.chdir(OUTPUT_DIR)
#
#    command = """python -m http.server
#              """
#
#    os.system(command)


if __name__ == '__main__':
    args = docopt(__doc__, version='0.2')

    #if args['server']:
    #    run_server()

    #elif args['git-push']:
    #    # commit and push git
    #    git_commit_and_push()

    #elif args['auto']:
    #    # default + git-push
    #    default()
    #    git_commit_and_push()

    #else:
    #    # default
    
    test()
