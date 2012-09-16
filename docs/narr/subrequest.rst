.. index::
   single: subrequest

.. _subrequest_chapter:

Invoking a Subrequest
=====================

.. warning:: 

   This feature was added in Pyramid 1.4a1.

:app:`Pyramid` allows you to invoke a subrequest at any point during the
processing of a request.  Invoking a subrequest allows you to obtain a
:term:`response` object from a view callable within your :app:`Pyramid`
application while you're executing a different view callable within the same
application.

Here's an example application which uses a subrequest:

.. code-block:: python

   from wsgiref.simple_server import make_server
   from pyramid.config import Configurator
   from pyramid.request import Request

   def view_one(request):
       subreq = Request.blank('/view_two')
       response = request.invoke_subrequest(subreq)
       return response

   def view_two(request):
       request.response.body = 'This came from view_two'
       return request.response

   if __name__ == '__main__':
       config = Configurator()
       config.add_route('one', '/view_one')
       config.add_route('two', '/view_two')
       config.add_view(view_one, route_name='one')
       config.add_view(view_two, route_name='two')
       app = config.make_wsgi_app()
       server = make_server('0.0.0.0', 8080, app)
       server.serve_forever()

When ``/view_one`` is visted in a browser, the text printed in the browser
pane will be ``This came from view_two``.  The ``view_one`` view used the
:meth:`pyramid.request.Request.invoke_subrequest` API to obtain a response
from another view (``view_two``) within the same application when it
executed.  It did so by constructing a new request that had a URL that it
knew would match the ``view_two`` view registration, and passed that new
request along to :meth:`pyramid.request.Request.invoke_subrequest`.  The
``view_two`` view callable was invoked, and it returned a response.  The
``view_one`` view callable then simply returned the response it obtained from
the ``view_two`` view callable.

Note that it doesn't matter if the view callable invoked via a subrequest
actually returns a literal Response object.  Any view callable that uses a
renderer or which returns an object that can be interpreted by a response
adapter will work too:

.. code-block:: python

   from wsgiref.simple_server import make_server
   from pyramid.config import Configurator
   from pyramid.request import Request

   def view_one(request):
       subreq = Request.blank('/view_two')
       response = request.invoke_subrequest(subreq)
       return response

   def view_two(request):
       return 'This came from view_two'

   if __name__ == '__main__':
       config = Configurator()
       config.add_route('one', '/view_one')
       config.add_route('two', '/view_two')
       config.add_view(view_one, route_name='one')
       config.add_view(view_two, route_name='two', renderer='string')
       app = config.make_wsgi_app()
       server = make_server('0.0.0.0', 8080, app)
       server.serve_forever()

Even though the ``view_two`` view callable returned a string, it was invoked
in such a way that the ``string`` renderer associated with the view
registration that was found turned it into a "real" response object for
consumption by ``view_one``.

Being able to unconditionally obtain a response object by invoking a view
callable indirectly is the main advantage to using
:meth:`pyramid.request.Request.invoke_subrequest` instead of simply importing
a view callable and executing it directly.  Note that there's not much
advantage to invoking a view using a subrequest if you *can* invoke a view
callable directly.  Subrequests are slower and are less convenient if you
actually do want just the literal information returned by a function that
happens to be a view callable.

Note that if a view callable invoked by a subrequest raises an exception, the
exception will usually be converted to a response if you have a
:term:`exception view` configured:

.. code-block:: python

   from wsgiref.simple_server import make_server
   from pyramid.config import Configurator
   from pyramid.request import Request

   def view_one(request):
       subreq = Request.blank('/view_two')
       response = request.invoke_subrequest(subreq)
       return response

   def view_two(request):
       raise ValueError('foo')

   def excview(request):
       request.response.body = b'An exception was raised'
       request.response.status_int = 500
       return request.response

   if __name__ == '__main__':
       config = Configurator()
       config.add_route('one', '/view_one')
       config.add_route('two', '/view_two')
       config.add_view(view_one, route_name='one')
       config.add_view(view_two, route_name='two', renderer='string')
       config.add_view(excview, context=Exception)
       app = config.make_wsgi_app()
       server = make_server('0.0.0.0', 8080, app)
       server.serve_forever()

Because the exception view handling tween is generally in the tween list, if
we run the above code, the ``excview`` :term:`exception view` will generate a
"500" error response, which will be returned to us within ``view_one``: a
Python exception will not be raised.

The :meth:`pyramid.request.Request.invoke_subrequest` API accepts two
arguments: a positional argument ``request`` that must be provided, and and
``use_tweens`` keyword argument that is optional; it defaults to ``True``.

