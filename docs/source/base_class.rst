
Protocol Related Classes
========================

GeekCMS defines serveral protocols for plugin registration and data operation.
All following classes are defined in *geekcms.protocol*.

Assets Related
--------------

.. class:: _BaseAsset(*args, **kwargs)

   _BaseAsset is the base class of :class:`BaseResource`, :class:`BaseProduct` and :class:`BaseMessage`.
   Initialize :class:`_BaseAsset` would Always raise an Exception, since _BaseAsset should not be initialized.


   .. method:: _BaseAsset.set_owner(self, owenr)
   
         Set the owner of asset instance. Instance of derived classes of :class:`_BaseAsset` must defined an owner, which
         should be the name of theme.
   
   .. classmethod:: _BaseAsset.get_manager_with_fixed_owner(cls, owner)
   
         Return an instance of :class:`ManagerProxyWithOwner`, bound with *cls* and *owner*.
   
   .. attribute:: objects
      
         Retrive an instance of :class:`Manager`, which bound with :class:`BaseResource`, :class:`BaseProduct` and :class:`BaseMessage`
         and its derived classes.


.. class:: BaseResource(*args, **kwargs)
   
   class derived from :class:`_BaseAsset`.


.. class:: BaseProduct(*args, **kwargs)

   class derived from :class:`_BaseAsset`.


.. class:: BaseMessage(*args, **kwargs)

   class derived from :class:`_BaseAsset`.


:class:`BaseResource`, :class:`BaseProduct` and :class:`BaseMessage` are base classes for data operations.
Developer should derived one of these classes for specific usage. Derived classes should overwrite `__init__` method,
since :class:`_BaseAsset` defines a `__init__` method which always raise an Exception.


.. class:: Manager(target_cls, data=None)

   The class derives from :class:`UserDict`.
   *target_cls* is a class derives from :class:`BaseResource`, :class:`BaseProduct` or :class:`BaseMessage`.
   *data* is a dictionary that used to store instances created by manager. If *data* is :class:`None`, a default dictionary would be initialized.

   .. method:: add(self, item)

         Add instance.

   .. method:: remove(self, item)
      
         Remove instance.

   .. method:: keys(self)

         Returns a list contanins all the owner of stored items.

   .. method:: create(self, *args, owner, **kwargs)

         Create and store an instance of :code:`self.target_cls`, with arguments :code:`(*args, **kwargs)`.
         *owner* is a keyword-only parameter.

   .. method:: filter(self, owner):

         Return a list of instances that:

         *  *owner* is the owner of instance.

         *  :code:`isinstance(instance, self.target_cls)` is True.

   .. method:: values(self)

         Return a list of instances that :code:`isinstance(instance, self.target_cls)` is True.

   .. method:: clear(self)

         Clean up all stored items.


.. class:: ManagerProxyWithOwner(self, owner, manager)

   Instance of this class would be a proxy of :class:`Manager` with fixed owner.
   All functions defined in :class:`Manager` are avaliable, except that the parameter *owner* is excluded from functions' parameter list.
   *manager* is an instance of :class:`Manager`, and *owner* is the owner to be fixed.


Default Procedure Related
-------------------------

.. class:: BasePlugin()

   .. classmethod:: get_manager_bind_with_plugin(cls, other_cls)

      Return an instance of :class:`ManagerProxyWithOwner` bound to class of asset.
      *other_cls* should be one of :class:`BaseResource`, :class:`BaseProduct` and :class:`BaseMessage` and its derived classes.
   

   .. method:: run(self, resources=None, products=None, messages=None)

      The interface that a derived plugin class must overwrite. `run` should be a function that implements plugin's bussiness.
      The return value of `run` function would be discarded.

      *resources* would be a list contains instances of :class:`BaseResource` or its derived class.
      *products* would be a list contains instances of :class:`BaseProduct` or its derived class.
      *messages* would be a list contains instances of :class:`BaseMessage` or its derived class.

All user defined plugin classes should derive from :class:`BasePlugin` and overwrite the `run` function.

Besides, class-level attributes *theme* and *plugin* can be defined for further customization. For exmaple::

   from geekcms import protocol
   
   class TestPlugin(protocol.BasePlugin):
   
       theme = 'test_theme'
       plugin = 'test_plugin'

       def run(self):
           pass

Explanation of class-level attributes are as follow:

   *theme*
      Defines the theme that a plugin belongs to.
      Value of theme that would be used to filter resources, products or messages passed to run method.
      For instances, suppose class *A*, *B* both definded :code:`theme = 'AB'`,
      and there is another class C definded :code:`theme = 'C'`.
      If *A*\ 's `run` method created some instance of resources owned by 'AB',
      and *B*, *C* were executed after *A*, then *B*\ 's `run` function might receive instances of
      resource created by *A*\ (or might not, due to the parameter controller) while *C*\ 's run function would not
      receive instances created by *A*. This attribute could be omitted,
      in such case the name of theme's top-level directory would be adapt.
   *plugin*
      Defines the name of plugin which related to the plugin names of theme settings.
      This attribute could be omitted, in that case, the class name would be used as the plugin name.

