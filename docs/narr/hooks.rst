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
only of naming the :exc:`pyramid.httpexceptions.HTTPNotFound` class as the
``context`` of the view configuration.

If your application uses :term:`imperative configuration`, you can replace
the Not Found view by using the :meth:`pyramid.config.Configurator.add_view`
method to register an "exception view":

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import HTTPNotFound
   from helloworld.views import notfound_view
   config.add_view(notfound_view, context=HTTPNotFound)

Replace ``helloworld.views.notfound_view`` with a reference to the
:term:`view callable` you want to use to represent the Not Found view.

Like any other view, the notfound view must accept at least a ``request``
parameter, or both ``context`` and ``request``.  The ``request`` is the
current :term:`request` representing the denied action.  The ``context`` (if
used in the call signature) will be the instance of the
:exc:`~pyramid.httpexceptions.HTTPNotFound` exception that caused the view to
be called.

Here's some sample code that implements a minimal NotFound view callable:

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import HTTPNotFound

   def notfound_view(request):
       return HTTPNotFound()

.. note::

   When a NotFound view callable is invoked, it is passed a
   :term:`request`.  The ``exception`` attribute of the request will be an
   instance of the :exc:`~pyramid.httpexceptions.HTTPNotFound` exception that
   caused the not found view to be called.  The value of
   ``request.exception.message`` will be a value explaining why the not found
   error was raised.  This message will be different when the
   ``pyramid.debug_notfound`` environment setting is true than it is when it
   is false.

.. warning::

   When a NotFound view callable accepts an argument list as
   described in :ref:`request_and_context_view_definitions`, the ``context``
   passed as the first argument to the view callable will be the
   :exc:`~pyramid.httpexceptions.HTTPNotFound` exception instance.  If
   available, the resource context will still be available as
   ``request.context``.

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
:term:`view configuration` which causes it to be a "forbidden" view consists
only of naming the :exc:`pyramid.httpexceptions.HTTPForbidden` class as the
``context`` of the view configuration.

You can replace the forbidden view by using the
:meth:`pyramid.config.Configurator.add_view` method to register an "exception
view":

.. code-block:: python
   :linenos:

   from helloworld.views import forbidden_view
   from pyramid.httpexceptions import HTTPForbidden
   config.add_view(forbidden_view, context=HTTPForbidden)

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

   from pyramid.view import view_config
   from pyramid.response import Response

   def forbidden_view(request):
       return Response('forbidden')

.. note::

   When a forbidden view callable is invoked, it is passed a
   :term:`request`.  The ``exception`` attribute of the request will be an
   instance of the :exc:`~pyramid.httpexceptions.HTTPForbidden` exception
   that caused the forbidden view to be called.  The value of
   ``request.exception.message`` will be a value explaining why the forbidden
   was raised and ``request.exception.result`` will be extended information
   about the forbidden exception.  These messages will be different when the
   ``pyramid.debug_authorization`` environment setting is true than it is when
   it is false.

.. index::
   single: request factory

.. _changing_the_request_factory:

Changing the Request Factory
----------------------------

Whenever :app:`Pyramid` handles a request from a :term:`WSGI` server, it
creates a :term:`request` object based on the WSGI environment it has been
passed.  By default, an instance of the :class:`pyramid.request.Request`
class is created to represent the request object.

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
   single: before render event
   single: adding renderer globals

.. _beforerender_event:

Using The Before Render Event
-----------------------------

Subscribers to the :class:`pyramid.events.BeforeRender` event may introspect
and modify the set of :term:`renderer globals` before they are passed to a
:term:`renderer`.  This event object iself has a dictionary-like interface
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

Another (deprecated) mechanism which allows event subscribers more control
when adding renderer global values exists in :ref:`adding_renderer_globals`.

.. index::
   single: adding renderer globals

.. _adding_renderer_globals:

Adding Renderer Globals (Deprecated)
------------------------------------

.. warning:: this feature is deprecated as of Pyramid 1.1.  A non-deprecated
   mechanism which allows event subscribers to add renderer global values
   is documented in :ref:`beforerender_event`.

