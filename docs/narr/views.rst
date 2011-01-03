.. _views_chapter:

Views
=====

One of the primary jobs of :app:`Pyramid` is to find and invoke a
:term:`view callable` when a :term:`request` reaches your application.  View
callables are bits of code which do something interesting in response to a
request made to your application.

.. note:: 

   A :app:`Pyramid` :term:`view callable` is often referred to in
   conversational shorthand as a :term:`view`.  In this documentation,
   however, we need to use less ambiguous terminology because there
   are significant differences between view *configuration*, the code
   that implements a view *callable*, and the process of view
   *lookup*.

The :ref:`urldispatch_chapter`, and :ref:`traversal_chapter` chapters
describes how, using information from the :term:`request`, a
:term:`context` resource is computed.  But the context resource itself
isn't very useful without an associated :term:`view callable`.  A view
callable returns a response to a user, often using the context resource
to do so.

The job of actually locating and invoking the "best" :term:`view callable` is
the job of the :term:`view lookup` subsystem.  The view lookup subsystem
compares the resource supplied by :term:`resource location` and information
in the :term:`request` against :term:`view configuration` statements made by
the developer to choose the most appropriate view callable for a specific
set of circumstances.

This chapter describes how view callables work. In the
:ref:`view_config_chapter` chapter, there are details about performing
view configuration, and a detailed explanation of view lookup.

View Callables
--------------

View callables are, at the risk of sounding obvious, callable Python
objects. Specifically, view callables can be functions, classes, or
instances that implement an ``__call__`` method (making the
instance callable).

View callables must, at a minimum, accept a single argument named
``request``.  This argument represents a :app:`Pyramid` :term:`Request`
object.  A request object encapsulates a WSGI environment provided to
:app:`Pyramid` by the upstream :term:`WSGI` server. As you might expect,
the request object contains everything your application needs to know
about the specific HTTP request being made.

A view callable's ultimate responsibility is to create a :mod:`Pyramid`
:term:`Response` object. This can be done by creating the response
object in the view callable code and returning it directly, as we will
be doing in this chapter. However, if a view callable does not return a
response itself, it can be configured to use a :term:`renderer` that
converts its return value into a :term:`Response` object. Using
renderers is the common way that templates are used with view callables
to generate markup.  See the :ref:`renderers_chapter` chapter for
details.

.. index::
   single: view calling convention
   single: view function

.. _function_as_view:

Defining a View Callable as a Function
--------------------------------------

One of the easiest way to define a view callable is to create a function that
accepts a single argument named ``request``, and which returns a
:term:`Response` object.  For example, this is a "hello world" view callable
implemented as a function:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   def hello_world(request):
       return Response('Hello world!')

.. index::
   single: view calling convention
   single: view class

.. _class_as_view:

Defining a View Callable as a Class
-----------------------------------

A view callable may also be represented by a Python class instead of a
function.  When a view callable is a class, the calling semantics are
slightly different than when it is a function or another non-class callable.
When a view callable is a class, the class' ``__init__`` is called with a
``request`` parameter.  As a result, an instance of the class is created.
Subsequently, that instance's ``__call__`` method is invoked with no
parameters.  Views defined as classes must have the following traits:

- an ``__init__`` method that accepts a ``request`` argument.

- a ``__call__`` (or other) method that accepts no parameters and which
  returns a response.

For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   class MyView(object):
       def __init__(self, request):
           self.request = request

       def __call__(self):
           return Response('hello')

The request object passed to ``__init__`` is the same type of request object
described in :ref:`function_as_view`.

If you'd like to use a different attribute than ``__call__`` to represent the
method expected to return a response, you can either:

- use an ``attr`` value as part of the configuration for the view.  See
  :ref:`view_configuration_parameters`.  The same view callable class can be
  used in different view configuration statements with different ``attr``
  values, each pointing at a different method of the class if you'd like the
  class to represent a collection of related view callables.

