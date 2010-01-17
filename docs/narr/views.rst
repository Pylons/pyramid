.. _views_chapter:

Views
=====

The primary job of any :mod:`repoze.bfg` application is is to find and
invoke a :term:`view callable` when a :term:`request` reaches the
application.  View callables are bits of code written by you -- the
application developer -- which do something interesting in response to
a request made to your application.

The :ref:`contextfinding_chapter` describes how a :term:`context` and
a :term:`view name` are computed using information from the
:term:`request`.  But neither the context nor the view name found are
very useful unless those elements can eventually be mapped to a
:term:`view callable`.

The job of actually locating and invoking the "best" :term:`view
callable` is the job of the :term:`view lookup` subsystem.  The view
lookup subsystem compares information supplied by :term:`context
finding` against :term:`view configuration` statements made by the
developer to choose the most appropriate view callable for a specific
request.

.. note:: 

   A :mod:`repoze.bfg` :term:`view callable` is oten referred to in
   conversational shorthand as a :term:`view`.  In this documentation,
   however, we need to use less ambiguous terminology because there is
   a significant difference between view *configuration*, the code
   that implements a view *callable*, and the process of view
   *lookup*.

Provided within this chapter is documentation of the process of
creating view callables, documentation about performing view
configuration, and a detailed explanation of view lookup.

View Callables
--------------

No matter how a view callable is eventually found, all view callables
used by :mod:`repoze.bfg` must be constructed in the same way, and
must return the same kind of return value.

Most view callables accept a single argument named ``request``.  This
argument represents a :term:`WebOb` :term:`Request` object as
represented to :mod:`repoze.bfg` by the upstream :term:`WSGI` server.

A view callable may always return a :term:`WebOb` :term:`Response`
object directly.  It may optionally return another arbitrary
non-Response value: if a view callable returns a non-Response result,
the result must be converted into a response by the :term:`renderer`
associated with the :term:`view configuration` for the view.

View callables can be functions, instances, or classes.  View
callables can optionally be defined with an alternate calling
convention.

.. index::
   pair: view; calling convention
   single: view function
   pair: view; function

.. _function_as_view:

Defining a View Callable as a Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to define a view callable is to create a function that
accepts a single argument named ``request`` and which returns a
:term:`Response` object.  For example, this is a "hello world" view
callable implemented as a function:

.. code-block:: python
   :linenos:

   from webob import Response

   def hello_world(request):
       return Response('Hello world!')

.. index::
   pair: view; calling convention
   single: view class
   pair: view; class

.. _class_as_view:

Defining a View Callable as a Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: This feature is new as of :mod:`repoze.bfg` 0.8.1.

A view callable may also be a class instead of a function.  When a
view callable is a class, the calling semantics are slightly different
than when it is a function or another non-class callable.  When a view
callable is a class, the class' ``__init__`` is called with the
request parameter.  As a result, an instance of the class is created.
Subsequently, that instance's ``__call__`` method is invoked with no
parameters.  Views defined as classes must have the following traits:

- an ``__init__`` method that accepts a ``request`` as its sole
  positional argument (or two arguments: ``request`` and ``context``,
  as per :ref:`request_and_context_view_definitions`).

- a ``__call__`` method that accepts no parameters and which returns a
  response.

For example:

.. code-block:: python
   :linenos:

   from webob import Response

   class MyView(object):
       def __init__(self, request):
           self.request = request

       def __call__(self):
           return Response('hello')

The request object passed to ``__init__`` is the same type of request
object described in :ref:`function_as_view`.

If you'd like to use a different attribute than ``__call__`` to
represent the method expected to return a response, you can use an
``attr`` value as part of view configuration.  See
:ref:`view_configuration`.

.. index::
   pair: view; calling convention

.. _request_and_context_view_definitions:

Request-And-Context View Callable Definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usually, view callables are defined to accept only a single argument:
``request``.  However, view callables may alternately be defined as
classes or functions (or any callable) that accept *two* positional
arguments: a :term:`context` as the first argument and a
:term:`request` as the second argument.

The :term:`context` and :term:`request` arguments passed to a view
function defined in this style can be defined as follows:

context
  An instance of a :term:`context` found via graph :term:`traversal`
  or :term:`URL dispatch`.  If the context is found via traversal, it
  will be a :term:`model` object.

request
  A :term:`WebOb` Request object representing the current WSGI
  request.

The following types work as view callables in this style:

#. Functions that accept two arguments: ``context``, and ``request``,
   e.g.:

   .. code-block:: python
      :linenos:

      from webob import Response

      def view(context, request):
          return Response('OK')

#. New-style and old-style classes that have an ``__init__`` method
   that accepts ``context, request``, e.g.:

   .. code-block:: python
      :linenos:

      from webob import Response

      class view(object):
          def __init__(self, context, request):
              return Response('OK')

#. Arbitrary callables that have a ``__call__`` method that accepts
   ``context, request``, e.g.:

   .. code-block:: python
      :linenos:

      from webob import Response

      class View(object):
          def __call__(self, context, request):
              return Response('OK')
      view = View() # this is the view callable

This style of calling convention is useful for :term:`traversal` based
applications, where the context object is frequently used within the
view callable code itself.

No matter which view calling convention is used, the view code always
has access to the context via ``request.context``.

.. index::
   pair: view; response

.. _the_response:

View Callable Responses
~~~~~~~~~~~~~~~~~~~~~~~

A view callable may always return an object that implements the
:term:`WebOb` :term:`Response` interface.  The easiest way to return
something that implements this interface is to return a
:class:`webob.Response` object instance directly.  But any object that
has the following attributes will work:

status
  The HTTP status code (including the name) for the response.
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

