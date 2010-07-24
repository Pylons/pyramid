.. _views_chapter:

Views
=====

The primary job of any :mod:`repoze.bfg` application is is to find and
invoke a :term:`view callable` when a :term:`request` reaches the
application.  View callables are bits of code written by you -- the
application developer -- which do something interesting in response to
a request made to your application.

.. note:: 

   A :mod:`repoze.bfg` :term:`view callable` is often referred to in
   conversational shorthand as a :term:`view`.  In this documentation,
   however, we need to use less ambiguous terminology because there
   are significant differences between view *configuration*, the code
   that implements a view *callable*, and the process of view
   *lookup*.

The chapter named :ref:`contextfinding_chapter` describes how, using
information from the :term:`request`, a :term:`context` and a
:term:`view name` are computed.  But neither the context nor the view
name found are very useful unless those elements can eventually be
mapped to a :term:`view callable`.

The job of actually locating and invoking the "best" :term:`view
callable` is the job of the :term:`view lookup` subsystem.  The view
lookup subsystem compares information supplied by :term:`context
finding` against :term:`view configuration` statements made by the
developer stored in the :term:`application registry` to choose the
most appropriate view callable for a specific request.

This chapter provides documentation detailing the process of creating
view callables, documentation about performing view configuration, and
a detailed explanation of view lookup.

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
   single: view calling convention
   single: view function

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
   single: view calling convention
   single: view class

.. _class_as_view:

Defining a View Callable as a Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: This feature is new as of :mod:`repoze.bfg` 0.8.1.

A view callable may also be a class instead of a function.  When a
view callable is a class, the calling semantics are slightly different
than when it is a function or another non-class callable.  When a view
callable is a class, the class' ``__init__`` is called with a
``request`` parameter.  As a result, an instance of the class is
created.  Subsequently, that instance's ``__call__`` method is invoked
with no parameters.  Views defined as classes must have the following
traits:

- an ``__init__`` method that accepts a ``request`` as its sole
  positional argument or an ``__init__`` method that accepts two
  arguments: ``request`` and ``context`` as per
  :ref:`request_and_context_view_definitions`.

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
:ref:`view_configuration_parameters`.

.. index::
   single: view calling convention

.. _request_and_context_view_definitions:

Context-And-Request View Callable Definitions
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

#. Classes that have an ``__init__`` method that accepts ``context,
   request`` and a ``__call__`` which accepts no arguments, e.g.:

   .. code-block:: python
      :linenos:

      from webob import Response

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

      from webob import Response

      class View(object):
          def __call__(self, context, request):
              return Response('OK')
      view = View() # this is the view callable

This style of calling convention is most useful for :term:`traversal`
based applications, where the context object is frequently used within
the view callable code itself.

No matter which view calling convention is used, the view code always
has access to the context via ``request.context``.

.. index::
   single: view response
   single: response

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
:mod:`repoze.bfg` will attempt to use a :term:`renderer` to
construct a response.  The renderer associated with a view callable
can be varied by changing the ``renderer`` attribute in the view's
configuration.  See :ref:`views_which_use_a_renderer`.

.. index::
   single: view http redirect
   single: http redirect (from a view)

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
it includes other response types that imply other HTTP response codes,
such as ``401 Unauthorized``.

.. index::
   single: renderer
   single: view renderer

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
when a view callable does not return an object which implements the
WebOb :term:`Response` interface, documented within
:ref:`the_response`.

View configuration can vary the renderer associated with a view
callable via the ``renderer`` attribute.  For example, this ZCML
associates the ``json`` renderer with a view callable:

.. code-block:: xml
   :linenos:

   <view
     view=".views.my_view"
     renderer="json"
     />

When this configuration is added to an application, the
``.views.my_view`` view callable will now use a ``json`` renderer,
which renders view return values to a :term:`JSON` serialization.

Other built-in renderers include renderers which use the
:term:`Chameleon` templating language to render a dictionary to a
response.

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
   single: renderers (built-in)
   single: built-in renderers

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
is returned by the view callable, it is not ``str()`` -ified.

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