Whenever :app:`Pyramid` handles a request to perform a rendering (after a
view with a ``renderer=`` configuration attribute is invoked, or when any of
the methods beginning with ``render`` within the :mod:`pyramid.renderers`
module are called), *renderer globals* can be injected into the *system*
values sent to the renderer.  By default, no renderer globals are injected,
and the "bare" system values (such as ``request``, ``context``, ``view``, and
``renderer_name``) are the only values present in the system dictionary
passed to every renderer.

A callback that :app:`Pyramid` will call every time a renderer is invoked can
be added by passing a ``renderer_globals_factory`` argument to the
constructor of the :term:`configurator`.  This callback can either be a
callable object or a :term:`dotted Python name` representing such a callable.

.. code-block:: python
   :linenos:

   def renderer_globals_factory(system):
       return {'a': 1}

   config = Configurator(
            renderer_globals_factory=renderer_globals_factory)

Such a callback must accept a single positional argument (notionally named
``system``) which will contain the original system values.  It must return a
dictionary of values that will be merged into the system dictionary.  See
:ref:`renderer_system_values` for description of the values present in the
system dictionary.

If you're doing imperative configuration, and you'd rather do it after you've
already constructed a :term:`configurator` it can also be registered via the
:meth:`pyramid.config.Configurator.set_renderer_globals_factory` method:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   def renderer_globals_factory(system):
       return {'a': 1}

   config = Configurator()
   config.set_renderer_globals_factory(renderer_globals_factory)


.. index::
   single: response callback

.. _using_response_callbacks:

Using Response Callbacks
------------------------

Unlike many other web frameworks, :app:`Pyramid` does not eagerly create a
global response object.  Adding a :term:`response callback` allows an
application to register an action to be performed against whatever response
object is returned by a view, usually in order to mutate the response.

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

   from pyramid.config import Configurator
   from myapp.traversal import Traverser
   config = Configurator()
   config.set_traverser(Traverser)

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
conditionally, you could claim that an alternate traverser adapter is "for"
only one particular class or interface.  When the root factory returned an
object that implemented that class or interface, a custom traverser would be
used.  Otherwise, the default traverser would be used.  For example:

.. code-block:: python
   :linenos:

   from myapp.traversal import Traverser
   from myapp.resources import MyRoot
   from pyramid.config import Configurator
   config = Configurator()
   config.set_traverser(Traverser, MyRoot)

If the above stanza was added to a Pyramid ``__init__.py`` file's ``main``
function, :app:`Pyramid` would use the ``myapp.traversal.Traverser`` only
when the application :term:`root factory` returned an instance of the
``myapp.resources.MyRoot`` object.  Otherwise it would use the default
:app:`Pyramid` traverser to do traversal.

.. index::
   single: url generator

.. _changing_resource_url:

Changing How :meth:`pyramid.request.Request.resource_url` Generates a URL
-------------------------------------------------------------------------

When you add a traverser as described in :ref:`changing_the_traverser`, it's
often convenient to continue to use the
:meth:`pyramid.request.Request.resource_url` API.  However, since the way
traversal is done will have been modified, the URLs it generates by default
may be incorrect when used against resources derived from your custom
traverser.

If you've added a traverser, you can change how
:meth:`~pyramid.request.Request.resource_url` generates a URL for a specific
type of resource by adding a call to
:meth:`pyramid.config.add_resource_url_adapter`.

For example:

.. code-block:: python
   :linenos:

   from myapp.traversal import ResourceURLAdapter
   from myapp.resources import MyRoot

   config.add_resource_url_adapter(ResourceURLAdapter, MyRoot)

In the above example, the ``myapp.traversal.ResourceURLAdapter`` class will
be used to provide services to :meth:`~pyramid.request.Request.resource_url`
any time the :term:`resource` passed to ``resource_url`` is of the class
``myapp.resources.MyRoot``.  The ``resource_iface`` argument ``MyRoot``
represents the type of interface that must be possessed by the resource for
this resource url factory to be found.  If the ``resource_iface`` argument is
omitted, this resource url adapter will be used for *all* resources.

The API that must be implemented by your a class that provides
:class:`~pyramid.interfaces.IResourceURL` is as follows:

.. code-block:: python
  :linenos:

  class MyResourceURL(object):
      """ An adapter which provides the virtual and physical paths of a
          resource
      """
      def __init__(self, resource, request):
          """ Accept the resource and request and set self.physical_path and 
          self.virtual_path"""
          self.virtual_path =  some_function_of(resource, request)
          self.physical_path =  some_other_function_of(resource, request)

