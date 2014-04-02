Deploy And Download Themes
==========================

Command Line Interface
----------------------

GeekCMS provides a friendly CLI interface of usage.
CLI of GeekCMS is implemented by using docopt_.

For code sharing, developer could package their codes as a template. A template is organized in
as a project.

Download
--------

If you type :code:`geekcms` in your prompt and current working directory is not a project,
then the shell would presents::

   $ geekcms
   Usage:
       geekcms startproject <template_name>

Entering :code:`startproject` option with <template_name> would automatically download a
directory with the name of <template_name>, which should be an empty project,
from `GeekCMS-Themes`_ to current working directory::

   $ ls
   $ geekcms startproject simple
   A    simple/inputs
   A    simple/inputs/about
   A    simple/inputs/about/about.md
   A    simple/inputs/article
   A    simple/inputs/article/test
   A    simple/inputs/article/test/codetest.md
   A    simple/inputs/article/test/longlong.md
   A    simple/inputs/article/test/top-level.md
   A    simple/inputs/index
   A    simple/inputs/index/welcome.md
   A    simple/inputs/static
   A    simple/inputs/static/delete it.
   A    simple/settings
   A    simple/themes
   A    simple/themes/git_upload
   A    simple/themes/git_upload/__init__.py
   A    simple/themes/git_upload/plugin.py
   A    simple/themes/git_upload/settings
   A    simple/themes/simple
   A    simple/themes/simple/__init__.py
   A    simple/themes/simple/assets.py
   A    simple/themes/simple/load.py
   A    simple/themes/simple/process.py
   A    simple/themes/simple/settings
   A    simple/themes/simple/static
   A    simple/themes/simple/static/css
   A    simple/themes/simple/static/css/github.css
   A    simple/themes/simple/templates
   A    simple/themes/simple/templates/archive.html
   A    simple/themes/simple/templates/article.html
   A    simple/themes/simple/templates/base.html
   A    simple/themes/simple/templates/time_line.html
   A    simple/themes/simple/utils.py
   A    simple/themes/simple/write.py
   Checked out revision 15.
   $ ls
   simple

After downloading such directory, GeekCMS would ensure *project settings* and *themes*,
*states*, *inputs*, *outputs* exists, so developer should not consider pushing an empty
directory to git repo.


Deploy
------

If you want to share your code with the others, just push your code to `GeekCMS-Themes`_.



.. _docopt: https://github.com/docopt/docopt
.. _`GeekCMS-Themes`: https://github.com/haoxun/GeekCMS-Themes

.. target-notes::