The parameter list of overwrited `run` function is a bit more complicated.
Since the bussiness of plugins various a lot, developers might defind `run` function with different parameters, such as::

   from geekcms import protocol
   
   class TestPlugin(protocol.BasePlugin):
   
       theme = 'test_theme'
   
       # accept all assets.
       def run(self, resources, products, messages):
           pass
   
       # only accept resources.
       def run(self, resources):
           pass
   
       # accept nothing.       
       def run(self):
           pass
   
GeekCMS would detect the signature of run function, with the default order `[resources, products, messages]`.
For example, if developer defined a run function with two positional parameters,
then GeekCMS would pass instances of resources and products to such function.


For further control of parameter list, developers should consider using decorators defined in :class:`PluginController`.

.. class:: PluginController

   .. attribute:: RESOURCES
   
         String indicating :class:`BaseResource` and its derived classes.
   
   .. attribute:: PRODUCTS
   
         String indicating :class:`BaseProduct` and its derived classes.
   
   .. attribute:: MESSAGES
   
         String indicating :class:`BaseMessage` and its derived classes.
   
   .. classmethod:: accept_owners(cls, *owners)

         `accept_owners` is a decorator for plugin's `run` function.
         The owner of assets passed into `run` function would be adjusted, with respect to *owners*.
         *owners* should be a list of avaliable owners.

   .. classmethod::  accept_parameters(cls, *fixed_params, **typed_params)

         `accept_parameters` is a decorator for plugin's `run` function. By decorating,
         the order and type of parameters would be adjusted, with respect to *fixed_params* and *typed_params*.

         *fixed_params* should be a list of: 

            * string of `[RESOURCES, PRODUCTS, MESSAGES]`. 
            * two-element tuple(or list) in the form of *(name, accept_cls)*,
              in which *name* should be string of `[RESOURCES, PRODUCTS, MESSAGES]`
              and *accept_cls* should be class of asset.

         *typed_params* is a dictionary with key-value pairs *(name, accept_cls)*,
         in which *name* should be string of `[RESOURCES, PRODUCTS, MESSAGES]`
         and *accept_cls* should be class of asset.

Example of `accept_parameters`:: 

   from geekcms import protocol
   pcl = protocol.PluginController
   
   
   class DerivedMessage(protocol.BaseMessage):
   
       def __init__(self):
           pass
   
   
   class TestPlugin(protocol.BasePlugin):
       theme = 'test_theme'

       # accept only messages of BaseMessage.
       @pcl.accept_parameters(pcl.MESSAGES)
       def run(self, messages):
           pass
   
       # accept only messages of DerivedMessage.
       @pcl.accept_parameters(
           (pcl.MESSAGES, DerivedMessage),
       )
       def run(self, messages):
           pass
   
       # accept only messages of DerivedMessage.
       @pcl.accept_parameters(
           **{pcl.MESSAGES: DerivedMessage}
       )
       def run(self, messages):
           pass

       # accept only messages of DerivedMessage.
       @pcl.accept_parameters(
           messages=DerivedMessage,
       )
       def run(self, messages):
           pass
   
Example of `accept_owners`::

   from geekcms import protocol
   
   pcl = protocol.PluginController
   
   class TestPlugin(protocol.BasePlugin):
   
       # accept only messages owned by test_theme and another_theme.
       @pcl.accept_parameters(pcl.MESSAGES)
       @pcl.accept_owners('test_theme', 'another_theme')
       def run(self, messages):
           pass

.. _extend_procedure_relate:
   
Extended Procedure Related
--------------------------

.. class:: BaseExtendedProcedure()

   .. method:: get_command_and_explanation(self)
      
      Should be a function returns *(command, explanation)* tuple,
      with *command* as string to trigger the extended procedure
      and *explanation* as a brief explanation of the extended procedure.
      Derived class should overwrite this function.

   .. method:: get_doc(self)
      
      Should return string that can be parsed by docopt_.
      Derived class should overwrite this function.

   .. method:: run(self, args)

      `run` should be a function that implements plugin's bussiness.
      *args* is the processed arguments return by docopt.
      The return value of `run` function would be discarded.
      Derived class should overwrite this function.


Plugins class of extended procedure should derive from :class:`BaseExtendedProcedure`.


.. _docopt: https://github.com/docopt/docopt


.. target-notes::
