.. _views_chapter:

Views
=====

A :term:`view` is a callable which is invoked when a request enters
your application.  The primary job of any :mod:`repoze.bfg`
application is is to find and call a :term:`view` when a
:term:`request` reaches it.  The value returned by a :term:`view` must
implement the :term:`WebOb` ``Response`` object interface.

.. _function_as_view:

Defining a View as a Function
-----------------------------

The easiest way to define a view is to create a function that accepts
two arguments: :term:`context`, and :term:`request`.  For example,
this is a hello world view implemented as a function:

.. code-block:: python
   :linenos:

   from webob import Response

   def hello_world(context, request):
       return Response('Hello world!')

The :term:`context` and :term:`request` arguments passed to a view
function can be defined as follows:

context

  An instance of a :term:`context` found via graph :term:`traversal`
  or :term:`URL dispatch`.  If the context is found via traversal, it
  will be a :term:`model` object.

request

  A WebOb request object representing the current WSGI request.

.. _class_as_view:

Defining a View as a Class 
--------------------------

.. note:: This feature is new as of :mod:`repoze.bfg` 0.8.1.

When a view callable is a class, the calling semantics are slightly
different than when it is a function or another non-class callable.
When a view is a class, the class' ``__init__`` is called with the
context and the request parameters.  As a result, an instance of the
class is created.  Subsequently, that instance's ``__call__`` method
is invoked with no parameters.  The class' ``__call__`` method must
return a response.  This provides behavior similar to a Zope 'browser
view' (Zope 'browser views' are typically classes instead of simple
callables).  So the simplest class that can be a view must have:

- an ``__init__`` method that accepts a ``context`` and a ``request``
  as positional arguments.

- a ``__call__`` method that accepts no parameters and returns a
  response.

For example:

.. code-block:: python
   :linenos:

   from webob import Response

   class MyView(object):
       def __init__(self, context, request):
           self.context = context
           self.request = request

       def __call__(self):
           return Response('hello from %r!' % self.context)

The context and request objects passed to ``__init__`` are the same
types of objects as described in :ref:`function_as_view`.

Alternate "Request-Only" View Argument Convention
-------------------------------------------------

Views may alternately be defined as callables that accept only a
request object, instead of both a context and a request.  The
following types work as views in this style:

#. Functions that accept a single argument ``request``, e.g.::

      from webob import Response

      def view(request):
          return Response('OK')

#. New-style and old-style classes that have an ``__init__`` method
   that accepts ``self, request``, e.g.::

      from webob import Response

      class view(object):
          __init__(self, request):
              return Response('OK')

#. Arbitrary callables that have a ``__call__`` method that accepts
   ``self, request``, e.g.::

      from webob import Response

      class View(object):
          def __call__(self, request):
              return Response('OK')
      view = View() # this is the view callable

This style of calling convention is useful for :term:`url dispatch`
based applications, where the context is seldom used within the view
code itself.  The view always has access to the context via
``request.context`` in any case, so it's still available even if you
use the request-only calling convention.

The Response
------------

A view callable must return an object that implements the
:term:`WebOb` ``Response`` interface.  The easiest way to return
something that implements this interface is to return a
``webob.Response`` object.  But any object that has the following
attributes will work:

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
:term:`router` that does not implement this interface, the router will
raise an error.

.. _mapping_views_to_urls_using_zcml_section:

Mapping Views to URLs Using ZCML
--------------------------------

You may associate a view with a URL by adding information to your
:term:`application registry` via :term:`ZCML` in your
``configure.zcml`` file using a ``view`` declaration.

.. code-block:: xml
   :linenos:

   <view
       for=".models.Hello"
       view=".views.hello_world"
       name="hello.html"
       />

The above maps the ``.views.hello_world`` view function to
:term:`context` objects which are instances (or subclasses) of the
Python class represented by ``.models.Hello`` when the *view name* is
``hello.html``.

