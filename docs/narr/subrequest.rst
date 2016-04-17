.. index::
   single: subrequest

.. _subrequest_chapter:

Invoking a Subrequest
=====================

.. versionadded:: 1.4

:app:`Pyramid` allows you to invoke a subrequest at any point during the
processing of a request.  Invoking a subrequest allows you to obtain a
:term:`response` object from a view callable within your :app:`Pyramid`
application while you're executing a different view callable within the same
application.

Here's an example application which uses a subrequest:

.. code-block:: python
   :linenos:

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

When ``/view_one`` is visted in a browser, the text printed in the browser pane
will be ``This came from view_two``.  The ``view_one`` view used the
:meth:`pyramid.request.Request.invoke_subrequest` API to obtain a response from
another view (``view_two``) within the same application when it executed.  It
did so by constructing a new request that had a URL that it knew would match
the ``view_two`` view registration, and passed that new request along to
:meth:`pyramid.request.Request.invoke_subrequest`.  The ``view_two`` view
callable was invoked, and it returned a response.  The ``view_one`` view
callable then simply returned the response it obtained from the ``view_two``
view callable.

Note that it doesn't matter if the view callable invoked via a subrequest
actually returns a *literal* Response object.  Any view callable that uses a
renderer or which returns an object that can be interpreted by a response
adapter when found and invoked via
:meth:`pyramid.request.Request.invoke_subrequest` will return a Response
object:

.. code-block:: python
   :linenos:
   :emphasize-lines: 11

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

Even though the ``view_two`` view callable returned a string, it was invoked in
such a way that the ``string`` renderer associated with the view registration
that was found turned it into a "real" response object for consumption by
``view_one``.

Being able to unconditionally obtain a response object by invoking a view
callable indirectly is the main advantage to using
:meth:`pyramid.request.Request.invoke_subrequest` instead of simply importing a
view callable and executing it directly.  Note that there's not much advantage
to invoking a view using a subrequest if you *can* invoke a view callable
directly.  Subrequests are slower and are less convenient if you actually do
want just the literal information returned by a function that happens to be a
view callable.

Note that, by default, if a view callable invoked by a subrequest raises an
exception, the exception will be raised to the caller of
:meth:`~pyramid.request.Request.invoke_subrequest` even if you have a
:term:`exception view` configured:

.. code-block:: python
   :linenos:
   :emphasize-lines: 11-16

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

When we run the above code and visit ``/view_one`` in a browser, the
``excview`` :term:`exception view` will *not* be executed.  Instead, the call
to :meth:`~pyramid.request.Request.invoke_subrequest` will cause a
:exc:`ValueError` exception to be raised and a response will never be
generated.  We can change this behavior; how to do so is described below in our
discussion of the ``use_tweens`` argument.

.. index::
   pair: subrequest; use_tweens

Subrequests with Tweens
-----------------------

The :meth:`pyramid.request.Request.invoke_subrequest` API accepts two
arguments: a required positional argument ``request``, and an optional keyword
argument ``use_tweens`` which defaults to ``False``.

The ``request`` object passed to the API must be an object that implements the
Pyramid request interface (such as a :class:`pyramid.request.Request`
instance).  If ``use_tweens`` is ``True``, the request will be sent to the
:term:`tween` in the tween stack closest to the request ingress.  If
``use_tweens`` is ``False``, the request will be sent to the main router
handler, and no tweens will be invoked.

In the example above, the call to
:meth:`~pyramid.request.Request.invoke_subrequest` will always raise an
exception.  This is because it's using the default value for ``use_tweens``,
which is ``False``.  Alternatively, you can pass ``use_tweens=True`` to ensure
that it will convert an exception to a Response if an :term:`exception view` is
configured, instead of raising the exception.  This is because exception views
are called by the exception view :term:`tween` as described in
:ref:`exception_views` when any view raises an exception.

We can cause the subrequest to be run through the tween stack by passing
``use_tweens=True`` to the call to
:meth:`~pyramid.request.Request.invoke_subrequest`, like this:

.. code-block:: python
   :linenos:
   :emphasize-lines: 7

   from wsgiref.simple_server import make_server
   from pyramid.config import Configurator
   from pyramid.request import Request

   def view_one(request):
       subreq = Request.blank('/view_two')
       response = request.invoke_subrequest(subreq, use_tweens=True)
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

In the above case, the call to ``request.invoke_subrequest(subreq)`` will not
raise an exception.  Instead, it will retrieve a "500" response from the
attempted invocation of ``view_two``, because the tween which invokes an
exception view to generate a response is run, and therefore ``excview`` is
executed.

