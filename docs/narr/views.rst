Views
=====

A view is a callable which is called when a a request enters your
application.  ``repoze.bfg's`` primary job is to find and call a view
when a request reaches it.  The view's return value must implement the
Response object interface.

Defining a View as a Function
-----------------------------

The easiest way to define a view is to create a function that accepts
two arguments: *context*, and *request*.  For example, this is a hello
world view implemented as a function::

  def hello_world(context, request):
      from webob import Response
      return Response('Hello world!')

Defining View Factories
-----------------------

Declarations in your view registry to point at a *view factory*
rather than pointing it at a view implemented as a function.  This
provides an additional level of convenience for some applications.

A view factory, like a view implemented as a function, accepts the
*context* and *request* arguments.  But unlike a view implemented as a
function it returns *another* callable instead of a response.  The
returned callable is then called by ``repoze.bfg``, with its arguments
filled in "magically".

The easiest way to implement a view factory is to imlement it as a
class.  Here's a hello world view factory that is implemented as a
class::

  class HelloWorld(object):
      def __init__(self, context, request):
          self.context = context
          self.request = request

      def __call__(self):
          from webob import Response
          return Response('Hello world!')

You can also implement a view factory as a function::

  def HelloWorld(context, request):
      def hello_world():
          from webob import Response
          return Response('Hello world!')
      return hello_world

Using View Factories for Convenience
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

View factories aren't just makework.  They exist for convenience,
because, unlike views as functions, views that are returned via a view
factory will have arguments "magically" mapped into them when they are
called by the router.  You can choose the arguments you'd like the
constructed view to receive simply by mentioning each in the signature
of the callable you return from the view factory (or the __call__ of
the class you use as the view factory).

The arguments that are available to be magically mapped into
constructed view calls are as follows.

context

  The current context

request

  The current request

environ

  The current WSGI environment

start_response

  The current  WSGI start_response callable

XXX We need to decide which other elements will be mapped in from the
request and map them in: e.g. query string/form elements, etc.

This means that the ``__call__`` of the following view factory
will have its *environ* and *start_response* arguments filled in
magically during view call time::

  def ViewFactory(object):
      def __init__(self, context, request):
          self.context = context
          self.request = request

      def __call__(self, environ, start_response):
          msg = 'Called via %s ' % environ['PATH_INFO']
          start_response('200 OK', ('Content-Length', len(msg))
          return msg

.. note:: If you're familiar with WSGI, you'll notice above that the
  view factory returns a valid WSGI application.  View
  factories in ``repoze.bfg`` can return any WSGI application.

View Functions Revisited
------------------------

Above we provided an example of a "view" imlemented as a function::

  def hello_world(context, request):
      from webob import Response
      return Response('Hello world!')

When ``repoze.bfg`` finds and calls this callable, has no a-priori
knowledge that would allow it to believe that this function would
return a response directly.  It assumes that what it's calling will
return a *view* instead of a *response*.  In other words, it expects
that everything configured in its view registry points at a view
factory.

However, there is a special case in the logic implemented in the
``repoze.bfg`` router that says if the return value of a view
factory is an object implementing the Response interface, use that
object as the response, and don't try to call the object or magically
map any arguments into it.  Instead, it just passes it along to the
upstream WSGI server.

This is purely for convenience: it's useful to be able to define
simple functions as "views" without the overhead of defining a view
factory.

View Factory Arguments
----------------------

Now that we know what view factories are, what are these *context*
and *request* arguments that are mapped in to it?

context

  An instance of a model found via graph traversal.

request

  A WebOb request object representing the current request.