.. note:: Values prefixed with a period (``.``) for the ``for`` and
   ``view`` attributes of a ``view`` (such as those above) mean
   "relative to the Python package directory in which this
   :term:`ZCML` file is stored".  So if the above ``view``
   declaration was made inside a ``configure.zcml`` file that lived in
   the ``hello`` package, you could replace the relative
   ``.models.Hello`` with the absolute ``hello.models.Hello``;
   likewise you could replace the relative ``.views.hello_world`` with
   the absolute ``hello.views.hello_world``.  Either the relative or
   absolute form is functionally equivalent.  It's often useful to use
   the relative form, in case your package's name changes.  It's also
   shorter to type.

You can also declare a *default view* for a model type:

.. code-block:: xml
   :linenos:

   <view
       for=".models.Hello"
       view=".views.hello_world"
       />

A *default view* has no ``name`` attribute.  When a :term:`context` is
traversed and there is no *view name* in the request, the *default
view* is the view that is used.

You can also declare that a view is good for any model type by using
the special ``*`` character in the ``for`` attribute:

.. code-block:: xml
   :linenos:

   <view
       for="*"
       view=".views.hello_world"
       name="hello.html"
       />

This indicates that when :mod:`repoze.bfg` identifies that the *view
name* is ``hello.html`` against *any* :term:`context`, this view will
be called.

A ZCML ``view`` declaration's ``view`` attribute can also name a
class.  In this case, the rules described in :ref:`class_as_view`
apply for the class which is named.

The ``view`` ZCML Directive
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``view`` ZCML directive has these possible attributes:

view

  The Python dotted-path name to the view callable.

for

  A Python dotted-path name representing the Python class that the
  :term:`context` must be an instance of, *or* the :term:`interface`
  that the :term:`context` must provide in order for this view to be
  found and called.

name

  The *view name*.  Read and understand :ref:`traversal_chapter` to
  understand the concept of a view name.

permission

  The name of a *permission* that the user must possess in order to
  call the view.  See :ref:`view_security_section` for more
  information about view security and permissions.

request_type

  This value can either be one of the strings 'GET', 'POST', 'PUT',
  'DELETE', or 'HEAD' representing an HTTP method, *or* it may be
  Python dotted-path string representing the :term:`interface` that
  the :term:`request` must have in order for this view to be found and
  called.  See :ref:`view_request_types_section` for more information
  about request types.

route_name

  *This attribute services an advanced feature that isn't often used
  unless you want to perform traversal *after* a route has matched.*
  This value must match the ``name`` of a ``<route>`` declaration (see
  :ref:`urldispatch_chapter`) that must match before this view will be
  called.  The ``<route>`` declaration specified by ``route_name`` must
  exist in ZCML before the view that names the route
  (XML-ordering-wise) .  Note that the ``<route>`` declaration
  referred to by ``route_name`` usually has a ``*traverse`` token in
  the value of its ``path`` attribute, representing a part of the path
  that will be used by traversal against the result of the route's
  :term:`root factory`.  See :ref:`hybrid_chapter` for more
  information on using this advanced feature.

.. _mapping_views_to_urls_using_a_decorator_section:

Mapping Views to URLs Using a Decorator
---------------------------------------

If you're allergic to reading and writing :term:`ZCML`, or you're just
more comfortable defining your view declarations using Python, you may
use the ``repoze.bfg.view.bfg_view`` decorator to associate your view
functions with URLs instead of using :term:`ZCML` for the same
purpose.  ``repoze.bfg.view.bfg_view`` can be used to associate
``for``, ``name``, ``permission`` and ``request_type`` information --
as done via the equivalent ZCML -- with a function that acts as a
:mod:`repoze.bfg` view.

To make :mod:`repoze.bfg` process your ``bfg_view`` declarations, you
*must* insert the following boilerplate into your application's
``configure.zcml``::

  <scan package="."/>

After you do so, you will not need to use any other ZCML to configure
:mod:`repoze.bfg` view declarations.  Instead, you will use a
decorator to do this work.

