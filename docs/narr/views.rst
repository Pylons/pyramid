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

The :ref:`urldispatch_chapter`, and :ref:`traversal_chapter` describes how,
using information from the :term:`request`, a :term:`context` resource is
computed.  But the context resource itself isn't very useful without an
associated :term:`view callable`.  A view callable returns a response to a
user, often using the context resource to do so.

The job of actually locating and invoking the "best" :term:`view callable` is
the job of the :term:`view lookup` subsystem.  The view lookup subsystem
compares the resource supplied by :term:`resource location` and information
in the :term:`request` against :term:`view configuration` statements made by
the developer to choose the most appropriate view callable for a specific
set of circumstances.

This chapter provides documentation detailing the process of creating
view callables, documentation about performing view configuration, and
a detailed explanation of view lookup.

View Callables
--------------

No matter how a view callable is eventually found, all view callables
used by :app:`Pyramid` must be constructed in the same way, and
must return the same kind of return value.

Most view callables accept a single argument named ``request``.  This
argument represents a :app:`Pyramid` :term:`Request` object.  A request
object encapsulates a WSGI environment as represented to :app:`Pyramid` by
the upstream :term:`WSGI` server.

In general, a view callable must return a :mod:`Pyramid` :term:`Response`
object.

.. note:: The above statement, though it sounds definitive, isn't always
   true.  See :ref:`renderers_chapter` for information related to using a
   :term:`renderer` to convert a non-Response view callable return value into
   a Response object.

View callables can be functions, instances, or classes.  

.. index::
   single: view calling convention
   single: view function

.. _function_as_view:

Defining a View Callable as a Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~

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

Handling Form Submissions in View Callables (Unicode and Character Set Issues)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most web applications need to accept form submissions from web browsers and
various other clients.  In :app:`Pyramid`, form submission handling logic is
always part of a :term:`view`.  For a general overview of how to handle form
submission data using the :term:`WebOb` API, see :ref:`webob_chapter` and
`"Query and POST variables" within the WebOb documentation
<http://pythonpaste.org/webob/reference.html#query-post-variables>`_.
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

If you are using the :class:`pyramid.response.Response` class to generate a
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
   single: view configuration

.. _view_configuration:

View Configuration: Mapping a Resource or URL Pattern to a View Callable
------------------------------------------------------------------------

A developer makes a :term:`view callable` available for use within a
:app:`Pyramid` application via :term:`view configuration`.  A view
configuration associates a view callable with a set of statements that
determine the set of circumstances which must be true for the view callable
to be invoked.

A view configuration statement is made about information present in the
:term:`context` resource and the :term:`request`.

View configuration is performed in one of these ways:

- by running a :term:`scan` against application source code which has a
  :class:`pyramid.view.view_config` decorator attached to a Python object as
  per :class:`pyramid.view.view_config` and
  :ref:`mapping_views_using_a_decorator_section`.

- by using the :meth:`pyramid.config.Configurator.add_view` method as per
  :meth:`pyramid.config.Configurator.add_view` and
  :ref:`mapping_views_using_imperative_config_section`.

- By specifying a view within a :term:`route configuration`.  View
  configuration via a route configuration is performed by using the
  :meth:`pyramid.config.Configurator.add_route` method, passing a ``view``
  argument specifying a view callable.

- by using the :meth:`pyramid.config.Configurator.add_handler` against a
  :term:`view handler` class (useful only for :term:`URL dispatch`
  applications).

.. note:: You can also add view configuration by adding a ``<view>``,
   ``<route>`` or ``<handler>`` declaration to :term:`ZCML` used by your
   application as per :ref:`mapping_views_using_zcml_section`,
   :ref:`view_directive`, :ref:`route_directive` or :ref:`handler_directive`.

.. _view_configuration_parameters:

View Configuration Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All forms of view configuration accept the same general types of arguments.

Many arguments supplied during view configuration are :term:`view predicate`
arguments.  View predicate arguments used during view configuration are used
to narrow the set of circumstances in which :mod:`view lookup` will find a
particular view callable.  In general, the fewer number of predicates which
are supplied to a particular view configuration, the more likely it is that
the associated view callable will be invoked.  The greater the number
supplied, the less likely.