If a view happens to return something to the :mod:`repoze.bfg`
:term:`router` which does not implement this interface,
:mod:`repoze.bfg` will attempt to use an associated :term:`renderer`
to construct a response.  The associated renderer can be varied for a
view by changing the ``renderer`` attribute in the view's
configuration.  See :ref:`views_which_use_a_renderer`.

.. index::
   pair: view; http redirect

Using a View Callable to Do A HTTP Redirect
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can issue an HTTP redirect from within a view by returning a
particular kind of response.

.. code-block:: python
   :linenos:

   from webob.exc import HTTPFound

   def myview(request):
       return HTTPFound(location='http://example.com')

All exception types from the :mod:`webob.exc` module implement the
Webob :term:`Response` interface; any can be returned as the response
from a view.  See :term:`WebOb` for the documentation for this module;
it includes other response types for ``Unauthorized``, etc.

.. index::
   single: renderer
   pair: view; renderer

.. _views_which_use_a_renderer:

Writing View Callables Which Use a Renderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: This feature is new as of :mod:`repoze.bfg` 1.1

View callables needn't always return a WebOb Response object.
Instead, they may return an arbitrary Python object, with the
expectation that a :term:`renderer` will convert that object into a
response instance on behalf of the developer.  Some renderers use a
templating system; other renderers use object serialization
techniques.

If you do not define a ``renderer`` attribute in :term:`view
configuration` for an associated :term:`view callable`, no renderer is
associated with the view.  In such a configuration, an error is raised
when a view callable does not return an object which implements
:term:`Response` interface.

View configuration can vary the renderer associated with a view
callable via the ``renderer`` attribute.  For example, this ZCML
associates the ``json`` renderer with a view:

.. code-block:: xml
   :linenos:

   <view
     view=".views.my_view"
     renderer="json"
     />

There is a ``json`` renderer, which renders view return values to a
:term:`JSON` serialization.  Other built-in renderers include
renderers which use the :term:`Chameleon` templating language to
render a dictionary to a response.  See :ref:`built_in_renderers` for
the available built-in renderers.

If the :term:`view callable` associated with a :term:`view
configuration` returns a Response object directly (an object with the
attributes ``status``, ``headerlist`` and ``app_iter``), any renderer
associated with the view configuration is ignored, and the response is
passed back to :mod:`repoze.bfg` unmolested.  For example, if your
view callable returns an instance of the :class:`webob.exc.HTTPFound`
class as a response, no renderer will be employed.

.. code-block:: python
   :linenos:

   from webob.exc import HTTPFound

   def view(request):
       return HTTPFound(location='http://example.com') # renderer avoided

Views which use a renderer can vary non-body response attributes (such
as headers and the HTTP status code) by attaching properties to the
request.  See :ref:`response_request_attrs`.

Additional renderers can be added to the system as necessary via a
ZCML directive (see :ref:`adding_and_overriding_renderers`).

.. index::
   pair: renderers; built-in

.. _built_in_renderers:

Built-In Renderers
~~~~~~~~~~~~~~~~~~

Several built-in "renderers" exist in :mod:`repoze.bfg`.  These
renderers can be used in the ``renderer`` attribute of view
configurations.

.. index::
   pair: renderer; string

``string``: String Renderer
+++++++++++++++++++++++++++

The ``string`` renderer is a renderer which renders a view callable
result to a string.  If a view callable returns a non-Response object,
and the ``string`` renderer is associated in that view's
configuration, the result will be to run the object through the Python
``str`` function to generate a string.  Note that if a Unicode object
is returned, it is not ``str()`` -ified.

Here's an example of a view that returns a dictionary.  If the
``string`` renderer is specified in the configuration for this view,
the view will render the returned dictionary to the ``str()``
representation of the dictionary:

.. code-block:: python
   :linenos:

   from webob import Response
   from repoze.bfg.view import bfg_view

   @bfg_view(renderer='string')
   def hello_world(request):
       return {'content':'Hello!'}

The body of the response returned by such a view will be a string
representing the ``str()`` serialization of the return value:

.. code-block: python
   :linenos:

   {'content': 'Hello!'}

Views which use the string renderer can vary non-body response
attributes by attaching properties to the request.  See
:ref:`response_request_attrs`.

.. index::
   pair: renderer; JSON

``json``: JSON Renderer
+++++++++++++++++++++++

The ``json`` renderer is a renderer which renders view callable
results to :term:`JSON`.  If a view callable returns a non-Response
object it is called.  It passes the return value through the
``simplejson.dumps`` function, and wraps the result in a response
object.

Here's an example of a view that returns a dictionary.  If the
``json`` renderer is specified in the configuration for this view, the
view will render the returned dictionary to a JSON serialization:

.. code-block:: python
   :linenos:

   from webob import Response
   from repoze.bfg.view import bfg_view

   @bfg_view(renderer='json')
   def hello_world(request):
       return {'content':'Hello!'}

The body of the response returned by such a view will be a string
representing the JSON serialization of the return value:

.. code-block: python
   :linenos:

   '{"content": "Hello!"}'

The return value needn't be a dictionary, but the return value must
contain values renderable by :func:`json.dumps`.

You can configure a view to use the JSON renderer in ZCML by naming
``json`` as the ``renderer`` attribute of a view configuration, e.g.:

.. code-block:: xml
   :linenos:

   <view
       context=".models.Hello"
       view=".views.hello_world"
       name="hello"
       renderer="json"
       />

Views which use the JSON renderer can vary non-body response
attributes by attaching properties to the request.  See
:ref:`response_request_attrs`.

.. index::
   pair: renderer; chameleon