.. code-block:: python
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
``json.dumps`` standard library function, and wraps the result in a
response object.  It also sets the response content-type to
``application/json``.

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

.. code-block:: python
   :linenos:

   '{"content": "Hello!"}'

The return value needn't be a dictionary, but the return value must
contain values serializable by :func:`json.dumps`.

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
returns anything but a Response object or a dictionary, an error will
be raised.

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

Views which use a Chameleon renderer can vary response attributes by
attaching properties to the request.  See
:ref:`response_request_attrs`.

.. index::
   single: response headers (from a renderer)
   single: renderer response headers

.. _response_request_attrs:

Varying Attributes of Rendered Responses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before a response that is constructed as the result of the use of a
:term:`renderer` is returned to :mod:`repoze.bfg`, several attributes
of the request are examined which have the potential to influence
response behavior.

View callables that don't directly return a response should set these
values on the ``request`` object via ``setattr`` within the view
callable to influence associated response attributes.

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

For example, if you need to change the response status from within a
view callable that uses a renderer, assign the ``response_status``
attribute to the request before returning a result:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view

   @bfg_view(name='gone', renderer='templates/gone.pt')
   def myview(request):
       request.response_status = '404 Not Found'
       return {'URL':request.URL}

.. index::
   single: renderer (adding)

.. _adding_and_overriding_renderers:

Adding and Overriding Renderers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

New templating systems and serializers can be associated with
:mod:`repoze.bfg` renderer names.  To this end, configuration
declarations can be made which override an existing :term:`renderer
factory` and which add a new renderer factory.

Adding or overriding a renderer is accomplished via :term:`ZCML` or
via imperative configuration.  Renderers can be registered
imperatively using the
:meth:`repoze.bfg.configuration.Configurator.add_renderer` API or via
the :ref:`renderer_directive` ZCML directive.

For example, to add a renderer which renders views which have a
``renderer`` attribute that is a path that ends in ``.jinja2``:

.. topic:: Via ZCML

   .. code-block:: xml
      :linenos:

      <renderer
        name=".jinja2"
        factory="my.package.MyJinja2Renderer"/>

   The ``factory`` attribute is a :term:`dotted Python name` that must
   point to an implementation of a :term:`renderer factory`.

   The ``name`` attribute is the renderer name.

.. topic:: Via Imperative Configuration

   .. code-block:: python
      :linenos:

      from my.package import MyJinja2Renderer
      config.add_renderer('.jinja2', MyJinja2Renderer)

   The first argument is the renderer name.

   The second argument is a reference to an implementation of a
   :term:`renderer factory`.

Adding a New Renderer
+++++++++++++++++++++

You may a new renderer by creating and registering a :term:`renderer
factory`.

A renderer factory implementation is usually a class which has the
following interface:

.. code-block:: python
   :linenos:

   class RendererFactory:
       def __init__(self, name):
           """ Constructor: ``name`` may be an absolute path or a
           resource specification """

       def __call__(self, value, system):
           """ Call a the renderer implementation with the value and
           the system value passed in as arguments and return the
           result (a string or unicode object).  The value is the
           return value of a view.  The system value is a dictionary
           containing available system values (e.g. ``view``,
           ``context``, and ``request``). """

There are essentially two different kinds of renderer factories:

- A renderer factory which expects to accept a :term:`resource
  specification` or an absolute path as the ``name`` value in its
  constructor.  These renderer factories are registered with a
  ``name`` value that begins with a dot (``.``).  These types of
  renderer factories usually relate to a file on the filesystem, such
  as a template.

- A renderer factory which expects to accept a token that does not
  represent a filesystem path or a resource specification in its
  constructor.  These renderer factories are registered with a
  ``name`` value that does not begin with a dot.  These renderer
  factories are typically object serializers.

.. sidebar:: Resource Specifications

   A resource specification is a colon-delimited identifier for a
   :term:`resource`.  The colon separates a Python :term:`package`
   name from a package subpath.  For example, the resource
   specification ``my.package:static/baz.css`` identifies the file
   named ``baz.css`` in the ``static`` subdirectory of the
   ``my.package`` Python :term:`package`.

