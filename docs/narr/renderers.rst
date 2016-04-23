.. _renderers_chapter:

Renderers
=========

A view callable needn't *always* return a :term:`Response` object.  If a view
happens to return something which does not implement the Pyramid Response
interface, :app:`Pyramid` will attempt to use a :term:`renderer` to construct a
response.  For example:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='json')
   def hello_world(request):
       return {'content':'Hello!'}

The above example returns a *dictionary* from the view callable.  A dictionary
does not implement the Pyramid response interface, so you might believe that
this example would fail.  However, since a ``renderer`` is associated with the
view callable through its :term:`view configuration` (in this case, using a
``renderer`` argument passed to :func:`~pyramid.view.view_config`), if the view
does *not* return a Response object, the renderer will attempt to convert the
result of the view to a response on the developer's behalf.

Of course, if no renderer is associated with a view's configuration, returning
anything except an object which implements the Response interface will result
in an error.  And, if a renderer *is* used, whatever is returned by the view
must be compatible with the particular kind of renderer used, or an error may
occur during view invocation.

One exception exists: it is *always* OK to return a Response object, even when
a ``renderer`` is configured.  In such cases, the renderer is bypassed
entirely.

Various types of renderers exist, including serialization renderers and
renderers which use templating systems.

.. index::
   single: renderer
   single: view renderer

.. _views_which_use_a_renderer:

Writing View Callables Which Use a Renderer
-------------------------------------------

As we've seen, a view callable needn't always return a Response object.
Instead, it may return an arbitrary Python object, with the expectation that a
:term:`renderer` will convert that object into a response instance on your
behalf.  Some renderers use a templating system, while other renderers use
object serialization techniques.  In practice, renderers obtain application
data values from Python dictionaries so, in practice, view callables which use
renderers return Python dictionaries.

View callables can :ref:`explicitly call <example_render_to_response_call>`
renderers, but typically don't.  Instead view configuration declares the
renderer used to render a view callable's results.  This is done with the
``renderer`` attribute.  For example, this call to
:meth:`~pyramid.config.Configurator.add_view` associates the ``json`` renderer
with a view callable:

.. code-block:: python

   config.add_view('myproject.views.my_view', renderer='json')

When this configuration is added to an application, the
``myproject.views.my_view`` view callable will now use a ``json`` renderer,
which renders view return values to a :term:`JSON` response serialization.

Pyramid defines several :ref:`built_in_renderers`, and additional renderers can
be added by developers to the system as necessary. See
:ref:`adding_and_overriding_renderers`.

Views which use a renderer and return a non-Response value can vary non-body
response attributes (such as headers and the HTTP status code) by attaching a
property to the ``request.response`` attribute. See
:ref:`request_response_attr`.

As already mentioned, if the :term:`view callable` associated with a
:term:`view configuration` returns a Response object (or its instance), any
renderer associated with the view configuration is ignored, and the response is
passed back to :app:`Pyramid` unchanged.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config(renderer='json')
   def view(request):
       return Response('OK') # json renderer avoided

Likewise for an :term:`HTTP exception` response:

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import HTTPFound
   from pyramid.view import view_config

   @view_config(renderer='json')
   def view(request):
       return HTTPFound(location='http://example.com') # json renderer avoided

You can of course also return the ``request.response`` attribute instead to
avoid rendering:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='json')
   def view(request):
       request.response.body = 'OK'
       return request.response # json renderer avoided

.. index::
   single: renderers (built-in)
   single: built-in renderers

.. _built_in_renderers:

Built-in Renderers
------------------

Several built-in renderers exist in :app:`Pyramid`.  These renderers can be
used in the ``renderer`` attribute of view configurations.

.. note::

   Bindings for officially supported templating languages can be found at
   :ref:`available_template_system_bindings`.

.. index::
   pair: renderer; string

``string``: String Renderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``string`` renderer renders a view callable result to a string.  If a view
callable returns a non-Response object, and the ``string`` renderer is
associated in that view's configuration, the result will be to run the object
through the Python ``str`` function to generate a string.  Note that if a
Unicode object is returned by the view callable, it is not ``str()``-ified.

Here's an example of a view that returns a dictionary.  If the ``string``
renderer is specified in the configuration for this view, the view will render
the returned dictionary to the ``str()`` representation of the dictionary:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='string')
   def hello_world(request):
       return {'content':'Hello!'}

The body of the response returned by such a view will be a string representing
the ``str()`` serialization of the return value:

.. code-block:: python

   {'content': 'Hello!'}

Views which use the string renderer can vary non-body response attributes by
using the API of the ``request.response`` attribute.  See
:ref:`request_response_attr`.

.. index::
   pair: renderer; JSON

.. _json_renderer:

