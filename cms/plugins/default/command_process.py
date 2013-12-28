from command_layer import CommandProcessor
from datetime import datetime
import os
from .settings import OUTPUT_DIR

class GitPush(CommandProcessor):

    def doc_elements(self):
        return (
            'git-push',
            None,
            'Commit and push git repo pointed by OUTPUT_DIR',
        )

    def check(self, args):
        if args['git-push']:
            return True
        return False

    def run(self):
        os.chdir(OUTPUT_DIR)
        command = """git add --all
                     git commit -m 'GeekCMS Update, {}'
                     git push
                  """.format(datetime.now().strftime('%c'))
        os.system(command)


class RunServer(CommandProcessor):

    def doc_elements(self):
        return (
            'server',
            None,
            'Run Python SimpleHTTPServer in output working directory',
        )

    def check(self, args):
        if args['server']:
            return True
        return False

    def run(self):
        os.chdir(OUTPUT_DIR)
        command = """python -m http.server
                  """
        os.system(command)
