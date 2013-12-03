from load_layer import SimpleLoader

def register_loader():
    return SimpleLoader('/Users/peter/Data/Project/haoxun.github.io/Article/articles',
                        '.md', 'articles')
