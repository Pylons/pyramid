Views
=====

A view is a callable which is called when a a request enters your
application.  :mod:`repoze.bfg's` primary job is to find and call a
view when a request reaches it.  The view's return value must
implement the Response object interface.

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