.. _chameleon_template_renderers:

``*.pt`` or ``*.txt``: Chameleon Template Renderers
+++++++++++++++++++++++++++++++++++++++++++++++++++

Two built-in renderers exist for :term:`Chameleon` templates.

If the ``renderer`` attribute of a view configuration is an absolute
path, a relative path or :term:`resource specification` which has a
final path element with a filename extension of ``.pt``, the Chameleon
ZPT renderer is used.  See :ref:`chameleon_zpt_templates` for more
information about ZPT templates.

If the ``renderer`` attribute of a view configuration is an absolute
path, a source-file relative path, or a :term:`resource specification`
which has a final path element with a filename extension of ``.txt``,
the :term:`Chameleon` text renderer is used.  See
:ref:`chameleon_zpt_templates` for more information about Chameleon
text templates.

The behavior of these renderers is the same, except for the engine
used to render the template.

When a ``renderer`` attribute that names a Chameleon template path
(e.g. ``templates/foo.pt`` or ``templates/foo.txt``) is used, the view
must return a Response object or a Python *dictionary*.  If the view
callable with an associated template returns a Python dictionary, the
named template will be passed the dictionary as its keyword arguments,
and the template renderer implementation will return the resulting
rendered template in a response to the user.  If the view callable
returns anything but a dictionary, an error will be raised.

Before passing keywords to the template, the keywords derived from the
dictionary returned by the view are augmented.  The callable object
-- whatever object was used to define the ``view`` -- will be
automatically inserted into the set of keyword arguments passed to the
template as the ``view`` keyword.  If the view callable was a class,
the ``view`` keyword will be an instance of that class.  Also inserted
into the keywords passed to the template are ``renderer_name`` (the
name of the renderer, which may be a full path or a package-relative
name, typically the full string used in the ``renderer`` attribute of
the directive), ``context`` (the context of the view used to render
the template), and ``request`` (the request passed to the view used to
render the template).

Here's an example view configuration which uses a Chameleon ZPT
renderer:

.. code-block:: xml
   :linenos:

   <view
       context=".models.Hello"
       view=".views.hello_world"
       name="hello"
       renderer="templates/foo.pt"
       />

Here's an example view configuration which uses a Chameleon text
renderer:

.. code-block:: xml
   :linenos:

   <view
       context=".models.Hello"
       view=".views.hello_world"
       name="hello"
       renderer="templates/foo.txt"
       />

Views with use a Chameleon renderer can vary response attributes by
attaching properties to the request.  See
:ref:`response_request_attrs`.

.. index::
   pair: renderer; response attributes
   pair: renderer; changing headers
   triple: headers; changing; renderer

.. _response_request_attrs:

Varying Attributes of Rendered Responses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before a response that is constructed as the result of the use of a
:term:`renderer` is returned to :mod:`repoze.bfg`, several attributes
of the request are examined which have the potential to influence
response behavior.

View callables that don't directly return a response should set these
values on the ``request`` object via ``setattr`` within the view
callable to influence automatically constructed response attributes.

``response_content_type``

  Defines the content-type of the resulting response,
  e.g. ``text/xml``.

``response_headerlist``

  A sequence of tuples describing cookie values that should be set in
  the response, e.g. ``[('Set-Cookie', 'abc=123'), ('X-My-Header',
  'foo')]``.

``response_status``

  A WSGI-style status code (e.g. ``200 OK``) describing the status of
  the response.

``response_charset``

  The character set (e.g. ``UTF-8``) of the response.

``response_cache_for``

  A value in seconds which will influence ``Cache-Control`` and
  ``Expires`` headers in the returned response.  The same can also be
  achieved by returning various values in the ``response_headerlist``,
  this is purely a convenience.

.. index::
   pair: renderers; adding

.. _adding_and_overriding_renderers:

Adding and Overriding Renderers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additional configuration declarations can be made which override an
existing :term:`renderer` or which add a new renderer.  Adding or
overriding a renderer is accomplished via :term:`ZCML` or via
imperative configuration. 

For example, to add a renderer which renders views which have a
``renderer`` attribute that is a path that ends in ``.jinja2``:

.. topic:: Via ZCML

   .. code-block:: xml
      :linenos:

      <renderer
        name=".jinja2"
        factory="my.package.MyJinja2Renderer"/>

   The ``factory`` attribute is a :term:`dotted Python name` that must
   point to an implementation of a :term:`renderer`.

   The ``name`` attribute is the renderer name.

.. topic:: Via Imperative Configuration

   .. code-block:: python
      :linenos:

      from my.package import MyJinja2Renderer
      config.add_renderer('.jinja2', MyJinja2Renderer)

   The first argument is the renderer name.

   The second argument is a reference to an to an implementation of a
   :term:`renderer`.

A renderer implementation is usually a class which has the following
interface:

.. code-block:: python
   :linenos:

   class RendererFactory:
       def __init__(self, name):
           """ Constructor: ``name`` may be a path """

       def __call__(self, value, system): """ Call a the renderer
           implementation with the value and the system value passed
           in as arguments and return the result (a string or unicode
           object).  The value is the return value of a view.  The
           system value is a dictionary containing available system
           values (e.g. ``view``, ``context``, and ``request``). """

There are essentially two different kinds of ``renderer``
registrations: registrations that use a dot (``.``) in their ``name``
argument and ones which do not.

Renderer registrations that have a ``name`` attribute which starts
with a dot are meant to be *wildcard* registrations.  When a ``view``
configuration is encountered which has a ``name`` attribute that
contains a dot, at startup time, the path is split on its final dot,
and the second element of the split (the filename extension,
typically) is used to look up a renderer for the configured view.  The
renderer's factory is still passed the entire ``name`` attribute value
(not just the extension).

