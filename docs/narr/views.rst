Views
=====

A view is a callable which is invoked when a request enters your
application.  :mod:`repoze.bfg's` primary job is to find and call a
view when a request reaches it.  The view's return value must
implement the :term:`WebOb` ``Response`` object interface.

Defining a View as a Function
-----------------------------

The easiest way to define a view is to create a function that accepts
two arguments: *context*, and *request*.  For example, this is a hello
world view implemented as a function::

  def hello_world(context, request):
      from webob import Response
      return Response('Hello world!')

View Arguments
--------------

context

  An instance of a model found via graph traversal.

request

  A WebOb request object representing the current request.

Response Construction
---------------------

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

If a view happens to return something to the :mod:``repoze.bfg``
publisher that does not implement this interface, the publisher will
raise an error.