- treat the class as a :term:`view handler` by using it as the ``handler=``
  argument of a call to :meth:`pyramid.config.Configurator.add_handler`.

.. index::
   single: view calling convention

.. _request_and_context_view_definitions:

Alternate View Callable Argument/Calling Conventions
----------------------------------------------------

Usually, view callables are defined to accept only a single argument:
``request``.  However, view callables may alternately be defined as classes,
functions, or any callable that accept *two* positional arguments: a
:term:`context` resource as the first argument and a :term:`request` as the
second argument.

The :term:`context` and :term:`request` arguments passed to a view function
defined in this style can be defined as follows:

context

  The :term:`resource` object found via tree :term:`traversal` or :term:`URL
  dispatch`.

request
  A :app:`Pyramid` Request object representing the current WSGI request.

The following types work as view callables in this style:

#. Functions that accept two arguments: ``context``, and ``request``,
   e.g.:

   .. code-block:: python
	  :linenos:

	  from pyramid.response import Response

	  def view(context, request):
		  return Response('OK')

#. Classes that have an ``__init__`` method that accepts ``context,
   request`` and a ``__call__`` which accepts no arguments, e.g.:

   .. code-block:: python
	  :linenos:

	  from pyramid.response import Response

	  class view(object):
		  def __init__(self, context, request):
			  self.context = context
			  self.request = request

		  def __call__(self):
			  return Response('OK')

#. Arbitrary callables that have a ``__call__`` method that accepts
   ``context, request``, e.g.:

   .. code-block:: python
	  :linenos:

	  from pyramid.response import Response

	  class View(object):
		  def __call__(self, context, request):
			  return Response('OK')
	  view = View() # this is the view callable

This style of calling convention is most useful for :term:`traversal` based
applications, where the context object is frequently used within the view
callable code itself.

No matter which view calling convention is used, the view code always has
access to the context via ``request.context``.

.. index::
   single: view response
   single: response

.. _the_response:

View Callable Responses
-----------------------

A view callable may always return an object that implements the :app:`Pyramid`
:term:`Response` interface.  The easiest way to return something that
implements the :term:`Response` interface is to return a
:class:`pyramid.response.Response` object instance directly.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   def view(request):
       return Response('OK')

You don't need to always use :class:`pyramid.response.Response` to represent a
response.  :app:`Pyramid` provides a range of different "exception" classes
which can act as response objects too.  For example, an instance of the class
:class:`pyramid.httpexceptions.HTTPFound` is also a valid response object (see
:ref:`http_redirect`).  A view can actually return any object that has the
following attributes.  

status
  The HTTP status code (including the name) for the response as a string.
  E.g. ``200 OK`` or ``401 Unauthorized``.

headerlist
  A sequence of tuples representing the list of headers that should be
  set in the response.  E.g. ``[('Content-Type', 'text/html'),
  ('Content-Length', '412')]``

