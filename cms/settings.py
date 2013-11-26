from extensions.max_depth_toc import MaxDepthTocExtension

OUTPUT_DIR = ''
ARTICLE_DIR = ''
ARCHIVE_DIR_NAME = ''
TEMPLATE_DIR = ''

MD_EXTENSIONS = [
    # necessary extensions
    'meta',
    # optional extensions
    MaxDepthTocExtension(),
]
