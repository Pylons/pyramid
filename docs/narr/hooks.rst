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

When :app:`Pyramid` can't map a URL to view code, it invokes a :term:`Not Found
View`, which is a :term:`view callable`. The default Not Found View can be
overridden through application configuration.

If your application uses :term:`imperative configuration`, you can replace the
Not Found View by using the
:meth:`pyramid.config.Configurator.add_notfound_view` method:

.. code-block:: python
   :linenos:

   def notfound(request):
       return Response('Not Found, dude', status='404 Not Found')

   def main(globals, **settings):
       config = Configurator()
       config.add_notfound_view(notfound)

The :term:`Not Found View` callable is a view callable like any other.

If your application instead uses :class:`pyramid.view.view_config` decorators
and a :term:`scan`, you can replace the Not Found View by using the
:class:`pyramid.view.notfound_view_config` decorator:

.. code-block:: python
   :linenos:

   from pyramid.view import notfound_view_config

   @notfound_view_config()
   def notfound(request):
       return Response('Not Found, dude', status='404 Not Found')

   def main(globals, **settings):
       config = Configurator()
       config.scan()

This does exactly what the imperative example above showed.

Your application can define *multiple* Not Found Views if necessary.  Both
:meth:`pyramid.config.Configurator.add_notfound_view` and
:class:`pyramid.view.notfound_view_config` take most of the same arguments as
:class:`pyramid.config.Configurator.add_view` and
:class:`pyramid.view.view_config`, respectively.  This means that Not Found
Views can carry predicates limiting their applicability.  For example:

.. code-block:: python
   :linenos:

   from pyramid.view import notfound_view_config

   @notfound_view_config(request_method='GET')
   def notfound_get(request):
       return Response('Not Found during GET, dude', status='404 Not Found')

   @notfound_view_config(request_method='POST')
   def notfound_post(request):
       return Response('Not Found during POST, dude', status='404 Not Found')

   def main(globals, **settings):
      config = Configurator()
      config.scan()

The ``notfound_get`` view will be called when a view could not be found and the
request method was ``GET``.  The ``notfound_post`` view will be called when a
view could not be found and the request method was ``POST``.

Like any other view, the Not Found View must accept at least a ``request``
parameter, or both ``context`` and ``request``.  The ``request`` is the current
:term:`request` representing the denied action.  The ``context`` (if used in
the call signature) will be the instance of the
:exc:`~pyramid.httpexceptions.HTTPNotFound` exception that caused the view to
be called.

Both :meth:`pyramid.config.Configurator.add_notfound_view` and
:class:`pyramid.view.notfound_view_config` can be used to automatically
redirect requests to slash-appended routes. See
:ref:`redirecting_to_slash_appended_routes` for examples.

Here's some sample code that implements a minimal :term:`Not Found View`
callable:

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import HTTPNotFound

   def notfound(request):
       return HTTPNotFound()

.. note::

   When a Not Found View callable is invoked, it is passed a :term:`request`.
   The ``exception`` attribute of the request will be an instance of the
   :exc:`~pyramid.httpexceptions.HTTPNotFound` exception that caused the Not
   Found View to be called.  The value of ``request.exception.message`` will be
   a value explaining why the Not Found exception was raised.  This message has
   different values depending on whether the ``pyramid.debug_notfound``
   environment setting is true or false.

.. note::

   Both :meth:`pyramid.config.Configurator.add_notfound_view` and
   :class:`pyramid.view.notfound_view_config` are new as of Pyramid 1.3.
   Older Pyramid documentation instructed users to use ``add_view`` instead,
   with a ``context`` of ``HTTPNotFound``.  This still works; the convenience
   method and decorator are just wrappers around this functionality.

.. warning::

   When a Not Found View callable accepts an argument list as described in
   :ref:`request_and_context_view_definitions`, the ``context`` passed as the
   first argument to the view callable will be the
   :exc:`~pyramid.httpexceptions.HTTPNotFound` exception instance.  If
   available, the resource context will still be available as
   ``request.context``.

.. index::
   single: forbidden view

.. _changing_the_forbidden_view:

Changing the Forbidden View
---------------------------

When :app:`Pyramid` can't authorize execution of a view based on the
:term:`authorization policy` in use, it invokes a :term:`forbidden view`. The
default forbidden response has a 403 status code and is very plain, but the
view which generates it can be overridden as necessary.

The :term:`forbidden view` callable is a view callable like any other.  The
:term:`view configuration` which causes it to be a "forbidden" view consists of
using the :meth:`pyramid.config.Configurator.add_forbidden_view` API or the
:class:`pyramid.view.forbidden_view_config` decorator.

For example, you can add a forbidden view by using the
:meth:`pyramid.config.Configurator.add_forbidden_view` method to register a
forbidden view:

.. code-block:: python
   :linenos:

   def forbidden(request):
       return Response('forbidden')

   def main(globals, **settings):
       config = Configurator()
       config.add_forbidden_view(forbidden_view)

If instead you prefer to use decorators and a :term:`scan`, you can use the
:class:`pyramid.view.forbidden_view_config` decorator to mark a view callable
as a forbidden view:

.. code-block:: python
   :linenos:

   from pyramid.view import forbidden_view_config

   @forbidden_view_config()
   def forbidden(request):
       return Response('forbidden')

   def main(globals, **settings):
      config = Configurator()
      config.scan()

Like any other view, the forbidden view must accept at least a ``request``
parameter, or both ``context`` and ``request``.  If a forbidden view callable
accepts both ``context`` and ``request``, the HTTP Exception is passed as
context. The ``context`` as found by the router when the view was denied (which
you normally would expect) is available as ``request.context``.  The
``request`` is the  current :term:`request` representing the denied action.

Here's some sample code that implements a minimal forbidden view:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from pyramid.response import Response

   def forbidden_view(request):
       return Response('forbidden')

.. note::

   When a forbidden view callable is invoked, it is passed a :term:`request`.
   The ``exception`` attribute of the request will be an instance of the
   :exc:`~pyramid.httpexceptions.HTTPForbidden` exception that caused the
   forbidden view to be called.  The value of ``request.exception.message``
   will be a value explaining why the forbidden exception was raised, and
   ``request.exception.result`` will be extended information about the
   forbidden exception.  These messages have different values depending on
   whether the ``pyramid.debug_authorization`` environment setting is true or
   false.

.. index::
   single: request factory

.. _changing_the_request_factory:

Changing the Request Factory
----------------------------

Whenever :app:`Pyramid` handles a request from a :term:`WSGI` server, it
creates a :term:`request` object based on the WSGI environment it has been
passed.  By default, an instance of the :class:`pyramid.request.Request` class
is created to represent the request object.

The class (a.k.a., "factory") that :app:`Pyramid` uses to create a request
object instance can be changed by passing a ``request_factory`` argument to the
constructor of the :term:`configurator`.  This argument can be either a
callable or a :term:`dotted Python name` representing a callable.

.. code-block:: python
   :linenos:

   from pyramid.request import Request

   class MyRequest(Request):
       pass

   config = Configurator(request_factory=MyRequest)

If you're doing imperative configuration, and you'd rather do it after you've
already constructed a :term:`configurator`, it can also be registered via the
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
   single: request method

.. _adding_request_method:

Adding Methods or Properties to a Request Object
------------------------------------------------

.. versionadded:: 1.4

Since each Pyramid application can only have one :term:`request` factory,
:ref:`changing the request factory <changing_the_request_factory>` is not that
extensible, especially if you want to build composable features (e.g., Pyramid
add-ons and plugins).

A lazy property can be registered to the request object via the
:meth:`pyramid.config.Configurator.add_request_method` API. This allows you to
specify a callable that will be available on the request object, but will not
actually execute the function until accessed.

.. warning::

   This will silently override methods and properties from :term:`request
   factory` that have the same name.

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   def total(request, *args):
       return sum(args)

   def prop(request):
       print("getting the property")
       return "the property"

   config = Configurator()
   config.add_request_method(total)
   config.add_request_method(prop, reify=True)

In the above example, ``total`` is added as a method. However, ``prop`` is
added as a property and its result is cached per-request by setting
``reify=True``. This way, we eliminate the overhead of running the function
multiple times.

.. testsetup:: group1

   from pyramid.config import Configurator


   def total(request, *args):
       return sum(args)


   def prop(request):
       print("getting the property")
       return "the property"



   config = Configurator()
   config.add_request_method(total)
   config.add_request_method(prop, reify=True)
   config.commit()

   from pyramid.scripting import prepare
   request = prepare(registry=config.registry)["request"]

.. doctest:: group1

   >>> request.total(1, 2, 3)
   6
   >>> request.prop
   getting the property
   'the property'
   >>> request.prop
   'the property'

To not cache the result of ``request.prop``, set ``property=True`` instead of
``reify=True``.

Here is an example of passing a class to ``Configurator.add_request_method``:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator
   from pyramid.decorator import reify

   class ExtraStuff(object):

       def __init__(self, request):
           self.request = request

       def total(self, *args):
           return sum(args)

       # use @property if you don't want to cache the result
       @reify
       def prop(self):
           print("getting the property")
           return "the property"

   config = Configurator()
   config.add_request_method(ExtraStuff, 'extra', reify=True)

We attach and cache an object named ``extra`` to the ``request`` object.

.. testsetup:: group2

   from pyramid.config import Configurator
   from pyramid.decorator import reify

   class ExtraStuff(object):

       def __init__(self, request):
           self.request = request

       def total(self, *args):
           return sum(args)

       # use @property if you don't want to cache the result
       @reify
       def prop(self):
           print("getting the property")
           return "the property"

   config = Configurator()
   config.add_request_method(ExtraStuff, 'extra', reify=True)
   config.commit()

   from pyramid.scripting import prepare
   request = prepare(registry=config.registry)["request"]

.. doctest:: group2

   >>> request.extra.total(1, 2, 3)
   6
   >>> request.extra.prop
   getting the property
   'the property'
   >>> request.extra.prop
   'the property'


.. index::
   single: response factory

.. _changing_the_response_factory:

Changing the Response Factory
-----------------------------

.. versionadded:: 1.6

Whenever :app:`Pyramid` returns a response from a view, it creates a
:term:`response` object.  By default, an instance of the
:class:`pyramid.response.Response` class is created to represent the response
object.

The factory that :app:`Pyramid` uses to create a response object instance can
be changed by passing a :class:`pyramid.interfaces.IResponseFactory` argument
to the constructor of the :term:`configurator`.  This argument can be either a
callable or a :term:`dotted Python name` representing a callable.

The factory takes a single positional argument, which is a :term:`Request`
object. The argument may be ``None``.

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   class MyResponse(Response):
       pass

   config = Configurator(response_factory=lambda r: MyResponse())

If you're doing imperative configuration and you'd rather do it after you've
already constructed a :term:`configurator`, it can also be registered via the
:meth:`pyramid.config.Configurator.set_response_factory` method:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator
   from pyramid.response import Response

   class MyResponse(Response):
       pass

   config = Configurator()
   config.set_response_factory(lambda r: MyResponse())

.. index::
   single: before render event
   single: adding renderer globals

.. _beforerender_event:

Using the Before Render Event
-----------------------------

Subscribers to the :class:`pyramid.events.BeforeRender` event may introspect
and modify the set of :term:`renderer globals` before they are passed to a
:term:`renderer`.  This event object iself has a dictionary-like interface that
can be used for this purpose.  For example:

.. code-block:: python
    :linenos:

    from pyramid.events import subscriber
    from pyramid.events import BeforeRender

    @subscriber(BeforeRender)
    def add_global(event):
        event['mykey'] = 'foo'

An object of this type is sent as an event just before a :term:`renderer` is
invoked.

If a subscriber attempts to add a key that already exists in the renderer
globals dictionary, a :exc:`KeyError` is raised.  This limitation is enforced
because event subscribers do not possess any relative ordering.  The set of
keys added to the renderer globals dictionary by all
:class:`pyramid.events.BeforeRender` subscribers and renderer globals factories
must be unique.

The dictionary returned from the view is accessible through the
:attr:`rendering_val` attribute of a :class:`~pyramid.events.BeforeRender`
event.

Suppose you return ``{'mykey': 'somevalue', 'mykey2': 'somevalue2'}`` from your
view callable, like so:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='some_renderer')
   def myview(request):
       return {'mykey': 'somevalue', 'mykey2': 'somevalue2'}

:attr:`rendering_val` can be used to access these values from the
:class:`~pyramid.events.BeforeRender` object:

.. code-block:: python
   :linenos:

   from pyramid.events import subscriber
   from pyramid.events import BeforeRender

   @subscriber(BeforeRender)
   def read_return(event):
       # {'mykey': 'somevalue'} is returned from the view
       print(event.rendering_val['mykey'])

See the API documentation for the :class:`~pyramid.events.BeforeRender` event
interface at :class:`pyramid.interfaces.IBeforeRender`.

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

No response callback is called if an unhandled exception happens in application
code, or if the response object returned by a :term:`view callable` is invalid.
Response callbacks *are*, however, invoked when a :term:`exception view` is
rendered successfully.  In such a case, the :attr:`request.exception` attribute
of the request when it enters a response callback will be an exception object
instead of its default value of ``None``.

Response callbacks are called in the order they're added
(first-to-most-recently-added).  All response callbacks are called *before* the
:class:`~pyramid.events.NewResponse` event is sent.  Errors raised by response
callbacks are not handled specially.  They will be propagated to the caller of
the :app:`Pyramid` router application.

A response callback has a lifetime of a *single* request.  If you want a
response callback to happen as the result of *every* request, you must
re-register the callback into every new request (perhaps within a subscriber of
a :class:`~pyramid.events.NewRequest` event).

.. index::
   single: finished callback

.. _using_finished_callbacks:

Using Finished Callbacks
------------------------

A :term:`finished callback` is a function that will be called unconditionally
by the :app:`Pyramid` :term:`router` at the very end of request processing. A
finished callback can be used to perform an action at the end of a request
unconditionally.

The :meth:`pyramid.request.Request.add_finished_callback` method is used to
register a finished callback.

A finished callback is a callable which accepts a single positional parameter:
``request``.  For example:

.. code-block:: python
   :linenos:

   import logging

   log = logging.getLogger(__name__)

   def log_callback(request):
       """Log information at the end of request"""
       log.debug('Request is finished.')
   request.add_finished_callback(log_callback)

Finished callbacks are called in the order they're added
(first-to-most-recently-added).  Finished callbacks (unlike a :term:`response
callback`) are *always* called, even if an exception happens in application
code that prevents a response from being generated.

The set of finished callbacks associated with a request are called *very late*
in the processing of that request; they are essentially the very last thing
called by the :term:`router` before a request "ends". They are called after
response processing has already occurred in a top-level ``finally:`` block
within the router request processing code.  As a result, mutations performed to
the ``request`` provided to a finished callback will have no meaningful effect,
because response processing will have already occurred, and the request's scope
will expire almost immediately after all finished callbacks have been
processed.

Errors raised by finished callbacks are not handled specially.  They will be
propagated to the caller of the :app:`Pyramid` router application.

A finished callback has a lifetime of a *single* request.  If you want a
finished callback to happen as the result of *every* request, you must
re-register the callback into every new request (perhaps within a subscriber of
a :class:`~pyramid.events.NewRequest` event).

.. index::
   single: traverser

.. _changing_the_traverser:

Changing the Traverser
----------------------

The default :term:`traversal` algorithm that :app:`Pyramid` uses is explained
in :ref:`traversal_algorithm`.  Though it is rarely necessary, this default
algorithm can be swapped out selectively for a different traversal pattern via
configuration.

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator
   from myapp.traversal import Traverser
   config = Configurator()
   config.add_traverser(Traverser)

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
conditionally, you could claim that an alternative traverser adapter is "for"
only one particular class or interface.  When the root factory returned an
object that implemented that class or interface, a custom traverser would be
used.  Otherwise the default traverser would be used.  For example:

.. code-block:: python
   :linenos:

   from myapp.traversal import Traverser
   from myapp.resources import MyRoot
   from pyramid.config import Configurator
   config = Configurator()
   config.add_traverser(Traverser, MyRoot)

If the above stanza was added to a Pyramid ``__init__.py`` file's ``main``
function, :app:`Pyramid` would use the ``myapp.traversal.Traverser`` only when
the application :term:`root factory` returned an instance of the
``myapp.resources.MyRoot`` object.  Otherwise it would use the default
:app:`Pyramid` traverser to do traversal.

.. index::
   single: URL generator

.. _changing_resource_url:

Changing How :meth:`pyramid.request.Request.resource_url` Generates a URL
-------------------------------------------------------------------------

When you add a traverser as described in :ref:`changing_the_traverser`, it's
often convenient to continue to use the
:meth:`pyramid.request.Request.resource_url` API.  However, since the way
traversal is done will have been modified, the URLs it generates by default may
be incorrect when used against resources derived from your custom traverser.

If you've added a traverser, you can change how
:meth:`~pyramid.request.Request.resource_url` generates a URL for a specific
type of resource by adding a call to
:meth:`pyramid.config.Configurator.add_resource_url_adapter`.

For example:

.. code-block:: python
   :linenos:

   from myapp.traversal import ResourceURLAdapter
   from myapp.resources import MyRoot

   config.add_resource_url_adapter(ResourceURLAdapter, MyRoot)

In the above example, the ``myapp.traversal.ResourceURLAdapter`` class will be
used to provide services to :meth:`~pyramid.request.Request.resource_url` any
time the :term:`resource` passed to ``resource_url`` is of the class
``myapp.resources.MyRoot``.  The ``resource_iface`` argument ``MyRoot``
represents the type of interface that must be possessed by the resource for
this resource url factory to be found.  If the ``resource_iface`` argument is
omitted, this resource URL adapter will be used for *all* resources.

The API that must be implemented by a class that provides
:class:`~pyramid.interfaces.IResourceURL` is as follows:

.. code-block:: python
  :linenos:

  class MyResourceURL(object):
      """ An adapter which provides the virtual and physical paths of a
          resource
      """
      def __init__(self, resource, request):
          """ Accept the resource and request and set self.physical_path and
          self.virtual_path """
          self.virtual_path =  some_function_of(resource, request)
          self.physical_path =  some_other_function_of(resource, request)

The default context URL generator is available for perusal as the class
:class:`pyramid.traversal.ResourceURL` in the `traversal module
<https://github.com/Pylons/pyramid/blob/master/pyramid/traversal.py>`_ of the
:term:`Pylons` GitHub Pyramid repository.