JSON Renderer
~~~~~~~~~~~~~

The ``json`` renderer renders view callable results to :term:`JSON`.  By
default, it passes the return value through the ``json.dumps`` standard library
function, and wraps the result in a response object.  It also sets the response
content-type to ``application/json``.

Here's an example of a view that returns a dictionary.  Since the ``json``
renderer is specified in the configuration for this view, the view will render
the returned dictionary to a JSON serialization:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='json')
   def hello_world(request):
       return {'content':'Hello!'}

The body of the response returned by such a view will be a string representing
the JSON serialization of the return value:

.. code-block:: python

   {"content": "Hello!"}

The return value needn't be a dictionary, but the return value must contain
values serializable by the configured serializer (by default ``json.dumps``).

You can configure a view to use the JSON renderer by naming ``json`` as the
``renderer`` argument of a view configuration, e.g., by using
:meth:`~pyramid.config.Configurator.add_view`:

.. code-block:: python
   :linenos:

   config.add_view('myproject.views.hello_world',
                   name='hello',
                   context='myproject.resources.Hello',
                   renderer='json')

Views which use the JSON renderer can vary non-body response attributes by
using the API of the ``request.response`` attribute.  See
:ref:`request_response_attr`.

.. _json_serializing_custom_objects:

Serializing Custom Objects
++++++++++++++++++++++++++

Some objects are not, by default, JSON-serializable (such as datetimes and
other arbitrary Python objects).  You can, however, register code that makes
non-serializable objects serializable in two ways:

- Define a ``__json__`` method on objects in your application.

- For objects you don't "own", you can register a JSON renderer that knows
  about an *adapter* for that kind of object.

Using a Custom ``__json__`` Method
**********************************

Custom objects can be made easily JSON-serializable in Pyramid by defining a
``__json__`` method on the object's class. This method should return values
natively JSON-serializable (such as ints, lists, dictionaries, strings, and so
forth).  It should accept a single additional argument, ``request``, which will
be the active request object at render time.

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   class MyObject(object):
       def __init__(self, x):
           self.x = x

       def __json__(self, request):
           return {'x':self.x}

   @view_config(renderer='json')
   def objects(request):
       return [MyObject(1), MyObject(2)]

   # the JSON value returned by ``objects`` will be:
   #    [{"x": 1}, {"x": 2}]

Using the ``add_adapter`` Method of a Custom JSON Renderer
**********************************************************

If you aren't the author of the objects being serialized, it won't be possible
(or at least not reasonable) to add a custom ``__json__`` method to their
classes in order to influence serialization.  If the object passed to the
renderer is not a serializable type and has no ``__json__`` method, usually a
:exc:`TypeError` will be raised during serialization.  You can change this
behavior by creating a custom JSON renderer and adding adapters to handle
custom types. The renderer will attempt to adapt non-serializable objects using
the registered adapters. A short example follows:

.. code-block:: python
   :linenos:

   from pyramid.renderers import JSON

   if __name__ == '__main__':
       config = Configurator()
       json_renderer = JSON()
       def datetime_adapter(obj, request):
           return obj.isoformat()
       json_renderer.add_adapter(datetime.datetime, datetime_adapter)
       config.add_renderer('json', json_renderer)

The ``add_adapter`` method should accept two arguments: the *class* of the
object that you want this adapter to run for (in the example above,
``datetime.datetime``), and the adapter itself.

The adapter should be a callable.  It should accept two arguments: the object
needing to be serialized and ``request``, which will be the current request
object at render time. The adapter should raise a :exc:`TypeError` if it can't
determine what  to do with the object.

See :class:`pyramid.renderers.JSON` and :ref:`adding_and_overriding_renderers`
for more information.

.. versionadded:: 1.4
   Serializing custom objects.

.. index::
   pair: renderer; JSONP

.. _jsonp_renderer:

JSONP Renderer
~~~~~~~~~~~~~~

.. versionadded:: 1.1

:class:`pyramid.renderers.JSONP` is a `JSONP
<https://en.wikipedia.org/wiki/JSONP>`_ renderer factory helper which implements
a hybrid JSON/JSONP renderer.  JSONP is useful for making cross-domain AJAX
requests.

Unlike other renderers, a JSONP renderer needs to be configured at startup time
"by hand".  Configure a JSONP renderer using the
:meth:`pyramid.config.Configurator.add_renderer` method:

.. code-block:: python

   from pyramid.config import Configurator
   from pyramid.renderers import JSONP

   config = Configurator()
   config.add_renderer('jsonp', JSONP(param_name='callback'))

Once this renderer is registered via
:meth:`~pyramid.config.Configurator.add_renderer` as above, you can use
``jsonp`` as the ``renderer=`` parameter to ``@view_config`` or
:meth:`pyramid.config.Configurator.add_view`:

.. code-block:: python

   from pyramid.view import view_config

   @view_config(renderer='jsonp')
   def myview(request):
       return {'greeting':'Hello world'}

When a view is called that uses a JSONP renderer:

- If there is a parameter in the request's HTTP query string (aka
  ``request.GET``) that matches the ``param_name`` of the registered JSONP
  renderer (by default, ``callback``), the renderer will return a JSONP
  response.

- If there is no callback parameter in the request's query string, the renderer
  will return a "plain" JSON response.

Javscript library AJAX functionality will help you make JSONP requests.
For example, JQuery has a `getJSON function
<http://api.jquery.com/jQuery.getJSON/>`_, and has equivalent (but more
complicated) functionality in its `ajax function
<http://api.jquery.com/jQuery.ajax/>`_.

For example (JavaScript):

.. code-block:: javascript

   var api_url = 'http://api.geonames.org/timezoneJSON' +
                 '?lat=38.301733840000004' +
                 '&lng=-77.45869621' +
                 '&username=fred' +
                 '&callback=?';
   jqhxr = $.getJSON(api_url);

The string ``callback=?`` above in the ``url`` param to the JQuery ``getJSON``
function indicates to jQuery that the query should be made as a JSONP request;
the ``callback`` parameter will be automatically filled in for you and used.

The same custom-object serialization scheme defined used for a "normal" JSON
renderer in :ref:`json_serializing_custom_objects` can be used when passing
values to a JSONP renderer too.

.. index::
   single: response headers (from a renderer)
   single: renderer response headers

.. _request_response_attr:

Varying Attributes of Rendered Responses
----------------------------------------

Before a response constructed by a :term:`renderer` is returned to
:app:`Pyramid`, several attributes of the request are examined which have the
potential to influence response behavior.

View callables that don't directly return a response should use the API of the
:class:`pyramid.response.Response` attribute, available as ``request.response``
during their execution, to influence associated response behavior.

For example, if you need to change the response status from within a view
callable that uses a renderer, assign the ``status`` attribute to the
``response`` attribute of the request before returning a result:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(name='gone', renderer='templates/gone.pt')
   def myview(request):
       request.response.status = '404 Not Found'
       return {'URL':request.URL}

Note that mutations of ``request.response`` in views which return a Response
object directly will have no effect unless the response object returned *is*
``request.response``.  For example, the following example calls
``request.response.set_cookie``, but this call will have no effect because a
different Response object is returned.

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   def view(request):
       request.response.set_cookie('abc', '123') # this has no effect
       return Response('OK') # because we're returning a different response

If you mutate ``request.response`` and you'd like the mutations to have an
effect, you must return ``request.response``:

.. code-block:: python
   :linenos:

   def view(request):
       request.response.set_cookie('abc', '123')
       return request.response

For more information on attributes of the request, see the API documentation in
:ref:`request_module`.  For more information on the API of
``request.response``, see :attr:`pyramid.request.Request.response`.

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

   config.add_renderer('.jinja2', 'mypackage.MyJinja2Renderer')

The first argument is the renderer name.  The second argument is a reference
to an implementation of a :term:`renderer factory` or a :term:`dotted Python
name` referring to such an object.

.. index::
   pair: renderer; adding

.. _adding_a_renderer:

Adding a New Renderer
~~~~~~~~~~~~~~~~~~~~~

You may add a new renderer by creating and registering a :term:`renderer
factory`.

A renderer factory implementation should conform to the
:class:`pyramid.interfaces.IRendererFactory` interface. It should be capable of
creating an object that conforms to the :class:`pyramid.interfaces.IRenderer`
interface. A typical class that follows this setup is as follows:

.. code-block:: python
   :linenos:

   class RendererFactory:
       def __init__(self, info):
           """ Constructor: info will be an object having the
           following attributes: name (the renderer name), package
           (the package that was 'current' at the time the
           renderer was registered), type (the renderer type
           name), registry (the current application registry) and
           settings (the deployment settings dictionary). """

       def __call__(self, value, system):
           """ Call the renderer implementation with the value
           and the system value passed in as arguments and return
           the result (a string or unicode object).  The value is
           the return value of a view.  The system value is a
           dictionary containing available system values
           (e.g., view, context, and request). """

The formal interface definition of the ``info`` object passed to a renderer
factory constructor is available as :class:`pyramid.interfaces.IRendererInfo`.

There are essentially two different kinds of renderer factories:

- A renderer factory which expects to accept an :term:`asset specification`, or
  an absolute path, as the ``name`` attribute of the ``info`` object fed to its
  constructor.  These renderer factories are registered with a ``name`` value
  that begins with a dot (``.``).  These types of renderer factories usually
  relate to a file on the filesystem, such as a template.

