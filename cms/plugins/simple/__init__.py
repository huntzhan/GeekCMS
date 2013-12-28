from load_layer import ContentFileLoader
from load_layer import VirtualFileLoader

from .settings import ARTICLE
from .settings import ABOUT
from .settings import ARTICLE_DIR
from .settings import ABOUT_DIR
from .settings import AVALIABLE_MD_EXTENSIONS

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

    article_loader = ContentFileLoader(
        ARTICLE_DIR,
        AVALIABLE_MD_EXTENSIONS,
        ARTICLE,
    )

    about_loader = ContentFileLoader(
        ABOUT_DIR,
        AVALIABLE_MD_EXTENSIONS,
        ABOUT,
    )

    article_resource_loader = VirtualFileLoader(
        ARTICLE_DIR,
        AVALIABLE_MD_EXTENSIONS,
    )

    about_resource_loader = VirtualFileLoader(
        ABOUT_DIR,
        AVALIABLE_MD_EXTENSIONS,
    )

    return [
        article_loader,
        article_resource_loader,
        about_loader,
        about_resource_loader,
    ]


def register_preprocessor():
    return del_fragments


def register_processor():
    return [
        article_processor,
        home_processor,
        archive_processor
    ]


def register_writer():
    return SimpleWriter()
