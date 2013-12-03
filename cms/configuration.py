from load_layer import SimpleLoader
# all plugins should be place in plugins

# __init__.py should contain a func named register_loader
# that returns a handler.
LOADERS = [
    SimpleLoader('/Users/peter/Data/Project/haoxun.github.io/Article/articles',
                 '.md', 'articles'),
    SimpleLoader('/Users/peter/Data/Project/haoxun.github.io/Article/about',
                 '.md', 'about'),


]

# __init__.py should contain a func named register_preprocessor
# that returns a handler.
PREPROCESSORS = [

]

# __init__.py should contain a func named register_processor
# that returns a handler.
PROCESSORS = [

]

# __init__.py should contain a func named register_printer
# that returns a handler.
PRINTERS = [

]
