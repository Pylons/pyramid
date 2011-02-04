.. _hooks_chapter:

Using Hooks
===========

"Hooks" can be used to influence the behavior of the :app:`Pyramid` framework
in various ways.

.. index::
   single: not found view

.. _changing_the_notfound_view:

Changing the Not Found View
---------------------------

When :app:`Pyramid` can't map a URL to view code, it invokes a :term:`not
found view`, which is a :term:`view callable`. A default notfound view
exists.  The default not found view can be overridden through application
configuration.

The :term:`not found view` callable is a view callable like any other.  The
:term:`view configuration` which causes it to be a "not found" view consists
only of naming the :exc:`pyramid.exceptions.NotFound` class as the
``context`` of the view configuration.

If your application uses :term:`imperative configuration`, you can replace
the Not Found view by using the :meth:`pyramid.config.Configurator.add_view`
method to register an "exception view":

.. code-block:: python
   :linenos:

   from pyramid.exceptions import NotFound
   from helloworld.views import notfound_view
   config.add_view(notfound_view, context=NotFound)

Replace ``helloworld.views.notfound_view`` with a reference to the
:term:`view callable` you want to use to represent the Not Found view.

Like any other view, the notfound view must accept at least a ``request``
parameter, or both ``context`` and ``request``.  The ``request`` is the
current :term:`request` representing the denied action.  The ``context`` (if
used in the call signature) will be the instance of the
:exc:`~pyramid.exceptions.NotFound` exception that caused the view to be
called.

Here's some sample code that implements a minimal NotFound view callable:

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import HTTPNotFound

   def notfound_view(request):
       return HTTPNotFound()

.. note:: When a NotFound view callable is invoked, it is passed a
   :term:`request`.  The ``exception`` attribute of the request will
   be an instance of the :exc:`~pyramid.exceptions.NotFound`
   exception that caused the not found view to be called.  The value
   of ``request.exception.args[0]`` will be a value explaining why the
   not found error was raised.  This message will be different when
   the ``debug_notfound`` environment setting is true than it is when
   it is false.

.. warning:: When a NotFound view callable accepts an argument list as
   described in :ref:`request_and_context_view_definitions`, the ``context``
   passed as the first argument to the view callable will be the
   :exc:`~pyramid.exceptions.NotFound` exception instance.  If available, the
   resource context will still be available as ``request.context``.

.. index::
   single: forbidden view

.. _changing_the_forbidden_view:

Changing the Forbidden View
---------------------------

When :app:`Pyramid` can't authorize execution of a view based on the
:term:`authorization policy` in use, it invokes a :term:`forbidden view`.
The default forbidden response has a 403 status code and is very plain, but
the view which generates it can be overridden as necessary.

The :term:`forbidden view` callable is a view callable like any other.  The
:term:`view configuration` which causes it to be a "not found" view consists
only of naming the :exc:`pyramid.exceptions.Forbidden` class as the
``context`` of the view configuration.

You can replace the forbidden view by using the
:meth:`pyramid.config.Configurator.add_view` method to register an "exception
view":

.. code-block:: python
   :linenos:

   from helloworld.views import forbidden_view
   from pyramid.exceptions import Forbidden
   config.add_view(forbidden_view, context=Forbidden)

Replace ``helloworld.views.forbidden_view`` with a reference to the Python
:term:`view callable` you want to use to represent the Forbidden view.

Like any other view, the forbidden view must accept at least a ``request``
parameter, or both ``context`` and ``request``.  The ``context`` (available
as ``request.context`` if you're using the request-only view argument
pattern) is the context found by the router when the view invocation was
denied.  The ``request`` is the current :term:`request` representing the
denied action.

Here's some sample code that implements a minimal forbidden view:

.. code-block:: python
   :linenos:

   from pyramid.views import view_config
   from pyramid.response import Response

   def forbidden_view(request):
       return Response('forbidden')

.. note:: When a forbidden view callable is invoked, it is passed a
   :term:`request`.  The ``exception`` attribute of the request will
   be an instance of the :exc:`~pyramid.exceptions.Forbidden`
   exception that caused the forbidden view to be called.  The value
   of ``request.exception.args[0]`` will be a value explaining why the
   forbidden was raised.  This message will be different when the
   ``debug_authorization`` environment setting is true than it is when
   it is false.

.. index::
   single: request factory

.. _changing_the_request_factory:

Changing the Request Factory
----------------------------

Whenever :app:`Pyramid` handles a :term:`WSGI` request, it creates a
:term:`request` object based on the WSGI environment it has been passed.  By
default, an instance of the :class:`pyramid.request.Request` class is created
to represent the request object.

The class (aka "factory") that :app:`Pyramid` uses to create a request object
instance can be changed by passing a ``request_factory`` argument to the
constructor of the :term:`configurator`.  This argument can be either a
callable or a :term:`dotted Python name` representing a callable.

.. code-block:: python
   :linenos:

   from pyramid.request import Request

   class MyRequest(Request):
       pass

   config = Configurator(request_factory=MyRequest)

If you're doing imperative configuration, and you'd rather do it after you've
already constructed a :term:`configurator` it can also be registered via the
:meth:`pyramid.config.Configurator.set_request_factory` method:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator
   from pyramid.request import Request

   class MyRequest(Request):
       pass

   config = Configurator()
   config.set_request_factory(MyRequest)

.. index::
   single: renderer globals

.. _adding_renderer_globals:

Adding Renderer Globals
-----------------------

Whenever :app:`Pyramid` handles a request to perform a rendering (after a
view with a ``renderer=`` configuration attribute is invoked, or when the any
of the methods beginning with ``render`` within the :mod:`pyramid.renderers`
module are called), *renderer globals* can be injected into the *system*
values sent to the renderer.  By default, no renderer globals are injected,
and the "bare" system values (such as ``request``, ``context``, and
``renderer_name``) are the only values present in the system dictionary
passed to every renderer.

A callback that :app:`Pyramid` will call every time a renderer is invoked can
be added by passing a ``renderer_globals_factory`` argument to the
constructor of the :term:`configurator`.  This callback can either be a
callable object or a :term:`dotted Python name` representing such a callable.

.. code-block:: python
   :linenos:

   def renderer_globals_factory(system):
       return {'a':1}

   config = Configurator(
            renderer_globals_factory=renderer_globals_factory)

Such a callback must accept a single positional argument (notionally named
``system``) which will contain the original system values.  It must return a
dictionary of values that will be merged into the system dictionary.  See
:ref:`renderer_system_values` for discription of the values present in the
system dictionary.

If you're doing imperative configuration, and you'd rather do it after you've
already constructed a :term:`configurator` it can also be registered via the
:meth:`pyramid.config.Configurator.set_renderer_globals_factory` method:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   def renderer_globals_factory(system):
       return {'a':1}

   config = Configurator()
   config.set_renderer_globals_factory(renderer_globals_factory)

Another mechanism which allows event subscribers to add renderer global values
exists in :ref:`beforerender_event`.

.. index::
   single: before render event

.. _beforerender_event:

Using The Before Render Event
-----------------------------

Subscribers to the :class:`pyramid.events.BeforeRender` event may introspect
the and modify the set of :term:`renderer globals` before they are passed to
a :term:`renderer`.  This event object iself has a dictionary-like interface
that can be used for this purpose.  For example:

.. code-block:: python
   :linenos:

    from pyramid.events import subscriber
    from pyramid.events import BeforeRender

    @subscriber(BeforeRender)
    def add_global(event):
        event['mykey'] = 'foo'

An object of this type is sent as an event just before a :term:`renderer` is
invoked (but *after* the application-level renderer globals factory added via
:class:`~pyramid.config.Configurator.set_renderer_globals_factory`, if any,
has injected its own keys into the renderer globals dictionary).

If a subscriber attempts to add a key that already exist in the renderer
globals dictionary, a :exc:`KeyError` is raised.  This limitation is enforced
because event subscribers do not possess any relative ordering.  The set of
keys added to the renderer globals dictionary by all
:class:`pyramid.events.BeforeRender` subscribers and renderer globals
factories must be unique.

See the API documentation for the :class:`~pyramid.events.BeforeRender` event
interface at :class:`pyramid.interfaces.IBeforeRender`.

Another mechanism which allows event subscribers more control when adding
renderer global values exists in :ref:`adding_renderer_globals`.

.. index::
   single: response callback

.. _using_response_callbacks:

Using Response Callbacks
------------------------

Unlike many other web frameworks, :app:`Pyramid` does not eagerly create a
global response object.  Adding a :term:`response callback` allows an
application to register an action to be performed against a response object
once it is created, usually in order to mutate it.

The :meth:`pyramid.request.Request.add_response_callback` method is used to
register a response callback.

A response callback is a callable which accepts two positional parameters:
``request`` and ``response``.  For example:

.. code-block:: python
   :linenos:

   def cache_callback(request, response):
       """Set the cache_control max_age for the response"""
       if request.exception is not None:
           response.cache_control.max_age = 360
   request.add_response_callback(cache_callback)

No response callback is called if an unhandled exception happens in
application code, or if the response object returned by a :term:`view
callable` is invalid.  Response callbacks *are*, however, invoked when a
:term:`exception view` is rendered successfully: in such a case, the
:attr:`request.exception` attribute of the request when it enters a response
callback will be an exception object instead of its default value of
``None``.

Response callbacks are called in the order they're added
(first-to-most-recently-added).  All response callbacks are called *after*
the :class:`~pyramid.events.NewResponse` event is sent.  Errors raised by
response callbacks are not handled specially.  They will be propagated to the
caller of the :app:`Pyramid` router application.

A response callback has a lifetime of a *single* request.  If you want a
response callback to happen as the result of *every* request, you must
re-register the callback into every new request (perhaps within a subscriber
of a :class:`~pyramid.events.NewRequest` event).

.. index::
   single: finished callback

.. _using_finished_callbacks:

Using Finished Callbacks
------------------------

A :term:`finished callback` is a function that will be called unconditionally
by the :app:`Pyramid` :term:`router` at the very end of request processing.
A finished callback can be used to perform an action at the end of a request
unconditionally.

The :meth:`pyramid.request.Request.add_finished_callback` method is used to
register a finished callback.

A finished callback is a callable which accepts a single positional
parameter: ``request``.  For example:

.. code-block:: python
   :linenos:

   import transaction

   def commit_callback(request):
       '''commit or abort the transaction associated with request'''
       if request.exception is not None:
           transaction.abort()
       else:
           transaction.commit()
   request.add_finished_callback(commit_callback)

Finished callbacks are called in the order they're added
(first-to-most-recently-added).  Finished callbacks (unlike a
:term:`response callback`) are *always* called, even if an exception
happens in application code that prevents a response from being
generated.

The set of finished callbacks associated with a request are called *very
late* in the processing of that request; they are essentially the very last
thing called by the :term:`router` before a request "ends". They are called
after response processing has already occurred in a top-level ``finally:``
block within the router request processing code.  As a result, mutations
performed to the ``request`` provided to a finished callback will have no
meaningful effect, because response processing will have already occurred,
and the request's scope will expire almost immediately after all finished
callbacks have been processed.

It is often necessary to tell whether an exception occurred within
:term:`view callable` code from within a finished callback: in such a case,
the :attr:`request.exception` attribute of the request when it enters a
response callback will be an exception object instead of its default value of
``None``.

Errors raised by finished callbacks are not handled specially.  They
will be propagated to the caller of the :app:`Pyramid` router
application.

A finished callback has a lifetime of a *single* request.  If you want a
finished callback to happen as the result of *every* request, you must
re-register the callback into every new request (perhaps within a subscriber
of a :class:`~pyramid.events.NewRequest` event).

.. index::
   single: traverser

.. _changing_the_traverser:

Changing the Traverser
----------------------

The default :term:`traversal` algorithm that :app:`Pyramid` uses is explained
in :ref:`traversal_algorithm`.  Though it is rarely necessary, this default
algorithm can be swapped out selectively for a different traversal pattern
via configuration.

.. code-block:: python
   :linenos:

   from pyramid.interfaces import ITraverser
   from zope.interface import Interface
   from myapp.traversal import Traverser

   config.registry.registerAdapter(Traverser, (Interface,), ITraverser)

In the example above, ``myapp.traversal.Traverser`` is assumed to be a class
that implements the following interface:

.. code-block:: python
   :linenos:

   class Traverser(object):
       def __init__(self, root):
           """ Accept the root object returned from the root factory """

       def __call__(self, request):
           """ Return a dictionary with (at least) the keys ``root``,
           ``context``, ``view_name``, ``subpath``, ``traversed``,
           ``virtual_root``, and ``virtual_root_path``.  These values are
           typically the result of a resource tree traversal.  ``root``
           is the physical root object, ``context`` will be a resource
           object, ``view_name`` will be the view name used (a Unicode
           name), ``subpath`` will be a sequence of Unicode names that
           followed the view name but were not traversed, ``traversed``
           will be a sequence of Unicode names that were traversed
           (including the virtual root path, if any) ``virtual_root``
           will be a resource object representing the virtual root (or the
           physical root if traversal was not performed), and
           ``virtual_root_path`` will be a sequence representing the
           virtual root path (a sequence of Unicode names) or None if
           traversal was not performed.

           Extra keys for special purpose functionality can be added as
           necessary.

           All values returned in the dictionary will be made available
           as attributes of the ``request`` object.
           """

More than one traversal algorithm can be active at the same time.  For
instance, if your :term:`root factory` returns more than one type of object
conditionally, you could claim that an alternate traverser adapter is ``for``
only one particular class or interface.  When the root factory returned an
object that implemented that class or interface, a custom traverser would be
used.  Otherwise, the default traverser would be used.  For example:

.. code-block:: python
   :linenos:

   from pyramid.interfaces import ITraverser
   from zope.interface import Interface
   from myapp.traversal import Traverser
   from myapp.resources import MyRoot

   config.registry.registerAdapter(Traverser, (MyRoot,), ITraverser)

If the above stanza was added to a Pyramid ``__init__.py`` file's ``main``
function, :app:`Pyramid` would use the ``myapp.traversal.Traverser`` only
when the application :term:`root factory` returned an instance of the
``myapp.resources.MyRoot`` object.  Otherwise it would use the default
:app:`Pyramid` traverser to do traversal.

.. index::
   single: url generator

.. _changing_resource_url:

Changing How :mod:`pyramid.url.resource_url` Generates a URL
------------------------------------------------------------

When you add a traverser as described in :ref:`changing_the_traverser`, it's
often convenient to continue to use the :func:`pyramid.url.resource_url` API.
However, since the way traversal is done will have been modified, the URLs it
generates by default may be incorrect.

If you've added a traverser, you can change how
:func:`~pyramid.url.resource_url` generates a URL for a specific type of
resource by adding a registerAdapter call for
:class:`pyramid.interfaces.IContextURL` to your application:

.. code-block:: python
   :linenos:

   from pyramid.interfaces import ITraverser
   from zope.interface import Interface
   from myapp.traversal import URLGenerator
   from myapp.resources import MyRoot

   config.registry.registerAdapter(URLGenerator, (MyRoot, Interface), 
                                   IContextURL)

In the above example, the ``myapp.traversal.URLGenerator`` class will be used
to provide services to :func:`~pyramid.url.resource_url` any time the
:term:`context` passed to ``resource_url`` is of class
``myapp.resources.MyRoot``.  The second argument in the ``(MyRoot,
Interface)`` tuple represents the type of interface that must be possessed by
the :term:`request` (in this case, any interface, represented by
``zope.interface.Interface``).

The API that must be implemented by a class that provides
:class:`~pyramid.interfaces.IContextURL` is as follows:

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

The default context URL generator is available for perusal as the class
:class:`pyramid.traversal.TraversalContextURL` in the `traversal module
<http://github.com/Pylons/pyramid/blob/master/pyramid/traversal.py>`_ of the
:term:`Pylons` GitHub Pyramid repository.