The default context URL generator is available for perusal as the class
:class:`pyramid.traversal.ResourceURL` in the `traversal module
<http://github.com/Pylons/pyramid/blob/master/pyramid/traversal.py>`_ of the
:term:`Pylons` GitHub Pyramid repository.

See :meth:`pyramid.config.add_resource_url_adapter` for more information.

.. index::
   single: IResponse
   single: special view responses

.. _using_iresponse:

Changing How Pyramid Treats View Responses
------------------------------------------

It is possible to control how Pyramid treats the result of calling a view
callable on a per-type basis by using a hook involving
:meth:`pyramid.config.Configurator.add_response_adapter` or the
:class:`~pyramid.response.response_adapter` decorator.

.. note:: This feature is new as of Pyramid 1.1.

Pyramid, in various places, adapts the result of calling a view callable to
the :class:`~pyramid.interfaces.IResponse` interface to ensure that the
object returned by the view callable is a "true" response object.  The vast
majority of time, the result of this adaptation is the result object itself,
as view callables written by "civilians" who read the narrative documentation
contained in this manual will always return something that implements the
:class:`~pyramid.interfaces.IResponse` interface.  Most typically, this will
be an instance of the :class:`pyramid.response.Response` class or a subclass.
If a civilian returns a non-Response object from a view callable that isn't
configured to use a :term:`renderer`, he will typically expect the router to
raise an error.  However, you can hook Pyramid in such a way that users can
return arbitrary values from a view callable by providing an adapter which
converts the arbitrary return value into something that implements
:class:`~pyramid.interfaces.IResponse`.

For example, if you'd like to allow view callables to return bare string
objects (without requiring a a :term:`renderer` to convert a string to a
response object), you can register an adapter which converts the string to a
Response:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   def string_response_adapter(s):
       response = Response(s)
       return response

   # config is an instance of pyramid.config.Configurator

   config.add_response_adapter(string_response_adapter, str)

Likewise, if you want to be able to return a simplified kind of response
object from view callables, you can use the IResponse hook to register an
adapter to the more complex IResponse interface:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   class SimpleResponse(object):
       def __init__(self, body):
           self.body = body

   def simple_response_adapter(simple_response):
       response = Response(simple_response.body)
       return response

   # config is an instance of pyramid.config.Configurator

   config.add_response_adapter(simple_response_adapter, SimpleResponse)

If you want to implement your own Response object instead of using the
:class:`pyramid.response.Response` object in any capacity at all, you'll have
to make sure the object implements every attribute and method outlined in
:class:`pyramid.interfaces.IResponse` and you'll have to ensure that it uses
``zope.interface.implementer(IResponse)`` as a class decoratoror.

.. code-block:: python
   :linenos:

   from pyramid.interfaces import IResponse
   from zope.interface import implementer

   @implementer(IResponse)
   class MyResponse(object):
       # ... an implementation of every method and attribute 
       # documented in IResponse should follow ...

When an alternate response object implementation is returned by a view
callable, if that object asserts that it implements
:class:`~pyramid.interfaces.IResponse` (via
``zope.interface.implementer(IResponse)``) , an adapter needn't be registered
for the object; Pyramid will use it directly.

An IResponse adapter for ``webob.Response`` (as opposed to
:class:`pyramid.response.Response`) is registered by Pyramid by default at
startup time, as by their nature, instances of this class (and instances of
subclasses of the class) will natively provide IResponse.  The adapter
registered for ``webob.Response`` simply returns the response object.

Instead of using :meth:`pyramid.config.Configurator.add_response_adapter`,
you can use the :class:`pyramid.response.response_adapter` decorator:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.response import response_adapter

   @response_adapter(str)
   def string_response_adapter(s):
       response = Response(s)
       return response

The above example, when scanned, has the same effect as:

.. code-block:: python

   config.add_response_adapter(string_response_adapter, str)

The :class:`~pyramid.response.response_adapter` decorator will have no effect
until activated by a :term:`scan`.

.. index::
   single: view mapper

.. _using_a_view_mapper:

Using a View Mapper
-------------------