Here's an example of the registration of a simple renderer factory via
ZCML:

.. code-block:: xml
   :linenos:

   <renderer
     name="amf"
     factory="my.package.MyAMFRenderer"/>

Adding the above ZCML to your application will allow you to use the
``my.package.MyAMFRenderer`` renderer factory implementation in view
configurations by referring to it as ``amf`` in the ``renderer``
attribute of a :term:`view configuration`:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view

   @bfg_view(renderer='amf')
   def myview(request):
       return {'Hello':'world'}

At startup time, when a :term:`view configuration` is encountered
which has a ``name`` argument that does not contain a dot, such as the
above ``amf`` is encountered, the full value of the ``name`` attribute
is used to construct a renderer from the associated renderer factory.
In this case, the view configuration will create an instance of an
``AMFRenderer`` for each view configuration which includes ``amf`` as
its renderer value.  The ``name`` passed to the ``AMFRenderer``
constructor will always be ``amf``.

Here's an example of the registration of a more complicated renderer
factory, which expects to be passed a filesystem path:

.. code-block:: xml
   :linenos:

   <renderer
     name=".jinja2"
     factory="my.package.MyJinja2Renderer"/>

Adding the above ZCML to your application will allow you to use the
``my.package.MyJinja2Renderer`` renderer factory implementation in
view configurations by referring to any ``renderer`` which *ends in*
``.jinja`` in the ``renderer`` attribute of a :term:`view
configuration`:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view

   @bfg_view(renderer='templates/mytemplate.jinja2')
   def myview(request):
       return {'Hello':'world'}

When a :term:`view configuration` which has a ``name`` attribute that
does contain a dot, such as ``templates/mytemplate.jinja2`` above is
encountered at startup time, the value of the name attribute is split
on its final dot.  The second element of the split is typically the
filename extension.  This extension is used to look up a renderer
factory for the configured view.  Then the value of ``renderer`` is
passed to the factory to create a renderer for the view.  In this
case, the view configuration will create an instance of a
``Jinja2Renderer`` for each view configuration which includes anything
ending with ``.jinja2`` as its ``renderer`` value.  The ``name``
passed to the ``Jinja2Renderer`` constructor will usually be a
:term:`resource specification`, but may also be an absolute path; the
renderer factory implementation should be able to deal with either.

See also :ref:`renderer_directive` and
:meth:`repoze.bfg.configuration.Configurator.add_renderer`.

Overriding an Existing Renderer
+++++++++++++++++++++++++++++++

You can associate more than one filename extension with the same
existing renderer implementation as necessary if you need to use a
different file extension for the same kinds of templates.  For
example, to associate the ``.zpt`` extension with the Chameleon ZPT
renderer factory, use:

.. code-block:: xml
   :linenos:

   <renderer
      name=".zpt"
      factory="repoze.bfg.chameleon_zpt.renderer_factory"/>

After you do this, :mod:`repoze.bfg` will treat templates ending in
both the ``.pt`` and ``.zpt`` filename extensions as Chameleon ZPT
templates.

To override the default mapping in which files with a ``.pt``
extension are rendered via a Chameleon ZPT page template renderer, use
a variation on the following in your application's ZCML:

.. code-block:: xml
   :linenos:

   <renderer
      name=".pt"
      factory="my.package.pt_renderer"/>

After you do this, the :term:`renderer factory` in
``my.package.pt_renderer`` will be used to render templates which end
in ``.pt``, replacing the default Chameleon ZPT renderer.

To override the default mapping in which files with a ``.txt``
extension are rendered via a Chameleon text template renderer, use a
variation on the following in your application's ZCML:

.. code-block:: xml
   :linenos:

   <renderer
      name=".txt"
      factory="my.package.text_renderer"/>

After you do this, the :term:`renderer factory` in
``my.package.text_renderer`` will be used to render templates which
end in ``.txt``, replacing the default Chameleon text renderer.

