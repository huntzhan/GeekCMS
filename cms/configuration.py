# all plugins should be place in plugins

# __init__.py should contain a func named register_command_processor
# that returns a callable.
COMMAND_PROCESSORS = [
    'simple',
]

# __init__.py should contain a func named register_loader
# that returns a callable.
LOADERS = [
    'simple',
]

# __init__.py should contain a func named register_preprocessor
# that returns a callable.
PREPROCESSORS = [
    'markdown',
    'simple',
]

# __init__.py should contain a func named register_processor
# that returns a callable.
PROCESSORS = [
    'simple',
]

# __init__.py should contain a func named register_writer
# that returns a callable.
WRITERS = [
    'simple',
]