Renderer registrations that have ``name`` attribute which *does not*
start with a dot are meant to be absolute registrations.  When a
``view`` configuration is encountered which has a ``name`` argument
that does not contain a dot, the full value of the ``name`` attribute
is used to look up the renderer for the configured view.

Here's an example of a renderer registration in ZCML:

.. code-block:: xml
   :linenos:

   <renderer
     name="amf"
     factory="my.package.MyAMFRenderer"/>

Adding the above ZCML to your application will allow you to use the
``my.package.MyAMFRenderer`` renderer implementation in ``view``
configurations by referring to it as ``amf`` in the ``renderer``
attribute:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view

   @bfg_view(renderer='amf')
   def myview(request):
       return {'Hello':'world'}

By default, when a template extension is unrecognized, an error is
thrown at rendering time.  You can associate more than one filename
extension with the same renderer implementation as necessary if you
need to use a different file extension for the same kinds of
templates.  For example, to associate the ``.zpt`` extension with the
Chameleon page template renderer factory, use:

.. code-block:: xml
   :linenos:

   <renderer
      name=".zpt"
      factory="repoze.bfg.chameleon_zpt.renderer_factory"/>

To override the default mapping in which files with a ``.pt``
extension are rendered via a Chameleon ZPT page template renderer, use
a variation on the following in your application's ZCML:

.. code-block:: xml
   :linenos:

   <renderer
      name=".pt"
      factory="my.package.pt_renderer"/>

To override the default mapping in which files with a ``.txt``
extension are rendered via a Chameleon text template renderer, use a
variation on the following in your application's ZCML:

.. code-block:: xml
   :linenos:

   <renderer
      name=".txt"
      factory="my.package.text_renderer"/>

To associate a *default* renderer with *all* view configurations (even
ones which do not possess a ``renderer`` attribute), use a variation
on the following (ie. omit the ``name`` attribute to the renderer
tag):

.. code-block:: xml
   :linenos:

   <renderer
      factory="repoze.bfg.renderers.json_renderer_factory"/>

See also :ref:`renderer_directive`.

.. index::
   triple: exceptions; special; view

Using Special Exceptions In View Callables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usually when a Python exception is raised within a view callable,
:mod:`repoze.bfg` allows the exception to propagate all the way out to
the :term:`WSGI` server which invoked the application.

However, for convenience, two special exceptions exist which are
always handled by :mod:`repoze.bfg` itself.  These are
:exc:`repoze.bfg.exceptions.NotFound` and
:exc:`repoze.bfg.exceptions.Forbidden`.  Both is an exception class
which accepts a single positional constructor argument: a ``message``.

If :exc:`repoze.bfg.exceptions.NotFound` is raised within view code,
the result of the :term:`Not Found View` will be returned to the user
agent which performed the request.

If :exc:`repoze.bfg.exceptions.Forbidden` is raised within view code,
the result of the :term:`Forbidden View` will be returned to the user
agent which performed the request.

In all cases, the message provided to the exception constructor is
made available to the view which :mod:`repoze.bfg` invokes as
``request.environ['repoze.bfg.message']``.

.. index::
   triple: view; forms; unicode

Handling Form Submissions in View Callables (Unicode and Character Set Issues)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most web applications need to accept form submissions from web
browsers and various other clients.  In :mod:`repoze.bfg`, form
submission handling logic is always part of a :term:`view`.  For a
general overview of how to handle form submission data using the
:term:`WebOb` API, see `"Query and POST variables" within the WebOb
documentation
<http://pythonpaste.org/webob/reference.html#query-post-variables>`_.
:mod:`repoze.bfg` defers to WebOb for its request and response
implementations, and handling form submission data is a property of
the request implementation.  Understanding WebOb's request API is the
key to understanding how to process form submission data.

There are some defaults that you need to be aware of when trying to
handle form submission data in a :mod:`repoze.bfg` view.  Because
having high-order (non-ASCII) characters in data contained within form
submissions is exceedingly common, and because the UTF-8 encoding is
the most common encoding used on the web for non-ASCII character data,
and because working and storing Unicode values is much saner than
working with and storing bytestrings, :mod:`repoze.bfg` configures the
:term:`WebOb` request machinery to attempt to decode form submission
values into Unicode from the UTF-8 character set implicitly.  This
implicit decoding happens when view code obtains form field values via
the :term:`WebOb` ``request.params``, ``request.GET``, or
``request.POST`` APIs.

For example, let's assume that the following form page is served up to
a browser client, and its ``action`` points at some :mod:`repoze.bfg`
view code:

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

The ``myview`` view code in the :mod:`repoze.bfg` application *must*
expect that the values returned by ``request.params`` will be of type
``unicode``, as opposed to type ``str``. The following will work to
accept a form post from the above form:

.. code-block:: python
   :linenos:

   def myview(request):
       firstname = request.params['firstname']
       lastname = request.params['lastname']

But the following ``myview`` view code *may not* work, as it tries to
decode already-decoded (``unicode``) values obtained from
``request.params``:

.. code-block:: python
   :linenos:

   def myview(request):
       # the .decode('utf-8') will break below if there are any high-order
       # characters in the firstname or lastname
       firstname = request.params['firstname'].decode('utf-8')
       lastname = request.params['lastname'].decode('utf-8')