.. warning:: using this feature tends to slows down application
   startup slightly, as more work is performed at application startup
   to scan for view declarations.  Additionally, if you use
   decorators, it means that other people will not be able to override
   your view declarations externally using ZCML: this is a common
   requirement if you're developing an extensible application (e.g. a
   framework).  See :ref:`extending_chapter` for more information
   about building extensible applications.

The ``bfg_view`` Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~

``repoze.bfg.view.bfg_view`` is a decorator which allows Python code
to make view registrations instead of using ZCML for the same purpose.

An example might reside in a bfg application module ``views.py``:

.. code-block:: python
   :linenos:

   from models import MyModel
   from repoze.bfg.view import bfg_view
   from repoze.bfg.chameleon_zpt import render_template_to_response

   @bfg_view(name='my_view', request_type='POST', for_=MyModel,
             permission='read')
   def my_view(context, request):
       return render_template_to_response('templates/my.pt')

Using this decorator as above replaces the need to add this ZCML to
your application registry:

.. code-block:: xml
   :linenos:

   <view
    for=".models.MyModel"
    view=".views.my_view"
    name="my_view"
    permission="read"
    request_type="POST"
    />

All arguments to ``bfg_view`` are optional.

If ``name`` is not supplied, the empty string is used (implying
the default view).

If ``request_type`` is not supplied, the interface ``None`` is used,
implying any request type.

If ``for_`` is not supplied, the interface
``zope.interface.Interface`` (which matches any model) is used.
``for_`` can also name a class, like its ZCML brother.