app_iter
  An iterable representing the body of the response.  This can be a
  list, e.g. ``['<html><head></head><body>Hello
  world!</body></html>']`` or it can be a file-like object, or any
  other sort of iterable.

These attributes form the notional "Pyramid Response interface".

.. index::
   single: view http redirect
   single: http redirect (from a view)

.. _http_redirect:

Using a View Callable to Do an HTTP Redirect
--------------------------------------------

You can issue an HTTP redirect from within a view by returning a particular
kind of response.

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import HTTPFound

   def myview(request):
       return HTTPFound(location='http://example.com')

All exception types from the :mod:`pyramid.httpexceptions` module implement
the :term:`Response` interface; any can be returned as the response from a
view.  See :mod:`pyramid.httpexceptions` for the documentation for the
``HTTPFound`` exception; it also includes other response types that imply
other HTTP response codes, such as ``HTTPUnauthorized`` for ``401
Unauthorized``.

.. note::

   Although exception types from the :mod:`pyramid.httpexceptions` module are
   in fact bona fide Python :class:`Exception` types, the :app:`Pyramid` view
   machinery expects them to be *returned* by a view callable rather than
   *raised*.

   It is possible, however, in Python 2.5 and above, to configure an
   *exception view* to catch these exceptions, and return an appropriate
   :class:`pyramid.response.Response`. The simplest such view could just
   catch and return the original exception. See :ref:`exception_views` for
   more details.

.. index::
   single: view exceptions

.. _special_exceptions_in_callables:

Using Special Exceptions In View Callables
------------------------------------------

Usually when a Python exception is raised within a view callable,
:app:`Pyramid` allows the exception to propagate all the way out to the
:term:`WSGI` server which invoked the application.

However, for convenience, two special exceptions exist which are always
handled by :app:`Pyramid` itself.  These are
:exc:`pyramid.exceptions.NotFound` and :exc:`pyramid.exceptions.Forbidden`.
Both are exception classes which accept a single positional constructor
argument: a ``message``.

If :exc:`pyramid.exceptions.NotFound` is raised within view code, the result
of the :term:`Not Found View` will be returned to the user agent which
performed the request.

If :exc:`pyramid.exceptions.Forbidden` is raised within view code, the result
of the :term:`Forbidden View` will be returned to the user agent which
performed the request.

In all cases, the message provided to the exception constructor is made
available to the view which :app:`Pyramid` invokes as
``request.exception.args[0]``.

.. index::
   single: exception views

.. _exception_views:

Exception Views
---------------

The machinery which allows the special :exc:`pyramid.exceptions.NotFound` and
:exc:`pyramid.exceptions.Forbidden` exceptions to be caught by specialized
views as described in :ref:`special_exceptions_in_callables` can also be used
by application developers to convert arbitrary exceptions to responses.

To register a view that should be called whenever a particular exception is
raised from with :app:`Pyramid` view code, use the exception class or one of
its superclasses as the ``context`` of a view configuration which points at a
view callable you'd like to generate a response.

For example, given the following exception class in a module named
``helloworld.exceptions``:

.. code-block:: python
   :linenos:

   class ValidationFailure(Exception):
       def __init__(self, msg):
           self.msg = msg


You can wire a view callable to be called whenever any of your *other* code
raises a ``hellworld.exceptions.ValidationFailure`` exception:

.. code-block:: python
   :linenos:

   from helloworld.exceptions import ValidationFailure

   @view_config(context=ValidationFailure)
   def failed_validation(exc, request):
       response =  Response('Failed validation: %s' % exc.msg)
       response.status_int = 500
       return response

Assuming that a :term:`scan` was run to pick up this view registration, this
view callable will be invoked whenever a
``helloworld.exceptions.ValidationError`` is raised by your application's
view code.  The same exception raised by a custom root factory or a custom
traverser is also caught and hooked.

Other normal view predicates can also be used in combination with an
exception view registration:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from pyramid.exceptions import NotFound
   from pyramid.httpexceptions import HTTPNotFound

   @view_config(context=NotFound, route_name='home')
   def notfound_view(request):
       return HTTPNotFound()

The above exception view names the ``route_name`` of ``home``, meaning that
it will only be called when the route matched has a name of ``home``.  You
can therefore have more than one exception view for any given exception in
the system: the "most specific" one will be called when the set of request
circumstances match the view registration.

The only view predicate that cannot be used successfully when creating
an exception view configuration is ``name``.  The name used to look up
an exception view is always the empty string.  Views registered as
exception views which have a name will be ignored.

.. note::

  Normal (i.e., non-exception) views registered against a context resource
  type which inherits from :exc:`Exception` will work normally.  When an
  exception view configuration is processed, *two* views are registered.  One
  as a "normal" view, the other as an "exception" view.  This means that you
  can use an exception as ``context`` for a normal view.

Exception views can be configured with any view registration mechanism:
``@view_config`` decorator, ZCML, or imperative ``add_view`` styles.

.. index::
   single: unicode, views, and forms
   single: forms, views, and unicode
   single: views, forms, and unicode

