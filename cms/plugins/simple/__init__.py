from load_layer import SimpleLoader
from .settings import ARTICLE
from .settings import ABOUT
from .settings import HOME
from .settings import ARCHIVE
from .settings import ARTICLE_DIR
from .settings import ABOUT_DIR
from .settings import AVALIABLE_EXTENSIONS
from .settings import OUTPUT_DIR

from .command_process import GitPush
from .command_process import RunServer
from .preprocess import del_fragments
from .process import article_processor
from .process import home_processor
from .process import archive_processor
from .write import SimpleWriter


def register_command_processor():
    return [GitPush(), RunServer()]


def register_loader():
    
    article_loader = SimpleLoader(
        ARTICLE_DIR,
        AVALIABLE_EXTENSIONS,
        ARTICLE,
    )

    about_loader = SimpleLoader(
        ABOUT_DIR,
        AVALIABLE_EXTENSIONS,
        ABOUT,
    )

    return [article_loader, about_loader]


def register_preprocessor():
    return del_fragments


def register_processor():
    return [article_processor, home_processor, archive_processor]


def register_writer():
    return SimpleWriter()