If ``permission`` is not supplied, no permission is registered for
this view (it's accessible by any caller).

If ``route_name`` is supplied, the view will be invoked only if the
named route matches.  *This is an advanced feature, not often used by
"civilians"*.

All arguments may be omitted.  For example:

.. code-block:: python
   :linenos:

   from webob import Response

   @bfg_view()
   def my_view(context, request):
       """ My view """
       return Response()

Such a registration as the one directly above implies that the view
name will be ``my_view``, registered ``for_`` any model type, using no
permission, registered against requests which implement any request
method or interface.

If your view callable is a class, the ``bfg_view`` decorator can also
be used as a class decorator in Python 2.6 and better (Python 2.5 and
below do not support class decorators).  All the arguments to the
decorator are the same when applied against a class as when they are
applied against a function.  For example:

.. code-block:: python
   :linenos:

   from webob import Response
   from repoze.bfg.view import bfg_view

   @bfg_view()
   class MyView(object):
       def __init__(self, context, request):
           self.context = context
           self.request = request

       def __call__(self):
           return Response('hello from %s!' % self.context)

You can use the ``bfg_view`` decorator as a simple callable to
manually decorate classes in Python 2.5 and below (without the
decorator syntactic sugar), if you wish:

.. code-block:: python
   :linenos:

   from webob import Response
   from repoze.bfg.view import bfg_view

   class MyView(object):
       def __init__(self, context, request):
           self.context = context
           self.request = request

       def __call__(self):
           return Response('hello from %s!' % self.context)

   my_view = bfg_view()(MyView)

.. _using_model_interfaces:

Using Model Interfaces
----------------------

Instead of registering your views ``for`` a Python model *class*, you
can optionally register a view for an :term:`interface`.  Since an
interface can be attached arbitrarily to any model instance (as
opposed to its identity being implied by only its class), associating
a view with an interface can provide more flexibility for sharing a
single view between two or more different implementations of a model
type.  For example, if two model object instances of different Python
class types share the same interface, you can use the same view
against each of them.

In order to make use of interfaces in your application during view
dispatch, you must create an interface and mark up your model classes
or instances with interface declarations that refer to this interface.

To attach an interface to a model *class*, you define the interface
and use the ``zope.interface.implements`` function to associate the
interface with the class.

.. code-block:: python
   :linenos:

   from zope.interface import Interface
   from zope.interface import implements

   class IHello(Interface):
       """ A marker interface """

   class Hello(object):
       implements(IHello)

To attach an interface to a model *instance*, you define the interface
and use the ``zope.interface.alsoProvides`` function to associate the
interface with the instance.  This function mutates the instance in
such a way that the interface is attached to it.

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
view is the same.  Assuming the above code that defines an ``IHello``
interface lives in the root of your application, and its module is
named "models.py", the below interface declaration will associate the
``.views.hello_world`` view with models that implement (aka provide)
this interface.

.. code-block:: xml
   :linenos:

   <view
       for=".models.IHello"
       view=".views.hello_world"
       name="hello.html"
       />

Any time a model that is determined to be the :term:`context` provides
this interface, and a view named ``hello.html`` is looked up against
it as per the URL, the ``.views.hello_world`` view will be invoked.

Note that views registered against a model class take precedence over
views registered for any interface the model class implements when an
ambiguity arises.  If a view is registered for both the class type of
the context and an interface implemented by the context's class, the
view registered for the context's class will "win".

See :term:`Interface` in the glossary to find more information about
interfaces.

.. _view_request_types_section:

Standard View Request Types
---------------------------

You can optionally add a *request_type* attribute to your ``view``
declaration or ``bfg_view`` decorator, which indicates what "kind" of
request the view should be used for.  If the request type for a
request doesn't match the request type that a view defines as its
``request_type`` argument, that view won't be called.

The request type can be one of the strings 'GET', 'POST', 'PUT',
'DELETE', or 'HEAD'.  When the request type is one of these strings,
the view will only be called when the HTTP method of a request matches
this type.

For example, the following bit of ZCML will match an HTTP POST
request:

.. code-block:: xml
   :linenos:

   <view
       for=".models.Hello"
       view=".views.handle_post"
       name="handle_post"
       request_type="POST"
       />

A ``bfg_view`` decorator that does the same as the above ZCML ``view``
declaration which matches only on HTTP POST might look something like:

.. code-block:: python
   :linenos:

   from myproject.models import Hello
   from webob import Response

   @bfg_view(for=Hello, request_type='POST')
   def handle_post(context, request):
       return Response('hello'

The above examples register views for the POST request type, so it
will only be called if the request's HTTP method is ``POST``.  Even if
all the other specifiers match (e.g. the model type is the class
``.models.Hello``, and the view_name is ``handle_post``), if the
request verb is not POST, it will not be invoked.  This provides a way
to ensure that views you write are only called via specific HTTP
verbs.

The least specific request type is ``None``.  All requests are
guaranteed to implement this request type.  It is also the default
request type for views that omit a ``request_type`` argument.

Custom View Request Types
-------------------------

You can make use of *custom* view request types by attaching an
:term:`interface` to the request and specifying this interface in the
``request_type`` parameter.  For example, you might want to make use
of simple "content negotiation", only invoking a particular view if
the request has a content-type of 'application/json'.

For information about using interface to specify a request type, see
:ref:`using_an_event_to_vary_the_request_type`.

.. _view_security_section:

View Security
-------------

If a :term:`authentication policy` (and a :term:`authorization
policy`) is active, any :term:`permission` attached to a ``view``
declaration will be consulted to ensure that the currently
authenticated user possesses that permission against the context
before the view function is actually called.  Here's an example of
specifying a permission in a ``view`` declaration:

.. code-block:: xml
   :linenos:

   <view
       for=".models.IBlog"
       view=".views.add_entry"
       name="add.html"
       permission="add"
       />

When an authentication policy is enabled, this view will be protected
with the ``add`` permission.  The view will *not be called* if the
user does not possess the ``add`` permission relative to the current
:term:`context` and an authorization policy is enabled.  Instead the
``forbidden`` view result will be returned to the client (see
:ref:`changing_the_forbidden_view`).

.. note::

   See the :ref:`security_chapter` chapter to find out how to turn on
   an authentication policy.

.. note::

   Packages such as :term:`repoze.who` are capable of intercepting an
   ``Unauthorized`` response and displaying a form that asks a user to
   authenticate.  Use this kind of package to ask the user for
   authentication credentials.

Using a View to Do A HTTP Redirect
----------------------------------

You can issue an HTTP redirect from within a view by returning a
slightly different response.

.. code-block:: python
   :linenos:

   from webob.exc import HTTPFound

   def myview(context, request):
       return HTTPFound(location='http://example.com')

All exception types from the :mod:`webob.exc` module implement the
Webob ``Response`` interface; any can be returned as the response from
a view.  See :term:`WebOb` for the documentation for this module; it
includes other response types for Unauthorized, etc.

.. _static_resources_section:

Serving Static Resources Using a View
-------------------------------------

Using the :mod:`repoze.bfg.view` ``static`` helper class is the
preferred way to serve static resources (like JavaScript and CSS
files) within :mod:`repoze.bfg`.  This class creates a callable that
is capable acting as a :mod:`repoze.bfg` view which serves static
resources from a directory.  For instance, to serve files within a
directory located on your filesystem at ``/path/to/static/dir``
mounted at the URL path ``/static`` in your application, create an
instance of :mod:`repoze.bfg.view` 's ``static`` class inside a
``static.py`` file in your application root as below.

.. code-block:: python
   :linenos:

   from repoze.bfg.view import static
   static_view = static('/path/to/static/dir')
 
Subsequently, wire this view up to be accessible as ``/static`` using
ZCML in your application's ``configure.zcml`` against either the class
or interface that represents your root object.

.. code-block:: xml
   :linenos:

    <view
      for=".models.Root"
      view=".static.static_view"
      name="static"
    />   

In this case, ``.models.Root`` refers to the class of which your
:mod:`repoze.bfg` application's root object is an instance.

.. note:: You can also give a ``for`` of ``*`` if you want the name
   ``static`` to be accessible as the static view against any model.
   This will also allow ``/static/foo.js`` to work, but it will allow
   for ``/anything/static/foo.js`` too, as long as ``anything`` itself
   is resolveable.

Now put your static files (JS, etc) on your filesystem in the
directory represented as ``/path/to/static/dir``.  After this is done,
you should be able to view the static files in this directory via a
browser at URLs prefixed with ``/static/``, for instance
``/static/foo.js`` will return the file
``/path/to/static/dir/foo.js``.  The static directory may contain
subdirectories recursively, and any subdirectories may hold files;
these will be resolved by the static view as you would expect.

.. note:: To ensure that model objects contained in the root don't
   "shadow" your static view (model objects take precedence during
   traversal), or to ensure that your root object's ``__getitem__`` is
   never called when a static resource is requested, you can refer to
   your static resources as registered above in URLs as,
   e.g. ``/@@static/foo.js``.  This is completely equivalent to
   ``/static/foo.js``.  See :ref:`traversal_chapter` for information
   about "goggles" (``@@``).

Using Views to Handle Form Submissions (Unicode and Character Set Issues)
-------------------------------------------------------------------------

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
working with an storing bytestrings, :mod:`repoze.bfg` configures the
:term:`WebOb` request machinery to attempt to decode form submission
values into Unicode from the UTF-8 character set implicitly.  This
implicit decoding happens when view code obtains form field values via
the :term:`WebOb` ``request.params``, ``request.GET``, or
``request.POST`` APIs.

For example, let's assume that the following form page is served up to
a browser client, and its ``action`` points at some :mod:`repoze.bfg`
view code:

.. code-block:: xml

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

   def myview(context, request):
       firstname = request.params['firstname']
       lastname = request.params['lastname']

But the following ``myview`` view code *may not* work, as it tries to
decode already-decoded (``unicode``) values obtained from
``request.params``:

.. code-block:: python

   def myview(context, request):
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

If you are using the ``webob.Response`` class to generate a response,
or if you use the ``render_template_*`` templating APIs, the UTF-8
charset is set automatically as the default via the ``Content-Type``
header.  If you return a ``Content-Type`` header without an explicit
charset, a WebOb request will add a ``;charset=utf-8`` trailer to the
``Content-Type`` header value for you for response content types that
are textual (e.g. ``text/html``, ``application/xml``, etc) as it is
rendered.  If you are using your own response object, you will need to
ensure you do this yourself.

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