The ``request`` object passed to the API must be an object that implements
the Pyramid request interface (such as a :class:`pyramid.request.Request`
instance).  If ``use_tweens`` is ``True``, the request will be sent to the
:term:`tween` in the tween stack closest to the request ingress.  If
``use_tweens`` is ``False``, the request will be sent to the main router
handler, and no tweens will be invoked.

In the example above, the call to
:meth:`~pyramid.request.Request.invoke_subrequest` will generally always
return a Response object, even when the view it invokes raises an exception,
because it uses the default ``use_tweens=True`` and a :term:`exception view`
is configured.

We can cause the subrequest to not be run through the tween stack by passing
``use_tweens=False`` to the call to
:meth:`~pyramid.request.Request.invoke_subrequest`, like this:

.. code-block:: python

   from wsgiref.simple_server import make_server
   from pyramid.config import Configurator
   from pyramid.request import Request

   def view_one(request):
       subreq = Request.blank('/view_two')
       response = request.invoke_subrequest(subreq, use_tweens=False)
       return response

   def view_two(request):
       raise ValueError('foo')

   def excview(request):
       request.response.body = b'An exception was raised'
       request.response.status_int = 500
       return request.response

   if __name__ == '__main__':
       config = Configurator()
       config.add_route('one', '/view_one')
       config.add_route('two', '/view_two')
       config.add_view(view_one, route_name='one')
       config.add_view(view_two, route_name='two', renderer='string')
       config.add_view(excview, context=Exception)
       app = config.make_wsgi_app()
       server = make_server('0.0.0.0', 8080, app)
       server.serve_forever()

In the above case, the call to ``request.invoke_subrequest(subreq)`` will
actually raise a :exc:`ValueError` exception instead of retrieving a "500"
response from the attempted invocation of ``view_two``, because the tween
which invokes an exception view to generate a response is never run, and
therefore ``excview`` is never executed.

This is one of the major differences between specifying the
``use_tweens=True`` and ``use_tweens=False`` arguments to
:meth:`~pyramid.request.Request.invoke_subrequest`.  ``use_tweens=True`` may
also imply invoking transaction commit/abort for the logic executed in the
subrequest if you've got ``pyramid_tm`` in the tween list, injecting debug
HTML if you've got ``pyramid_debugtoolbar`` in the tween list, and other
tween-related side effects as defined by your particular tween list.

The :meth:`~pyramid.request.Request.invoke_subrequest` function also:
        
- manages the threadlocal stack so that
  :func:`~pyramid.threadlocal.get_current_request` and
  :func:`~pyramid.threadlocal.get_current_registry` work during a request 
  (they will return the subrequest instead of the original request)

- Adds a ``registry`` attribute and a ``invoke_subrequest`` attribute (a
  callable) to the request object it's handed.

- sets request extensions (such as those added via
  :meth:`~pyramid.config.Configurator.add_request_method` or
  :meth:`~pyramid.config.Configurator.set_request_property`) on the subrequest
  object passed as ``request``

- causes a :class:`~pyramid.event.NewRequest` event to be sent at the
  beginning of request processing.

- causes a :class:`~pyramid.event.ContextFound` event to be sent when a
  context resource is found.
  
- causes a :class:`~pyramid.event.NewResponse` event to be sent when the
  Pyramid application returns a response.

- Calls any :term:`response callback` functions defined within the subrequest's
  lifetime if a response is obtained from the Pyramid application.

- Calls any :term:`finished callback` functions defined within the subrequest's
  lifetime.

It's a poor idea to use the original ``request`` object as an argument to
:meth:`~pyramid.request.Request.invoke_subrequest`.  You should construct a
new request instead as demonstrated in the above example, using
:meth:`pyramid.request.Request.blank`.  Once you've constructed a request
object, you'll need to massage the it to match the view callable you'd like
to be executed during the subrequest.  This can be done by adjusting the
subrequest's URL, its headers, its request method, and other attributes.  The
documentation for :class:`pyramid.request.Request` exposes the methods you
should call and attributes you should set on the request you create to
massage it into something that will actually match the view you'd like to
call via a subrequest.

We've demonstrated use of a subrequest from within a view callable, but you
can use the :meth:`~pyramid.request.Request.invoke_subrequest` API from
within a tween or an event handler as well.  It's usually a poor idea to
invoke :meth:`~pyramid.request.Request.invoke_subrequest` from within a
tween, because tweens already by definition have access to a function that
will cause a subrequest (they are passed a ``handle`` function), but you can
do it.  It's fine to invoke
:meth:`~pyramid.request.Request.invoke_subrequest` from within an event
handler, however.