This is one of the major differences between specifying the ``use_tweens=True``
and ``use_tweens=False`` arguments to
:meth:`~pyramid.request.Request.invoke_subrequest`.  ``use_tweens=True`` may
also imply invoking a transaction commit or abort for the logic executed in the
subrequest if you've got ``pyramid_tm`` in the tween list, injecting debug HTML
if you've got ``pyramid_debugtoolbar`` in the tween list, and other
tween-related side effects as defined by your particular tween list.

The :meth:`~pyramid.request.Request.invoke_subrequest` function also
unconditionally does the following:

- It manages the threadlocal stack so that
  :func:`~pyramid.threadlocal.get_current_request` and
  :func:`~pyramid.threadlocal.get_current_registry` work during a request (they
  will return the subrequest instead of the original request).

- It adds a ``registry`` attribute and an ``invoke_subrequest`` attribute (a
  callable) to the request object to which it is handed.

- It sets request extensions (such as those added via
  :meth:`~pyramid.config.Configurator.add_request_method` or
  :meth:`~pyramid.config.Configurator.set_request_property`) on the subrequest
  object passed as ``request``.

- It causes a :class:`~pyramid.events.NewRequest` event to be sent at the
  beginning of request processing.

- It causes a :class:`~pyramid.events.ContextFound` event to be sent when a
  context resource is found.

- It ensures that the user implied by the request passed in has the necessary
  authorization to invoke the view callable before calling it.

- It calls any :term:`response callback` functions defined within the
  subrequest's lifetime if a response is obtained from the Pyramid application.

- It causes a :class:`~pyramid.events.NewResponse` event to be sent if a
  response is obtained.

- It calls any :term:`finished callback` functions defined within the
  subrequest's lifetime.

The invocation of a subrequest has more or less exactly the same effect as the
invocation of a request received by the :app:`Pyramid` router from a web client
when ``use_tweens=True``.  When ``use_tweens=False``, the tweens are skipped
but all the other steps take place.

It's a poor idea to use the original ``request`` object as an argument to
:meth:`~pyramid.request.Request.invoke_subrequest`.  You should construct a new
request instead as demonstrated in the above example, using
:meth:`pyramid.request.Request.blank`.  Once you've constructed a request
object, you'll need to massage it to match the view callable that you'd like to
be executed during the subrequest.  This can be done by adjusting the
subrequest's URL, its headers, its request method, and other attributes.  The
documentation for :class:`pyramid.request.Request` exposes the methods you
should call and attributes you should set on the request that you create, then
massage it into something that will actually match the view you'd like to call
via a subrequest.

We've demonstrated use of a subrequest from within a view callable, but you can
use the :meth:`~pyramid.request.Request.invoke_subrequest` API from within a
tween or an event handler as well.  Even though you can do it, it's usually a
poor idea to invoke :meth:`~pyramid.request.Request.invoke_subrequest` from
within a tween, because tweens already, by definition, have access to a
function that will cause a subrequest (they are passed a ``handle`` function).
It's fine to invoke :meth:`~pyramid.request.Request.invoke_subrequest` from
within an event handler, however.


.. index::
   pair: subrequest; exception view

Invoking an Exception View
--------------------------

.. versionadded:: 1.7

:app:`Pyramid` apps may define :term:`exception views <exception view>` which
can handle any raised exceptions that escape from your code while processing
a request. By default an unhandled exception will be caught by the ``EXCVIEW``
:term:`tween`, which will then lookup an exception view that can handle the
exception type, generating an appropriate error response.

In :app:`Pyramid` 1.7 the :meth:`pyramid.request.Request.invoke_exception_view`
was introduced, allowing a user to invoke an exception view while manually
handling an exception. This can be useful in a few different circumstances:

- Manually handling an exception losing the current call stack or flow.

- Handling exceptions outside of the context of the ``EXCVIEW`` tween. The
  tween only covers certain parts of the request processing pipeline (See
  :ref:`router_chapter`). There are also some corner cases where an exception
  can be raised that will still bubble up to middleware, and possibly to the
  web server in which case a generic ``500 Internal Server Error`` will be
  returned to the client.

Below is an example usage of
:meth:`pyramid.request.Request.invoke_exception_view`:

.. code-block:: python
   :linenos:

   def foo(request):
       try:
           some_func_that_errors()
           return response
       except Exception:
           response = request.invoke_exception_view()
           if response is not None:
               return response
           else:
               # there is no exception view for this exception, simply
               # re-raise and let someone else handle it
               raise

Please note that in most cases you do not need to write code like this, and you
may rely on the ``EXCVIEW`` tween to handle this for you.
