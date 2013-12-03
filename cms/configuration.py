from load_layer import SimpleLoader
# all plugins should be place in plugins

# __init__.py should contain a func named register_loader
# that returns a callable.
LOADERS = [
    SimpleLoader('/Users/peter/Data/Project/haoxun.github.io/Article/articles',
                 '.md', 'articles'),
    SimpleLoader('/Users/peter/Data/Project/haoxun.github.io/Article/about',
                 '.md', 'about'),

]

# __init__.py should contain a func named register_preprocessor
# that returns a callable.
PREPROCESSORS = [

]

# __init__.py should contain a func named register_processor
# that returns a callable.
PROCESSORS = [

]

# __init__.py should contain a func named register_printer
# that returns a callable.
PRINTERS = [

]