.. index::
   single: view mapper

.. _using_a_view_mapper:

Using a View Mapper
-------------------

The default calling conventions for view callables are documented in the
:ref:`views_chapter` chapter.  You can change the way users define view
callbles by employing a :term:`view mapper`.

A view mapper is an object that accepts a set of keyword arguments and which
returns a callable.  The returned callable is called with the :term:`view
callable` object.  The returned callable should itself return another
callable which can be called with the "internal calling protocol" ``(context,
request)``.

You can use a view mapper in a number of ways:

- by setting a ``__view_mapper__`` attribute (which is the view mapper
  object) on the view callable itself

- by passing the mapper object to
  :meth:`pyramid.config.Configurator.add_view` (or its declarative/decorator
  equivalents) as the ``mapper`` argument.

- by registering a *default* view mapper.

Here's an example of a view mapper that emulates (somewhat) a Pylons
"controller".  The mapper is initialized with some keyword arguments.  Its
``__call__`` method accepts the view object (which will be a class).  It uses
the ``attr`` keyword argument it is passed to determine which attribute
should be used as an action method.  The wrapper method it returns accepts
``(context, request)`` and returns the result of calling the action method
with keyword arguments implied by the :term:`matchdict` after popping the
``action`` out of it.  This somewhat emulates the Pylons style of calling
action methods with routing parameters pulled out of the route matching dict
as keyword arguments.