The default calling conventions for view callables are documented in the
:ref:`views_chapter` chapter.  You can change the way users define view
callables by employing a :term:`view mapper`.

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

   from pyramid.response import Response
   from pyramid.config import Configurator
   import pyramid_handlers
   from wsgiref.simple_server import make_server

   class MyController(BaseController):
       def index(self, id):
           return Response(id)

   if __name__ == '__main__':
       config = Configurator()
       config.include(pyramid_handlers)
       config.add_handler('one', '/{id}', MyController, action='index')
       config.add_handler('two', '/{action}/{id}', MyController)
       server.make_server('0.0.0.0', 8080, config.make_wsgi_app())
       server.serve_forever()

The :meth:`pyramid.config.Configurator.set_view_mapper` method can be used to
set a *default* view mapper (overriding the superdefault view mapper used by
Pyramid itself).

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
   from mypackage.interfaces import IMyUtility

   class registerFunction(object):

       def __init__(self, path):
           self.path = path

       def register(self, scanner, name, wrapped):
           registry = scanner.config.registry
           registry.getUtility(IMyUtility).register(
               self.path, wrapped)

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

   from zope.interface import implementer

   from wsgiref.simple_server import make_server
   from pyramid.config import Configurator
   from mypackage.interfaces import IMyUtility

   @implementer(IMyUtility)
   class UtilityImplementation:

       def __init__(self):
          self.registrations = {}

       def register(self, path, callable_):
          self.registrations[path] = callable_

   if __name__ == '__main__':
       config = Configurator()
       config.registry.registerUtility(UtilityImplementation())
       config.scan()
       app = config.make_wsgi_app()
       server = make_server('0.0.0.0', 8080, app)
       server.serve_forever()

For full details, please read the `Venusian documentation
<http://docs.repoze.org/venusian>`_.

.. _registering_tweens:

Registering "Tweens"
--------------------

.. note:: Tweens are a feature which were added in Pyramid 1.2.  They are
   not available in any previous version.

A :term:`tween` (a contraction of the word "between") is a bit of code that
sits between the Pyramid router's main request handling function and the
upstream WSGI component that uses :app:`Pyramid` as its "app".  This is a
feature that may be used by Pyramid framework extensions, to provide, for
example, Pyramid-specific view timing support bookkeeping code that examines
exceptions before they are returned to the upstream WSGI application.  Tweens
behave a bit like :term:`WSGI` middleware but they have the benefit of
running in a context in which they have access to the Pyramid
:term:`application registry` as well as the Pyramid rendering machinery.

Creating a Tween Factory
~~~~~~~~~~~~~~~~~~~~~~~~

To make use of tweens, you must construct a "tween factory".  A tween factory
must be a globally importable callable which accepts two arguments:
``handler`` and ``registry``.  ``handler`` will be the either the main
Pyramid request handling function or another tween.  ``registry`` will be the
Pyramid :term:`application registry` represented by this Configurator.  A
tween factory must return a tween when it is called.

A tween is a callable which accepts a :term:`request` object and returns
a :term:`response` object.

Here's an example of a tween factory:

.. code-block:: python
   :linenos:

    # in a module named myapp.tweens

    import time
    from pyramid.settings import asbool
    import logging

    log = logging.getLogger(__name__)

    def timing_tween_factory(handler, registry):
        if asbool(registry.settings.get('do_timing')):
            # if timing support is enabled, return a wrapper
            def timing_tween(request):
                start = time.time()
                try:
                    response = handler(request)
                finally:
                    end = time.time()
                    log.debug('The request took %s seconds' %
                              (end - start))
                return response
            return timing_tween
        # if timing support is not enabled, return the original
        # handler
        return handler

If you remember, a tween is an object which accepts a :term:`request` object
and which returns a :term:`response` argument.  The ``request`` argument to a
tween will be the request created by Pyramid's router when it receives a WSGI
request.  The response object will be generated by the downstream Pyramid
application and it should be returned by the tween.

In the above example, the tween factory defines a ``timing_tween`` tween and
returns it if ``asbool(registry.settings.get('do_timing'))`` is true.  It
otherwise simply returns the handler it was given.  The ``registry.settings``
attribute is a handle to the deployment settings provided by the user
(usually in an ``.ini`` file).  In this case, if the user has defined a
``do_timing`` setting, and that setting is ``True``, the user has said she
wants to do timing, so the tween factory returns the timing tween; it
otherwise just returns the handler it has been provided, preventing any
timing.