See :meth:`pyramid.config.Configurator.add_resource_url_adapter` for more
information.

.. index::
   single: IResponse
   single: special view responses

.. _using_iresponse:

Changing How Pyramid Treats View Responses
------------------------------------------

.. versionadded:: 1.1

It is possible to control how Pyramid treats the result of calling a view
callable on a per-type basis by using a hook involving
:meth:`pyramid.config.Configurator.add_response_adapter` or the
:class:`~pyramid.response.response_adapter` decorator.

Pyramid, in various places, adapts the result of calling a view callable to the
:class:`~pyramid.interfaces.IResponse` interface to ensure that the object
returned by the view callable is a "true" response object.  The vast majority
of time, the result of this adaptation is the result object itself, as view
callables written by "civilians" who read the narrative documentation contained
in this manual will always return something that implements the
:class:`~pyramid.interfaces.IResponse` interface.  Most typically, this will be
an instance of the :class:`pyramid.response.Response` class or a subclass. If a
civilian returns a non-Response object from a view callable that isn't
configured to use a :term:`renderer`, they will typically expect the router to
raise an error.  However, you can hook Pyramid in such a way that users can
return arbitrary values from a view callable by providing an adapter which
converts the arbitrary return value into something that implements
:class:`~pyramid.interfaces.IResponse`.

