# Warning

**This document contains information related to prototype design of GeekCMS, might change quickly and leak of necessary information.**

# Introduction

GeekCMS, short for 'geeky content management system', is a tool that can generate static pages with serval articles as its input.

# Architecture

## Lesson Learned
The system is designed to be highly configurable, meaning that the runtime procedure of generating static pages is seperated into components, and the user could control the behavior by replacing some components of the system.

After developing GeekCMS v0.2.1, which became "a big ball of mud", I've learned a lot about what should and should not be done:

1. GeekCMS v0.2.1 is such a platform that can not do anything without plugins, bussinesses from loading text file to writing static pages are performed by plugins. The idea behides that is plugin based architecture, which is just fine, but since GeekCMS v0.2.1 do not well define the protocals that was necessary, and finally the system became a joke. Interfaces and protocals must be set up for plugin based architecture, by trading of some unnecessary freedom.
1. Lacks of definition of how user interacts with the system, including how user starts a project, how developer deploys their theme.
1. Lacks of unit test, which should be done.
1. GeekCMS v0.2.1 do not support python 2.x. Considering the popularity of python 2.x, the system should support it in following versions.

In short, the future work will foucs on the plugin protocals of the program.

## Basic Concept

### Project

GeekCMS would be finally deploied as a tool with command line interface(CLI), which essentially reads some text files and transform it to another text files(mainly HTML pages). With the inspiration of Django's CLI and for better organization of input and output files, GeekCMS would maintained a directory containing all files required to generate a website, including user created articles and images. Such directory is treated as a **projcet**.

Sturcture of a project is as follow:
	
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

Brief explanations of each item:

* **themes**: Different from pelican and any other static page generators, _themes_ contains not only the templates but also some **codes** for formatting the website. Increasing flexibility is the purpose of such design. If the system allows only Jinja2 templates to be placed in _themes_(methods has been done by pelican), the system must well defined kinds of templates and tags could be rendered by different kinds of templates, which limits the ways to generated web page and leads to a huge configuration file.
* **states**: As many static page generators, such as pelican, are considered stateless, which means the program would not keep the internal state of some data, such as the ordering of articles, insteads generating contents by all the input materials(such as markdown text files with meta-data). But there's sort of demands with which the program should not be stateless, such as ordering the articles in archive page(my classmate once tried to alert the ordering of artilces by changing the date meta-header in pelican). _states_ should be the directory keeping such information.
* **inputs**: _inputs_ holds text files with contents to be embeded in website.
* **outputs**: All final products would be placed in _outputs_.
* **settings**: A text file that contains necessary settings of the project.

_themes_ and _settings_ should be created and packaged by developers. Users of packages should just alerting the values in _settings_ and create some text files in _inputs_ following the introduction of the package developers. Detials of these items would be covered later.

### Layer, Runtime Component and Plugin

Runtime procedure of GeekCMS is divided into several componets(or periods), which would be sequentially executed by GeekCMS. Each runtime component could contain zero or more **plugins**, details of that would be covered later.

All runtime components of GeekCMS are as follow:

1. **load layer**:
	1. **pre_load**: prepares data for the *in_load* component, for example, the component might generate a list consists of paths to be loaded based on files' last modified time, or extract a tree representing the relations of text files.
	1. **in_load**: loads files from operating system(or somewhere else), and might process the content of files, such as transforming markdown to html.
	1. **post_load**: cotains bussiness should be performed after *in_load*, for example, translating the title of each articles into english.
1. **process layer**:
	1. **pre_process**: prepares data for *in_proecess*, such as initiating pages with url.
	1. **in_process**: might generate the content of static pages.
	1. **post_process**: contains bussiness should be performed after *in_proecess*, for example, generating a sitemap of website.
1. **write layer**:
	1. **pre_write**: prepares data for *in_write*, for example, coping the static resources.
	1. **in_write**: might write static pages to output directory.
	1. **post_write**: contains bussiness should be performed after *in_write*, for example, compressing data with gzip.

The components can be classified into three **layers**, load/process/write. Notice that the distinction of components **within a layer** is vague, for instance, a plugin transforming markdown to html can be placed in *in_load* or *post_load*, depending on developers understanding of components' semantics. By dividing a layer into three components, theme developer could well control the sequence of plugin execution. Plugin execution order within a layer is a little bit complicated, and would be introduce later.

As mentioned, runtime components are classified into three *layers*, *load*, *process* and *write*. Information of layers are as follow:

* **Execution**: Layers are exectured in order, **load --> process --> write**, very simple and intuitive.
* **Communication**: Actually, layers could be viewed as implementation of pipe-and-filter architecture.
	* **load** layer would deliver some **resources** and **messages** to *process* layer.
	* **process** layer would process **resource** and deal with **messages**, generating **products** and some other **messages**, and deliver them to **write** layer.
	* **write** layer would process **products** and deal with **messages**, and execute logic related to generate output files.
	
	**resource**, **product**, **message** are data structures provided by GeekCMS.
	
### Default/Extended Procedure(s)

* **Default procedure**: Procedure consists of all nine runtime components, in which the text files would be transformed to several static web pages. 
* **Extended procedures**: Besides, there is kind of behaviors can not be classified into above components, for instance, automatically uploading static pages to a git repo. Such behaviors could be implemented as independent *extended procedures*, and triggered by CLI options by GeekCMS.

## Details of GeekCMS

### Responsibility of GeekCMS and Themes

From the view of theme(in short, **theme = templates + plugins**) developers, GeekCMS is a *platform* with various tools and protocals which would be helpful for plugin and theme development. It's important to know that, GeekCMS is a **plugin driven tool. 
Without a theme, GeekCMS can do nothing!**

### Theme/Plugin Protocal

#### Plugin Registration

For explanation, an example project structure is presented here:

	example_project/
		themes/
			theme_A/
				settings
				...
			theme_B/
				settings
				...
		states/
			...
		inputs/
			...
		outputs/
			...
		settings

**settings** files, both for project and themes, should be written in INI format, which can be parsed by [configparser](http://docs.python.org/3/library/configparser.html#module-ConfigParser). There are two kind of **settings** files, one for **project** and the other for **theme**:

* **theme settings**: a text file with information of plugins contained by theme, such as names and the execution order of plugins. This file should be maintained by theme developer.
* **project settings**: a text file contains settings should be customized by user. This file should be created by developer with guidance.

**theme settings** handles **plugin registration**, while **project settings** handles **theme registration**.

It's easy to customize plugins' execution order by placing them in different *runtime components*, for more, GeekCMS support some syntax to customize plugins' execution order **within** a *runtime component*.

For demonstration, plugin section of **theme setting** is presented:

	[Plugin]
	# load layer
	pre_load:
	in_load:
	post_load:
	
	# process layer
	pre_process:
	in_process:
	post_process:
	
	# write layer
	pre_write:
	in_write:
	post_write:

Above configuration presents an "empty" theme, nothing would happen if such theme were registered in *project settings*, because the theme does not register any plugins. 

In *settings* files, section headers(i.e. [Plugin]) is case-sensitive but keys are not(i.e. for "pre_load", you can type "PRE_LOAD" as well). If a runtime component do not contain a plugin, the name of that component can be delete from *theme settings*.

Syntax of ordering plugins within a runtime component is as follow:

	runtime_component ::= component_name (':' | '=') [NEWLINE] plugin_relation*
	
	plugin_relation ::= binary_relation_expr | unary_relation_expr NEWLINE
	binary_relation_expr ::= plugin_name (left_relation | right_relation) plugin_name
	unary_plugin_expr ::= (plugin_name [left_relation]) | ([right_relation] plugin_name)
	
	left_relation ::= '<<' [decimalinteger]
	right_relation ::= [decimalinteger] '>>'
	component_name ::= identifier
	plugin_name ::= identifier
	
*identifier*, *decimalinteger* and *NEWLINE* are corresponding to the definitions in [Python Lexical Analysis](http://docs.python.org/3/reference/lexical_analysis.html).

Semantics of above syntax are as follow:

"pre_load: my_loader": register plugin "my_loader" to component "pre_load".

"pre_load: my_loader << my_filter": register plugins "my_loader" and "my_filter" to component "pre_load", with "my_loader" being executed **before** "my_filter".

"pre_load: my_filter >> my_loader": has the same meaning as "pre_load: my_loader << my_filter".

"pre_load: loader_a <<0 loader_b NEWLINE loader_c <<1 loader_b"
the execution order would be "loader_c" --> "loader_a" --> "loader_b". "<<" is equivalent to "<<0", and "<< decimalinteger" is equivalent to "decimalinteger >>".

"pre_load: my_loader <<": means "my_loader" would be executed before the other plugins within a component, unless another relation such as "anther_loader <<1" is established.

"pre_load: >> my_filter": reverse meaning of "pre_load: my_loader <<".


#### Tools Provided By GeekCMS

#### File Organization



# QuickStart

## A Simple Theme

## Examples





 







