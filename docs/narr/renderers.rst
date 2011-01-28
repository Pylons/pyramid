.. _renderers_chapter:

Renderers
=========

A view needn't *always* return a :term:`Response` object.  If a view
happens to return something which does not implement the Pyramid
Response interface, :app:`Pyramid` will attempt to use a
:term:`renderer` to construct a response.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config(renderer='json')
   def hello_world(request):
       return {'content':'Hello!'}

The above example returns a *dictionary* from the view callable.  A
dictionary does not implement the Pyramid response interface, so you might
believe that this example would fail.  However, since a ``renderer`` is
associated with the view callable through its :term:`view configuration` (in
this case, using a ``renderer`` argument passed to
:func:`~pyramid.view.view_config`), if the view does *not* return a Response
object, the renderer will attempt to convert the result of the view to a
response on the developer's behalf.

Of course, if no renderer is associated with a view's configuration,
returning anything except an object which implements the Response interface
will result in an error.  And, if a renderer *is* used, whatever is returned
by the view must be compatible with the particular kind of renderer used, or
an error may occur during view invocation.

One exception exists: it is *always* OK to return a Response object, even
when a ``renderer`` is configured.  If a view callable returns a response
object from a view that is configured with a renderer, the renderer is
bypassed entirely.

Various types of renderers exist, including serialization renderers
and renderers which use templating systems.  See also
:ref:`views_which_use_a_renderer`.


.. index::
   single: renderer
   single: view renderer

.. _views_which_use_a_renderer:

Writing View Callables Which Use a Renderer
-------------------------------------------

As we've seen, view callables needn't always return a Response object.
Instead, they may return an arbitrary Python object, with the expectation
that a :term:`renderer` will convert that object into a response instance on
your behalf.  Some renderers use a templating system; other renderers use
object serialization techniques.

View configuration can vary the renderer associated with a view callable via
the ``renderer`` attribute.  For example, this call to
:meth:`~pyramid.config.Configurator.add_view` associates the ``json`` renderer
with a view callable:

.. code-block:: python
   :linenos:

   config.add_view('myproject.views.my_view', renderer='json')

When this configuration is added to an application, the
``myproject.views.my_view`` view callable will now use a ``json`` renderer,
which renders view return values to a :term:`JSON` response serialization.

Other built-in renderers include renderers which use the :term:`Chameleon`
templating language to render a dictionary to a response.

If the :term:`view callable` associated with a :term:`view configuration`
returns a Response object directly (an object with the attributes ``status``,
``headerlist`` and ``app_iter``), any renderer associated with the view
configuration is ignored, and the response is passed back to :app:`Pyramid`
unmolested.  For example, if your view callable returns an instance of the
:class:`pyramid.httpexceptions.HTTPFound` class as a response, no renderer
will be employed.

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import HTTPFound

   def view(request):
       return HTTPFound(location='http://example.com') # any renderer avoided

Views which use a renderer can vary non-body response attributes (such as
headers and the HTTP status code) by attaching properties to the request.
See :ref:`response_request_attrs`.

Additional renderers can be added by developers to the system as necessary
(see :ref:`adding_and_overriding_renderers`).

.. index::
   single: renderers (built-in)
   single: built-in renderers

.. _built_in_renderers:

Built-In Renderers
------------------

Several built-in renderers exist in :app:`Pyramid`.  These renderers can be
used in the ``renderer`` attribute of view configurations.

.. index::
   pair: renderer; string

``string``: String Renderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``string`` renderer is a renderer which renders a view callable result to
a string.  If a view callable returns a non-Response object, and the
``string`` renderer is associated in that view's configuration, the result
will be to run the object through the Python ``str`` function to generate a
string.  Note that if a Unicode object is returned by the view callable, it
is not ``str()`` -ified.

Here's an example of a view that returns a dictionary.  If the ``string``
renderer is specified in the configuration for this view, the view will
render the returned dictionary to the ``str()`` representation of the
dictionary:

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

Views which use the string renderer can vary non-body response attributes by
attaching properties to the request.  See :ref:`response_request_attrs`.

.. index::
   pair: renderer; JSON

``json``: JSON Renderer
~~~~~~~~~~~~~~~~~~~~~~~

The ``json`` renderer renders view callable results to :term:`JSON`.  It
passes the return value through the ``json.dumps`` standard library function,
and wraps the result in a response object.  It also sets the response
content-type to ``application/json``.

Here's an example of a view that returns a dictionary.  Since the ``json``
renderer is specified in the configuration for this view, the view will
render the returned dictionary to a JSON serialization:

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

The return value needn't be a dictionary, but the return value must contain
values serializable by :func:`json.dumps`.

You can configure a view to use the JSON renderer by naming ``json`` as the
``renderer`` argument of a view configuration, e.g. by using
:meth:`~pyramid.config.Configurator.add_view`:

.. code-block:: python
   :linenos:

   config.add_view('myproject.views.hello_world', 
                    name='hello',
                    context='myproject.resources.Hello',
                    renderer='json')
    

Views which use the JSON renderer can vary non-body response attributes by
attaching properties to the request.  See :ref:`response_request_attrs`.

.. index::
   pair: renderer; chameleon

.. _chameleon_template_renderers:

``*.pt`` or ``*.txt``: Chameleon Template Renderers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two built-in renderers exist for :term:`Chameleon` templates.

If the ``renderer`` attribute of a view configuration is an absolute path, a
relative path or :term:`asset specification` which has a final path element
with a filename extension of ``.pt``, the Chameleon ZPT renderer is used.
See :ref:`chameleon_zpt_templates` for more information about ZPT templates.

If the ``renderer`` attribute of a view configuration is an absolute path or
a :term:`asset specification` which has a final path element with a filename
extension of ``.txt``, the :term:`Chameleon` text renderer is used.  See
:ref:`chameleon_zpt_templates` for more information about Chameleon text
templates.

The behavior of these renderers is the same, except for the engine
used to render the template.

When a ``renderer`` attribute that names a template path or :term:`asset
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
renderer-related information), ``context`` (the context resource of the view
used to render the template), and ``request`` (the request passed to the view
used to render the template).

Here's an example view configuration which uses a Chameleon ZPT renderer:

.. code-block:: python
   :linenos:

    # config is an instance of pyramid.config.Configurator

    config.add_view('myproject.views.hello_world',
                    name='hello',
                    context='myproject.resources.Hello',
                    renderer='myproject:templates/foo.pt')

Here's an example view configuration which uses a Chameleon text renderer:

.. code-block:: python
   :linenos:

    config.add_view('myproject.views.hello_world',
                    name='hello',
                    context='myproject.resources.Hello',
                    renderer='myproject:templates/foo.txt')

Views which use a Chameleon renderer can vary response attributes by
attaching properties to the request.  See :ref:`response_request_attrs`.

.. index::
   pair: renderer; mako

.. _mako_template_renderers:

``*.mak`` or ``*.mako``: Mako Template Renderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``Mako`` template renderer renders views using a Mako template.  When
used, the view must return a Response object or a Python *dictionary*.  The
dictionary items will then be used in the global template space. If the view
callable returns anything but a Response object, or a dictionary, an error
will be raised.

When using a ``renderer`` argument to a :term:`view configuration` to specify
a Mako template, the value of the ``renderer`` may be a path relative to the
``mako.directories`` setting (e.g.  ``some/template.mak``) or, alternately,
it may be a :term:`asset specification`
(e.g. ``apackage:templates/sometemplate.mak``).  Mako templates may
internally inherit other Mako templates using a relative filename or a
:term:`asset specification` as desired.

Here's an example view configuration which uses a relative path:

.. code-block:: python
   :linenos:

    # config is an instance of pyramid.config.Configurator

    config.add_view('myproject.views.hello_world',
                    name='hello',
                    context='myproject.resources.Hello',
                    renderer='foo.mak')

It's important to note that in Mako's case, the 'relative' path name
``foo.mak`` above is not relative to the package, but is relative to the
directory (or directories) configured for Mako via the ``mako.directories``
configuration file setting.

The renderer can also be provided in :term:`asset specification`
format. Here's an example view configuration which uses one:

.. code-block:: python
   :linenos:

    config.add_view('myproject.views.hello_world',
                    name='hello',
                    context='myproject.resources.Hello',
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
----------------------------------------

Before a response constructed by a :term:`renderer` is returned to
:app:`Pyramid`, several attributes of the request are examined which have the
potential to influence response behavior.

View callables that don't directly return a response should set these
attributes on the ``request`` object via ``setattr`` during their execution,
to influence associated response attributes.

``response_content_type``
  Defines the content-type of the resulting response,
  e.g. ``text/xml``.

``response_headerlist``
  A sequence of tuples describing cookie values that should be set in the
  response, e.g. ``[('Set-Cookie', 'abc=123'), ('X-My-Header', 'foo')]``.

``response_status``
  A WSGI-style status code (e.g. ``200 OK``) describing the status of the
  response.

``response_charset``
  The character set (e.g. ``UTF-8``) of the response.

``response_cache_for``
  A value in seconds which will influence ``Cache-Control`` and ``Expires``
  headers in the returned response.  The same can also be achieved by
  returning various values in the ``response_headerlist``, this is purely a
  convenience.

For example, if you need to change the response status from within a view
callable that uses a renderer, assign the ``response_status`` attribute to
the request before returning a result:

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

Adding and Changing Renderers
-----------------------------

New templating systems and serializers can be associated with :app:`Pyramid`
renderer names.  To this end, configuration declarations can be made which
change an existing :term:`renderer factory`, and which add a new renderer
factory.

Renderers can be registered imperatively using the
:meth:`pyramid.config.Configurator.add_renderer` API.

For example, to add a renderer which renders views which have a
``renderer`` attribute that is a path that ends in ``.jinja2``:

.. code-block:: python
   :linenos:

   config.add_renderer('.jinja2', 'mypackage.MyJinja2Renderer')

The first argument is the renderer name.  The second argument is a reference
to an implementation of a :term:`renderer factory` or a :term:`dotted Python
name` referring to such an object.

.. _adding_a_renderer:

Adding a New Renderer
~~~~~~~~~~~~~~~~~~~~~

You may add a new renderer by creating and registering a :term:`renderer
factory`.

A renderer factory implementation is typically a class with the
following interface:

.. code-block:: python
   :linenos:

   class RendererFactory:
       def __init__(self, info):
           """ Constructor: info will be an object having the the
           following attributes: name (the renderer name), package
           (the package that was 'current' at the time the
           renderer was registered), type (the renderer type
           name), registry (the current application registry) and
           settings (the deployment settings dictionary).  """

       def __call__(self, value, system):
           """ Call a the renderer implementation with the value
           and the system value passed in as arguments and return
           the result (a string or unicode object).  The value is
           the return value of a view.  The system value is a
           dictionary containing available system values
           (e.g. view, context, and request). """

The formal interface definition of the ``info`` object passed to a renderer
factory constructor is available as :class:`pyramid.interfaces.IRendererInfo`.

There are essentially two different kinds of renderer factories:

- A renderer factory which expects to accept a :term:`asset
  specification`, or an absolute path, as the ``name`` attribute of the
  ``info`` object fed to its constructor.  These renderer factories are
  registered with a ``name`` value that begins with a dot (``.``).  These
  types of renderer factories usually relate to a file on the filesystem,
  such as a template.

- A renderer factory which expects to accept a token that does not represent
  a filesystem path or a asset specification in the ``name``
  attribute of the ``info`` object fed to its constructor.  These renderer
  factories are registered with a ``name`` value that does not begin with a
  dot.  These renderer factories are typically object serializers.

.. sidebar:: Asset Specifications

   A asset specification is a colon-delimited identifier for a
   :term:`asset`.  The colon separates a Python :term:`package`
   name from a package subpath.  For example, the asset
   specification ``my.package:static/baz.css`` identifies the file named
   ``baz.css`` in the ``static`` subdirectory of the ``my.package`` Python
   :term:`package`.

Here's an example of the registration of a simple renderer factory via
:meth:`~pyramid.config.Configurator.add_renderer`:

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator

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

Changing an Existing Renderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can associate more than one filename extension with the same existing
renderer implementation as necessary if you need to use a different file
extension for the same kinds of templates.  For example, to associate the
``.zpt`` extension with the Chameleon ZPT renderer factory, use the
:meth:`pyramid.config.Configurator.add_renderer` method:

.. code-block:: python
   :linenos:

   config.add_renderer('.zpt', 'pyramid.chameleon_zpt.renderer_factory')

After you do this, :app:`Pyramid` will treat templates ending in both the
``.pt`` and ``.zpt`` filename extensions as Chameleon ZPT templates.

To change the default mapping in which files with a ``.pt`` extension are
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

Overriding A Renderer At Runtime
--------------------------------

.. warning:: This is an advanced feature, not typically used by "civilians".

In some circumstances, it is necessary to instruct the system to ignore the
static renderer declaration provided by the developer in view configuration,
replacing the renderer with another *after a request starts*.  For example,
an "omnipresent" XML-RPC implementation that detects that the request is from
an XML-RPC client might override a view configuration statement made by the
user instructing the view to use a template renderer with one that uses an
XML-RPC renderer.  This renderer would produce an XML-RPC representation of
the data returned by an arbitrary view callable.

To use this feature, create a :class:`~pyramid.events.NewRequest`
:term:`subscriber` which sniffs at the request data and which conditionally
sets an ``override_renderer`` attribute on the request itself, which is the
*name* of a registered renderer.  For example:

.. code-block:: python
   :linenos:

   from pyramid.event import subscriber
   from pyramid.event import NewRequest

   @subscriber(NewRequest)
   def set_xmlrpc_params(event):
       request = event.request
       if (request.content_type == 'text/xml'
           and request.method == 'POST'
           and not 'soapaction' in request.headers
           and not 'x-pyramid-avoid-xmlrpc' in request.headers):
           params, method = parse_xmlrpc_request(request)
           request.xmlrpc_params, request.xmlrpc_method = params, method
           request.is_xmlrpc = True
           request.override_renderer = 'xmlrpc'
           return True

The result of such a subscriber will be to replace any existing static
renderer configured by the developer with a (notional, nonexistent) XML-RPC
renderer if the request appears to come from an XML-RPC client.