Some view configuration arguments are non-predicate arguments.  These tend to
modify the response of the view callable or prevent the view callable from
being invoked due to an authorization policy.  The presence of non-predicate
arguments in a view configuration does not narrow the circumstances in which
the view callable will be invoked.

Non-Predicate Arguments
+++++++++++++++++++++++

``permission``
  The name of a :term:`permission` that the user must possess in order to
  invoke the :term:`view callable`.  See :ref:`view_security_section` for
  more information about view security and permissions.
  
  If ``permission`` is not supplied, no permission is registered for this
  view (it's accessible by any caller).

``attr``
  The view machinery defaults to using the ``__call__`` method of the
  :term:`view callable` (or the function itself, if the view callable is a
  function) to obtain a response.  The ``attr`` value allows you to vary the
  method attribute used to obtain the response.  For example, if your view
  was a class, and the class has a method named ``index`` and you wanted to
  use this method instead of the class' ``__call__`` method to return the
  response, you'd say ``attr="index"`` in the view configuration for the
  view.  This is most useful when the view definition is a class.

  If ``attr`` is not supplied, ``None`` is used (implying the function itself
  if the view is a function, or the ``__call__`` callable attribute if the
  view is a class).

``renderer``
  Denotes the :term:`renderer` implementation which will be used to construct
  a :term:`response` from the associated view callable's return value. (see
  also :ref:`renderers_chapter`).

  This is either a single string term (e.g. ``json``) or a string implying a
  path or :term:`asset specification` (e.g. ``templates/views.pt``) naming a
  :term:`renderer` implementation.  If the ``renderer`` value does not
  contain a dot (``.``), the specified string will be used to look up a
  renderer implementation, and that renderer implementation will be used to
  construct a response from the view return value.  If the ``renderer`` value
  contains a dot (``.``), the specified term will be treated as a path, and
  the filename extension of the last element in the path will be used to look
  up the renderer implementation, which will be passed the full path.

  When the renderer is a path, although a path is usually just a simple
  relative pathname (e.g. ``templates/foo.pt``, implying that a template
  named "foo.pt" is in the "templates" directory relative to the directory of
  the current :term:`package`), a path can be absolute, starting with a slash
  on UNIX or a drive letter prefix on Windows.  The path can alternately be a
  :term:`asset specification` in the form
  ``some.dotted.package_name:relative/path``, making it possible to address
  template assets which live in a separate package.

  The ``renderer`` attribute is optional.  If it is not defined, the "null"
  renderer is assumed (no rendering is performed and the value is passed back
  to the upstream :app:`Pyramid` machinery unmolested).  Note that if the
  view callable itself returns a :term:`response` (see :ref:`the_response`),
  the specified renderer implementation is never called.

``wrapper``
  The :term:`view name` of a different :term:`view configuration` which will
  receive the response body of this view as the ``request.wrapped_body``
  attribute of its own :term:`request`, and the :term:`response` returned by
  this view as the ``request.wrapped_response`` attribute of its own request.
  Using a wrapper makes it possible to "chain" views together to form a
  composite response.  The response of the outermost wrapper view will be
  returned to the user.  The wrapper view will be found as any view is found:
  see :ref:`view_lookup`.  The "best" wrapper view will be found based on the
  lookup ordering: "under the hood" this wrapper view is looked up via
  ``pyramid.view.render_view_to_response(context, request,
  'wrapper_viewname')``. The context and request of a wrapper view is the
  same context and request of the inner view.

  If ``wrapper`` is not supplied, no wrapper view is used.

Predicate Arguments
+++++++++++++++++++

These arguments modify view lookup behavior. In general, the more predicate
arguments that are supplied, the more specific, and narrower the usage of the
configured view.

``name``
  The :term:`view name` required to match this view callable.  Read
  :ref:`traversal_chapter` to understand the concept of a view name.

  If ``name`` is not supplied, the empty string is used (implying the default
  view).

