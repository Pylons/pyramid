.. _views_chapter:

Views
=====

A :term:`view` is a callable which is invoked when a request enters
your application.  :mod:`repoze.bfg's` primary job is to find and call
a view when a :term:`request` reaches it.  The view's return value
must implement the :term:`WebOb` ``Response`` object interface.

Defining a View as a Function
-----------------------------

The easiest way to define a view is to create a function that accepts
two arguments: :term:`context`, and :term:`request`.  For example,
this is a hello world view implemented as a function:

.. code-block:: python
   :linenos:

   def hello_world(context, request):
       from webob import Response
       return Response('Hello world!')

The :term:`context` and :term:`request` arguments can be defined as
follows:

context

  An instance of a model found via graph :term:`traversal` or
  :term:`URL dispatch`.

request

  A WebOb request object representing the current WSGI request.

A view must return an object that implements the :term:`WebOb`
``Response`` interface.  The easiest way to return something that
implements this interface is to return a ``webob.Response`` object.
But any object that has the following attributes will work:

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
  world!</body></html>']`` or it can be a filelike object, or any
  other sort of iterable.

If a view happens to return something to the :mod:`repoze.bfg`
publisher that does not implement this interface, the publisher will
raise an error.

Mapping Views to URLs
----------------------

You may associate a view with a URL by adding information to your
:term:`application registry` via :term:`ZCML` in your
``configure.zcml`` file using a ``bfg:view`` declaration.

.. code-block:: xml
   :linenos:

   <bfg:view
       for=".models.Hello"
       view=".views.hello_world"
       name="hello.html"
       />

The above maps the ``.views.hello_world`` view function to
:term:`context` objects which are instances of the Python class
represented by ``.models.Hello`` when the *view name* is
``hello.html``.

.. note:: Values prefixed with a period (``.``)for the ``for`` and
   ``view`` attributes of a ``bfg:view`` (such as those above) mean
   "relative to the Python package directory in which this
   :term:`ZCML` file is stored".  So if the above ``bfg:view``
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

   <bfg:view
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

   <bfg:view
       for="*"
       view=".views.hello_world"
       name="hello.html"
       />

This indicates that when :mod:`repoze.bfg` identifies that the *view
name* is ``hello.html`` against *any* :term:`context`, this view will
be called.

.. note::

   If you're allergic to reading and writing :term:`ZCML`, or you're
   just more comfortable defining your view declarations using Python,
   you may use the :term:`repoze.bfg.convention` package.  This
   package provides a decorator named ``bfg_view`` that can be used to
   associate ``for``, ``name``, ``permission`` and ``request_type``
   information with a function that acts as a BFG view instead of
   needing to rely on ZCML for the same task.  You only need to add a
   single ZCML stanza to your ``configure.zcml`` for
   :term:`repoze.bfg.convention` to find all views decorated in this
   fashion.

Using Model Interfaces
----------------------

Instead of registering your views ``for`` a Python *class*, you can
instead register a view for an :term:`interface`.  Since an interface
can be attached arbitrarily to any instance (as opposed to its
identity being implied by only its class), associating a view with an
interface can provide more flexibility for sharing a single view
between two or more different implementations of a model type.  For
example, if two model object instances of different Python class types
share the same interface, you can use the same view against each of
them.

In order to make use of interfaces in your application during view
dispatch, you must create an interface and mark up your classes or
instances with interface declarations that refer to this interface.

To attach an interface to a *class*, you define the interface and use
the ``zope.interface.implements`` function to associate the interface
with the class.

.. code-block:: python
   :linenos:

   from zope.interface import Interface
   from zope.interface import implements

   class IHello(Interface):
       """ A marker interface """

   class Hello(object):
       implements(IHello)

To attach an interface to an *instance*, you define the interface and
use the ``zope.interface.alsoProvides`` function to associate the
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

