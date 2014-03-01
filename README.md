# Introduction

GeekCMS, short for 'geeky content management system', is a tool that can generate static pages with serval articles as its input.

# Architecture

## Lesson Learned
The system is designed with highly configurable property, meaning that the procedure of generating static pages is seperated into components, and the user could adjust the behavior by replacing some components of the system.

After developing GeekCMS v0.2.1, which became a big ball of mud, I've learned a lot about what should not be done and what should be done:

1. GeekCMS v0.2.1 is such a platform that can not do anything without plugins, the procedure from loading text file to writing static pages is performed by the logic of plugins. The idea behides that is plugin based architecture, which is just fine, but since GeekCMS v0.2.1 do not well define the protocals related to plugins, the system finally became a joke. Interfaces and protocals must be set up for plugin based architecture, by trading of some unnecessary freedom.
1. Lacks of definition of how user interacts with the system, including how user starts a project, how developer deploys their theme.
1. Lacks of unit test, which should be done.
1. GeekCMS v0.2.1 do not support python 2.x. Considering the popularity of python 2.x, the system should support it in following versions.

In short, the future work will foucs on the plugin protocals of the program.

## Basic Concept

### Project

GeekCMS would be finally deploied as a tool with command line interface(CLI), which essentially reads some text files and 'compile' it into another text files(mainly HTML pages). With the inspiration of Django's CLI and for better organization of input and output files, GeekCMS would maintained a directory containing all files required to generate a website, including user created articles and generated HTML static pages. Such directory is treated as a **projcet**.

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

* **themes**: Different from pelican and any other static page generators, _themes_ contains not only the templates but also some **codes** for formatting the website. Increasing flexibility is the mainly purpose of such design. If the system allows only Jinja2 templates to be placed in _themes_(methods has been done by pelican), the system must well defined kinds of templates and tags could be rendered by different kinds of templates, which limits the ways to generated web page and leads to a huge configuration file.
* **states**: As many static page generators, such as pelican, are considered stateless, which means the program would not keep the internal state of some data, such as the ordering of articles, insteads generating contents by all the input materials(such as markdown text files with meta-data). But there's sort of demands with which the program should not be stateless, such as ordering the articles in archive page(my classmate once tried to alert the ordering of artilces by changing the date meta-header in pelican). _states_ should be the directory keeping such information.
* **inputs**: _inputs_ holds text files with contents to be embeded in website.
* **outputs**: All final products would be placed in _outputs_.
* **settings**: A text file that contains necessary settings of the project.

_themes_ and _settings_ should be created and packaged by developers. Users of packages should just alerting the values in _settings_ and create some text files in _inputs_ following the introduction of the package developers. Detials of these items would be covered latter.

### Runtime Component

Runtime procedure of GeekCMS is divided into several componets(or periods), which would be sequentially executed by GeekCMS. Each runtime component could contain zero or more plugins, details of that would be covered latter.

Runtime components are as follow:

1. **pre_load**: the component prepares data for the _in_load_ component, for example, the component might generate a list consists of paths to be loaded based on files' last modified time, or extract a tree representing the relations of text files.
1. **in_load**: the component loads files from operating system(or somewhere else), and might process the content of files, such as transforming markdown to html.
1. **post_load**: the component cotains bussiness should be performed after _in_load_, for example, translating the title of each articles into english.
1. **pre_process**: the component prepares data for _in_proecess_, such as initiating pages with url.
1. **in_process**: the component might generate the content of static pages.
1. **post_process**: the component contains bussiness should be performed after _in_proecess_, for example, generating a sitemap of website.
1. **pre_write**: the component prepares data for _in_write_, for example, coping the static resources.
1. **in_write**: the component might write static pages to output directory.
1. **post_write**: the component contains bussiness should be performed after _in_write_, for example, compressing data with gzip.

Above nine components build up the **default procedure**, in which the text files would be transformed to several static web pages. The components can be classified into three layers, load/process/write. Notice that the distinction of components in a layer is vague, for instance, a plugin transforming markdown to html can be placed in _in_load_, _post_load_ or _pre_process_, depending on developers understanding of components' semantics.

Besides, there is kind of behaviors can not be classified into above nine components, such as automatically uploading static pages to a git repo. Such behavior could be implemented as **extended procedures**.


## Details of GeekCMS

### Responsibility of GeekCMS

### Plugin Protocal

### Theme Development

### Settings

# QuickStart

## A Simple Theme

## Examples





 