``context``
  An object representing a Python class that the :term:`context` resource
  must be an instance of *or* the :term:`interface` that the :term:`context`
  resource must provide in order for this view to be found and called.  This
  predicate is true when the :term:`context` resource is an instance of the
  represented class or if the :term:`context` resource provides the
  represented interface; it is otherwise false.

  If ``context`` is not supplied, the value ``None``, which matches any
  resource, is used.

``route_name``
  If ``route_name`` is supplied, the view callable will be invoked only when
  the named route has matched.

  This value must match the ``name`` of a :term:`route configuration`
  declaration (see :ref:`urldispatch_chapter`) that must match before this
  view will be called.  Note that the ``route`` configuration referred to by
  ``route_name`` will usually have a ``*traverse`` token in the value of its
  ``pattern``, representing a part of the path that will be used by
  :term:`traversal` against the result of the route's :term:`root factory`.

  If ``route_name`` is not supplied, the view callable will be have a chance
  of being invoked if no other route was matched. This is when the
  request/context pair found via :term:`resource location` does not indicate
  it matched any configured route.

``request_type``
  This value should be an :term:`interface` that the :term:`request` must
  provide in order for this view to be found and called.

  If ``request_type`` is not supplied, the value ``None`` is used, implying
  any request type.

  *This is an advanced feature, not often used by "civilians"*.

``request_method``
  This value can either be one of the strings ``GET``, ``POST``, ``PUT``,
  ``DELETE``, or ``HEAD`` representing an HTTP ``REQUEST_METHOD``.  A view
  declaration with this argument ensures that the view will only be called
  when the request's ``method`` attribute (aka the ``REQUEST_METHOD`` of the
  WSGI environment) string matches the supplied value.

  If ``request_method`` is not supplied, the view will be invoked regardless
  of the ``REQUEST_METHOD`` of the :term:`WSGI` environment.

``request_param``
  This value can be any string.  A view declaration with this argument
  ensures that the view will only be called when the :term:`request` has a
  key in the ``request.params`` dictionary (an HTTP ``GET`` or ``POST``
  variable) that has a name which matches the supplied value.

  If the value supplied has a ``=`` sign in it,
  e.g. ``request_params="foo=123"``, then the key (``foo``) must both exist
  in the ``request.params`` dictionary, *and* the value must match the right
  hand side of the expression (``123``) for the view to "match" the current
  request.

  If ``request_param`` is not supplied, the view will be invoked without
  consideration of keys and values in the ``request.params`` dictionary.

``containment``
  This value should be a reference to a Python class or :term:`interface`
  that a parent object in the context resource's :term:`lineage` must provide
  in order for this view to be found and called.  The resources in your
  resource tree must be "location-aware" to use this feature.

  If ``containment`` is not supplied, the interfaces and classes in the
  lineage are not considered when deciding whether or not to invoke the view
  callable.

  See :ref:`location_aware` for more information about location-awareness.

``xhr``
  This value should be either ``True`` or ``False``.  If this value is
  specified and is ``True``, the :term:`WSGI` environment must possess an
  ``HTTP_X_REQUESTED_WITH`` (aka ``X-Requested-With``) header that has the
  value ``XMLHttpRequest`` for the associated view callable to be found and
  called.  This is useful for detecting AJAX requests issued from jQuery,
  Prototype and other Javascript libraries.

  If ``xhr`` is not specified, the ``HTTP_X_REQUESTED_WITH`` HTTP header is
  not taken into consideration when deciding whether or not to invoke the
  associated view callable.

``accept``
  The value of this argument represents a match query for one or more
  mimetypes in the ``Accept`` HTTP request header.  If this value is
  specified, it must be in one of the following forms: a mimetype match token
  in the form ``text/plain``, a wildcard mimetype match token in the form
  ``text/*`` or a match-all wildcard mimetype match token in the form
  ``*/*``.  If any of the forms matches the ``Accept`` header of the request,
  this predicate will be true.

  If ``accept`` is not specified, the ``HTTP_ACCEPT`` HTTP header is not
  taken into consideration when deciding whether or not to invoke the
  associated view callable.