For example, if you'd like to allow view callables to return bare string
objects (without requiring a :term:`renderer` to convert a string to a response
object), you can register an adapter which converts the string to a Response:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   def string_response_adapter(s):
       response = Response(s)
       return response

   # config is an instance of pyramid.config.Configurator

   config.add_response_adapter(string_response_adapter, str)

Likewise, if you want to be able to return a simplified kind of response object
from view callables, you can use the IResponse hook to register an adapter to
the more complex IResponse interface:

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
to make sure that the object implements every attribute and method outlined in
:class:`pyramid.interfaces.IResponse` and you'll have to ensure that it uses
``zope.interface.implementer(IResponse)`` as a class decorator.

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

Instead of using :meth:`pyramid.config.Configurator.add_response_adapter`, you
can use the :class:`pyramid.response.response_adapter` decorator:

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
callable` object.  The returned callable should itself return another callable
which can be called with the "internal calling protocol" ``(context,
request)``.

You can use a view mapper in a number of ways:

- by setting a ``__view_mapper__`` attribute (which is the view mapper object)
  on the view callable itself

- by passing the mapper object to :meth:`pyramid.config.Configurator.add_view`
  (or its declarative and decorator equivalents) as the ``mapper`` argument

- by registering a *default* view mapper

Here's an example of a view mapper that emulates (somewhat) a Pylons
"controller".  The mapper is initialized with some keyword arguments.  Its
``__call__`` method accepts the view object (which will be a class).  It uses
the ``attr`` keyword argument it is passed to determine which attribute should
be used as an action method.  The wrapper method it returns accepts ``(context,
request)`` and returns the result of calling the action method with keyword
arguments implied by the :term:`matchdict` after popping the ``action`` out of
it.  This somewhat emulates the Pylons style of calling action methods with
routing parameters pulled out of the route matching dict as keyword arguments.

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
               inst = view(request)
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

A *single* view registration can use a view mapper by passing the mapper as the
``mapper`` argument to :meth:`~pyramid.config.Configurator.add_view`.

.. index::
   single: configuration decorator

.. _registering_configuration_decorators:

Registering Configuration Decorators
------------------------------------

Decorators such as :class:`~pyramid.view.view_config` don't change the behavior
of the functions or classes they're decorating.  Instead when a :term:`scan` is
performed, a modified version of the function or class is registered with
:app:`Pyramid`.

You may wish to have your own decorators that offer such behaviour. This is
possible by using the :term:`Venusian` package in the same way that it is used
by :app:`Pyramid`.

By way of example, let's suppose you want to write a decorator that registers
the function it wraps with a :term:`Zope Component Architecture` "utility"
within the :term:`application registry` provided by :app:`Pyramid`. The
application registry and the utility inside the registry is likely only to be
available once your application's configuration is at least partially
completed. A normal decorator would fail as it would be executed before the
configuration had even begun.

However, using :term:`Venusian`, the decorator could be written as follows:

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

This decorator could then be used to register functions throughout your code:

.. code-block:: python
   :linenos:

   @registerFunction('/some/path')
   def my_function():
       do_stuff()

However, the utility would only be looked up when a :term:`scan` was performed,
enabling you to set up the utility in advance:

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

Registering Tweens
------------------

.. versionadded:: 1.2
   Tweens

A :term:`tween` (a contraction of the word "between") is a bit of code that
sits between the Pyramid router's main request handling function and the
upstream WSGI component that uses :app:`Pyramid` as its "app".  This is a
feature that may be used by Pyramid framework extensions to provide, for
example, Pyramid-specific view timing support bookkeeping code that examines
exceptions before they are returned to the upstream WSGI application.  Tweens
behave a bit like :term:`WSGI` :term:`middleware`, but they have the benefit of
running in a context in which they have access to the Pyramid :term:`request`,
:term:`response`, and :term:`application registry`, as well as the Pyramid
rendering machinery.

Creating a Tween
~~~~~~~~~~~~~~~~

To create a tween, you must write a "tween factory".  A tween factory must be a
globally importable callable which accepts two arguments: ``handler`` and
``registry``.  ``handler`` will be either the main Pyramid request handling
function or another tween.  ``registry`` will be the Pyramid :term:`application
registry` represented by this Configurator.  A tween factory must return the
tween (a callable object) when it is called.

A tween is called with a single argument, ``request``, which is the
:term:`request` created by Pyramid's router when it receives a WSGI request. A
tween should return a :term:`response`, usually the one generated by the
downstream Pyramid application.

You can write the tween factory as a simple closure-returning function:

.. code-block:: python
    :linenos:

    def simple_tween_factory(handler, registry):
        # one-time configuration code goes here

        def simple_tween(request):
            # code to be executed for each request before
            # the actual application code goes here

            response = handler(request)

            # code to be executed for each request after
            # the actual application code goes here

            return response

        return simple_tween

Alternatively, the tween factory can be a class with the ``__call__`` magic
method:

.. code-block:: python
    :linenos:

    class simple_tween_factory(object):
        def __init__(self, handler, registry):
            self.handler = handler
            self.registry = registry

            # one-time configuration code goes here

        def __call__(self, request):
            # code to be executed for each request before
            # the actual application code goes here

            response = self.handler(request)

            # code to be executed for each request after
            # the actual application code goes here

            return response

You should avoid mutating any state on the tween instance. The tween is invoked
once per request and any shared mutable state needs to be carefully handled to
avoid any race conditions.

The closure style performs slightly better and enables you to conditionally
omit the tween from the request processing pipeline (see the following timing
tween example), whereas the class style makes it easier to have shared mutable
state and allows subclassing.

Here's a complete example of a tween that logs the time spent processing each
request:

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

In the above example, the tween factory defines a ``timing_tween`` tween and
returns it if ``asbool(registry.settings.get('do_timing'))`` is true.  It
otherwise simply returns the handler which it was given.  The
``registry.settings`` attribute is a handle to the deployment settings provided
by the user (usually in an ``.ini`` file).  In this case, if the user has
defined a ``do_timing`` setting and that setting is ``True``, the user has said
they want to do timing, so the tween factory returns the timing tween; it
otherwise just returns the handler it has been provided, preventing any timing.

The example timing tween simply records the start time, calls the downstream
handler, logs the number of seconds consumed by the downstream handler, and
returns the response.

Registering an Implicit Tween Factory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've created a tween factory, you can register it into the implicit
tween chain using the :meth:`pyramid.config.Configurator.add_tween` method
using its :term:`dotted Python name`.

Here's an example of registering a tween factory as an "implicit" tween in a
Pyramid application:

.. code-block:: python
    :linenos:

    from pyramid.config import Configurator
    config = Configurator()
    config.add_tween('myapp.tweens.timing_tween_factory')

Note that you must use a :term:`dotted Python name` as the first argument to
:meth:`pyramid.config.Configurator.add_tween`; this must point at a tween
factory.  You cannot pass the tween factory object itself to the method: it
must be :term:`dotted Python name` that points to a globally importable object.
In the above example, we assume that a ``timing_tween_factory`` tween factory
was defined in a module named ``myapp.tweens``, so the tween factory is
importable as ``myapp.tweens.timing_tween_factory``.

When you use :meth:`pyramid.config.Configurator.add_tween`, you're instructing
the system to use your tween factory at startup time unless the user has
provided an explicit tween list in their configuration.  This is what's meant
by an "implicit" tween.  A user can always elect to supply an explicit tween
list, reordering or disincluding implicitly added tweens.  See
:ref:`explicit_tween_ordering` for more information about explicit tween
ordering.

If more than one call to :meth:`pyramid.config.Configurator.add_tween` is made
within a single application configuration, the tweens will be chained together
at application startup time.  The *first* tween factory added via ``add_tween``
will be called with the Pyramid exception view tween factory as its ``handler``
argument, then the tween factory added directly after that one will be called
with the result of the first tween factory as its ``handler`` argument, and so
on, ad infinitum until all tween factories have been called. The Pyramid router
will use the outermost tween produced by this chain (the tween generated by the
very last tween factory added) as its request handler function.  For example:

.. code-block:: python
    :linenos:

    from pyramid.config import Configurator

    config = Configurator()
    config.add_tween('myapp.tween_factory1')
    config.add_tween('myapp.tween_factory2')

The above example will generate an implicit tween chain that looks like this::

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
``add_tween`` can provide an optional hint that can influence the implicit
tween chain ordering by supplying ``under`` or ``over`` (or both) arguments to
:meth:`~pyramid.config.Configurator.add_tween`.  These hints are only used when
an explicit tween ordering is not used. See :ref:`explicit_tween_ordering` for
a description of how to set an explicit tween ordering.

Allowable values for ``under`` or ``over`` (or both) are:

- ``None`` (the default),

- a :term:`dotted Python name` to a tween factory: a string representing the
  predicted dotted name of a tween factory added in a call to ``add_tween`` in
  the same configuration session,

- one of the constants :attr:`pyramid.tweens.MAIN`,
  :attr:`pyramid.tweens.INGRESS`, or :attr:`pyramid.tweens.EXCVIEW`, or

- an iterable of any combination of the above. This allows the user to specify
  fallbacks if the desired tween is not included, as well as compatibility
  with multiple other tweens.

Effectively, ``over`` means "closer to the request ingress than" and ``under``
means "closer to the main Pyramid application than". You can think of an onion
with outer layers over the inner layers, the application being under all the
layers at the center.

For example, the following call to
:meth:`~pyramid.config.Configurator.add_tween` will attempt to place the tween
factory represented by ``myapp.tween_factory`` directly "above" (in ``ptweens``
order) the main Pyramid request handler.

.. code-block:: python
   :linenos:

   import pyramid.tweens

   config.add_tween('myapp.tween_factory', over=pyramid.tweens.MAIN)

The above example will generate an implicit tween chain that looks like this::

    INGRESS (implicit)
    pyramid.tweens.excview_tween_factory (implicit)
    myapp.tween_factory
    MAIN (implicit)

Likewise, calling the following call to
:meth:`~pyramid.config.Configurator.add_tween` will attempt to place this tween
factory "above" the main handler but "below" a separately added tween factory:

.. code-block:: python
   :linenos:

   import pyramid.tweens

   config.add_tween('myapp.tween_factory1',
                    over=pyramid.tweens.MAIN)
   config.add_tween('myapp.tween_factory2',
                    over=pyramid.tweens.MAIN,
                    under='myapp.tween_factory1')

The above example will generate an implicit tween chain that looks like this::

    INGRESS (implicit)
    pyramid.tweens.excview_tween_factory (implicit)
    myapp.tween_factory1
    myapp.tween_factory2
    MAIN (implicit)

Specifying neither ``over`` nor ``under`` is equivalent to specifying
``under=INGRESS``.

If all options for ``under`` (or ``over``) cannot be found in the current
configuration, it is an error. If some options are specified purely for
compatibilty with other tweens, just add a fallback of ``MAIN`` or ``INGRESS``.
For example, ``under=('someothertween', 'someothertween2', INGRESS)``. This
constraint will require the tween to be located under the ``someothertween``
tween, the ``someothertween2`` tween, and ``INGRESS``. If any of these is not
in the current configuration, this constraint will only organize itself based
on the tweens that are present.

.. _explicit_tween_ordering:

Explicit Tween Ordering
~~~~~~~~~~~~~~~~~~~~~~~

Implicit tween ordering is obviously only best-effort.  Pyramid will attempt to
provide an implicit order of tweens as best it can using hints provided by
calls to :meth:`~pyramid.config.Configurator.add_tween`.  But because it's only
best-effort, if very precise tween ordering is required, the only surefire way
to get it is to use an explicit tween order.  The deploying user can override
the implicit tween inclusion and ordering implied by calls to
:meth:`~pyramid.config.Configurator.add_tween` entirely by using the
``pyramid.tweens`` settings value.  When used, this settings value must be a
list of Python dotted names which will override the ordering (and inclusion) of
tween factories in the implicit tween chain.  For example:

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
``pyramid.tweens`` configuration setting (each is a :term:`dotted Python name`
which points to a tween factory) instead of any tween factories added via
:meth:`pyramid.config.Configurator.add_tween`.  The *first* tween factory in
the ``pyramid.tweens`` list will be used as the producer of the effective
:app:`Pyramid` request handling function; it will wrap the tween factory
declared directly "below" it, ad infinitum.  The "main" Pyramid request handler
is implicit, and always "at the bottom".

.. note::

   Pyramid's own :term:`exception view` handling logic is implemented as a
   tween factory function: :func:`pyramid.tweens.excview_tween_factory`.  If
   Pyramid exception view handling is desired, and tween factories are
   specified via the ``pyramid.tweens`` configuration setting, the
   :func:`pyramid.tweens.excview_tween_factory` function must be added to the
   ``pyramid.tweens`` configuration setting list explicitly.  If it is not
   present, Pyramid will not perform exception view handling.

Tween Conflicts and Ordering Cycles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pyramid will prevent the same tween factory from being added to the tween chain
more than once using configuration conflict detection.  If you wish to add the
same tween factory more than once in a configuration, you should either: (a)
use a tween factory that is a separate globally importable instance object from
the factory that it conflicts with; (b) use a function or class as a tween
factory with the same logic as the other tween factory it conflicts with, but
with a different ``__name__`` attribute; or (c) call
:meth:`pyramid.config.Configurator.commit` between calls to
:meth:`pyramid.config.Configurator.add_tween`.

If a cycle is detected in implicit tween ordering when ``over`` and ``under``
are used in any call to ``add_tween``, an exception will be raised at startup
time.

Displaying Tween Ordering
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ptweens`` command-line utility can be used to report the current implict
and explicit tween chains used by an application.  See
:ref:`displaying_tweens`.

.. _registering_thirdparty_predicates:

Adding a Third Party View, Route, or Subscriber Predicate
---------------------------------------------------------

.. versionadded:: 1.4

.. _view_and_route_predicates:

View and Route Predicates
~~~~~~~~~~~~~~~~~~~~~~~~~

View and route predicates used during configuration allow you to narrow the set
of circumstances under which a view or route will match.  For example, the
``request_method`` view predicate can be used to ensure a view callable is only
invoked when the request's method is ``POST``:

.. code-block:: python

    @view_config(request_method='POST')
    def someview(request):
        ...

Likewise, a similar predicate can be used as a *route* predicate:

.. code-block:: python

    config.add_route('name', '/foo', request_method='POST')

Many other built-in predicates exists (``request_param``, and others).  You can
add third-party predicates to the list of available predicates by using one of
:meth:`pyramid.config.Configurator.add_view_predicate` or
:meth:`pyramid.config.Configurator.add_route_predicate`.  The former adds a
view predicate, the latter a route predicate.

When using one of those APIs, you pass a *name* and a *factory* to add a
predicate during Pyramid's configuration stage.  For example:

.. code-block:: python

    config.add_view_predicate('content_type', ContentTypePredicate)

The above example adds a new predicate named ``content_type`` to the list of
available predicates for views.  This will allow the following view
configuration statement to work:

.. code-block:: python
   :linenos:

   @view_config(content_type='File')
   def aview(request): ...

The first argument to :meth:`pyramid.config.Configurator.add_view_predicate`,
the name, is a string representing the name that is expected to be passed to
``view_config`` (or its imperative analogue ``add_view``).

The second argument is a view or route predicate factory, or a :term:`dotted
Python name` which refers to a view or route predicate factory.  A view or
route predicate factory is most often a class with a constructor
(``__init__``), a ``text`` method, a ``phash`` method, and a ``__call__``
method. For example:

.. code-block:: python
    :linenos:

    class ContentTypePredicate(object):
        def __init__(self, val, config):
            self.val = val

        def text(self):
            return 'content_type = %s' % (self.val,)

        phash = text

        def __call__(self, context, request):
            return getattr(context, 'content_type', None) == self.val

The constructor of a predicate factory takes two arguments: ``val`` and
``config``.  The ``val`` argument will be the argument passed to
``view_config`` (or ``add_view``).  In the example above, it will be the string
``File``.  The second argument, ``config``, will be the Configurator instance
at the time of configuration.

The ``text`` method must return a string.  It should be useful to describe the
behavior of the predicate in error messages.

The ``phash`` method must return a string or a sequence of strings.  It's most
often the same as ``text``, as long as ``text`` uniquely describes the
predicate's name and the value passed to the constructor.  If ``text`` is more
general, or doesn't describe things that way, ``phash`` should return a string
with the name and the value serialized.  The result of ``phash`` is not seen in
output anywhere, it just informs the uniqueness constraints for view
configuration.

The ``__call__`` method of a predicate factory must accept a resource
(``context``) and a request, and must return ``True`` or ``False``.  It is the
"meat" of the predicate.

You can use the same predicate factory as both a view predicate and as a route
predicate, but you'll need to call ``add_view_predicate`` and
``add_route_predicate`` separately with the same factory.

.. _subscriber_predicates:

Subscriber Predicates
~~~~~~~~~~~~~~~~~~~~~

Subscriber predicates work almost exactly like view and route predicates. They
narrow the set of circumstances in which a subscriber will be called. There are
several minor differences between a subscriber predicate and a view or route
predicate:

- There are no default subscriber predicates.  You must register one to use
  one.

- The ``__call__`` method of a subscriber predicate accepts a single ``event``
  object instead of a ``context`` and a ``request``.

- Not every subscriber predicate can be used with every event type.  Some
  subscriber predicates will assume a certain event type.

Here's an example of a subscriber predicate that can be used in conjunction
with a subscriber that subscribes to the :class:`pyramid.events.NewRequest`
event type.

.. code-block:: python
    :linenos:

    class RequestPathStartsWith(object):
        def __init__(self, val, config):
            self.val = val

        def text(self):
            return 'path_startswith = %s' % (self.val,)

        phash = text

        def __call__(self, event):
            return event.request.path.startswith(self.val)

Once you've created a subscriber predicate, it may registered via
:meth:`pyramid.config.Configurator.add_subscriber_predicate`.  For example:

.. code-block:: python

    config.add_subscriber_predicate(
        'request_path_startswith', RequestPathStartsWith)

Once a subscriber predicate is registered, you can use it in a call to
:meth:`pyramid.config.Configurator.add_subscriber` or to
:class:`pyramid.events.subscriber`.  Here's an example of using the previously
registered ``request_path_startswith`` predicate in a call to
:meth:`~pyramid.config.Configurator.add_subscriber`:

.. code-block:: python
    :linenos:

    # define a subscriber in your code

    def yosubscriber(event):
        event.request.yo = 'YO!'

    # and at configuration time

    config.add_subscriber(yosubscriber, NewRequest,
           request_path_startswith='/add_yo')

Here's the same subscriber/predicate/event-type combination used via
:class:`~pyramid.events.subscriber`.

.. code-block:: python
    :linenos:

    from pyramid.events import subscriber

    @subscriber(NewRequest, request_path_startswith='/add_yo')
    def yosubscriber(event):
        event.request.yo = 'YO!'

In either of the above configurations, the ``yosubscriber`` callable will only
be called if the request path starts with ``/add_yo``.  Otherwise the event
subscriber will not be called.

Note that the ``request_path_startswith`` subscriber you defined can be used
with events that have a ``request`` attribute, but not ones that do not.  So,
for example, the predicate can be used with subscribers registered for
:class:`pyramid.events.NewRequest` and :class:`pyramid.events.ContextFound`
events, but it cannot be used with subscribers registered for
:class:`pyramid.events.ApplicationCreated` because the latter type of event has
no ``request`` attribute.  The point being, unlike route and view predicates,
not every type of subscriber predicate will necessarily be applicable for use
in every subscriber registration.  It is not the responsibility of the
predicate author to make every predicate make sense for every event type; it is
the responsibility of the predicate consumer to use predicates that make sense
for a particular event type registration.


.. index::
   single: view derivers

.. _view_derivers:

View Derivers
-------------

.. versionadded:: 1.7

Every URL processed by :app:`Pyramid` is matched against a custom view
pipeline. See :ref:`router_chapter` for how this works. The view pipeline
itself is built from the user-supplied :term:`view callable`, which is then
composed with :term:`view derivers <view deriver>`. A view deriver is a
composable element of the view pipeline which is used to wrap a view with
added functionality. View derivers are very similar to the ``decorator``
argument to :meth:`pyramid.config.Configurator.add_view`, except that they have
the option to execute for every view in the application.

It is helpful to think of a :term:`view deriver` as middleware for views.
Unlike tweens or WSGI middleware which are scoped to the application itself,
a view deriver is invoked once per view in the application, and can use
configuration options from the view to customize its behavior.

Built-in View Derivers
~~~~~~~~~~~~~~~~~~~~~~

There are several built-in view derivers that :app:`Pyramid` will automatically
apply to any view. Below they are defined in order from furthest to closest to
the user-defined :term:`view callable`:

``secured_view``

  Enforce the ``permission`` defined on the view. This element is a no-op if no
  permission is defined. Note there will always be a permission defined if a
  default permission was assigned via
  :meth:`pyramid.config.Configurator.set_default_permission`.

  This element will also output useful debugging information when
  ``pyramid.debug_authorization`` is enabled.

``csrf_view``

  Used to check the CSRF token provided in the request. This element is a
  no-op if ``require_csrf`` view option is not ``True``. Note there will
  always be a ``require_csrf`` option if a default value was assigned via
  :meth:`pyramid.config.Configurator.set_default_csrf_options`.

``owrapped_view``

  Invokes the wrapped view defined by the ``wrapper`` option.

``http_cached_view``

  Applies cache control headers to the response defined by the ``http_cache``
  option. This element is a no-op if the ``pyramid.prevent_http_cache`` setting
  is enabled or the ``http_cache`` option is ``None``.

``decorated_view``

  Wraps the view with the decorators from the ``decorator`` option.

``rendered_view``

  Adapts the result of the :term:`view callable` into a :term:`response`
  object. Below this point the result may be any Python object.

``mapped_view``

  Applies the :term:`view mapper` defined by the ``mapper`` option or the
  application's default view mapper to the :term:`view callable`. This
  is always the closest deriver to the user-defined view and standardizes the
  view pipeline interface to accept ``(context, request)`` from all previous
  view derivers.

.. warning::

   Any view derivers defined ``under`` the ``rendered_view`` are not
   guaranteed to receive a valid response object. Rather they will receive the
   result from the :term:`view mapper` which is likely the original response
   returned from the view. This is possibly a dictionary for a renderer but it
   may be any Python object that may be adapted into a response.

Custom View Derivers
~~~~~~~~~~~~~~~~~~~~

It is possible to define custom view derivers which will affect all views in an
application. There are many uses for this, but most will likely be centered
around monitoring and security. In order to register a custom :term:`view
deriver`, you should create a callable that conforms to the
:class:`pyramid.interfaces.IViewDeriver` interface, and then register it with
your application using :meth:`pyramid.config.Configurator.add_view_deriver`.
For example, below is a callable that can provide timing information for the
view pipeline:

.. code-block:: python
   :linenos:

   import time

   def timing_view(view, info):
       if info.options.get('timed'):
           def wrapper_view(context, request):
               start = time.time()
               response = view(context, request)
               end = time.time()
               response.headers['X-View-Performance'] = '%.3f' % (end - start,)
               return response
           return wrapper_view
       return view

   timing_view.options = ('timed',)

   config.add_view_deriver(timing_view)

The setting of ``timed`` on the timing_view signifies to Pyramid that ``timed``
is a valid ``view_config`` keyword argument now.  The ``timing_view`` custom
view deriver as registered above will only be active for any view defined with
a ``timed=True`` value passed as one of its ``view_config`` keywords.

For example, this view configuration will *not* be a timed view:

.. code-block:: python
   :linenos:

   @view_config(route_name='home')
   def home(request):
       return Response('Home')

But this view *will* have timing information added to the response headers:

.. code-block:: python
   :linenos:

   @view_config(route_name='home', timed=True)
   def home(request):
       return Response('Home')

View derivers are unique in that they have access to most of the options
passed to :meth:`pyramid.config.Configurator.add_view` in order to decide what
to do, and they have a chance to affect every view in the application.

Ordering View Derivers
~~~~~~~~~~~~~~~~~~~~~~

By default, every new view deriver is added between the ``decorated_view`` and
``rendered_view`` built-in derivers. It is possible to customize this ordering
using the ``over`` and ``under`` options. Each option can use the names of
other view derivers in order to specify an ordering. There should rarely be a
reason to worry about the ordering of the derivers except when the deriver
depends on other operations in the view pipeline.

Both ``over`` and ``under`` may also be iterables of constraints. For either
option, if one or more constraints was defined, at least one must be satisfied,
else a :class:`pyramid.exceptions.ConfigurationError` will be raised. This may
be used to define fallback constraints if another deriver is missing.

Two sentinel values exist, :attr:`pyramid.viewderivers.INGRESS` and
:attr:`pyramid.viewderivers.VIEW`, which may be used when specifying
constraints at the edges of the view pipeline. For example, to add a deriver
at the start of the pipeline you may use ``under=INGRESS``.

It is not possible to add a view deriver under the ``mapped_view`` as the
:term:`view mapper` is intimately tied to the signature of the user-defined
:term:`view callable`. If you simply need to know what the original view
callable was, it can be found as ``info.original_view`` on the provided
:class:`pyramid.interfaces.IViewDeriverInfo` object passed to every view
deriver.

.. warning::

   The default constraints for any view deriver are ``over='rendered_view'``
   and ``under='decorated_view'``. When escaping these constraints you must
   take care to avoid cyclic dependencies between derivers. For example, if
   you want to add a new view deriver before ``secured_view`` then
   simply specifying ``over='secured_view'`` is not enough, because the
   default is also under ``decorated view`` there will be an unsatisfiable
   cycle. You must specify a valid ``under`` constraint as well, such as
   ``under=INGRESS`` to fall between INGRESS and ``secured_view`` at the
   beginning of the view pipeline.