.. code-block:: python
   :linenos:

   # framework

   class PylonsControllerViewMapper(object):
       def __init__(self, **kw):
           self.kw = kw

       def __call__(self, view):
           attr = self.kw['attr']
           def wrapper(context, request):
               matchdict = request.matchdict.copy()
               matchdict.pop('action', None)
               inst = view()
               meth = getattr(inst, attr)
               return meth(**matchdict)
           return wrapper

   class BaseController(object):
       __view_mapper__ = PylonsControllerViewMapper

A user might make use of these framework components like so:

.. code-block:: python
   :linenos:

   # user application

   from webob import Response
   from pyramid.config import Configurator
   import pyramid_handlers
   from paste.httpserver import serve

   class MyController(BaseController):
       def index(self, id):
           return Response(id)

   if __name__ == '__main__':
       config = Configurator()
       config.include(pyramid_handlers)
       config.add_handler('one', '/{id}', MyController, action='index')
       config.add_handler('two', '/{action}/{id}', MyController)
       serve(config.make_wsgi_app())

The :meth:`pyramid.config.Configurator.set_default_mapper` method can be used
to set a *default* view mapper (overriding the superdefault view mapper used
by Pyramid itself).

A *single* view registration can use a view mapper by passing the mapper as
the ``mapper`` argument to :meth:`~pyramid.config.Configuration.add_view`.

