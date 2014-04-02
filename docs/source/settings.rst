Project Organization
====================

Structure Of Project
--------------------

GeekCMS would maintained a directory containing all files required to generate a website,
such directory is organized as a *projcet*.

Sturcture of a project is as follow:

.. code-block:: text

   example_project/
                   themes/
                       ...
                   states/
                       ...
                   inputs/
                       ...
                   outputs/
                       ...
                   settings

Brief explanations of above file and direcroties:

   *themes*
      
      A directory where all the code of theme exists.

   *states*
      
      A directory for themes to place its intermediate data.

   *inputs*

      A direcroty contains all input files.

   *outputs*

      A directory contains all generated files.

   *settings*
      
      A text file named *project settings*, in which defines registered themes and global shared data.

The names of above file and direcroties is hardcoded in GeekCMS.


Structure Of Theme
------------------

A theme should be organized as a *python package*, structure is as follow:

.. code-block:: text

   example_project/
                   themes/
                          theme_A/
                              __init__.py
                              settings       # theme settings
                              ...
                          theme_B/
                              __init__.py
                              settings       # theme settings
                              ...
                   states/
                       ...
                   inputs/
                       ...
                   outputs/
                       ...
                   settings                  # project settings

All themes should be placed in *themes* directory.
As you can see, there is *settings file* exists in each theme package.
Such settings file is named *theme settings*.


Settings File
-------------

GeekCMS's behavior is guided by *project settings* and *theme settings*.
Format of *settings* is described in configparser_.

*projcet settings* should defines a *RegisterTheme*\ (case-sensitive) section.
Names of themes(the name of theme's directory) to be loaded by GeekCMS should
be seperated by whitespaces and set as the value of *themes* key(case-insensitive). Example is as follow::
   
   # project settings.
   [RegisterTheme]
   themes: simple git_upload

where directories *simple* and *git_upload* are registered.

*themes settings* should defines a *RegisterPlugin*\ (case-sensitive) section.
Keys in the section should be one of *[pre_load, in_load, post_load, 
pre_process, in_process, post_process, pre_write, in_write, post_write]* and *[cli_extend]*.
All avaliable keys except *cli_extend* is discussed in :ref:`default_procedure`, and *cli_extend*
is a key for registering *extended procedure*. An example for demonstration::

   # settings of simple.
   [RegisterPlugin]
   
   in_load:
           load_inputs_static
           load_article
           load_about
           load_index
           load_theme_static
   
   in_process:
           md_to_html << gen_article_page
   
   post_process:
           gen_about_page
           gen_index_page
           gen_time_line_page
           gen_archive_page
   
   pre_write:
           clean
   
   in_write:
           write_static
           write_page
   
   post_write:
           cname

   # settings of git_upload
   [RegisterPlugin]

   cli_extend: GitUploader

Both *projcet settings* and *theme settings* can define a *Share* section.
Key-value pairs defined in *Share* section can be retrived by :class:`ShareData`.
An example for demonstration::

   # settings of simple.
   [Share]
   # special pages
   index_page: index.html
   time_line_page: speical/time_line.html
   about_page: speical/about.html
   archive_page: speical/archive.html

where the value of *index_page* can be retrived by :code:`ShareData.get('simple.index_page')`.


Plugin Registration
-------------------

Execution order of plugins within the same *runtime component* is defined by
*plugin registration syntax*. The syntax is:

.. productionlist::
   runtime_component    : component_name (':' | '=') [NEWLINE] plugin_relation*
   plugin_relation      : binary_relation_expr | unary_relation_expr NEWLINE
   binary_relation_expr : plugin_name (left_relation | right_relation) plugin_name
   unary_plugin_expr    : plugin_name [left_relation]
                        : | [right_relation] plugin_name
   left_relation        : '<<' [decimalinteger]
   right_relation       : [decimalinteger] '>>'
   component_name       : identifier
   plugin_name          : identifier

where *identifier*, *decimalinteger* and *NEWLINE* are corresponding to the definitions in
`Python Lexical Analysis`_.

Semantics:

    1. :code:`pre_load: my_loader`
           register plugin `my_loader` to component `pre_load`.

    2. :code:`pre_load: my_loader << my_filter`
           register plugins `my_loader` and
           `my_filter` to component `pre_load`, with `my_loader` being executed before
           `my_filter`.

    3. :code:`pre_load: my_filter >> my_loader`
           has the same meaning as `pre_load: my_loader << my_filter`.

    4. :code:`pre_load: loader_a <<0 loader_b NEWLINE loader_c <<1 loader_b`
           the execution order would be `loader_c` --> `loader_a` --> `loader_b`.
           `<<` is equivalent to `<<0`, and `<< decimalinteger` is equivalent to
           `decimalinteger >>`.

    5. :code:`pre_load: my_loader <<`
           means `my_loader` would be executed before the
           other plugins within a component, unless another relation such as
           `anther_loader <<1` is established.

    6. :code:`pre_load: >> my_filter`
           reverse meaning of `pre_load: my_loader <<`.

Notice that the *plugin_name* should be presented in the pattern of  'theme_name.plugin_name'.
'theme_name.' can be omitted, as presented in above example, if *plugin_name* points to a plugin exists in current theme directory.


GeekCMS would automatically import the `__init__` module of registered theme packages.
Besides writing a *theme settings*, developer should import the module(s) that defines plugin(s) in `__init__`.
An example is given for demonstration::

   # ../git_upload/__init__.py
   
   # necessary!
   from . import plugin


   # ../git_upload/plugin.py
   
   """
   Usage:
       geekcms gitupload
   
   """
   
   from datetime import datetime
   import subprocess
   import os
   
   from geekcms.protocol import BaseExtendedProcedure
   from geekcms.utils import PathResolver
   
   
   class CWDContextManager:
   
       def __enter__(self):
           os.chdir(PathResolver.outputs())
   
       def __exit__(self, *args, **kwargs):
           os.chdir(PathResolver.project_path)
   
   
   class GitUploader(BaseExtendedProcedure):
   
       def get_command_and_explanation(self):
           return ('gitupload',
                   'Automatically commit and push all files of outputs.')
   
       def get_doc(self):
           return __doc__
   
       def run(self, args):
           commit_text = 'GeekCMS Update, {}'.format(
               datetime.now().strftime('%c'),
           )
           commands = [
               ['git', 'add', '--all', '.'],
               ['git', 'commit', '-m', commit_text],
               ['git', 'push'],
           ]
           with CWDContextManager():
               for command in commands:
                   subprocess.check_call(command)

GeekCMS would automatically loaded :code:`GitUploader` in above example.


.. _configparser: http://docs.python.org/3/library/configparser.html
.. _`Python Lexical Analysis`: http://docs.python.org/3/reference/lexical_analysis.html

.. target-notes::
