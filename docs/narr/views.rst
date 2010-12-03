.. _views_chapter:

Views
=====

The primary job of any :app:`Pyramid` application is is to find and
invoke a :term:`view callable` when a :term:`request` reaches the
application.  View callables are bits of code written by you -- the
application developer -- which do something interesting in response to
a request made to your application.

.. note:: 

   A :app:`Pyramid` :term:`view callable` is often referred to in
   conversational shorthand as a :term:`view`.  In this documentation,
   however, we need to use less ambiguous terminology because there
   are significant differences between view *configuration*, the code
   that implements a view *callable*, and the process of view
   *lookup*.

The chapter :ref:`contextfinding_chapter` describes how, using
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
used by :app:`Pyramid` must be constructed in the same way, and
must return the same kind of return value.

Most view callables accept a single argument named ``request``.  This argument
represents a :app:`Pyramid` :term:`Request` object.  A request object
encapsulates a WSGI environment as represented to :app:`Pyramid` by the
upstream :term:`WSGI` server.

A view callable can return a :mod:`Pyramid` :term:`Response` object
directly.  It may return another arbitrary non-Response value,
however, this return value must be converted into a :term:`Response`
object by the :term:`renderer` associated with the :term:`view
configuration` for the view.

View callables can be functions, instances, or classes.  

.. index::
   single: view calling convention
   single: view function

.. _function_as_view:

Defining a View Callable as a Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to define a view callable is to create a function that
accepts a single argument named ``request``, and which returns a
:term:`Response` object.  For example, this is a "hello world" view
callable implemented as a function:

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

A view callable may also be a class instead of a function.  When a
view callable is a class, the calling semantics are slightly different
than when it is a function or another non-class callable.  When a view
callable is a class, the class' ``__init__`` is called with a
``request`` parameter.  As a result, an instance of the class is
created.  Subsequently, that instance's ``__call__`` method is invoked
with no parameters.  Views defined as classes must have the following
traits:

- an ``__init__`` method that accepts a ``request`` argument.

- a ``__call__`` method that accepts no parameters and which returns a
  response.

For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

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

