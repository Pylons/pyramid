.. _views_chapter:

Views
=====

One of the primary jobs of :app:`Pyramid` is to find and invoke a :term:`view
callable` when a :term:`request` reaches your application.  View callables
are bits of code which do something interesting in response to a request made
to your application.  They are the "meat" of any interesting web application.

.. note:: 

   A :app:`Pyramid` :term:`view callable` is often referred to in
   conversational shorthand as a :term:`view`.  In this documentation,
   however, we need to use less ambiguous terminology because there
   are significant differences between view *configuration*, the code
   that implements a view *callable*, and the process of view
   *lookup*.

This chapter describes how view callables should be defined. We'll have to
wait until a following chapter (entitled :ref:`view_config_chapter`) to find
out how we actually tell :app:`Pyramid` to wire up view callables to
particular URL patterns and other request circumstances.

.. index::
   single: view callables

View Callables
--------------

View callables are, at the risk of sounding obvious, callable Python
objects. Specifically, view callables can be functions, classes, or instances
that implement an ``__call__`` method (making the instance callable).

View callables must, at a minimum, accept a single argument named
``request``.  This argument represents a :app:`Pyramid` :term:`Request`
object.  A request object represents a :term:`WSGI` environment provided to
:app:`Pyramid` by the upstream WSGI server. As you might expect, the request
object contains everything your application needs to know about the specific
HTTP request being made.

A view callable's ultimate responsibility is to create a :mod:`Pyramid`
:term:`Response` object. This can be done by creating a :term:`Response`
object in the view callable code and returning it directly or by raising
special kinds of exceptions from within the body of a view callable.

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
When a view callable is a class, the class' ``__init__`` method is called with a
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
method expected to return a response, you can use an ``attr`` value as part 
of the configuration for the view.  See :ref:`view_configuration_parameters`.
The same view callable class can be used in different view configuration 
statements with different ``attr`` values, each pointing at a different 
method of the class if you'd like the class to represent a collection of 
related view callables.

.. index::
   single: view response
   single: response

.. _the_response:

View Callable Responses
-----------------------

A view callable may return an object that implements the :app:`Pyramid`
:term:`Response` interface.  The easiest way to return something that
implements the :term:`Response` interface is to return a
:class:`pyramid.response.Response` object instance directly.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   def view(request):
       return Response('OK')

:app:`Pyramid` provides a range of different "exception" classes which
inherit from :class:`pyramid.response.Response`.  For example, an instance of
the class :class:`pyramid.httpexceptions.HTTPFound` is also a valid response
object because it inherits from :class:`~pyramid.response.Response`.  For
examples, see :ref:`http_exceptions` and :ref:`http_redirect`.

.. note::

   You can also return objects from view callables that aren't instances of
   :class:`pyramid.response.Response` in various circumstances.  This can be
   helpful when writing tests and when attempting to share code between view
   callables.  See :ref:`renderers_chapter` for the common way to allow for
   this.  A much less common way to allow for view callables to return
   non-Response objects is documented in :ref:`using_iresponse`.

.. index::
   single: view exceptions

.. _special_exceptions_in_callables:

Using Special Exceptions In View Callables
------------------------------------------

Usually when a Python exception is raised within a view callable,
:app:`Pyramid` allows the exception to propagate all the way out to the
:term:`WSGI` server which invoked the application.  It is usually caught and
logged there.

However, for convenience, a special set of exceptions exists.  When one of
these exceptions is raised within a view callable, it will always cause
:app:`Pyramid` to generate a response.  These are known as :term:`HTTP
exception` objects.

.. index::
   single: HTTP exceptions

.. _http_exceptions:

HTTP Exceptions
~~~~~~~~~~~~~~~

All classes documented in the :mod:`pyramid.httpexceptions` module documented
as inheriting from the :class:`pryamid.httpexceptions.HTTPException` are
:term:`http exception` objects.  An instances of an HTTP exception object may
either be *returned* or *raised* from within view code.  In either case
(return or raise) the instance will be used as as the view's response.

For example, the :class:`pyramid.httpexceptions.HTTPUnauthorized` exception
can be raised.  This will cause a response to be generated with a ``401
Unauthorized`` status:

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import HTTPUnauthorized

   def aview(request):
       raise HTTPUnauthorized()

An HTTP exception, instead of being raised, can alternately be *returned*
(HTTP exceptions are also valid response objects):

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import HTTPUnauthorized

   def aview(request):
       return HTTPUnauthorized()