``header``
  This value represents an HTTP header name or a header name/value pair.

  If ``header`` is specified, it must be a header name or a
  ``headername:headervalue`` pair.

  If ``header`` is specified without a value (a bare header name only,
  e.g. ``If-Modified-Since``), the view will only be invoked if the HTTP
  header exists with any value in the request.

  If ``header`` is specified, and possesses a name/value pair
  (e.g. ``User-Agent:Mozilla/.*``), the view will only be invoked if the HTTP
  header exists *and* the HTTP header matches the value requested.  When the
  ``headervalue`` contains a ``:`` (colon), it will be considered a
  name/value pair (e.g. ``User-Agent:Mozilla/.*`` or ``Host:localhost``).
  The value portion should be a regular expression.

  Whether or not the value represents a header name or a header name/value
  pair, the case of the header name is not significant.

  If ``header`` is not specified, the composition, presence or absence of
  HTTP headers is not taken into consideration when deciding whether or not
  to invoke the associated view callable.

``path_info``
  This value represents a regular expression pattern that will be tested
  against the ``PATH_INFO`` WSGI environment variable to decide whether or
  not to call the associated view callable.  If the regex matches, this
  predicate will be ``True``.

  If ``path_info`` is not specified, the WSGI ``PATH_INFO`` is not taken into
  consideration when deciding whether or not to invoke the associated view
  callable.

``custom_predicates``
  If ``custom_predicates`` is specified, it must be a sequence of references
  to custom predicate callables.  Use custom predicates when no set of
  predefined predicates do what you need.  Custom predicates can be combined
  with predefined predicates as necessary.  Each custom predicate callable
  should accept two arguments: ``context`` and ``request`` and should return
  either ``True`` or ``False`` after doing arbitrary evaluation of the
  context resource and/or the request.  If all callables return ``True``, the
  associated view callable will be considered viable for a given request.

  If ``custom_predicates`` is not specified, no custom predicates are
  used.

.. index::
   single: view_config decorator

.. _mapping_views_using_a_decorator_section:

View Configuration Using the ``@view_config`` Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For better locality of reference, you may use the
:class:`pyramid.view.view_config` decorator to associate your view functions
with URLs instead of using :term:`ZCML` or imperative configuration for the
same purpose.

.. warning::

   Using this feature tends to slows down application startup slightly, as
   more work is performed at application startup to scan for view
   declarations.

Usage of the ``view_config`` decorator is a form of :term:`declarative
configuration`, like ZCML, but in decorator form.
:class:`pyramid.view.view_config` can be used to associate :term:`view
configuration` information -- as done via the equivalent imperative code or
ZCML -- with a function that acts as a :app:`Pyramid` view callable.  All
arguments to the :meth:`pyramid.config.Configurator.add_view` method (save
for the ``view`` argument) are available in decorator form and mean precisely
the same thing.

An example of the :class:`pyramid.view.view_config` decorator might reside in
a :app:`Pyramid` application module ``views.py``:

.. ignore-next-block
.. code-block:: python
   :linenos:

   from resources import MyResource
   from pyramid.view import view_config
   from pyramid.response import Response

   @view_config(name='my_view', request_method='POST', context=MyResource,
                permission='read')
   def my_view(request):
       return Response('OK')

Using this decorator as above replaces the need to add this imperative
configuration stanza:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.add_view('.views.my_view', name='my_view', request_method='POST', 
                   context=MyResource, permission='read')

All arguments to ``view_config`` may be omitted.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config()
   def my_view(request):
       """ My view """
       return Response()

Such a registration as the one directly above implies that the view name will
be ``my_view``, registered with a ``context`` argument that matches any
resource type, using no permission, registered against requests with any
request method, request type, request param, route name, or containment.

The mere existence of a ``@view_config`` decorator doesn't suffice to perform
view configuration.  All that the decorator does is "annotate" the function
with your configuration declarations, it doesn't process them. To make
:app:`Pyramid` process your :class:`pyramid.view.view_config` declarations,
you *must* do use the ``scan`` method of a
:class:`pyramid.config.Configurator`:

.. code-block:: python
   :linenos:

   # config is assumed to be an instance of the
   # pyramid.config.Configurator class
   config.scan()