.. sidebar:: Context-And-Request View Callable Definitions

	Usually, view callables are defined to accept only a single argument:
	``request``.  However, view callables may alternately be defined as
	classes, functions, or any callable that accept *two* positional
	arguments: a :term:`context` as the first argument and a
	:term:`request` as the second argument.

	The :term:`context` and :term:`request` arguments passed to a view
	function defined in this style can be defined as follows:

	context
	  An instance of a :term:`context` found via graph :term:`traversal`
	  or :term:`URL dispatch`.  If the context is found via traversal, it
	  will be a :term:`model` object.

	request
	  A :app:`Pyramid` Request object representing the current WSGI
	  request.

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
following attributes (these attributes form the notional "Pyramid Response
interface"):

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

Furthermore, a view needn't *always* return a Response object.  If a view
happens to return something which does not implement the Pyramid Response
interface, :app:`Pyramid` will attempt to use a :term:`renderer` to construct a
response.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config(renderer='json')
   def hello_world(request):
       return {'content':'Hello!'}

The above example returns a *dictionary* from the view callable.  A dictionary
does not implement the Pyramid response interface, so you might believe that
this example would fail.  However, since a ``renderer`` is associated with the
view callable through its :term:`view configuration` (in this case, using a
``renderer`` argument passed to :func:`pyramid.view.view_config`), if the view
does *not* return a Response object, the renderer will attempt to convert the
result of the view to a response on the developer's behalf.  Of course, if no
renderer is associated with a view's configuration, returning anything except
an object which implements the Response interface will result in an error.
And, if a renderer *is* used, whatever is returned by the view must be
compatible with the particular kind of renderer used, or an error may occur
during view invocation.  One exception exists: it is *always* OK to return a
Response object, even when a ``renderer`` is configured.  If a view callable
returns a response object from a view that is configured with a renderer, the
renderer is bypassed entirely.

Various types of renderers exist, including serialization renderers
and renderers which use templating systems.  See also
:ref:`views_which_use_a_renderer`.

.. index::
   single: view http redirect
   single: http redirect (from a view)

.. _http_redirect:

Using a View Callable to Do an HTTP Redirect
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can issue an HTTP redirect from within a view by returning a
particular kind of response.

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import HTTPFound

   def myview(request):
       return HTTPFound(location='http://example.com')

All exception types from the :mod:`pyramid.httpexceptions` module implement the
:term:`Response` interface; any can be returned as the response from a view.
See :mod:`pyramid.httpexceptions` for the documentation for the ``HTTPFound``
exception; it also includes other response types that imply other HTTP response
codes, such as ``HTTPUnauthorized`` for ``401 Unauthorized``.

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
   single: renderer
   single: view renderer

.. _views_which_use_a_renderer:

Writing View Callables Which Use a Renderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

View callables needn't always return a Response object.  Instead, they may
return an arbitrary Python object, with the expectation that a :term:`renderer`
will convert that object into a response instance on behalf of the developer.
Some renderers use a templating system; other renderers use object
serialization techniques.

If you do not define a ``renderer`` attribute in :term:`view configuration` for
an associated :term:`view callable`, no renderer is associated with the view.
In such a configuration, an error is raised when a view callable does not
return an object which implements the :term:`Response` interface, documented
within :ref:`the_response`.

View configuration can vary the renderer associated with a view callable via
the ``renderer`` attribute.  For example, this call to
:meth:`pyramid.configuration.Configurator.add_view` associates the ``json``
renderer with a view callable:

.. code-block:: python
   :linenos:

   config.add_view('myproject.views.my_view', renderer='json')

When this configuration is added to an application, the
``myproject.views.my_view`` view callable will now use a ``json`` renderer,
which renders view return values to a :term:`JSON` serialization.

Other built-in renderers include renderers which use the
:term:`Chameleon` templating language to render a dictionary to a
response.

If the :term:`view callable` associated with a :term:`view configuration`
returns a Response object directly (an object with the attributes ``status``,
``headerlist`` and ``app_iter``), any renderer associated with the view
configuration is ignored, and the response is passed back to :app:`Pyramid`
unmolested.  For example, if your view callable returns an instance of the
:class:`pyramid.httpexceptions.HTTPFound` class as a response, no renderer will
be employed.

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import HTTPFound

   def view(request):
       return HTTPFound(location='http://example.com') # renderer avoided

Views which use a renderer can vary non-body response attributes (such
as headers and the HTTP status code) by attaching properties to the
request.  See :ref:`response_request_attrs`.

Additional renderers can be added to the system as necessary (see
:ref:`adding_and_overriding_renderers`).

.. index::
   single: renderers (built-in)
   single: built-in renderers

.. _built_in_renderers:

Built-In Renderers
~~~~~~~~~~~~~~~~~~

Several built-in renderers exist in :app:`Pyramid`.  These
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

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config(renderer='string')
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

The ``json`` renderer renders view callable
results to :term:`JSON`.  It passes the return value through the
``json.dumps`` standard library function, and wraps the result in a
response object.  It also sets the response content-type to
``application/json``.

Here's an example of a view that returns a dictionary.  Since the
``json`` renderer is specified in the configuration for this view, the
view will render the returned dictionary to a JSON serialization:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config(renderer='json')
   def hello_world(request):
       return {'content':'Hello!'}

The body of the response returned by such a view will be a string
representing the JSON serialization of the return value:

.. code-block:: python
   :linenos:

   '{"content": "Hello!"}'

The return value needn't be a dictionary, but the return value must
contain values serializable by :func:`json.dumps`.

You can configure a view to use the JSON renderer by naming ``json`` as the
``renderer`` argument of a view configuration, e.g. by using
:meth:`pyramid.configuration.Configurator.add_view`:

.. code-block:: python
   :linenos:

   config.add_view('myproject.views.hello_world', 
                    name='hello',
                    context='myproject.models.Hello',
                    renderer='json')
    

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

If the ``renderer`` attribute of a view configuration is an absolute path or
a :term:`resource specification` which has a final path element with a
filename extension of ``.txt``, the :term:`Chameleon` text renderer is used.
See :ref:`chameleon_zpt_templates` for more information about Chameleon text
templates.

The behavior of these renderers is the same, except for the engine
used to render the template.

When a ``renderer`` attribute that names a template path or :term:`resource
specification` (e.g. ``myproject:templates/foo.pt`` or
``myproject:templates/foo.txt``) is used, the view must return a
:term:`Response` object or a Python *dictionary*.  If the view callable with
an associated template returns a Python dictionary, the named template will
be passed the dictionary as its keyword arguments, and the template renderer
implementation will return the resulting rendered template in a response to
the user.  If the view callable returns anything but a Response object or a
dictionary, an error will be raised.

Before passing keywords to the template, the keyword arguments derived from
the dictionary returned by the view are augmented.  The callable object --
whatever object was used to define the ``view`` -- will be automatically
inserted into the set of keyword arguments passed to the template as the
``view`` keyword.  If the view callable was a class, the ``view`` keyword
will be an instance of that class.  Also inserted into the keywords passed to
the template are ``renderer_name`` (the string used in the ``renderer``
attribute of the directive), ``renderer_info`` (an object containing
renderer-related information), ``context`` (the context of the view used to
render the template), and ``request`` (the request passed to the view used to
render the template).

Here's an example view configuration which uses a Chameleon ZPT
renderer:

.. code-block:: python
   :linenos:

    # config is an instance of pyramid.configuration.Configurator

    config.add_view('myproject.views.hello_world',
                    name='hello',
                    context='myproject.models.Hello',
                    renderer='myproject:templates/foo.pt')

Here's an example view configuration which uses a Chameleon text
renderer:

.. code-block:: python
   :linenos:

    config.add_view('myproject.views.hello_world',
                    name='hello',
                    context='myproject.models.Hello',
                    renderer='myproject:templates/foo.txt')

Views which use a Chameleon renderer can vary response attributes by
attaching properties to the request.  See
:ref:`response_request_attrs`.

.. index::
   pair: renderer; mako

.. _mako_template_renderers:

``*.mak`` or ``*.mako``: Mako Template Renderer
+++++++++++++++++++++++++++++++++++++++++++++++

The ``Mako`` template renderer renders views using a Mako template.
When used, the view must return a Response object or a Python *dictionary*.
The dictionary items will then be used in the global template space. If the
view callable returns anything but a Response object, or a dictionary, an error
will be raised.

When using a ``renderer`` argument to a :term:`view configuration` to
specify a Mako template, the value of the ``renderer`` may be a path
relative to the ``mako.directories`` setting (e.g.
``some/template.mak``) or, alternately, it may be a :term:`resource
specification` (e.g. ``apackage:templates/sometemplate.mak``).  Mako
templates may internally inherit other Mako templates using a relative
filename or a :term:`resource specification` as desired.

XXX Further explanation or link to mako inheritance info

Here's an example view configuration which uses a relative path:

.. code-block:: python
   :linenos:

    # config is an instance of pyramid.configuration.Configurator

    config.add_view('myproject.views.hello_world',
                    name='hello',
                    context='myproject.models.Hello',
                    renderer='foo.mak')

It's important to note that in Mako's case, the 'relative' path name
``foo.mak`` above is not relative to the package, but is relative to the
directory (or directories) configured for Mako via the ``mako.directories``
configuration file setting.

The renderer can also be provided in :term:`resource specification`
format. Here's an example view configuration which uses a :term:`resource
specification`:

.. code-block:: python
   :linenos:

    config.add_view('myproject.views.hello_world',
                    name='hello',
                    context='myproject.models.Hello',
                    renderer='mypackage:templates/foo.mak')

The above configuration will use the file named ``foo.mak`` in the
``templates`` directory of the ``mypackage`` package.

The ``Mako`` template renderer can take additional arguments beyond the
standard ``reload_templates`` setting, see the :ref:`environment_chapter` for
additional :ref:`mako_template_renderer_settings`.

.. index::
   single: response headers (from a renderer)
   single: renderer response headers

.. _response_request_attrs:

Varying Attributes of Rendered Responses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before a response constructed by a :term:`renderer` is returned to
:app:`Pyramid`, several attributes of the request are examined which
have the potential to influence response behavior.

View callables that don't directly return a response should set these
attributes on the ``request`` object via ``setattr`` during their
execution, to influence associated response attributes.

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

   from pyramid.view import view_config

   @view_config(name='gone', renderer='templates/gone.pt')
   def myview(request):
       request.response_status = '404 Not Found'
       return {'URL':request.URL}

For more information on attributes of the request, see the API
documentation in :ref:`request_module`.

.. index::
   single: renderer (adding)

.. _adding_and_overriding_renderers:

Adding and Overriding Renderers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

New templating systems and serializers can be associated with :app:`Pyramid`
renderer names.  To this end, configuration declarations can be made which
override an existing :term:`renderer factory`, and which add a new renderer
factory.

Renderers can be registered imperatively using the
:meth:`pyramid.configuration.Configurator.add_renderer` API.

.. note:: The tasks described in this section can also be performed via
   :term:`declarative configuration`.  See
   :ref:`zcml_adding_and_overriding_renderers`.

For example, to add a renderer which renders views which have a
``renderer`` attribute that is a path that ends in ``.jinja2``:

.. code-block:: python
   :linenos:

   config.add_renderer('.jinja2', 'mypackage.MyJinja2Renderer')

The first argument is the renderer name.

The second argument is a reference to an implementation of a
:term:`renderer factory` or a :term:`dotted Python name` referring
to such an object.

.. _adding_a_renderer:

Adding a New Renderer
+++++++++++++++++++++

You may add a new renderer by creating and registering a :term:`renderer
factory`.

A renderer factory implementation is typically a class with the
following interface:

.. code-block:: python
   :linenos:

   class RendererFactory:
       def __init__(self, info):
           """ Constructor: ``info`` will be an object having the
           the following attributes: ``name`` (the renderer name), ``package`` 
           (the package that was 'current' at the time the renderer was 
           registered), ``type`` (the renderer type name), ``registry`` 
           (the current application registry) and ``settings`` (the 
           deployment settings dictionary).
           """

       def __call__(self, value, system):
           """ Call a the renderer implementation with the value and
           the system value passed in as arguments and return the
           result (a string or unicode object).  The value is the
           return value of a view.  The system value is a dictionary
           containing available system values (e.g. ``view``,
           ``context``, and ``request``). """

The formal interface definition of the ``info`` object passed to a renderer
factory constructor is available as :class:`pyramid.interfaces.IRendererInfo`.

There are essentially two different kinds of renderer factories:

- A renderer factory which expects to accept a :term:`resource specification`,
  or an absolute path, as the ``name`` attribute of the ``info`` object fed to
  its constructor.  These renderer factories are registered with a ``name``
  value that begins with a dot (``.``).  These types of renderer factories
  usually relate to a file on the filesystem, such as a template.

- A renderer factory which expects to accept a token that does not represent a
  filesystem path or a resource specification in the ``name`` attribute of the
  ``info`` object fed to its constructor.  These renderer factories are
  registered with a ``name`` value that does not begin with a dot.  These
  renderer factories are typically object serializers.

.. sidebar:: Resource Specifications

   A resource specification is a colon-delimited identifier for a
   :term:`resource`.  The colon separates a Python :term:`package`
   name from a package subpath.  For example, the resource
   specification ``my.package:static/baz.css`` identifies the file
   named ``baz.css`` in the ``static`` subdirectory of the
   ``my.package`` Python :term:`package`.

Here's an example of the registration of a simple renderer factory via
:meth:`pyramid.configuration.Configurator.add_renderer`:

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.configuration.Configurator

   config.add_renderer(name='amf', factory='my.package.MyAMFRenderer')

Adding the above code to your application startup configuration will
allow you to use the ``my.package.MyAMFRenderer`` renderer factory
implementation in view configurations. Your application can use this
renderer by specifying ``amf`` in the ``renderer`` attribute of a
:term:`view configuration`:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='amf')
   def myview(request):
       return {'Hello':'world'}

At startup time, when a :term:`view configuration` is encountered, which
has a ``name`` attribute that does not contain a dot, the full ``name``
value is used to construct a renderer from the associated renderer
factory.  In this case, the view configuration will create an instance
of an ``AMFRenderer`` for each view configuration which includes ``amf``
as its renderer value.  The ``name`` passed to the ``AMFRenderer``
constructor will always be ``amf``.

Here's an example of the registration of a more complicated renderer
factory, which expects to be passed a filesystem path:

.. code-block:: python
   :linenos:

   config.add_renderer(name='.jinja2', 
                       factory='my.package.MyJinja2Renderer')

Adding the above code to your application startup will allow you to use the
``my.package.MyJinja2Renderer`` renderer factory implementation in view
configurations by referring to any ``renderer`` which *ends in* ``.jinja`` in
the ``renderer`` attribute of a :term:`view configuration`:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='templates/mytemplate.jinja2')
   def myview(request):
       return {'Hello':'world'}

When a :term:`view configuration` is encountered at startup time, which
has a ``name`` attribute that does contain a dot, the value of the name
attribute is split on its final dot.  The second element of the split is
typically the filename extension.  This extension is used to look up a
renderer factory for the configured view.  Then the value of
``renderer`` is passed to the factory to create a renderer for the view.
In this case, the view configuration will create an instance of a
``Jinja2Renderer`` for each view configuration which includes anything
ending with ``.jinja2`` in its ``renderer`` value.  The ``name`` passed
to the ``Jinja2Renderer`` constructor will be the full value that was
set as ``renderer=`` in the view configuration.

See also :ref:`renderer_directive` and
:meth:`pyramid.configuration.Configurator.add_renderer`.

Overriding an Existing Renderer
+++++++++++++++++++++++++++++++

You can associate more than one filename extension with the same existing
renderer implementation as necessary if you need to use a different file
extension for the same kinds of templates.  For example, to associate the
``.zpt`` extension with the Chameleon ZPT renderer factory, use the
:meth:`pyramid.configuration.Configurator.add_renderer` method:

.. code-block:: python
   :linenos:

   config.add_renderer('.zpt', 'pyramid.chameleon_zpt.renderer_factory')

After you do this, :app:`Pyramid` will treat templates ending in both the
``.pt`` and ``.zpt`` filename extensions as Chameleon ZPT templates.

To override the default mapping in which files with a ``.pt`` extension are
rendered via a Chameleon ZPT page template renderer, use a variation on the
following in your application's startup code:

.. code-block:: python
   :linenos:

   config.add_renderer('.pt', 'mypackage.pt_renderer')

After you do this, the :term:`renderer factory` in
``mypackage.pt_renderer`` will be used to render templates which end
in ``.pt``, replacing the default Chameleon ZPT renderer.

To associate a *default* renderer with *all* view configurations (even
ones which do not possess a ``renderer`` attribute), pass ``None`` as
the ``name`` attribute to the renderer tag:

.. code-block:: python
   :linenos:

   config.add_renderer(None, 'mypackage.json_renderer_factory')

.. index::
   single: view exceptions

.. _special_exceptions_in_callables:

Using Special Exceptions In View Callables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usually when a Python exception is raised within a view callable,
:app:`Pyramid` allows the exception to propagate all the way out to
the :term:`WSGI` server which invoked the application.

However, for convenience, two special exceptions exist which are
always handled by :app:`Pyramid` itself.  These are
:exc:`pyramid.exceptions.NotFound` and
:exc:`pyramid.exceptions.Forbidden`.  Both are exception classes
which accept a single positional constructor argument: a ``message``.

If :exc:`pyramid.exceptions.NotFound` is raised within view code,
the result of the :term:`Not Found View` will be returned to the user
agent which performed the request.

If :exc:`pyramid.exceptions.Forbidden` is raised within view code,
the result of the :term:`Forbidden View` will be returned to the user
agent which performed the request.

In all cases, the message provided to the exception constructor is
made available to the view which :app:`Pyramid` invokes as
``request.exception.args[0]``.

.. index::
   single: exception views

.. _exception_views:

Exception Views
~~~~~~~~~~~~~~~~

The machinery which allows the special
:exc:`pyramid.exceptions.NotFound` and
:exc:`pyramid.exceptions.Forbidden` exceptions to be caught by
specialized views as described in
:ref:`special_exceptions_in_callables` can also be used by application
developers to convert arbitrary exceptions to responses.

To register a view that should be called whenever a particular
exception is raised from with :app:`Pyramid` view code, use the
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

   @view_config(context=ValidationFailure)
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

   from pyramid.view import view_config
   from pyramid.exceptions import NotFound
   from pyramid.httpexceptions import HTTPNotFound

   @view_config(context=NotFound, route_name='home')
   def notfound_view(request):
       return HTTPNotFound()

The above exception view names the ``route_name`` of ``home``, meaning
that it will only be called when the route matched has a name of
``home``.  You can therefore have more than one exception view for any
given exception in the system: the "most specific" one will be called
when the set of request circumstances match the view registration.

The only view predicate that cannot be used successfully when creating
an exception view configuration is ``name``.  The name used to look up
an exception view is always the empty string.  Views registered as
exception views which have a name will be ignored.

.. note::

  Normal (i.e., non-exception) views registered against a context which
  inherits from :exc:`Exception` will work normally.  When an
  exception view configuration is processed, *two* views are
  registered.  One as a "normal" view, the other as an "exception"
  view.  This means that you can use an exception as ``context`` for a
  normal view.

The feature can be used with any view registration mechanism
(``@view_config`` decorator, ZCML, or imperative ``add_view`` styles).

.. index::
   single: unicode, views, and forms
   single: forms, views, and unicode
   single: views, forms, and unicode

Handling Form Submissions in View Callables (Unicode and Character Set Issues)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most web applications need to accept form submissions from web
browsers and various other clients.  In :app:`Pyramid`, form
submission handling logic is always part of a :term:`view`.  For a
general overview of how to handle form submission data using the
:term:`WebOb` API, see :ref:`webob_chapter` and `"Query and POST
variables" within the WebOb documentation
<http://pythonpaste.org/webob/reference.html#query-post-variables>`_.
:app:`Pyramid` defers to WebOb for its request and response
implementations, and handling form submission data is a property of
the request implementation.  Understanding WebOb's request API is the
key to understanding how to process form submission data.

There are some defaults that you need to be aware of when trying to handle form
submission data in a :app:`Pyramid` view.  Because having high-order
(non-ASCII) characters in data contained within form submissions is exceedingly
common, and because the UTF-8 encoding is the most common encoding used on the
web for non-ASCII character data, and because working and storing Unicode
values is much saner than working with and storing bytestrings, :app:`Pyramid`
configures the :term:`WebOb` request machinery to attempt to decode form
submission values into Unicode from the UTF-8 character set implicitly.  This
implicit decoding happens when view code obtains form field values via the
``request.params``, ``request.GET``, or ``request.POST`` APIs (see
:ref:`request_module` for details about these APIs).

For example, let's assume that the following form page is served up to
a browser client, and its ``action`` points at some :app:`Pyramid`
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

The ``myview`` view code in the :app:`Pyramid` application *must*
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

For implicit decoding to work reliably, you should ensure that every form you
render that posts to a :app:`Pyramid` view is rendered via a response that has
a ``;charset=UTF-8`` in its ``Content-Type`` header; or, as in the form above,
with a ``meta http-equiv`` tag that implies that the charset is UTF-8 within
the HTML ``head`` of the page containing the form.  This must be done
explicitly because all known browser clients assume that they should encode
form data in the character set implied by ``Content-Type`` value of the
response containing the form when subsequently submitting that form; there is
no other generally accepted way to tell browser clients which charset to use to
encode form data.  If you do not specify an encoding explicitly, the browser
client will choose to encode form data in its default character set before
submitting it.  The browser client may have a non-UTF-8 default encoding.  If
such a request is handled by your view code, when the form submission data is
encoded in a non-UTF8 charset, eventually the request code accessed within your
view will throw an error when it can't decode some high-order character encoded
in another character set within form data e.g. when
``request.params['somename']`` is accessed.

If you are using the :class:`pyramid.response.Response` class to generate a
response, or if you use the ``render_template_*`` templating APIs, the UTF-8
charset is set automatically as the default via the ``Content-Type`` header.
If you return a ``Content-Type`` header without an explicit charset, a request
will add a ``;charset=utf-8`` trailer to the ``Content-Type`` header value for
you for response content types that are textual (e.g. ``text/html``,
``application/xml``, etc) as it is rendered.  If you are using your own
response object, you will need to ensure you do this yourself.

.. note:: Only the *values* of request params obtained via
   ``request.params``, ``request.GET`` or ``request.POST`` are decoded
   to Unicode objects implicitly in the :app:`Pyramid` default
   configuration.  The keys are still strings.

.. index::
   single: view configuration

.. _view_configuration:

View Configuration: Mapping a Context to a View
-----------------------------------------------

A developer makes a :term:`view callable` available for use within a
:app:`Pyramid` application via :term:`view configuration`.  A view
configuration associates a view callable with a set of statements
about the set of circumstances which must be true for the view
callable to be invoked.

A view configuration statement is made about information present in
the :term:`context` and in the :term:`request`, as well as the
:term:`view name`.  These three pieces of information are known,
collectively, as a :term:`triad`.

View configuration is performed in one of these ways:

- by running a :term:`scan` against application source code which has
  a :class:`pyramid.view.view_config` decorator attached to a Python
  object as per :class:`pyramid.view.view_config` and
  :ref:`mapping_views_using_a_decorator_section`.

- by using the :meth:`pyramid.configuration.Configurator.add_view`
  method as per :meth:`pyramid.configuration.Configurator.add_view`
  and :ref:`mapping_views_using_imperative_config_section`.

Both of these mechanisms is completely equivalent to the other.

.. note:: You can also add view configuration by adding a ``<view>``
   declaration to :term:`ZCML` used by your application as per
   :ref:`mapping_views_using_zcml_section` and :ref:`view_directive`.

A view configuration might also be performed by virtue of :term:`route
configuration`.  View configuration via route configuration is performed by
using the :meth:`pyramid.configuration.Configurator.add_route` method to
create a route with a ``view`` argument.

.. note:: ZCML users can use :ref:`route_directive` to perform the same task.
   See also :ref:`zcml_route_configuration`.

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
  is passed back to the upstream :app:`Pyramid` machinery
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
  ``pyramid.view.render_view_to_response(context, request,
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
  the value of its ``pattern``, representing a part of the path that will
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

.. index::
   single: view_config decorator

.. _mapping_views_using_a_decorator_section:

View Configuration Using the ``@view_config`` Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For better locality of reference, you may use the
:class:`pyramid.view.view_config` decorator to associate your view
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

Usage of the ``view_config`` decorator is a form of :term:`declarative
configuration`, like ZCML, but in decorator form.
:class:`pyramid.view.view_config` can be used to associate :term:`view
configuration` information -- as done via the equivalent imperative code or
ZCML -- with a function that acts as a :app:`Pyramid` view callable.  All
arguments to the :meth:`pyramid.configuration.Configurator.add_view` method
(save for the ``view`` argument) are available in decorator form and mean
precisely the same thing.

An example of the :class:`pyramid.view.view_config` decorator might
reside in a :app:`Pyramid` application module ``views.py``:

.. ignore-next-block
.. code-block:: python
   :linenos:

   from models import MyModel
   from pyramid.view import view_config
   from pyramid.chameleon_zpt import render_template_to_response

   @view_config(name='my_view', request_method='POST', context=MyModel,
             permission='read', renderer='templates/my.pt')
   def my_view(request):
       return {'a':1}

Using this decorator as above replaces the need to add this imperative
configuration stanza:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.add_view('.views.my_view', name='my_view', request_method='POST', 
                   context=MyModel, permission='read')

All arguments to ``view_config`` may be omitted.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config()
   def my_view(request):
       """ My view """
       return Response()

Such a registration as the one directly above implies that the view
name will be ``my_view``, registered with a ``context`` argument that
matches any model type, using no permission, registered against
requests with any request method / request type / request param /
route name / containment.

The mere existence of a ``@view_config`` decorator doesn't suffice to perform
view configuration.  To make :app:`Pyramid` process your
:class:`pyramid.view.view_config` declarations, you *must* do use the
``scan`` method of a :class:`pyramid.configuration.Configurator`:

.. code-block:: python
   :linenos:

   # config is assumed to be an instance of the
   # pyramid.configuration.Configurator class
   config.scan()

.. note:: See :ref:`zcml_scanning` for information about how to invoke a scan
   via ZCML (if you're not using imperative configuration).

Please see :ref:`decorations_and_code_scanning` for detailed information
about what happens when code is scanned for configuration declarations
resulting from use of decorators like :class:`pyramid.view.view_config`.

See :ref:`configuration_module` for additional API arguments to the
:meth:`pyramid.configuration.Configurator.scan` method.  For example, the
method allows you to supply a ``package`` argument to better control exactly
*which* code will be scanned.

``@view_config`` Placement
++++++++++++++++++++++++++

A :class:`pyramid.view.view_config` decorator can be placed in various
points in your application.

If your view callable is a function, it may be used as a function
decorator:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from pyramid.response import Response

   @view_config(name='edit')
   def edit(request):
       return Response('edited!')

If your view callable is a class, the decorator can also be used as a
class decorator in Python 2.6 and better (Python 2.5 and below do not
support class decorators).  All the arguments to the decorator are the
same when applied against a class as when they are applied against a
function.  For example:

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

You can use the :class:`pyramid.view.view_config` decorator as a
simple callable to manually decorate classes in Python 2.5 and below
without the decorator syntactic sugar, if you wish:

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

More than one :class:`pyramid.view.view_config` decorator can be
stacked on top of any number of others.  Each decorator creates a
separate view registration.  For example:

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

View Configuration Using the ``add_view`` Method of a Configurator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :meth:`pyramid.configuration.Configurator.add_view` method
within :ref:`configuration_module` is used to configure a view
imperatively.  The arguments to this method are very similar to the
arguments that you provide to the ``@view_config`` decorator.  For
example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   def hello_world(request):
       return Response('hello!')

   # config is assumed to be an instance of the
   # pyramid.configuration.Configurator class
   config.add_view(hello_world, name='hello.html')

The first argument, ``view``, is required.  It must either be a Python
object which is the view itself or a :term:`dotted Python name` to
such an object.  All other arguments are optional.  See
:meth:`pyramid.configuration.Configurator.add_view` for more
information.

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

Regardless of how you associate an interface with a model instance or a model
class, the resulting code to associate that interface with a view callable is
the same.  Assuming the above code that defines an ``IHello`` interface lives
in the root of your application, and its module is named "models.py", the
below interface declaration will associate the
``mypackage.views.hello_world`` view with models that implement (aka provide)
this interface.

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.configuration.Configurator

   config.add_view('mypackage.views.hello_world', name='hello.html',
                   context='mypackage.models.IHello')

Any time a model that is determined to be the :term:`context` provides this
interface, and a view named ``hello.html`` is looked up against it as per the
URL, the ``mypackage.views.hello_world`` view callable will be invoked.

Note that views registered against a model class take precedence over views
registered for any interface the model class implements when an ambiguity
arises.  If a view is registered for both the class type of the context and
an interface implemented by the context's class, the view registered for the
context's class will "win".

For more information about defining models with interfaces for use within
view configuration, see :ref:`models_which_implement_interfaces`.

.. index::
   single: view security
   pair: security; view

.. _view_security_section:

Configuring View Security
~~~~~~~~~~~~~~~~~~~~~~~~~

If a :term:`authorization policy` is active, any :term:`permission` attached
to a :term:`view configuration` found during view lookup will be consulted to
ensure that the currently authenticated user possesses that permission
against the :term:`context` before the view function is actually called.
Here's an example of specifying a permission in a view configuration using
:meth:`pyramid.configuration.Configurator.add_view`:

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.configuration.Configurator

   config.add_view('myproject.views.add_entry', name='add.html',
                   context='myproject.models.IBlog', permission='add')

When an authentication policy is enabled, this view will be protected with
the ``add`` permission.  The view will *not be called* if the user does not
possess the ``add`` permission relative to the current :term:`context` and an
authorization policy is enabled.  Instead the :term:`forbidden view` result
will be returned to the client as per :ref:`protecting_views`.

.. index::
   single: view lookup

.. _view_lookup:

View Lookup and Invocation
--------------------------

:term:`View lookup` is the :app:`Pyramid` subsystem responsible for
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

This does not mean however, that :app:`Pyramid` "stops looking"
when it finds a view registration with predicates that don't match.
If one set of view predicates does not match, the "next most specific"
view (if any) view is consulted for predicates, and so on, until a
view is found, or no view can be matched up with the request.  The
first view with a set of predicates all of which match the request
environment will be invoked.

If no view can be found which has predicates which allow it to be
matched up with the request, :app:`Pyramid` will return an error to
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