To associate a *default* renderer with *all* view configurations (even
ones which do not possess a ``renderer`` attribute), use a variation
on the following (ie. omit the ``name`` attribute to the renderer
tag):

.. code-block:: xml
   :linenos:

   <renderer
      factory="repoze.bfg.renderers.json_renderer_factory"/>

See also :ref:`renderer_directive` and
:meth:`repoze.bfg.configuration.Configurator.add_renderer`.

.. index::
   single: view exceptions

.. _special_exceptions_in_callables:

Using Special Exceptions In View Callables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usually when a Python exception is raised within a view callable,
:mod:`repoze.bfg` allows the exception to propagate all the way out to
the :term:`WSGI` server which invoked the application.

However, for convenience, two special exceptions exist which are
always handled by :mod:`repoze.bfg` itself.  These are
:exc:`repoze.bfg.exceptions.NotFound` and
:exc:`repoze.bfg.exceptions.Forbidden`.  Both are exception classes
which accept a single positional constructor argument: a ``message``.

If :exc:`repoze.bfg.exceptions.NotFound` is raised within view code,
the result of the :term:`Not Found View` will be returned to the user
agent which performed the request.

If :exc:`repoze.bfg.exceptions.Forbidden` is raised within view code,
the result of the :term:`Forbidden View` will be returned to the user
agent which performed the request.

In all cases, the message provided to the exception constructor is
made available to the view which :mod:`repoze.bfg` invokes as
``request.exception.args[0]``.

.. index::
   single: exception views

.. _exception_views:

Exception Views
~~~~~~~~~~~~~~~~

The machinery which allows the special
:exc:`repoze.bfg.exceptions.NotFound` and
:exc:`repoze.bfg.exceptions.Forbidden` exceptions to be caught by
specialized views as described in
:ref:`special_exceptions_in_callables` can also be used by application
developers to convert arbitrary exceptions to responses.

To register a view that should be called whenever a particular
exception is raised from with :mod:`repoze.bfg` view code, use the
exception class or one of its superclasses as the ``context`` of a
view configuration which points at a view callable you'd like to
generate a response.

For example, given the following exception class in a module named
``helloworld.exceptions``:

.. code-block:: python
   :linenos:

   class ValidationFailure(Exception):
       def __init__(self, msg):
           self.msg = msg


You can wire a view callable to be called whenever any of your *other*
code raises a ``hellworld.exceptions.ValidationFailure`` exception:

.. code-block:: python
   :linenos:

   from helloworld.exceptions import ValidationFailure

   @bfg_view(context=ValidationFailure)
   def failed_validation(exc, request):
       response =  Response('Failed validation: %s' % exc.msg)
       response.status_int = 500
       return response

Assuming that a :term:`scan` was run to pick up this view
registration, this view callable will be invoked whenever a
``helloworld.exceptions.ValidationError`` is raised by your
application's view code.  The same exception raised by a custom root
factory or a custom traverser is also caught and hooked.

Other normal view predicates can also be used in combination with an
exception view registration:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view
   from repoze.bfg.exceptions import NotFound
   from webob.exc import HTTPNotFound

   @bfg_view(context=NotFound, route_name='home')
   def notfound_view(request):
       return HTTPNotFound()

The above exception view names the ``route_name`` of ``home``, meaning
that it will only be called when the route matched has a name of
``home``.  You can therefore have more than one exception view for any
given exception in the system: the "most specific" one will be called
when the set of request circumstances which match the view
registration.

The only view predicate that cannot be not be used successfully when
creating an exception view configuration is ``name``.  The name used
to look up an exception view is always the empty string.  Views
registered as exception views which have a name will be ignored.

.. note::

  Normal (non-exception) views registered against a context which
  inherits from :exc:`Exception` will work normally.  When an
  exception view configuraton is processed, *two* exceptions are
  registered.  One as a "normal" view, the other as an "exception"
  view.  This means that you can use an exception as ``context`` for a
  normal view.

The feature can be used with any view registration mechanism
(``@bfg_view`` decorator, ZCML, or imperative ``add_view`` styles).

