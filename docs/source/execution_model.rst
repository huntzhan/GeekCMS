.. _ecex_model:

Execution Model
===============

From the view of theme(in short, **theme = theme settings + plugins**\ ) developers,
GeekCMS is a framework with protocols and helpful libraries, to:

*  control the behavior of each individual plugin.

*  customize the calling sequence of multiple plugins.


For users, GeekCMS is a theme driven tool, means that without plugins, GeekCMS can do nothing!


There are two kinds of plugin execution procedures defined in GeekCMS:

*  **Default procedure**: Procedure consists of several runtime components. A runtime component is an area to place plugins to be executed.

*  **Extended procedure**: Besides, there are kinds of behaviors can not be classified into components,
   for instance, automatically pushing static pages to a remote git repo.
   Such behaviors could be implemented as independent extended procedures, and triggered by CLI command by user.


.. _default_procedure:

Default Procedure
-----------------


Default procedure is divided into *nine* runtime components:

#. *pre_load*, *in_load*, *post_load*

#. *pre_process*, *in_process*, *post_process*

#. *pre_write*, *in_write*, *post_write*

which would be sequentially executed by GeekCMS. Each runtime component could contain zero or more plugins, details of that would be covered later.

The components can be classified into three layers, load/process/write.
Layers are exectured in order, **load --> process --> write**, which is simple and intuitive.
Notice that the distinction of components is vague,
for instance, a plugin transforming markdown to html can be placed in *in_load*, *post_load* or even *post_write*,
depending on developers understanding of components' semantics.
By dividing a layer into three components, theme developer could well control the sequence of plugin execution.
Plugin execution order within a layer is a little bit complicated, and would be introduce later.

Extended Procedure
------------------

GeekCMS allow developer to define extended procedure for special usage. For more information: :ref:`extend_procedure_relate`.
