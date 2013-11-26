from extensions.max_depth_toc import MaxDepthTocExtension

#OUTPUT_DIR = '/Users/peter/Data/Project/GeekCMS/GeekCMS/output'
#ARTICLE_DIR = '/Users/peter/Data/Project/GeekCMS/GeekCMS/Article'
NORMAL_DIR = 'articles'
TEMPLATE_DIR = '/Users/peter/Data/Project/GeekCMS/GeekCMS/templates'


ARTICLE_DIR = '/Users/peter/Data/Project/haoxun.github.io/Article'
OUTPUT_DIR = '/Users/peter/Data/Project/haoxun.github.io'


MD_EXTENSIONS = [
    # necessary extensions
    'meta',
    # optional extensions
    MaxDepthTocExtension(),
]