.. index::
   single: unicode, views, and forms
   single: forms, views, and unicode
   single: views, forms, and unicode

Handling Form Submissions in View Callables (Unicode and Character Set Issues)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most web applications need to accept form submissions from web
browsers and various other clients.  In :mod:`repoze.bfg`, form
submission handling logic is always part of a :term:`view`.  For a
general overview of how to handle form submission data using the
:term:`WebOb` API, see :ref:`webob_chapter` and `"Query and POST
variables" within the WebOb documentation
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
  application as per :ref:`mapping_views_using_zcml_section` and
  :ref:`view_directive`.

- by running a :term:`scan` against application source code which has
  a :class:`repoze.bfg.view.bfg_view` decorator attached to a Python
  object as per :class:`repoze.bfg.view.bfg_view` and
  :ref:`mapping_views_using_a_decorator_section`.

- by using the :meth:`repoze.bfg.configuration.Configurator.add_view`
  method as per :meth:`repoze.bfg.configuration.Configurator.add_view`
  and :ref:`mapping_views_using_imperative_config_section`.

Each of these mechanisms is completely equivalent to the other.

A view configuration might also be performed by virtue of :term:`route
configuration`.  View configuration via route configuration is
performed in one of the following two ways:

- by using the :meth:`repoze.bfg.configuration.Configurator.add_route`
  method to create a route with a ``view`` argument.

- by adding a ``<route>`` declaration that uses a ``view`` attribute to
  :term:`ZCML` used by your application as per :ref:`route_directive`.

.. _view_configuration_parameters:

View Configuration Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All forms of view configuration accept the same general types of
arguments. 

Many arguments supplied during view configuration are :term:`view
predicate` arguments.  View predicate arguments used during view
configuration are used to narrow the set of circumstances in which
:mod:`view lookup` will find a particular view callable.  In general,
the fewer number of predicates which are supplied to a particular view
configuration, the more likely it is that the associated view callable
will be invoked.  The greater the number supplied, the less likely.

Some view configuration arguments are non-predicate arguments.  These
tend to modify the response of the view callable or prevent the view
callable from being invoked due to an authorization policy.  The
presence of non-predicate arguments in a view configuration does not
narrow the circumstances in which the view callable will be invoked.

Non-Predicate Arguments
+++++++++++++++++++++++

``permission``
  The name of a :term:`permission` that the user must possess in order
  to invoke the :term:`view callable`.  See
  :ref:`view_security_section` for more information about view
  security and permissions.
  
  If ``permission`` is not supplied, no permission is registered for
  this view (it's accessible by any caller).

``attr``
  The view machinery defaults to using the ``__call__`` method of the
  :term:`view callable` (or the function itself, if the view callable
  is a function) to obtain a response.  The ``attr`` value allows you
  to vary the method attribute used to obtain the response.  For
  example, if your view was a class, and the class has a method named
  ``index`` and you wanted to use this method instead of the class'
  ``__call__`` method to return the response, you'd say
  ``attr="index"`` in the view configuration for the view.  This is
  most useful when the view definition is a class.

  If ``attr`` is not supplied, ``None`` is used (implying the function
  itself if the view is a function, or the ``__call__`` callable
  attribute if the view is a class).

``renderer``
  This is either a single string term (e.g. ``json``) or a string
  implying a path or :term:`resource specification`
  (e.g. ``templates/views.pt``) naming a :term:`renderer`
  implementation.  If the ``renderer`` value does not contain a dot
  (``.``), the specified string will be used to look up a renderer
  implementation, and that renderer implementation will be used to
  construct a response from the view return value.  If the
  ``renderer`` value contains a dot (``.``), the specified term will
  be treated as a path, and the filename extension of the last element
  in the path will be used to look up the renderer implementation,
  which will be passed the full path.  The renderer implementation
  will be used to construct a :term:`response` from the view return
  value.

  When the renderer is a path, although a path is usually just a
  simple relative pathname (e.g. ``templates/foo.pt``, implying that a
  template named "foo.pt" is in the "templates" directory relative to
  the directory of the current :term:`package`), a path can be
  absolute, starting with a slash on UNIX or a drive letter prefix on
  Windows.  The path can alternately be a :term:`resource
  specification` in the form
  ``some.dotted.package_name:relative/path``, making it possible to
  address template resources which live in a separate package.

  The ``renderer`` attribute is optional.  If it is not defined, the
  "null" renderer is assumed (no rendering is performed and the value
  is passed back to the upstream :mod:`repoze.bfg` machinery
  unmolested).  Note that if the view callable itself returns a
  :term:`response` (see :ref:`the_response`), the specified renderer
  implementation is never called.

``wrapper``
  The :term:`view name` of a different :term:`view configuration`
  which will receive the response body of this view as the
  ``request.wrapped_body`` attribute of its own :term:`request`, and
  the :term:`response` returned by this view as the
  ``request.wrapped_response`` attribute of its own request.  Using a
  wrapper makes it possible to "chain" views together to form a
  composite response.  The response of the outermost wrapper view will
  be returned to the user.  The wrapper view will be found as any view
  is found: see :ref:`view_lookup`.  The "best" wrapper view will be
  found based on the lookup ordering: "under the hood" this wrapper
  view is looked up via
  ``repoze.bfg.view.render_view_to_response(context, request,
  'wrapper_viewname')``. The context and request of a wrapper view is
  the same context and request of the inner view.  

  If ``wrapper`` is not supplied, no wrapper view is used.

Predicate Arguments
+++++++++++++++++++

``name``
  The :term:`view name` required to match this view callable.  Read
  :ref:`traversal_chapter` to understand the concept of a view name.

  If ``name`` is not supplied, the empty string is used (implying the
  default view).

``context``
  An object representing Python class that the :term:`context` must be
  an instance of, *or* the :term:`interface` that the :term:`context`
  must provide in order for this view to be found and called.  This
  predicate is true when the :term:`context` is an instance of the
  represented class or if the :term:`context` provides the represented
  interface; it is otherwise false.  

  If ``context`` is not supplied, the value ``None``, which matches
  any model, is used.

``route_name``
  If ``route_name`` is supplied, the view callable will be invoked
  only when the named route has matched.

  This value must match the ``name`` of a :term:`route configuration`
  declaration (see :ref:`urldispatch_chapter`) that must match before
  this view will be called.  Note that the ``route`` configuration
  referred to by ``route_name`` usually has a ``*traverse`` token in
  the value of its ``path``, representing a part of the path that will
  be used by :term:`traversal` against the result of the route's
  :term:`root factory`.

  If ``route_name`` is not supplied, the view callable will be have a
  chance of being invoked for when the :term:`triad` includes a
  request object that does not indicate it matched a route.

``request_type``
  This value should be an :term:`interface` that the :term:`request`
  must provide in order for this view to be found and called.

  If ``request_type`` is not supplied, the value ``None`` is used,
  implying any request type.

  *This is an advanced feature, not often used by "civilians"*.

``request_method``
  This value can either be one of the strings ``GET``, ``POST``,
  ``PUT``, ``DELETE``, or ``HEAD`` representing an HTTP
  ``REQUEST_METHOD``.  A view declaration with this argument ensures
  that the view will only be called when the request's ``method``
  attribute (aka the ``REQUEST_METHOD`` of the WSGI environment)
  string matches the supplied value.

  If ``request_method`` is not supplied, the view will be invoked
  regardless of the ``REQUEST_METHOD`` of the :term:`WSGI`
  environment.

``request_param``
  This value can be any string.  A view declaration with this argument
  ensures that the view will only be called when the :term:`request`
  has a key in the ``request.params`` dictionary (an HTTP ``GET`` or
  ``POST`` variable) that has a name which matches the supplied value.

  If the value supplied has a ``=`` sign in it,
  e.g. ``request_params="foo=123"``, then the key (``foo``) must both
  exist in the ``request.params`` dictionary, *and* the value must
  match the right hand side of the expression (``123``) for the view
  to "match" the current request.

  If ``request_param`` is not supplied, the view will be invoked
  without consideration of keys and values in the ``request.params``
  dictionary.

``containment``
  This value should be a reference to a Python class or
  :term:`interface` that a parent object in the :term:`lineage` must
  provide in order for this view to be found and called.  The nodes in
  your object graph must be "location-aware" to use this feature.

  If ``containment`` is not supplied, the interfaces and classes in
  the lineage are not considered when deciding whether or not to
  invoke the view callable.

  See :ref:`location_aware` for more information about
  location-awareness.

``xhr``
  This value should be either ``True`` or ``False``.  If this value is
  specified and is ``True``, the :term:`WSGI` environment must possess
  an ``HTTP_X_REQUESTED_WITH`` (aka ``X-Requested-With``) header that
  has the value ``XMLHttpRequest`` for the associated view callable to
  be found and called.  This is useful for detecting AJAX requests
  issued from jQuery, Prototype and other Javascript libraries.

  If ``xhr`` is not specified, the ``HTTP_X_REQUESTED_WITH`` HTTP
  header is not taken into consideration when deciding whether or not
  to invoke the associated view callable.

``accept``
  The value of this argument represents a match query for one or more
  mimetypes in the ``Accept`` HTTP request header.  If this value is
  specified, it must be in one of the following forms: a mimetype
  match token in the form ``text/plain``, a wildcard mimetype match
  token in the form ``text/*`` or a match-all wildcard mimetype match
  token in the form ``*/*``.  If any of the forms matches the
  ``Accept`` header of the request, this predicate will be true.

  If ``accept`` is not specified, the ``HTTP_ACCEPT`` HTTP header is
  not taken into consideration when deciding whether or not to invoke
  the associated view callable.

``header``
  This value represents an HTTP header name or a header name/value
  pair.

  If ``header`` is specified, it must be a header name or a
  ``headername:headervalue`` pair.

  If ``header`` is specified without a value (a bare header name only,
  e.g. ``If-Modified-Since``), the view will only be invoked if the
  HTTP header exists with any value in the request.

  If ``header`` is specified, and possesses a name/value pair
  (e.g. ``User-Agent:Mozilla/.*``), the view will only be invoked if
  the HTTP header exists *and* the HTTP header matches the value
  requested.  When the ``headervalue`` contains a ``:`` (colon), it
  will be considered a name/value pair (e.g. ``User-Agent:Mozilla/.*``
  or ``Host:localhost``).  The value portion should be a regular
  expression.

  Whether or not the value represents a header name or a header
  name/value pair, the case of the header name is not significant.

  If ``header`` is not specified, the composition, presence or absence
  of HTTP headers is not taken into consideration when deciding
  whether or not to invoke the associated view callable.

``path_info``
  This value represents a regular expression pattern that will be
  tested against the ``PATH_INFO`` WSGI environment variable to decide
  whether or not to call the associated view callable.  If the regex
  matches, this predicate will be ``True``.

  If ``path_info`` is not specified, the WSGI ``PATH_INFO`` is not
  taken into consideration when deciding whether or not to invoke the
  associated view callable.

``custom_predicates``
  If ``custom_predicates`` is specified, it must be a sequence of
  references to custom predicate callables.  Use custom predicates
  when no set of predefined predicates do what you need.  Custom
  predicates can be combined with predefined predicates as necessary.
  Each custom predicate callable should accept two arguments:
  ``context`` and ``request`` and should return either ``True`` or
  ``False`` after doing arbitrary evaluation of the context and/or the
  request.  If all callables return ``True``, the associated view
  callable will be considered viable for a given request.

  If ``custom_predicates`` is not specified, no custom predicates are
  used.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.2.

.. index::
   single: ZCML view configuration

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

You can also declare a *default view callable* for a :term:`model`
type:

.. code-block:: xml
   :linenos:

   <view
       context=".models.Hello"
       view=".views.hello_world"
       />

A *default view callable* simply has no ``name`` attribute.  For the
above registration, when a :term:`context` is found that is of the
type ``.models.Hello`` and there is no :term:`view name` associated
with the result of :term:`context finding`, the *default view
callable* will be used.  In this case, it's the view at
``.views.hello_world``.

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
   single: bfg_view decorator

.. _mapping_views_using_a_decorator_section:

View Configuration Using the ``@bfg_view`` Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For better locality of reference, you may use the
:class:`repoze.bfg.view.bfg_view` decorator to associate your view
functions with URLs instead of using :term:`ZCML` or imperative
configuration for the same purpose.

.. warning::

   Using this feature tends to slows down application startup
   slightly, as more work is performed at application startup to scan
   for view declarations.  Additionally, if you use decorators, it
   means that other people will not be able to override your view
   declarations externally using ZCML: this is a common requirement if
   you're developing an extensible application (e.g. a framework).
   See :ref:`extending_chapter` for more information about building
   extensible applications.

Usage of the ``bfg_view`` decorator is a form of :term:`declarative
configuration`, like ZCML, but in decorator form.
:class:`repoze.bfg.view.bfg_view` can be used to associate :term:`view
configuration` information -- as done via the equivalent ZCML -- with
a function that acts as a :mod:`repoze.bfg` view callable.  All ZCML
:ref:`view_directive` attributes (save for the ``view`` attribute) are
available in decorator form and mean precisely the same thing.

An example of the :class:`repoze.bfg.view.bfg_view` decorator might
reside in a :mod:`repoze.bfg` application module ``views.py``:

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

All arguments to ``bfg_view`` may be omitted.  For example:

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
without the decorator syntactic sugar, if you wish:

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
   cancelling the effect of the decorator "beneath" it.

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
registered for the *class*, so the class constructor must accept an
argument list in one of two forms: either it must accept a single
argument ``request`` or it must accept two arguments, ``context,
request`` as per :ref:`request_and_context_view_definitions`.

The method which is decorated must return a :term:`response` or it
must rely on a :term:`renderer` to generate one.

Using the decorator against a particular method of a class is
equivalent to using the ``attr`` parameter in a decorator attached to
the class itself.  For example, the above registration implied by the
decorator being used against the ``amethod`` method could be spelled
equivalently as the below:

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
   single: model interfaces

.. _using_model_interfaces:

Using Model Interfaces In View Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of registering your views with a ``context`` that names a
Python model *class*, you can optionally register a view callable with
a ``context`` which is an :term:`interface`.  An interface can be
attached arbitrarily to any model instance.  View lookup treats
context interfaces specially, and therefore the identity of a model
can be divorced from that of the class which implements it.  As a
result, associating a view with an interface can provide more
flexibility for sharing a single view between two or more different
implementations of a model type.  For example, if two model object
instances of different Python class types share the same interface,
you can use the same view against each of them.

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
   single: view security
   pair: security; view

.. _view_security_section:

Configuring View Security
~~~~~~~~~~~~~~~~~~~~~~~~~

If a :term:`authorization policy` is active, any :term:`permission`
attached to a :term:`view configuration` found during view lookup will
be consulted to ensure that the currently authenticated user possesses
that permission against the :term:`context` before the view function
is actually called.  Here's an example of specifying a permission in a
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
:term:`forbidden view` result will be returned to the client as per
:ref:`protecting_views`.

.. index::
   single: view lookup

.. _view_lookup:

View Lookup and Invocation
--------------------------

:term:`View lookup` is the :mod:`repoze.bfg` subsystem responsible for
finding an invoking a :term:`view callable`.  The view lookup
subsystem is passed a :term:`context`, a :term:`view name`, and the
:term:`request` object.  These three bits of information are referred
to within this chapter as a :term:`triad`.

:term:`View configuration` information stored within in the
:term:`application registry` is compared against a triad by the view
lookup subsystem in order to find the "best" view callable for the set
of circumstances implied by the triad.

Predicate attributes of view configuration can be thought of like
"narrowers".  In general, the greater number of predicate attributes
possessed by a view's configuration, the more specific the
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

.. index::
   single: debugging not found errors
   single: not found error (debugging)

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

