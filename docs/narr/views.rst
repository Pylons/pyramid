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
this is a hello world view implemented as a function::

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

You must associate a view with a URL by adding information to your
:term:`application registry` via :term:`ZCML` in your
``configure.zcml`` file using a ``bfg:view`` declaration.

.. sourcecode:: xml

  <bfg:view
      for=".models.IHello"
      view=".views.hello_world"
      name="hello.html"
      />

The above maps the ``.views.hello_world`` view function to
:term:`context` objects which implement the ``.models.IHello``
interface when the *view name* is ``hello.html``.

Note that values prefixed with a period (``.``)for the ``for`` and
``view`` attributes of a ``bfg:view`` (such as those above) mean
"relative to the Python package directory in which this :term:`ZCML`
file is stored".  So if the above ``bfg:view`` declaration was made
inside a ``configure.zcml`` file that lived in the ``hello`` package,
you could replace the relative ``.models.IHello`` with the absolute
``hello.models.IHello``; likewise you could replace the relative
``.views.hello_world`` with the absolute ``hello.views.hello_world``.
Either the relative or absolute form is functionally equivalent.  It's
often useful to use the relative form, in case your package's name
changes.  It's also shorter to type.

You can also declare a *default view* for a model type:

.. sourcecode:: xml

  <bfg:view
      for=".models.IHello"
      view=".views.hello_world"
      />

A *default view* has no ``name`` attribute.  When a :term:`context` is
traversed and there is no *view name* in the request, the *default
view* is the view that is used.

You can also declare that a view is good for any model type by using
the special ``*`` character in the ``for`` attribute:

.. sourcecode:: xml

  <bfg:view
      for="*"
      view=".views.hello_world"
      name="hello.html"
      />

This indicates that when :mod:`repoze.bfg` identifies that the *view
name* is ``hello.html`` against *any* :term:`context`, this view will
be called.

View Security
-------------

If a :term:`security policy` is active, any :term:`permission`
attached to a ``bfg:view`` declaration will be consulted to ensure
that the currently authenticated user possesses that permission
against the context before the view function is actually called.
Here's an example of specifying a permission in a ``bfg:view``
declaration:

.. sourcecode:: xml

  <bfg:view
      for=".models.IBlog"
      view=".views.add_entry"
      name="add.html"
      permission="add"
      />

When a security policy is enabled, this view will be protected with
the ``add`` permission.  See the :ref:`security_chapter` chapter to
find out how to turn on a security policy.