For implicit decoding to work reliably, you must ensure that every
form you render that posts to a :mod:`repoze.bfg` view is rendered via
a response that has a ``;charset=UTF-8`` in its ``Content-Type``
header; or, as in the form above, with a ``meta http-equiv`` tag that
implies that the charset is UTF-8 within the HTML ``head`` of the page
containing the form.  This must be done explicitly because all known
browser clients assume that they should encode form data in the
character set implied by ``Content-Type`` value of the response
containing the form when subsequently submitting that form; there is
no other generally accepted way to tell browser clients which charset
to use to encode form data.  If you do not specify an encoding
explicitly, the browser client will choose to encode form data in its
default character set before submitting it.  The browser client may
have a non-UTF-8 default encoding.  If such a request is handled by
your view code, when the form submission data is encoded in a non-UTF8
charset, eventually the WebOb request code accessed within your view
will throw an error when it can't decode some high-order character
encoded in another character set within form data e.g. when
``request.params['somename']`` is accessed.

If you are using the :class:`webob.Response` class to generate a
response, or if you use the ``render_template_*`` templating APIs, the
UTF-8 charset is set automatically as the default via the
``Content-Type`` header.  If you return a ``Content-Type`` header
without an explicit charset, a WebOb request will add a
``;charset=utf-8`` trailer to the ``Content-Type`` header value for
you for response content types that are textual (e.g. ``text/html``,
``application/xml``, etc) as it is rendered.  If you are using your
own response object, you will need to ensure you do this yourself.

To avoid implicit form submission value decoding, so that the values
returned from ``request.params``, ``request.GET`` and ``request.POST``
are returned as bytestrings rather than Unicode, add the following to
your application's ``configure.zcml``::

    <subscriber for="repoze.bfg.interfaces.INewRequest"
                handler="repoze.bfg.request.make_request_ascii"/>

You can then control form post data decoding "by hand" as necessary.
For example, when this subscriber is active, the second example above
will work unconditionally as long as you ensure that your forms are
rendered in a request that has a ``;charset=utf-8`` stanza on its
``Content-Type`` header.

.. note:: The behavior that form values are decoded from UTF-8 to
   Unicode implicitly was introduced in :mod:`repoze.bfg` 0.7.0.
   Previous versions of :mod:`repoze.bfg` performed no implicit
   decoding of form values (the default was to treat values as
   bytestrings).

.. note:: Only the *values* of request params obtained via
   ``request.params``, ``request.GET`` or ``request.POST`` are decoded
   to Unicode objects implicitly in :mod:`repoze.bfg`'s default
   configuration.  The keys are still strings.



.. index::
   single: view configuration
   pair: view; configuration

.. _view_configuration:

View Configuration: Mapping a Context to a View
-----------------------------------------------

A developer makes a :term:`view callable` available for use within a
:mod:`repoze.bfg` application via :term:`view configuration`.  A view
configuration associates a view callable with a set of statements
about the set of circumstances which must be true for the view
callable to be invoked.

A view configuration statement is made about information present in
the :term:`context` and in the :term:`request`, as well as the
:term:`view name`.  These three pieces of information are known,
collectively, as a :term:`triad`.

View configuration is performed in one of three ways:

- by adding a ``<view>`` declaration to :term:`ZCML` used by your
  application (see :ref:`mapping_views_using_zcml_section` and
  :ref:`view_directive`).

- by running a :term:`scan` against application source code which has
  a :class:`repoze.bfg.view.bfg_view` decorator attached to a Python
  object (see :class:`repoze.bfg.view.bfg_view` and
  :ref:`mapping_views_using_a_decorator_section`).

- by using the :meth:`repoze.bfg.configuration.Configurator.add_view`
  method (see :meth:`repoze.bfg.configuration.Configurator.add_view`
  and :ref:`mapping_views_using_imperative_config_section`).

Each of these mechanisms is completely equivalent to the other.

A view might also be mapped to a URL by virtue of :term:`route
configuration`.  Route configuration is performed in one of the
following two ways:

- by using the :meth:`repoze.bfg.configuration.Configurator.add_route`
  method.

- by adding a ``<route>`` declaration to :term:`ZCML` used by
  your application.

.. index::
   triple: zcml; view; configuration

.. _mapping_views_using_zcml_section:

View Configuration Via ZCML
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may associate a view with a URL by adding :ref:`view_directive`
declarations via :term:`ZCML` in a ``configure.zcml`` file.  An
example of a view declaration in ZCML is as follows:

.. code-block:: xml
   :linenos:

   <view
       context=".models.Hello"
       view=".views.hello_world"
       name="hello.html"
       />

The above maps the ``.views.hello_world`` view callable function to
the following set of :term:`context finding` results:

- A :term:`context` object which is an instance (or subclass) of the
  Python class represented by ``.models.Hello``

- A :term:`view name` equalling ``hello.html``.

.. note:: Values prefixed with a period (``.``) for the ``context``
   and ``view`` attributes of a ``view`` declaration (such as those
   above) mean "relative to the Python package directory in which this
   :term:`ZCML` file is stored".  So if the above ``view`` declaration
   was made inside a ``configure.zcml`` file that lived in the
   ``hello`` package, you could replace the relative ``.models.Hello``
   with the absolute ``hello.models.Hello``; likewise you could
   replace the relative ``.views.hello_world`` with the absolute
   ``hello.views.hello_world``.  Either the relative or absolute form
   is functionally equivalent.  It's often useful to use the relative
   form, in case your package's name changes.  It's also shorter to
   type.

You can also declare a *default view callable* for a model type:

.. code-block:: xml
   :linenos:

   <view
       context=".models.Hello"
       view=".views.hello_world"
       />

A *default view callable* simply has no ``name`` attribute.  When a
:term:`context` is found and there is no :term:`view name` associated
with the result of :term:`context finding`, the *default view
callable* is the view callable that is used.

A default view callable can alternately be defined by using the empty
string as its ``name`` attribute:

.. code-block:: xml
   :linenos:

   <view
       context=".models.Hello"
       view=".views.hello_world"
       name=""
       />

You may also declare that a view callable is good for any context type
by using the special ``*`` character as the value of the ``context``
attribute:

.. code-block:: xml
   :linenos:

   <view
       context="*"
       view=".views.hello_world"
       name="hello.html"
       />

This indicates that when :mod:`repoze.bfg` identifies that the
:term:`view name` is ``hello.html`` and the context is of any type,
the ``.views.hello_world`` view callable will be invoked.

A ZCML ``view`` declaration's ``view`` attribute can also name a
class.  In this case, the rules described in :ref:`class_as_view`
apply for the class which is named.

See :ref:`view_directive` for complete ZCML directive documentation.

.. index::
   triple: view; bfg_view; decorator

.. _mapping_views_using_a_decorator_section:

View Configuration Using the ``@bfg_view`` Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For better locality of reference, you may use the
:class:`repoze.bfg.view.bfg_view` decorator to associate your view
functions with URLs instead of using :term:`ZCML` or imperative
configuration for the same purpose.

:class:`repoze.bfg.view.bfg_view` can be used to associate
``context``, ``name``, ``permission`` and ``request_method``,
``containment``, ``request_param`` and ``request_type``, ``attr``,
``renderer``, ``wrapper``, ``xhr``, ``accept``, and ``header``
information -- as done via the equivalent ZCML -- with a function that
acts as a :mod:`repoze.bfg` view callable.  All ZCML attributes (save
for the ``view`` attribute) are available in decorator form and mean
precisely the same thing.

The mere existence of a ``@bfg_view`` decorator doesn't suffice to
perform view configuration.  To make :mod:`repoze.bfg` process your
:class:`repoze.bfg.view.bfg_view` declarations, you *must* do one of
the following:

- If you are using :term:`ZCML`, insert the following boilerplate into
  your application's ``configure.zcml``:

  .. code-block:: xml

      <scan package="."/>

- If you are using :term:`imperative configuration`, use the ``scan``
  method of a :class:`repoze.bfg.configuration.Configurator`:

  .. code-block:: python

      # config is assumed to be an instance of the
      # repoze.bfg.configuration.Configurator class
      config.scan()

If you invoke a scan, you will not need to use ZCML or imperative
configuration to create :mod:`repoze.bfg` view declarations.  Instead,
you will be able to do all the work in
:class:`repoze.bfg.view.bfg_view` decorators.

Please see :ref:`decorations_and_code_scanning` for detailed
information about what happens when code is scanned for configuration
declarations resulting from use of decorators like
:class:`repoze.bfg.view.bfg_view`.

See :ref:`configuration_module` for additional API arguments to the
:meth:`repoze.bfg.configuration.Configurator.scan` method.  For
example, the method allows you to supply a ``package`` argument to
better control exactly *which* code will be scanned.  This is the same
value implied by the ``package`` attribute of the ZCML ``<scan>``
directive (see :ref:`scan_directive`).

.. warning:: using this feature tends to slows down application
   startup slightly, as more work is performed at application startup
   to scan for view declarations.  Additionally, if you use
   decorators, it means that other people will not be able to override
   your view declarations externally using ZCML: this is a common
   requirement if you're developing an extensible application (e.g. a
   framework).  See :ref:`extending_chapter` for more information
   about building extensible applications.

An example of the :class:`repoze.bfg.view.bfg_view` decorator might
reside in a bfg application module ``views.py``:

.. ignore-next-block
.. code-block:: python
   :linenos:

   from models import MyModel
   from repoze.bfg.view import bfg_view
   from repoze.bfg.chameleon_zpt import render_template_to_response

   @bfg_view(name='my_view', request_method='POST', context=MyModel,
             permission='read', renderer='templates/my.pt')
   def my_view(request):
       return {'a':1}

Using this decorator as above replaces the need to add this ZCML to
your application registry:

.. code-block:: xml
   :linenos:

   <view
    context=".models.MyModel"
    view=".views.my_view"
    name="my_view"
    permission="read"
    request_method="POST"
    renderer="templates/my.pt"
    />

Or replaces the need to add this imperative configuration stanza:

.. ignore-next-block
.. code-block:: python

   config.add_view(name='my_view', request_method='POST', context=MyModel,
                   permission='read')

``@bfg_view`` Arguments
+++++++++++++++++++++++

All arguments to :class:`repoze.bfg.view.bfg_view` are optional.
Every argument to :class:`repoze.bfg.view.bfg_view` matches the
meaning of the same-named attribute in ZCML view configuration
described in :ref:`view_directive`.

If ``name`` is not supplied, the empty string is used (implying
the default view).

If ``attr`` is not supplied, ``None`` is used (implying the function
itself if the view is a function, or the ``__call__`` callable
attribute if the view is a class).

If ``renderer`` is not supplied, ``None`` is used (meaning that no
renderer is associated with this view).

If ``request_type`` is not supplied, the value ``None`` is used,
implying any request type.  Otherwise, this should be a class or
interface.

If ``context`` is not supplied, the interface
:class:`zope.interface.Interface` (which matches any model) is used.
``context`` can also name a class, like its ZCML brother.  An alias for
``context`` is ``for_`` (``for_`` is an older spelling).

