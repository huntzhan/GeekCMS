# Introduction

GeekCMS, short for 'geeky content management system', is a tool that can generate static pages with serval articles as its input.

# Architecture

The system is designed with highly configurable property, meaning that the procedure of generating static pages is seperated into components, and the user could adjust the behavior by replacing some components of the system.

After developing GeekCMS v0.2.1, which became a big ball of mud, I've learned a lot about what should not be done and what should be done:

1. GeekCMS v0.2.1 is such a platform that can not do anything without plugins, the procedure from loading text file to writing static pages is performed by the logic of plugins. The idea behides that is 'plug and play', which is just fine, but since GeekCMS v0.2.1 do not well define the protocals related to plugins, the system finally became a joke. Interfaces and protocals must be set up for 'plug and play' architecture, by trading of some unnecessary freedom.
1. Lacks of definition of how user interacts with the system, including how user starts a project, how developer deploys their theme.
1. Lacks of unit test, which should be done.
1. GeekCMS v0.2.1 do not support python 2.x. Considering the popularity of python 2.x, the system should support it in following versions.

In short, the future work will foucs on the 'plug and play' protocals.