The example timing tween simply records the start time, calls the downstream
handler, logs the number of seconds consumed by the downstream handler, and
returns the response.

Registering an Implicit Tween Factory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've created a tween factory, you can register it into the implicit
tween chain using the :meth:`pyramid.config.Configurator.add_tween` method
using its :term:`dotted Python name`.

Here's an example of registering the a tween factory as an "implicit"
tween in a Pyramid application:

.. code-block:: python
   :linenos:

    from pyramid.config import Configurator
    config = Configurator()
    config.add_tween('myapp.tweens.timing_tween_factory')

Note that you must use a :term:`dotted Python name` as the first argument to
:meth:`pyramid.config.Configurator.add_tween`; this must point at a tween
factory.  You cannot pass the tween factory object itself to the method: it
must be :term:`dotted Python name` that points to a globally importable
object.  In the above example, we assume that a ``timing_tween_factory``
tween factory was defined in a module named ``myapp.tweens``, so the tween
factory is importable as ``myapp.tweens.timing_tween_factory``.

When you use :meth:`pyramid.config.Configurator.add_tween`, you're
instructing the system to use your tween factory at startup time unless the
user has provided an explicit tween list in his configuration.  This is
what's meant by an "implicit" tween.  A user can always elect to supply an
explicit tween list, reordering or disincluding implicitly added tweens.  See
:ref:`explicit_tween_ordering` for more information about explicit tween
ordering.

If more than one call to :meth:`pyramid.config.Configurator.add_tween` is
made within a single application configuration, the tweens will be chained
together at application startup time.  The *first* tween factory added via
``add_tween`` will be called with the Pyramid exception view tween factory as
its ``handler`` argument, then the tween factory added directly after that
one will be called with the result of the first tween factory as its
``handler`` argument, and so on, ad infinitum until all tween factories have
been called. The Pyramid router will use the outermost tween produced by this
chain (the tween generated by the very last tween factory added) as its
request handler function.  For example:

.. code-block:: python
   :linenos:

    from pyramid.config import Configurator

    config = Configurator()
    config.add_tween('myapp.tween_factory1')
    config.add_tween('myapp.tween_factory2')

The above example will generate an implicit tween chain that looks like
this::

    INGRESS (implicit)
    myapp.tween_factory2
    myapp.tween_factory1
    pyramid.tweens.excview_tween_factory (implicit)
    MAIN (implicit)

Suggesting Implicit Tween Ordering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, as described above, the ordering of the chain is controlled
entirely by the relative ordering of calls to
:meth:`pyramid.config.Configurator.add_tween`.  However, the caller of
add_tween can provide an optional hint that can influence the implicit tween
chain ordering by supplying ``under`` or ``over`` (or both) arguments to
:meth:`~pyramid.config.Configurator.add_tween`.  These hints are only used
used when an explicit tween ordering is not used. See
:ref:`explicit_tween_ordering` for a description of how to set an explicit
tween ordering.

Allowable values for ``under`` or ``over`` (or both) are:

- ``None`` (the default).

- A :term:`dotted Python name` to a tween factory: a string representing the
  predicted dotted name of a tween factory added in a call to ``add_tween``
  in the same configuration session.

- One of the constants :attr:`pyramid.tweens.MAIN`,
  :attr:`pyramid.tweens.INGRESS`, or :attr:`pyramid.tweens.EXCVIEW`.

- An iterable of any combination of the above. This allows the user to specify
  fallbacks if the desired tween is not included, as well as compatibility
  with multiple other tweens.

Effectively, ``under`` means "closer to the main Pyramid application than",
``over`` means "closer to the request ingress than".

For example, the following call to
:meth:`~pyramid.config.Configurator.add_tween` will attempt to place the
tween factory represented by ``myapp.tween_factory`` directly 'above' (in
``ptweens`` order) the main Pyramid request handler.

.. code-block:: python
   :linenos:

   import pyramid.tweens

   config.add_tween('myapp.tween_factory', over=pyramid.tweens.MAIN)

The above example will generate an implicit tween chain that looks like
this::

    INGRESS (implicit)
    pyramid.tweens.excview_tween_factory (implicit)
    myapp.tween_factory
    MAIN (implicit)

Likewise, calling the following call to
:meth:`~pyramid.config.Configurator.add_tween` will attempt to place this
tween factory 'above' the main handler but 'below' a separately added tween
factory:

.. code-block:: python
   :linenos:

   import pyramid.tweens

   config.add_tween('myapp.tween_factory1',
                    over=pyramid.tweens.MAIN)
   config.add_tween('myapp.tween_factory2',
                    over=pyramid.tweens.MAIN,
                    under='myapp.tween_factory1')

The above example will generate an implicit tween chain that looks like
this::

    INGRESS (implicit)
    pyramid.tweens.excview_tween_factory (implicit)
    myapp.tween_factory1
    myapp.tween_factory2
    MAIN (implicit)

Specifying neither ``over`` nor ``under`` is equivalent to specifying
``under=INGRESS``.

If all options for ``under`` (or ``over``) cannot be found in the current
configuration, it is an error. If some options are specified purely for
compatibilty with other tweens, just add a fallback of MAIN or INGRESS.
For example, ``under=('someothertween', 'someothertween2', INGRESS)``.
This constraint will require the tween to be located under both the
'someothertween' tween, the 'someothertween2' tween, and INGRESS. If any of
these is not in the current configuration, this constraint will only organize
itself based on the tweens that are present.

.. _explicit_tween_ordering:

Explicit Tween Ordering
~~~~~~~~~~~~~~~~~~~~~~~

Implicit tween ordering is obviously only best-effort.  Pyramid will attempt
to provide an implicit order of tweens as best it can using hints provided by
calls to :meth:`~pyramid.config.Configurator.add_tween`, but because it's
only best-effort, if very precise tween ordering is required, the only
surefire way to get it is to use an explicit tween order.  The deploying user
can override the implicit tween inclusion and ordering implied by calls to
:meth:`~pyramid.config.Configurator.add_tween` entirely by using the
``pyramid.tweens`` settings value.  When used, this settings value must be a
list of Python dotted names which will override the ordering (and inclusion)
of tween factories in the implicit tween chain.  For example:

.. code-block:: ini
   :linenos:

   [app:main]
   use = egg:MyApp
   pyramid.reload_templates = true
   pyramid.debug_authorization = false
   pyramid.debug_notfound = false
   pyramid.debug_routematch = false
   pyramid.debug_templates = true
   pyramid.tweens = myapp.my_cool_tween_factory
                    pyramid.tweens.excview_tween_factory

In the above configuration, calls made during configuration to
:meth:`pyramid.config.Configurator.add_tween` are ignored, and the user is
telling the system to use the tween factories he has listed in the
``pyramid.tweens`` configuration setting (each is a :term:`dotted Python
name` which points to a tween factory) instead of any tween factories added
via :meth:`pyramid.config.Configurator.add_tween`.  The *first* tween factory
in the ``pyramid.tweens`` list will be used as the producer of the effective
:app:`Pyramid` request handling function; it will wrap the tween factory
declared directly "below" it, ad infinitum.  The "main" Pyramid request
handler is implicit, and always "at the bottom".

.. note::

   Pyramid's own :term:`exception view` handling logic is implemented
   as a tween factory function: :func:`pyramid.tweens.excview_tween_factory`.
   If Pyramid exception view handling is desired, and tween factories are
   specified via the ``pyramid.tweens`` configuration setting, the
   :func:`pyramid.tweens.excview_tween_factory` function must be added to the
   ``pyramid.tweens`` configuration setting list explicitly.  If it is not
   present, Pyramid will not perform exception view handling.

Tween Conflicts and Ordering Cycles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pyramid will prevent the same tween factory from being added to the tween
chain more than once using configuration conflict detection.  If you wish to
add the same tween factory more than once in a configuration, you should
either: a) use a tween factory that is a separate globally importable
instance object from the factory that it conflicts with b) use a function or
class as a tween factory with the same logic as the other tween factory it
conflicts with but with a different ``__name__`` attribute or c) call
:meth:`pyramid.config.Configurator.commit` between calls to
:meth:`pyramid.config.Configurator.add_tween`.

If a cycle is detected in implicit tween ordering when ``over`` and ``under``
are used in any call to "add_tween", an exception will be raised at startup
time.

Displaying Tween Ordering
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ptweens`` command-line utility can be used to report the current
implict and explicit tween chains used by an application.  See
:ref:`displaying_tweens`.