Regardless of how you associate an interface with an instance or
class, the resulting ZCML to associate that interface with a view is
the same.  Assuming the above code that defines an ``IHello``
interface lives in the root of your application, and its module is
named "models.py", the below interface declaration will associate the
``.views.hello_world`` view with models that implement (aka provide)
this interface.

.. code-block:: xml
   :linenos:

   <bfg:view
       for=".models.IHello"
       view=".views.hello_world"
       name="hello.html"
       />

Any time a model that is determined to be the :term:`context` provides
this interface, and a view named ``hello.html`` is looked up against
it as per the URL, the ``.views.hello_world`` view will be invoked.

See :term:`Interface` in the glossary to find more information about
interfaces.

The ``bfg:view`` ZCML Element
-----------------------------

The ``bfg:view`` ZCML element has these possible attributes:

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

  A Python dotted-path name representing the :term:`interface` that
  the :term:`request` must have in order for this view to be found and
  called.  See :ref:`view_request_types_section` for more
  information about view security and permissions.

.. _view_request_types_section:

View Request Types
------------------

You can optionally add a *request_type* attribute to your ``bfg:view``
declaration, which indicates what "kind" of request the view should be
used for.  For example:

.. code-block:: xml
   :linenos:

   <bfg:view
       for=".models.IHello"
       view=".views.hello_json"
       name="hello.json"
       request_type=".interfaces.IJSONRequest"
       />

Where the code behind ``.interfaces.IJSONRequest`` might look like:

.. code-block:: python
   :linenos:

   from repoze.bfg.interfaces import IRequest

   class IJSONRequest(IRequest):
      """ An marker interface for representing a JSON request """

This is an example of simple "content negotiation", using JSON as an
example.  To make sure that this view will be called when the request
comes from a JSON client, you can use an ``INewRequest`` event
subscriber to attach the ``IJSONRequest`` interface to the request if
and only if the request headers indicate that the request has come
from a JSON client.  Since we've indicated that the ``request_type``
in our ZCML for this particular view is ``.interfaces.IJSONRequest``,
the view will only be called if the request provides this interface.

You can also use this facility for "skinning" a by using request
parameters to vary the interface(s) that a request provides.  By
attaching to the request an arbitrary interface after examining the
hostname or any other information available in the request within an
``INewRequest`` event subscriber, you can control view lookup
precisely.  For example, if you wanted to have two slightly different
views for requests to two different hostnames, you might register one
view with a ``request_type`` of ``.interfaces.IHostnameFoo`` and
another with a ``request_type`` of ``.interfaces.IHostnameBar`` and
then arrange for an event subscriber to attach
``.interfaces.IHostnameFoo`` to the request when the HTTP_HOST is
``foo`` and ``.interfaces.IHostnameBar`` to the request when the
HTTP_HOST is ``bar``.  The appropriate view will be called.

You can also form an inheritance hierarchy out of ``request_type``
interfaces.  When :mod:`repoze.bfg` looks up a view, the most specific
view for the interface(s) found on the request based on standard
Python method resolution order through the interface class hierarchy
will be called.

See :ref:`events_chapter` for more information about event
subscribers.

.. _view_security_section:

View Security
-------------

If a :term:`security policy` is active, any :term:`permission`
attached to a ``bfg:view`` declaration will be consulted to ensure
that the currently authenticated user possesses that permission
against the context before the view function is actually called.
Here's an example of specifying a permission in a ``bfg:view``
declaration:

.. code-block:: xml
   :linenos:

   <bfg:view
       for=".models.IBlog"
       view=".views.add_entry"
       name="add.html"
       permission="add"
       />

When a security policy is enabled, this view will be protected with
the ``add`` permission.  The view will not be called if the user does
not possess the ``add`` permission relative to the current
:term:`context`.  Instead an HTTP ``Unauthorized`` status will be
returned to the client.

.. note::

   See the :ref:`security_chapter` chapter to find out how to turn on
   a security policy.