- A renderer factory which expects to accept a token that does not represent a
  filesystem path or an asset specification in the ``name`` attribute of the
  ``info`` object fed to its constructor.  These renderer factories are
  registered with a ``name`` value that does not begin with a dot.  These
  renderer factories are typically object serializers.

.. sidebar:: Asset Specifications

   An asset specification is a colon-delimited identifier for an :term:`asset`.
   The colon separates a Python :term:`package` name from a package subpath.
   For example, the asset specification ``my.package:static/baz.css``
   identifies the file named ``baz.css`` in the ``static`` subdirectory of the
   ``my.package`` Python :term:`package`.

Here's an example of the registration of a simple renderer factory via
:meth:`~pyramid.config.Configurator.add_renderer`, where ``config`` is an
instance of :meth:`pyramid.config.Configurator`:

.. code-block:: python

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

At startup time, when a :term:`view configuration` is encountered which has a
``name`` attribute that does not contain a dot, the full ``name`` value is used
to construct a renderer from the associated renderer factory.  In this case,
the view configuration will create an instance of an ``MyAMFRenderer`` for each
view configuration which includes ``amf`` as its renderer value.  The ``name``
passed to the ``MyAMFRenderer`` constructor will always be ``amf``.

Here's an example of the registration of a more complicated renderer factory,
which expects to be passed a filesystem path:

.. code-block:: python

   config.add_renderer(name='.jinja2', factory='my.package.MyJinja2Renderer')

Adding the above code to your application startup will allow you to use the
``my.package.MyJinja2Renderer`` renderer factory implementation in view
configurations by referring to any ``renderer`` which *ends in* ``.jinja2`` in
the ``renderer`` attribute of a :term:`view configuration`:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='templates/mytemplate.jinja2')
   def myview(request):
       return {'Hello':'world'}

When a :term:`view configuration` is encountered at startup time which has a
``name`` attribute that does contain a dot, the value of the name attribute is
split on its final dot.  The second element of the split is typically the
filename extension.  This extension is used to look up a renderer factory for
the configured view.  Then the value of ``renderer`` is passed to the factory
to create a renderer for the view. In this case, the view configuration will
create an instance of a ``MyJinja2Renderer`` for each view configuration which
includes anything ending with ``.jinja2`` in its ``renderer`` value.  The
``name`` passed to the ``MyJinja2Renderer`` constructor will be the full value
that was set as ``renderer=`` in the view configuration.

Adding a Default Renderer
~~~~~~~~~~~~~~~~~~~~~~~~~

To associate a *default* renderer with *all* view configurations (even ones
which do not possess a ``renderer`` attribute), pass ``None`` as the ``name``
attribute to the renderer tag:

.. code-block:: python

   config.add_renderer(None, 'mypackage.json_renderer_factory')

.. index::
   pair: renderer; changing

Changing an Existing Renderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pyramid supports overriding almost every aspect of its setup through its
:ref:`Conflict Resolution <automatic_conflict_resolution>` mechanism. This
means that, in most cases, overriding a renderer is as simple as using the
:meth:`pyramid.config.Configurator.add_renderer` method to redefine the
template extension. For example, if you would like to override the ``json``
renderer to specify a new renderer, you could do the following:

.. code-block:: python

   json_renderer = pyramid.renderers.JSON()
   config.add_renderer('json', json_renderer)

After doing this, any views registered with the ``json`` renderer will use the
new renderer.

.. index::
   pair: renderer; overriding at runtime

Overriding a Renderer at Runtime
--------------------------------

.. warning:: This is an advanced feature, not typically used by "civilians".

In some circumstances, it is necessary to instruct the system to ignore the
static renderer declaration provided by the developer in view configuration,
replacing the renderer with another *after a request starts*.  For example, an
"omnipresent" XML-RPC implementation that detects that the request is from an
XML-RPC client might override a view configuration statement made by the user
instructing the view to use a template renderer with one that uses an XML-RPC
renderer.  This renderer would produce an XML-RPC representation of the data
returned by an arbitrary view callable.

To use this feature, create a :class:`~pyramid.events.NewRequest`
:term:`subscriber` which sniffs at the request data and which conditionally
sets an ``override_renderer`` attribute on the request itself, which in turn is
the *name* of a registered renderer.  For example:

.. code-block:: python
   :linenos:

   from pyramid.events import subscriber
   from pyramid.events import NewRequest

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

The result of such a subscriber will be to replace any existing static renderer
configured by the developer with a (notional, nonexistent) XML-RPC renderer, if
the request appears to come from an XML-RPC client.
