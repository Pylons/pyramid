.. _hooks_chapter:

Using Hooks
===========

"Hooks" can be used to influence the behavior of the :mod:`repoze.bfg`
framework in various ways.

.. index::
   single: not found view

.. _changing_the_notfound_view:

Changing the Not Found View
---------------------------

When :mod:`repoze.bfg` can't map a URL to view code, it invokes a
:term:`not found view`, which is a :term:`view callable`. A default
notfound view exists.  The default not found view can be overridden
through application configuration.  This override can be done via
:term:`imperative configuration` or :term:`ZCML`.

The :term:`not found view` callable is a view callable like any other.
The :term:`view configuration` which causes it to be a "not found"
view consists only of naming the :exc:`repoze.bfg.exceptions.NotFound`
class as the ``context`` of the view configuration.

.. topic:: Using Imperative Configuration

   If your application uses :term:`imperative configuration`, you can
   replace the Not Found view by using the
   :meth:`repoze.bfg.configuration.Configurator.add_view` method to
   register an "exception view":

   .. code-block:: python
      :linenos:

      from repoze.bfg.exceptions import NotFound
      from helloworld.views import notfound_view
      config.add_view(notfound_view, context=NotFound)

   Replace ``helloworld.views.notfound_view`` with a reference to the
   Python :term:`view callable` you want to use to represent the Not
   Found view.

.. topic:: Using ZCML

   If your application uses :term:`ZCML`, you can replace the Not Found
   view by placing something like the following ZCML in your
   ``configure.zcml`` file.

   .. code-block:: xml
      :linenos:

      <view
        view="helloworld.views.notfound_view"
        context="repoze.bfg.exceptions.NotFound"/>

   Replace ``helloworld.views.notfound_view`` with the Python dotted name
   to the notfound view you want to use.

Like any other view, the notfound view must accept at least a
``request`` parameter, or both ``context`` and ``request``.  The
``request`` is the current :term:`request` representing the denied
action.  The ``context`` (if used in the call signature) will be the
instance of the :exc:`repoze.bfg.exceptions.NotFound` exception that
caused the view to be called.

Here's some sample code that implements a minimal NotFound view
callable:

.. code-block:: python
   :linenos:

   from webob.exc import HTTPNotFound

   def notfound_view(request):
       return HTTPNotFound()

.. note:: When a NotFound view callable is invoked, it is passed a
   :term:`request`.  The ``exception`` attribute of the request will
   be an instance of the :exc:`repoze.bfg.exceptions.NotFound`
   exception that caused the not found view to be called.  The value
   of ``request.exception.args[0]`` will be a value explaining why the
   not found error was raised.  This message will be different when
   the ``debug_notfound`` environment setting is true than it is when
   it is false.

.. warning:: When a NotFound view callable accepts an argument list as
   described in :ref:`request_and_context_view_definitions`, the
   ``context`` passed as the first argument to the view callable will
   be the :exc:`repoze.bfg.exceptions.NotFound` exception instance.
   If available, the *model* context will still be available as
   ``request.context``.

.. index::
   single: forbidden view

.. _changing_the_forbidden_view:

Changing the Forbidden View
---------------------------

When :mod:`repoze.bfg` can't authorize execution of a view based on
the :term:`authorization policy` in use, it invokes a :term:`forbidden
view`.  The default forbidden response has a 401 status code and is
very plain, but the view which generates it can be overridden as
necessary using either :term:`imperative configuration` or
:term:`ZCML`.

The :term:`forbidden view` callable is a view callable like any other.
The :term:`view configuration` which causes it to be a "not found"
view consists only of naming the :exc:`repoze.bfg.exceptions.Forbidden`
class as the ``context`` of the view configuration.

.. topic:: Using Imperative Configuration

   If your application uses :term:`imperative configuration`, you can
   replace the Forbidden view by using the
   :meth:`repoze.bfg.configuration.Configurator.add_view` method to
   register an "exception view":

   .. code-block:: python
      :linenos:

      from helloworld.views import forbidden_view
      from repoze.bfg.exceptions import Forbidden
      config.add_view(forbidden_view, context=Forbidden)

   Replace ``helloworld.views.forbidden_view`` with a reference to the
   Python :term:`view callable` you want to use to represent the
   Forbidden view.

