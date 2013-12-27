# all plugins should be place in /cms/plugins

# plugin package's __init__.py should contain a func named
# register_command_processor
# that returns a callable.
COMMAND_PROCESSORS = [
    'simple',
]

# plugin package's __init__.py should contain a func named
# register_loader
# that returns a callable.
LOADERS = [
    'simple',
]

# plugin package's __init__.py should contain a func named
# register_preprocessor
# that returns a callable.
PREPROCESSORS = [
    'markdown',
    'simple',
]

# plugin package's __init__.py should contain a func named
# register_processor
# that returns a callable.
PROCESSORS = [
    'simple',
]

# plugin package's __init__.py should contain a func named
# register_postprocessor
# that returns a callable.
POSTPROCESSORS = [
]

# plugin package's __init__.py should contain a func named
# register_writer
# that returns a callable.
WRITERS = [
    'simple',
]