If ``permission`` is not supplied, no permission is registered for
this view (it's accessible by any caller).

If ``wrapper`` is not supplied, no wrapper view is used.

If ``route_name`` is supplied, the view will be invoked only if the
named route matches.  *This is an advanced feature, not often used by
"civilians"*.

If ``request_method`` is supplied, the view will be invoked only if
the ``REQUEST_METHOD`` of the request matches the value.

If ``request_param`` is supplied, the view will be invoked only if the
``request.params`` data structure contains a key matching the value
provided.

If ``containment`` is supplied, the view will be invoked only if a
location parent supplies the interface or class implied by the
provided value.

If ``xhr`` is specified, it must be a boolean value.  If the value is
``True``, the view will only be invoked if the request's
``X-Requested-With`` header has the value ``XMLHttpRequest``.

If ``accept`` is specified, it must be a mimetype value.  If
``accept`` is specified, the view will only be invoked if the
``Accept`` HTTP header matches the value requested.  See the
description of ``accept`` in :ref:`view_directive` for information
about the allowable composition and matching behavior of this value.

If ``header`` is specified, it must be a header name or a
``headername:headervalue`` pair.  If ``header`` is specified, and
possesses a value the view will only be invoked if an HTTP header
matches the value requested.  If ``header`` is specified without a
value (a bare header name only), the view will only be invoked if the
HTTP header exists with any value in the request.  See the description
of ``header`` in :ref:`view_directive` for information about the
allowable composition and matching behavior of this value.

All arguments may be omitted.  For example:

.. code-block:: python
   :linenos:

   from webob import Response
   from repoze.bfg.view import bfg_view

   @bfg_view()
   def my_view(request):
       """ My view """
       return Response()

Such a registration as the one directly above implies that the view
name will be ``my_view``, registered with a ``context`` argument that
matches any model type, using no permission, registered against
requests with any request method / request type / request param /
route name / containment.

``@bfg_view`` Placement
+++++++++++++++++++++++

A :class:`repoze.bfg.view.bfg_view` decorator can be placed in various
points in your application.

If your view callable is a function, it may be used as a function
decorator:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view
   from webob import Response

   @bfg_view(name='edit')
   def edit(request):
       return Response('edited!')

If your view callable is a class, the decorator can also be used as a
class decorator in Python 2.6 and better (Python 2.5 and below do not
support class decorators).  All the arguments to the decorator are the
same when applied against a class as when they are applied against a
function.  For example:

.. code-block:: python
   :linenos:

   from webob import Response
   from repoze.bfg.view import bfg_view

   @bfg_view()
   class MyView(object):
       def __init__(self, request):
           self.request = request

       def __call__(self):
           return Response('hello')

You can use the :class:`repoze.bfg.view.bfg_view` decorator as a
simple callable to manually decorate classes in Python 2.5 and below
(without the decorator syntactic sugar), if you wish:

.. code-block:: python
   :linenos:

   from webob import Response
   from repoze.bfg.view import bfg_view

   class MyView(object):
       def __init__(self, request):
           self.request = request

       def __call__(self):
           return Response('hello')

   my_view = bfg_view()(MyView)

More than one :class:`repoze.bfg.view.bfg_view` decorator can be
stacked on top of any number of others.  Each decorator creates a
separate view registration.  For example:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view
   from webob import Response

   @bfg_view(name='edit')
   @bfg_view(name='change')
   def edit(request):
       return Response('edited!')

This registers the same view under two different names.

.. note:: :class:`repoze.bfg.view.bfg_view` decorator stacking is a
   feature new in :mod:`repoze.bfg` 1.1.  Previously, these decorators
   could not be stacked without the effect of the "upper" decorator
   cancelling the effect of the the decorator "beneath" it.

The decorator can also be used against class methods:

.. code-block:: python
   :linenos:

   from webob import Response
   from repoze.bfg.view import bfg_view

   class MyView(object):
       def __init__(self, request):
           self.request = request

       @bfg_view(name='hello')
       def amethod(self):
           return Response('hello')

When the decorator is used against a class method, a view is
registered for the *class*, so the class constructor must accept
either ``request`` or ``context, request``.  The method which is
decorated must return a response (or rely on a :term:`renderer` to
generate one). Using the decorator against a particular method of a
class is equivalent to using the ``attr`` parameter in a decorator
attached to the class itself.  For example, the above registration
implied by the decorator being used against the ``amethod`` method
could be spelled equivalently as the below:

.. code-block:: python
   :linenos:

   from webob import Response
   from repoze.bfg.view import bfg_view

   @bfg_view(attr='amethod', name='hello')
   class MyView(object):
       def __init__(self, request):
           self.request = request

       def amethod(self):
           return Response('hello')

.. note:: The ability to use the :class:`repoze.bfg.view.bfg_view`
          decorator as a method decorator is new in :mod:`repoze.bfg`
          version 1.1.  Previously it could only be used as a class or
          function decorator.

.. index::
   single: add_view
   triple: imperative; adding; view

.. _mapping_views_using_imperative_config_section:

View Configuration Using the ``add_view`` Method of a Configurator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :meth:`repoze.bfg.configuration.Configurator.add_view` method
within :ref:`configuration_module` is used to configure a view
imperatively.  The arguments to this method are very similar to the
arguments that you provide to the ``@bfg_view`` decorator.  For
example:

.. code-block:: python
   :linenos:

   from webob import Response

   def hello_world(request):
       return Response('hello!')

   # config is assumed to be an instance of the
   # repoze.bfg.configuration.Configurator class
   config.add_view(hello_world, name='hello.html')

.. index::
   pair: model; interfaces

.. _using_model_interfaces:

Using Model Interfaces In View Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of registering your views with a ``context`` that names a
Python model *class* as a context, you can optionally register a view
callable for an :term:`interface`.  Since an interface can be attached
arbitrarily to any model instance (as opposed to its identity being
implied by only its class), associating a view with an interface can
provide more flexibility for sharing a single view between two or more
different implementations of a model type.  For example, if two model
object instances of different Python class types share the same
interface, you can use the same view against each of them.

In order to make use of interfaces in your application during view
dispatch, you must create an interface and mark up your model classes
or instances with interface declarations that refer to this interface.

To attach an interface to a model *class*, you define the interface
and use the :func:`zope.interface.implements` function to associate
the interface with the class.

.. code-block:: python
   :linenos:

   from zope.interface import Interface
   from zope.interface import implements

   class IHello(Interface):
       """ A marker interface """

   class Hello(object):
       implements(IHello)

To attach an interface to a model *instance*, you define the interface
and use the :func:`zope.interface.alsoProvides` function to associate
the interface with the instance.  This function mutates the instance
in such a way that the interface is attached to it.

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

Regardless of how you associate an interface with a model instance or
a model class, the resulting ZCML to associate that interface with a
view callable is the same.  Assuming the above code that defines an
``IHello`` interface lives in the root of your application, and its
module is named "models.py", the below interface declaration will
associate the ``.views.hello_world`` view with models that implement
(aka provide) this interface.

.. code-block:: xml
   :linenos:

   <view
       context=".models.IHello"
       view=".views.hello_world"
       name="hello.html"
       />

Any time a model that is determined to be the :term:`context` provides
this interface, and a view named ``hello.html`` is looked up against
it as per the URL, the ``.views.hello_world`` view callable will be
invoked.

Note that views registered against a model class take precedence over
views registered for any interface the model class implements when an
ambiguity arises.  If a view is registered for both the class type of
the context and an interface implemented by the context's class, the
view registered for the context's class will "win".

For more information about defining models with interfaces for use
within view configuration, see
:ref:`models_which_implement_interfaces`.

.. index::
   pair: view; security

.. _view_security_section:

Configuring View Security
~~~~~~~~~~~~~~~~~~~~~~~~~

If a :term:`authorization policy` is active, any :term:`permission`
attached to a :term:`view configuration` found during view lookup will
be consulted to ensure that the currently authenticated user possesses
that permission against the context before the view function is
actually called.  Here's an example of specifying a permission in a
view configuration declaration in ZCML:

.. code-block:: xml
   :linenos:

   <view
       context=".models.IBlog"
       view=".views.add_entry"
       name="add.html"
       permission="add"
       />

When an authentication policy is enabled, this view will be protected
with the ``add`` permission.  The view will *not be called* if the
user does not possess the ``add`` permission relative to the current
:term:`context` and an authorization policy is enabled.  Instead the
:term:`forbidden view` result will be returned to the client (see
:ref:`changing_the_forbidden_view`).

.. note::

   See the :ref:`security_chapter` chapter to find out how to turn on
   an authentication policy.

.. index::
   pair: view; lookup

.. _view_lookup:

View Lookup and Invocation
--------------------------

:term:`View lookup` is the :mod:`repoze.bfg` subsystem responsible for
finding an invoking a :term:`view callable`.  The view lookup
subsystem is passed a :term:`context`, a :term:`view name`, and the
:term:`request` object.  These three bits of information are referred
to within this chapter as a :term:`triad`.

Many attributes of view configuration can be thought of like
"narrowers" or "predicates".  In general, the greater number of
attributes possessed by a view's configuration, the more specific the
circumstances need to be before the registered view callable will be
invoked.

For any given request, a view with five predicates will always be
found and evaluated before a view with two, for example.  All
predicates must match for the associated view to be called.

This does not mean however, that :mod:`repoze.bfg` "stops looking"
when it finds a view registration with predicates that don't match.
If one set of view predicates does not match, the "next most specific"
view (if any) view is consulted for predicates, and so on, until a
view is found, or no view can be matched up with the request.  The
first view with a set of predicates all of which match the request
environment will be invoked.

If no view can be found which has predicates which allow it to be
matched up with the request, :mod:`repoze.bfg` will return an error to
the user's browser, representing a "not found" (404) page.  See
:ref:`changing_the_notfound_view` for more information about changing
the default notfound view.

There are a several exceptions to the the rule which says that view
configuration attributes represent "narrowings".  Several attributes
of the ``view`` directive are *not* narrowing predicates.  These are
``permission``, ``name``, ``renderer``, and ``attr``.

The value of the ``permission`` attribute represents the permission
that must be possessed by the user to invoke any found view.  When a
view is found that matches all predicates, but the invoking user does
not possess the permission implied by any associated ``permission`` in
the current context, processing stops, and an
:exc:`repoze.bfg.exception.Forbidden` error is raised, usually
resulting in the :term:`forbidden view` being shown to the invoking
user.  No further view narrowing or view lookup is done.

.. note:: 

   See :ref:`changing_the_forbidden_view` for more information about
   changing the default forbidden view.

The value of the ``name`` attribute represents a direct match of the
view name returned via traversal.  It is part of initial view lookup
rather than a predicate/narrower.

The value of the ``renderer`` attribute represents the renderer used
to convert non-response return values from a view.

The value of the ``attr`` attribute represents the attribute name
looked up on the view object to return a response.

.. index::
   pair: debugging; not found errors

.. _debug_notfound_section:

:exc:`NotFound` Errors
~~~~~~~~~~~~~~~~~~~~~~

It's useful to be able to debug :exc:`NotFound` error responses when
they occur unexpectedly due to an application registry
misconfiguration.  To debug these errors, use the
``BFG_DEBUG_NOTFOUND`` environment variable or the ``debug_notfound``
configuration file setting.  Details of why a view was not found will
be printed to ``stderr``, and the browser representation of the error
will include the same information.  See :ref:`environment_chapter` for
more information about how and where to set these values.