A shortcut for creating an HTTP exception is the
:func:`pyramid.httpexceptions.exception_response` function.  This function
accepts an HTTP status code and returns the corresponding HTTP exception.
For example, instead of importing and constructing a
:class:`~pyramid.httpexceptions.HTTPUnauthorized` response object, you can
use the :func:`~pyramid.httpexceptions.exception_response` function to
construct and return the same object.

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import exception_response

   def aview(request):
       raise exception_response(401)

This is the case because ``401`` is the HTTP status code for "HTTP
Unauthorized".  Therefore, ``raise exception_response(401)`` is functionally
equivalent to ``raise HTTPUnauthorized()``.  Documentation which maps each
HTTP response code to its purpose and its associated HTTP exception object is
provided within :mod:`pyramid.httpexceptions`.

.. note:: The :func:`~pyramid.httpexceptions.exception_response` function is
   new as of Pyramid 1.1.

How Pyramid Uses HTTP Exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HTTP exceptions are meant to be used directly by application
developers.  However, Pyramid itself will raise two HTTP exceptions at
various points during normal operations:
:exc:`pyramid.httpexceptions.HTTPNotFound` and
:exc:`pyramid.httpexceptions.HTTPForbidden`.  Pyramid will raise the
:exc:`~pyramid.httpexceptions.HTTPNotFound` exception are raised when it
cannot find a view to service a request.  Pyramid will raise the
:exc:`~pyramid.httpexceptions.Forbidden` exception or when authorization was
forbidden by a security policy.

If :exc:`~pyramid.httpexceptions.HTTPNotFound` is raised by Pyramid itself or
within view code, the result of the :term:`Not Found View` will be returned
to the user agent which performed the request.

If :exc:`~pyramid.httpexceptions.HTTPForbidden` is raised by Pyramid itself
within view code, the result of the :term:`Forbidden View` will be returned
to the user agent which performed the request.

.. index::
   single: exception views

.. _exception_views:

Custom Exception Views
----------------------

The machinery which allows HTTP exceptions to be raised and caught by
specialized views as described in :ref:`special_exceptions_in_callables` can
also be used by application developers to convert arbitrary exceptions to
responses.

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
raises a ``helloworld.exceptions.ValidationFailure`` exception:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from helloworld.exceptions import ValidationFailure

   @view_config(context=ValidationFailure)
   def failed_validation(exc, request):
       response =  Response('Failed validation: %s' % exc.msg)
       response.status_int = 500
       return response

Assuming that a :term:`scan` was run to pick up this view registration, this
view callable will be invoked whenever a
``helloworld.exceptions.ValidationFailure`` is raised by your application's
view code.  The same exception raised by a custom root factory, a custom
traverser, or a custom view or route predicate is also caught and hooked.

Other normal view predicates can also be used in combination with an
exception view registration:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from helloworld.exceptions import ValidationFailure

   @view_config(context=ValidationFailure, route_name='home')
   def failed_validation(exc, request):
       response =  Response('Failed validation: %s' % exc.msg)
       response.status_int = 500
       return response

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
``@view_config`` decorator or imperative ``add_view`` styles.

.. index::
   single: view http redirect
   single: http redirect (from a view)

.. _http_redirect:

Using a View Callable to Do an HTTP Redirect
--------------------------------------------

You can issue an HTTP redirect by using the
:class:`pyramid.httpexceptions.HTTPFound` class.  Raising or returning an
instance of this class will cause the client to receive a "302 Found"
response.

To do so, you can *return* a :class:`pyramid.httpexceptions.HTTPFound`
instance.

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import HTTPFound

   def myview(request):
       return HTTPFound(location='http://example.com')

Alternately, you can *raise* an HTTPFound exception instead of returning one.

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import HTTPFound

   def myview(request):
       raise HTTPFound(location='http://example.com')

When the instance is raised, it is caught by the default :term:`exception
response` handler and turned into a response.

.. index::
   single: unicode, views, and forms
   single: forms, views, and unicode
   single: views, forms, and unicode

Handling Form Submissions in View Callables (Unicode and Character Set Issues)
------------------------------------------------------------------------------

Most web applications need to accept form submissions from web browsers and
various other clients.  In :app:`Pyramid`, form submission handling logic is
always part of a :term:`view`.  For a general overview of how to handle form
submission data using the :term:`WebOb` API, see :ref:`webob_chapter` and
`"Query and POST variables" within the WebOb documentation
<http://docs.webob.org/en/latest/reference.html#query-post-variables>`_.
:app:`Pyramid` defers to WebOb for its request and response implementations,
and handling form submission data is a property of the request
implementation.  Understanding WebOb's request API is the key to
understanding how to process form submission data.