.. index::
   single: configuration decorator

.. _registering_configuration_decorators:

Registering Configuration Decorators
------------------------------------

Decorators such as :class:`~pyramid.view.view_config` don't change the
behavior of the functions or classes they're decorating.  Instead, when a
:term:`scan` is performed, a modified version of the function or class is
registered with :app:`Pyramid`.

You may wish to have your own decorators that offer such behaviour. This is
possible by using the :term:`Venusian` package in the same way that it is
used by :app:`Pyramid`.

By way of example, let's suppose you want to write a decorator that registers
the function it wraps with a :term:`Zope Component Architecture` "utility"
within the :term:`application registry` provided by :app:`Pyramid`. The
application registry and the utility inside the registry is likely only to be
available once your application's configuration is at least partially
completed. A normal decorator would fail as it would be executed before the
configuration had even begun.

However, using :term:`Venusian`, the decorator could be written as
follows:

.. code-block:: python
   :linenos:

   import venusian
   from pyramid.threadlocal import get_current_registry
   from mypackage.interfaces import IMyUtility
    
   class registerFunction(object):
        
       def __init__(self, path):
           self.path = path

       def register(self, scanner, name, wrapped):
           registry = scanner.config.registry
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
   from pyramid.config import Configurator

   class UtilityImplementation:

       implements(ISomething)

       def __init__(self):
          self.registrations = {}

       def register(self,path,callable_):
          self.registrations[path]=callable_

   if __name__ == '__main__':
       config = Configurator()
       config.registry.registerUtility(UtilityImplementation())
       config.scan()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

For full details, please read the `Venusian documentation
<http://docs.repoze.org/venusian>`_.