.. topic:: Using ZCML

   If your application uses :term:`ZCML`, you can replace the
   Forbidden view by placing something like the following ZCML in your
   ``configure.zcml`` file.

   .. code-block:: xml
      :linenos:

      <view
        view="helloworld.views.notfound_view"
        context="repoze.bfg.exceptions.Forbidden"/>

   Replace ``helloworld.views.forbidden_view`` with the Python
   dotted name to the forbidden view you want to use.

Like any other view, the forbidden view must accept at least a
``request`` parameter, or both ``context`` and ``request``.  The
``context`` (available as ``request.context`` if you're using the
request-only view argument pattern) is the context found by the router
when the view invocation was denied.  The ``request`` is the current
:term:`request` representing the denied action.

Here's some sample code that implements a minimal forbidden view:

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import render_template_to_response

   def forbidden_view(request):
       return render_template_to_response('templates/login_form.pt')

.. note:: When a forbidden view callable is invoked, it is passed a
   :term:`request`.  The ``exception`` attribute of the request will
   be an instance of the :exc:`repoze.bfg.exceptions.Forbidden`
   exception that caused the forbidden view to be called.  The value
   of ``request.exception.args[0]`` will be a value explaining why the
   forbidden was raised.  This message will be different when the
   ``debug_authorization`` environment setting is true than it is when
   it is false.

.. warning:: the default forbidden view sends a response with a ``401
   Unauthorized`` status code for backwards compatibility reasons.
   You can influence the status code of Forbidden responses by using
   an alternate forbidden view.  For example, it would make sense to
   return a response with a ``403 Forbidden`` status code.

.. index::
   single: traverser

.. _changing_the_traverser:

Changing the Traverser
----------------------

The default :term:`traversal` algorithm that BFG uses is explained in
:ref:`traversal_algorithm`.  Though it is rarely necessary, this
default algorithm can be swapped out selectively for a different
traversal pattern via configuration.

Use an ``adapter`` stanza in your application's ``configure.zcml`` to
change the default traverser:

.. code-block:: xml
   :linenos:

    <adapter
      factory="myapp.traversal.Traverser"
      provides="repoze.bfg.interfaces.ITraverser"
      for="*"
      />

In the example above, ``myapp.traversal.Traverser`` is assumed to be
a class that implements the following interface:

.. code-block:: python
   :linenos:

   class Traverser(object):
       def __init__(self, root):
           """ Accept the root object returned from the root factory """

       def __call__(self, request):
           """ Return a dictionary with (at least) the keys ``root``,
           ``context``, ``view_name``, ``subpath``, ``traversed``,
           ``virtual_root``, and ``virtual_root_path``.  These values are
           typically the result of an object graph traversal.  ``root``
           is the physical root object, ``context`` will be a model
           object, ``view_name`` will be the view name used (a Unicode
           name), ``subpath`` will be a sequence of Unicode names that
           followed the view name but were not traversed, ``traversed``
           will be a sequence of Unicode names that were traversed
           (including the virtual root path, if any) ``virtual_root``
           will be a model object representing the virtual root (or the
           physical root if traversal was not performed), and
           ``virtual_root_path`` will be a sequence representing the
           virtual root path (a sequence of Unicode names) or None if
           traversal was not performed.

           Extra keys for special purpose functionality can be added as
           necessary.

           All values returned in the dictionary will be made available
           as attributes of the ``request`` object.
           """

.. warning:: In :mod:`repoze.bfg.` 1.0 and previous versions, the
     traverser ``__call__`` method accepted a WSGI *environment*
     dictionary rather than a :term:`request` object.  The request
     object passed to the traverser implements a dictionary-like API
     which mutates and queries the environment, as a backwards
     compatibility shim, in order to allow older code to work.
     However, for maximum forward compatibility, traverser code
     targeting :mod:`repoze.bfg` 1.1 and higher should expect a
     request object directly.

More than one traversal algorithm can be active at the same time.  For
instance, if your :term:`root factory` returns more than one type of
object conditionally, you could claim that an alternate traverser
adapter is ``for`` only one particular class or interface.  When the
root factory returned an object that implemented that class or
interface, a custom traverser would be used.  Otherwise, the default
traverser would be used.  For example:

.. code-block:: xml
   :linenos:

    <adapter
      factory="myapp.traversal.Traverser"
      provides="repoze.bfg.interfaces.ITraverser"
      for="myapp.models.MyRoot"
      />

If the above stanza was added to a ``configure.zcml`` file,
:mod:`repoze.bfg` would use the ``myapp.traversal.Traverser`` only
when the application :term:`root factory` returned an instance of the
``myapp.models.MyRoot`` object.  Otherwise it would use the default
:mod:`repoze.bfg` traverser to do traversal.

Example implementations of alternate traversers can be found "in the
wild" within `repoze.bfg.traversalwrapper
<http://pypi.python.org/pypi/repoze.bfg.traversalwrapper>`_ and
`repoze.bfg.metatg <http://svn.repoze.org/repoze.bfg.metatg/trunk/>`_.

.. index::
   single: url generator

Changing How :mod:`repoze.bfg.url.model_url` Generates a URL
------------------------------------------------------------

When you add a traverser as described in
:ref:`changing_the_traverser`, it's often convenient to continue to
use the :func:`repoze.bfg.url.model_url` API.  However, since the way
traversal is done will have been modified, the URLs it generates by
default may be incorrect.

If you've added a traverser, you can change how
:func:`repoze.bfg.url.model_url` generates a URL for a specific type
of :term:`context` by adding an adapter stanza for
:class:`repoze.bfg.interfaces.IContextURL` to your application's
``configure.zcml``:

.. code-block:: xml
   :linenos:

    <adapter
      factory="myapp.traversal.URLGenerator"
      provides="repoze.bfg.interfaces.IContextURL"
      for="myapp.models.MyRoot *"
      />

In the above example, the ``myapp.traversal.URLGenerator`` class will
be used to provide services to :func:`repoze.bfg.url.model_url` any
time the :term:`context` passed to ``model_url`` is of class
``myapp.models.MyRoot``.  The asterisk following represents the type
of interface that must be possessed by the :term:`request` (in this
case, any interface, represented by asterisk).

The API that must be implemented by a class that provides
:class:`repoze.bfg.interfaces.IContextURL` is as follows:

.. code-block:: python
  :linenos:

  from zope.interface import Interface

  class IContextURL(Interface):
      """ An adapter which deals with URLs related to a context.
      """
      def __init__(self, context, request):
          """ Accept the context and request """

      def virtual_root(self):
          """ Return the virtual root object related to a request and the
          current context"""

      def __call__(self):
          """ Return a URL that points to the context """

The default context URL generator is available for perusal as the
class :class:`repoze.bfg.traversal.TraversalContextURL` in the
`traversal module
<http://svn.repoze.org/repoze.bfg/trunk/repoze/bfg/traversal.py>`_ of
the :term:`Repoze` Subversion repository.

.. _changing_the_request_factory:

Changing the Request Factory
----------------------------

Whenever :mod:`repoze.bfg` handles a :term:`WSGI` request, it creates
a :term:`request` object based on the WSGI environment it has been
passed.  By default, an instance of the
:class:`repoze.bfg.request.Request` class is created to represent the
request object.

The class (aka "factory") that :mod:`repoze.bfg` uses to create a
request object instance can be changed by passing a
``request_factory`` argument to the constructor of the
:term:`configurator`.

.. code-block:: python
   :linenos:

   from repoze.bfg.request import Request

   class MyRequest(Request):
       pass

   config = Configurator(request_factory=MyRequest)

The same ``MyRequest`` class can alternately be registered via ZCML as
a request factory through the use of the ZCML ``utility`` directive.
In the below, we assume it lives in a package named
``mypackage.mymodule``.

.. code-block:: xml
   :linenos:

   <utility
      component="mypackage.mymodule.MyRequest"
      provides="repoze.bfg.interfaces.IRequestFactory"
    />

Lastly, if you're doing imperative configuration, and you'd rather do
it after you've already constructed a :term:`configurator` it can also
be registered via the
:meth:`repoze.bfg.configuration.Configurator.set_request_factory`
method:

.. code-block:: python
   :linenos:

   from repoze.bfg.configuration import Configurator
   from repoze.bfg.request import Request

   class MyRequest(Request):
       pass

   config = Configurator()
   config.set_request_factory(MyRequestFactory)

.. _adding_renderer_globals:

Adding Renderer Globals
-----------------------

Whenever :mod:`repoze.bfg` handles a request to perform a rendering
(after a view with a ``renderer=`` configuration attribute is invoked,
or when the any of the methods beginning with ``render`` within the
:mod:`repoze.bfg.renderers` module are called), *renderer globals* can
be injected into the *system* values sent to the renderer.  By
default, no renderer globals are injected, and the "bare" system
values (such as ``request``, ``context``, and ``renderer_name``) are
the only values present in the system dictionary passed to every
renderer.

A callback that :mod:`repoze.bfg` will call every time a renderer is
invoked can be added by passing a ``renderer_globals_factory``
argument to the constructor of the :term:`configurator`.

.. code-block:: python
   :linenos:

   def renderer_globals_factory(system):
       return {'a':1}

   config = Configurator(
            renderer_globals_factory=renderer_globals_factory)

Such a callback must accept a single positional argument (notionally
named ``system``) which will contain the original system values.  It
must return a dictionary of values that will be merged into the system
dictionary.  See :ref:`renderer_system_values` for discription of the
values present in the system dictionary.

A renderer globals factory can alternately be registered via ZCML as a
through the use of the ZCML ``utility`` directive.  In the below, we
assume a ``renderers_globals_factory`` function lives in a package
named ``mypackage.mymodule``.

.. code-block:: xml
   :linenos:

   <utility
      component="mypackage.mymodule.renderer_globals_factory"
      provides="repoze.bfg.interfaces.IRendererGlobalsFactory"
    />

Lastly, if you're doing imperative configuration, and you'd rather do
it after you've already constructed a :term:`configurator` it can also
be registered via the
:meth:`repoze.bfg.configuration.Configurator.set_renderer_globals_factory`
method:

.. code-block:: python
   :linenos:

   from repoze.bfg.configuration import Configurator

   def renderer_globals_factory(system):
       return {'a':1}

   config = Configurator()
   config.set_renderer_globals_factory(renderer_globals_factory)

.. _registering_configuration_decorators:

Registering Configuration Decorators
------------------------------------

Decorators such as :class:`repoze.bfg.view.bfg_view` don't change the
behavior of the functions or classes they're decorating.  Instead,
when a :term:`scan` is performed, a modified version of the function
or class is registered with :mod:`repoze.bfg`.

You may wish to have your own decorators that offer such
behaviour. This is possible by using the :term:`Venusian` package in
the same way that it is used by :mod:`repoze.bfg`.

By way of example, let's suppose you want to write a decorator that
registers the function it wraps with a :term:`Zope Component
Architecture` "utility" within the :term:`application registry`
provided by :mod:`repoze.bfg`. The application registry and the
utility inside the registry is likely only to be available once your
application's configuration is at least partially completed. A normal
decorator would fail as it would be executed before the configuration
had even begun.

However, using :term:`Venusian`, the decorator could be written as
follows:

.. code-block:: python
   :linenos:

   import venusian
   from repoze.bfg.threadlocal import get_current_registry
   from mypackage.interfaces import IMyUtility
    
   class registerFunction(object):
        
       def __init__(self, path):
           self.path = path

       def register(self, scanner, name, wrapped):
           registry = get_current_registry()
           registry.getUtility(IMyUtility).register(
               self.path, wrapped
               )
        
       def __call__(self, wrapped):
           venusian.attach(wrapped, self.register)
           return wrapped
    
This decorator could then be used to register functions throughout
your code:

.. code-block:: python
   :linenos:

   @registerFunction('/some/path')
   def my_function():
      do_stuff()

However, the utility would only be looked up when a :term:`scan` was
performed, enabling you to set up the utility in advance:

.. code-block:: python
   :linenos:

   from paste.httpserver import serve
   from repoze.bfg.configuration import Configurator

   class UtilityImplementation:

       implements(ISomething)

       def __init__(self):
          self.registrations = {}

       def register(self,path,callable_):
          self.registrations[path]=callable_

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.registry.registerUtility(UtilityImplementation())
       config.scan()
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

For full details, please read the `Venusian documentation
<http://docs.repoze.org/venusian>`_.

.. note::

   Application-developer-registerable configuration decorators were
   introduced in :mod:`repoze.bfg` 1.3.