There are some defaults that you need to be aware of when trying to handle
form submission data in a :app:`Pyramid` view.  Having high-order (i.e.,
non-ASCII) characters in data contained within form submissions is
exceedingly common, and the UTF-8 encoding is the most common encoding used
on the web for character data. Since Unicode values are much saner than
working with and storing bytestrings, :app:`Pyramid` configures the
:term:`WebOb` request machinery to attempt to decode form submission values
into Unicode from UTF-8 implicitly.  This implicit decoding happens when view
code obtains form field values via the ``request.params``, ``request.GET``,
or ``request.POST`` APIs (see :ref:`request_module` for details about these
APIs).

.. note::

   Many people find the difference between Unicode and UTF-8 confusing.
   Unicode is a standard for representing text that supports most of the
   world's writing systems. However, there are many ways that Unicode data
   can be encoded into bytes for transit and storage. UTF-8 is a specific
   encoding for Unicode, that is backwards-compatible with ASCII. This makes
   UTF-8 very convenient for encoding data where a large subset of that data
   is ASCII characters, which is largely true on the web. UTF-8 is also the
   standard character encoding for URLs.

As an example, let's assume that the following form page is served up to a
browser client, and its ``action`` points at some :app:`Pyramid` view code:

.. code-block:: xml
   :linenos:

   <html xmlns="http://www.w3.org/1999/xhtml">
     <head>
       <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
     </head>
     <form method="POST" action="myview">
       <div>
         <input type="text" name="firstname"/>
       </div> 
       <div>
         <input type="text" name="lastname"/>
       </div>
       <input type="submit" value="Submit"/>
     </form>
   </html>

The ``myview`` view code in the :app:`Pyramid` application *must* expect that
the values returned by ``request.params`` will be of type ``unicode``, as
opposed to type ``str``. The following will work to accept a form post from
the above form:

.. code-block:: python
   :linenos:

   def myview(request):
       firstname = request.params['firstname']
       lastname = request.params['lastname']

But the following ``myview`` view code *may not* work, as it tries to decode
already-decoded (``unicode``) values obtained from ``request.params``:

.. code-block:: python
   :linenos:

   def myview(request):
       # the .decode('utf-8') will break below if there are any high-order
       # characters in the firstname or lastname
       firstname = request.params['firstname'].decode('utf-8')
       lastname = request.params['lastname'].decode('utf-8')

For implicit decoding to work reliably, you should ensure that every form you
render that posts to a :app:`Pyramid` view explicitly defines a charset
encoding of UTF-8. This can be done via a response that has a
``;charset=UTF-8`` in its ``Content-Type`` header; or, as in the form above,
with a ``meta http-equiv`` tag that implies that the charset is UTF-8 within
the HTML ``head`` of the page containing the form.  This must be done
explicitly because all known browser clients assume that they should encode
form data in the same character set implied by ``Content-Type`` value of the
response containing the form when subsequently submitting that form. There is
no other generally accepted way to tell browser clients which charset to use
to encode form data.  If you do not specify an encoding explicitly, the
browser client will choose to encode form data in its default character set
before submitting it, which may not be UTF-8 as the server expects.  If a
request containing form data encoded in a non-UTF8 charset is handled by your
view code, eventually the request code accessed within your view will throw
an error when it can't decode some high-order character encoded in another
character set within form data, e.g., when ``request.params['somename']`` is
accessed.

If you are using the :class:`~pyramid.response.Response` class to generate a
response, or if you use the ``render_template_*`` templating APIs, the UTF-8
charset is set automatically as the default via the ``Content-Type`` header.
If you return a ``Content-Type`` header without an explicit charset, a
request will add a ``;charset=utf-8`` trailer to the ``Content-Type`` header
value for you, for response content types that are textual
(e.g. ``text/html``, ``application/xml``, etc) as it is rendered.  If you are
using your own response object, you will need to ensure you do this yourself.

.. note:: Only the *values* of request params obtained via
   ``request.params``, ``request.GET`` or ``request.POST`` are decoded
   to Unicode objects implicitly in the :app:`Pyramid` default
   configuration.  The keys are still (byte) strings.


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
   request`` and a ``__call__`` method which accepts no arguments, e.g.:

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
   single: Pylons-style controller dispatch

Pylons-1.0-Style "Controller" Dispatch
--------------------------------------

A package named :term:`pyramid_handlers` (available from PyPI) provides an
analogue of :term:`Pylons` -style "controllers", which are a special kind of
view class which provides more automation when your application uses
:term:`URL dispatch` solely.