.. note:: See :ref:`zcml_scanning` for information about how to invoke a scan
   via ZCML (if you're not using imperative configuration).

Please see :ref:`decorations_and_code_scanning` for detailed information
about what happens when code is scanned for configuration declarations
resulting from use of decorators like :class:`pyramid.view.view_config`.

See :ref:`configuration_module` for additional API arguments to the
:meth:`pyramid.config.Configurator.scan` method.  For example, the method
allows you to supply a ``package`` argument to better control exactly *which*
code will be scanned.

``@view_config`` Placement
++++++++++++++++++++++++++

A :class:`pyramid.view.view_config` decorator can be placed in various points
in your application.

If your view callable is a function, it may be used as a function decorator:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from pyramid.response import Response

   @view_config(name='edit')
   def edit(request):
       return Response('edited!')

If your view callable is a class, the decorator can also be used as a class
decorator in Python 2.6 and better (Python 2.5 and below do not support class
decorators).  All the arguments to the decorator are the same when applied
against a class as when they are applied against a function.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config()
   class MyView(object):
       def __init__(self, request):
           self.request = request

       def __call__(self):
           return Response('hello')

You can use the :class:`pyramid.view.view_config` decorator as a simple
callable to manually decorate classes in Python 2.5 and below without the
decorator syntactic sugar, if you wish:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   class MyView(object):
       def __init__(self, request):
           self.request = request

       def __call__(self):
           return Response('hello')

   my_view = view_config()(MyView)

More than one :class:`pyramid.view.view_config` decorator can be stacked on
top of any number of others.  Each decorator creates a separate view
registration.  For example:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from pyramid.response import Response

   @view_config(name='edit')
   @view_config(name='change')
   def edit(request):
       return Response('edited!')

This registers the same view under two different names.

The decorator can also be used against class methods:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   class MyView(object):
       def __init__(self, request):
           self.request = request

       @view_config(name='hello')
       def amethod(self):
           return Response('hello')

When the decorator is used against a class method, a view is registered for
the *class*, so the class constructor must accept an argument list in one of
two forms: either it must accept a single argument ``request`` or it must
accept two arguments, ``context, request``.

The method which is decorated must return a :term:`response`.

Using the decorator against a particular method of a class is equivalent to
using the ``attr`` parameter in a decorator attached to the class itself.
For example, the above registration implied by the decorator being used
against the ``amethod`` method could be spelled equivalently as the below:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config(attr='amethod', name='hello')
   class MyView(object):
       def __init__(self, request):
           self.request = request

       def amethod(self):
           return Response('hello')

.. index::
   single: add_view

.. _mapping_views_using_imperative_config_section:

View Registration Using :meth:`~pyramid.config.Configurator.add_view`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :meth:`pyramid.config.Configurator.add_view` method within
:ref:`configuration_module` is used to configure a view imperatively.  The
arguments to this method are very similar to the arguments that you provide
to the ``@view_config`` decorator.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   def hello_world(request):
       return Response('hello!')

   # config is assumed to be an instance of the
   # pyramid.config.Configurator class
   config.add_view(hello_world, name='hello.html')

The first argument, ``view``, is required.  It must either be a Python object
which is the view itself or a :term:`dotted Python name` to such an object.
All other arguments are optional.  See
:meth:`pyramid.config.Configurator.add_view` for more information.

.. _using_add_handler:

Handler Registration Using :meth:`~pyramid.config.Configurator.add_handler`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:app:`Pyramid` provides the special concept of a :term:`view handler`.  View
handlers are view classes that implement a number of methods, each of which
is a :term:`view callable` as a convenience for :term:`URL dispatch` users.

.. note:: 

   View handlers are *not* useful when using :term:`traversal`, only when using
   :term:`url dispatch`.  

Using a view handler instead of a plain function or class :term:`view
callable` makes it unnecessary to call
:meth:`pyramid.config.Configurator.add_route` (and/or
:meth:`pyramid.config.Configurator.add_view`) "by hand" multiple times,
making it more pleasant to register a collection of views as a single class
when using :term:`url dispatch`.  The view handler machinery also introduces
the concept of an ``action``, which is used as a :term:`view predicate` to
control which method of the handler is called.  The method name is the
default *action name* of a handler view callable.

The concept of a view handler is analogous to a "controller" in Pylons 1.0.

The view handler class is initialized by :app:`Pyramid` in the same manner as
a "plain" view class.  Its ``__init__`` is called with a request object (see
:ref:`class_as_view`).  It implements methods, each of which is a :term:`view
callable`.  When a request enters the system which corresponds with an
*action* related to one of its view callable methods, this method is called,
and it is expected to return a response.

Here's an example view handler class:

.. code-block:: python
    :linenos:
    
    from pyramid.response import Response
   
    from pyramid.view import action
   
    class Hello(object):
        def __init__(self, request):
            self.request = request
       
        def index(self):
            return Response('Hello world!')

        @action(renderer="mytemplate.mak")
        def bye(self):
            return {}

The :class:`pyramid.view.action` decorator is used to fine-tune the view
parameters for each potential view callable which is a method of the handler.

Handlers are added to application configuration via the
:meth:`pyramid.config.Configurator.add_handler` API.  The
:meth:`~pyramid.config.Configurator.add_handler` method will scan a
:term:`view handler` class and automatically set up view configurations for
its methods that represent "auto-exposed" view callable, or those that were
decorated explicitly with the :class:`~pyramid.view.action` decorator. This
decorator is used to setup additional view configuration information for
individual methods of the class, and can be used repeatedly for a single view
method to register multiple view configurations for it.

.. code-block:: python
    :linenos:

    from myapp.handlers import Hello
    config.add_handler('hello', '/hello/{action}', handler=Hello)

This example will result in a route being added for the pattern
``/hello/{action}``, and each method of the ``Hello`` class will then be
examined to see if it should be registered as a potential view callable when
the ``/hello/{action}`` pattern matches.  The value of ``{action}`` in the
route pattern will be used to determine which view should be called, and each
view in the class will be setup with a view predicate that requires a
specific ``action`` name.  By default, the action name for a method of a
handler is the method name.

If the URL was ``/hello/index``, the above example pattern would match, and,
by default, the ``index`` method of the ``Hello`` class would be called.

Alternatively, the action can be declared specifically for a URL to be
registered for a *specific* ``action`` name:

.. code-block:: python
    :linenos:
    
    from myapp.handlers import Hello
    config.add_handler('hello_index', '/hello/index', 
                       handler=Hello, action='index')

This will result one of the methods that are configured for the ``action`` of
'index' in the ``Hello`` handler class to be called. In this case the name of
the method is the same as  the action name: ``index``. However, this need not
be the case, as we will see below.

When calling :meth:`~pyramid.config.Configurator.add_handler`, an ``action``
is required in either the route pattern or as a keyword argument, but
**cannot appear in both places**. A ``handler`` argument must also be
supplied, which can be either a :term:`asset specification` or a Python
reference to the handler class. Additional keyword arguments are passed
directly through to :meth:`pyramid.config.Configurator.add_route`.

For example:

.. code-block:: python
    :linenos:
    
    config.add_handler('hello', '/hello/{action}',
                       handler='mypackage.handlers.MyHandler')

Multiple :meth:`~pyramid.config.Configurator.add_handler` calls can specify
the same handler, to register specific route names for different
handler/action combinations. For example:

.. code-block:: python
    :linenos:
    
    config.add_handler('hello_index', '/hello/index', 
                       handler=Hello, action='index')
    config.add_handler('bye_index', '/hello/bye', 
                       handler=Hello, action='bye')

.. note::

  Handler configuration may also be added to the system via :term:`ZCML` (see
  :ref:`zcml_handler_configuration`).

View Setup in the Handler Class
+++++++++++++++++++++++++++++++

A handler class can have a single class level attribute called
``__autoexpose__`` which should be a regular expression or the value
``None``. It's used to determine which method names will result in additional
view configurations being registered.

When :meth:`~pyramid.config.Configurator.add_handler` runs, every method in
the handler class will be searched and a view registered if the method name
matches the ``__autoexpose__`` regular expression, or if the method was
decorated with :class:`~pyramid.view.action`.

Every method in the handler class that has a name meeting the
``__autoexpose__`` regular expression will have a view registered for an
``action`` name corresponding to the method name. This functionality can be
disabled by setting the ``__autoexpose__`` attribute to ``None``:

.. code-block:: python
    :linenos:

    from pyramid.view import action
   
    class Hello(object):
        __autoexpose__ = None
        
        def __init__(self, request):
            self.request = request
        
        @action()
        def index(self):
            return Response('Hello world!')

        @action(renderer="mytemplate.mak")
        def bye(self):
            return {}

With auto-expose effectively disabled, no views will be registered for a
method unless it is specifically decorated with
:class:`~pyramid.view.action`.

Action Decorators in a Handler
++++++++++++++++++++++++++++++

The :class:`~pyramid.view.action` decorator registers view configuration
information on the handler method, which is used by
:meth:`~pyramid.config.Configurator.add_handler` to setup the view
configuration.

All keyword arguments are recorded, and passed to
:meth:`~pyramid.config.Configurator.add_view`. Any valid keyword arguments
for :meth:`~pyramid.config.Configurator.add_view` can thus be used with the
:class:`~pyramid.view.action` decorator to further restrict when the view
will be called.

One important difference is that a handler method can respond to an
``action`` name that is different from the method name by passing in a
``name`` argument.

Example:

.. code-block:: python
    :linenos:
    
    from pyramid.view import action
   
    class Hello(object):
        def __init__(self, request):
            self.request = request
        
        @action(name='index', renderer='created.mak', request_method='POST')
        def create(self):
            return {}

        @action(renderer="view_all.mak", request_method='GET')
        def index(self):
            return {}

This will register two views that require the ``action`` to be ``index``,
with the additional view predicate requiring a specific request method.

It can be useful to decorate a single method multiple times with
:class:`~pyramid.view.action`. Each action decorator will register a new view
for the method. By specifying different names and renderers for each action,
the same view logic can be exposed and rendered differently on multiple URLs.

Example:

.. code-block:: python
    :linenos:
    
    from pyramid.view import action
   
    class Hello(object):
        def __init__(self, request):
            self.request = request
        
        @action(name='home', renderer='home.mak')
        @action(name='about', renderer='about.mak')
        def show_template(self):
            # prep some template vars
            return {}

    # in the config
    config.add_handler('hello', '/hello/{action}', handler=Hello)

With this configuration, the url ``/hello/home`` will find a view
configuration that results in calling the ``show_template`` method, then
rendering the template with ``home.mak``, and the url ``/hello/about`` will
call the same method and render the ``about.mak`` template.

.. index::
   single: resource interfaces

.. _using_resource_interfaces:

Using Resource Interfaces In View Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of registering your views with a ``context`` that names a Python
resource *class*, you can optionally register a view callable with a
``context`` which is an :term:`interface`.  An interface can be attached
arbitrarily to any resource object.  View lookup treats context interfaces
specially, and therefore the identity of a resource can be divorced from that
of the class which implements it.  As a result, associating a view with an
interface can provide more flexibility for sharing a single view between two
or more different implementations of a resource type.  For example, if two
resource objects of different Python class types share the same interface,
you can use the same view configuration to specify both of them as a
``context``.

In order to make use of interfaces in your application during view dispatch,
you must create an interface and mark up your resource classes or instances
with interface declarations that refer to this interface.

To attach an interface to a resource *class*, you define the interface and
use the :func:`zope.interface.implements` function to associate the interface
with the class.

.. code-block:: python
   :linenos:

   from zope.interface import Interface
   from zope.interface import implements

   class IHello(Interface):
       """ A marker interface """

   class Hello(object):
       implements(IHello)

To attach an interface to a resource *instance*, you define the interface and
use the :func:`zope.interface.alsoProvides` function to associate the
interface with the instance.  This function mutates the instance in such a
way that the interface is attached to it.

.. code-block:: python
   :linenos:

   from zope.interface import Interface
   from zope.interface import alsoProvides

   class IHello(Interface):
       """ A marker interface """

   class Hello(object):
       pass

   def make_hello():
       hello = Hello()
       alsoProvides(hello, IHello)
       return hello

Regardless of how you associate an interface, with a resource instance, or a
resource class, the resulting code to associate that interface with a view
callable is the same.  Assuming the above code that defines an ``IHello``
interface lives in the root of your application, and its module is named
"resources.py", the interface declaration below will associate the
``mypackage.views.hello_world`` view with resources that implement, or
provide, this interface.

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator

   config.add_view('mypackage.views.hello_world', name='hello.html',
                   context='mypackage.resources.IHello')

Any time a resource that is determined to be the :term:`context` provides
this interface, and a view named ``hello.html`` is looked up against it as
per the URL, the ``mypackage.views.hello_world`` view callable will be
invoked.

Note, in cases where a view is registered against a resource class, and a
view is also registered against an interface that the resource class
implements, an ambiguity arises. Views registered for the resource class take
precedence over any views registered for any interface the resource class
implements. Thus, if one view configuration names a ``context`` of both the
class type of a resource, and another view configuration names a ``context``
of interface implemented by the resource's class, and both view
configurations are otherwise identical, the view registered for the context's
class will "win".

For more information about defining resources with interfaces for use within
view configuration, see :ref:`resources_which_implement_interfaces`.

.. index::
   single: view security
   pair: security; view

.. _view_security_section:

Configuring View Security
~~~~~~~~~~~~~~~~~~~~~~~~~

If an :term:`authorization policy` is active, any :term:`permission` attached
to a :term:`view configuration` found during view lookup will be verified.
This will ensure that the currently authenticated user possesses that
permission against the :term:`context` resource before the view function is
actually called.  Here's an example of specifying a permission in a view
configuration using :meth:`pyramid.config.Configurator.add_view`:

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator

   config.add_view('myproject.views.add_entry', name='add.html',
                   context='myproject.resources.IBlog', permission='add')

When an :term:`authorization policy` is enabled, this view will be protected
with the ``add`` permission.  The view will *not be called* if the user does
not possess the ``add`` permission relative to the current :term:`context`.
Instead the :term:`forbidden view` result will be returned to the client as
per :ref:`protecting_views`.

.. index::
   single: view lookup

.. _view_lookup:

View Lookup and Invocation
--------------------------

:term:`View lookup` is the :app:`Pyramid` subsystem responsible for finding
an invoking a :term:`view callable`.  The view lookup subsystem is passed a
:term:`context` and a :term:`request` object.

:term:`View configuration` information stored within in the
:term:`application registry` is compared against the context and request by
the view lookup subsystem in order to find the "best" view callable for the
set of circumstances implied by the context and request.

Predicate attributes of view configuration can be thought of like
"narrowers".  In general, the greater number of predicate attributes
possessed by a view's configuration, the more specific the circumstances need
to be before the registered view callable will be invoked.

For any given request, a view with five predicates will always be found and
evaluated before a view with two, for example.  All predicates must match for
the associated view to be called.

This does not mean however, that :app:`Pyramid` "stops looking" when it finds
a view registration with predicates that don't match.  If one set of view
predicates does not match, the "next most specific" view (if any) view is
consulted for predicates, and so on, until a view is found, or no view can be
matched up with the request.  The first view with a set of predicates all of
which match the request environment will be invoked.

If no view can be found with predicates which allow it to be matched up with
the request, :app:`Pyramid` will return an error to the user's browser,
representing a "not found" (404) page.  See :ref:`changing_the_notfound_view`
for more information about changing the default notfound view.

.. index::
   single: debugging not found errors
   single: not found error (debugging)

.. _debug_notfound_section:

:exc:`NotFound` Errors
~~~~~~~~~~~~~~~~~~~~~~

It's useful to be able to debug :exc:`NotFound` error responses when they
occur unexpectedly due to an application registry misconfiguration.  To debug
these errors, use the ``PYRAMID_DEBUG_NOTFOUND`` environment variable or the
``debug_notfound`` configuration file setting.  Details of why a view was not
found will be printed to ``stderr``, and the browser representation of the
error will include the same information.  See :ref:`environment_chapter` for
more information about how, and where to set these values.

Further Information
-------------------

The chapter entitled :ref:`renderers_chapter` explains how to create
functions (or instances/classes) which do not return a :term:`Response`
object, yet which still can be used as view callables.

