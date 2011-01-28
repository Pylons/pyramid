.. index::
   single: thread locals
   single: get_current_request
   single: get_current_registry

.. _threadlocals_chapter:

Thread Locals
=============

A :term:`thread local` variable is a variable that appears to be a
"global" variable to an application which uses it.  However, unlike a
true global variable, one thread or process serving the application
may receive a different value than another thread or process when that
variable is "thread local".

When a request is processed, :app:`Pyramid` makes two :term:`thread
local` variables available to the application: a "registry" and a
"request".

Why and How :app:`Pyramid` Uses Thread Local Variables
---------------------------------------------------------

How are thread locals beneficial to :app:`Pyramid` and application
developers who use :app:`Pyramid`?  Well, usually they're decidedly
**not**.  Using a global or a thread local variable in any application
usually makes it a lot harder to understand for a casual reader.  Use
of a thread local or a global is usually just a way to avoid passing
some value around between functions, which is itself usually a very
bad idea, at least if code readability counts as an important concern.

For historical reasons, however, thread local variables are indeed
consulted by various :app:`Pyramid` API functions.  For example,
the implementation of the :mod:`pyramid.security` function named
:func:`~pyramid.security.authenticated_userid` retrieves the thread
local :term:`application registry` as a matter of course to find an
:term:`authentication policy`.  It uses the
:func:`pyramid.threadlocal.get_current_registry` function to
retrieve the application registry, from which it looks up the
authentication policy; it then uses the authentication policy to
retrieve the authenticated user id.  This is how :app:`Pyramid`
allows arbitrary authentication policies to be "plugged in".

When they need to do so, :app:`Pyramid` internals use two API
functions to retrieve the :term:`request` and :term:`application
registry`: :func:`~pyramid.threadlocal.get_current_request` and
:func:`~pyramid.threadlocal.get_current_registry`.  The former
returns the "current" request; the latter returns the "current"
registry.  Both ``get_current_*`` functions retrieve an object from a
thread-local data structure.  These API functions are documented in
:ref:`threadlocal_module`.

These values are thread locals rather than true globals because one
Python process may be handling multiple simultaneous requests or even
multiple :app:`Pyramid` applications.  If they were true globals,
:app:`Pyramid` could not handle multiple simultaneous requests or
allow more than one :app:`Pyramid` application instance to exist in
a single Python process.

Because one :app:`Pyramid` application is permitted to call
*another* :app:`Pyramid` application from its own :term:`view` code
(perhaps as a :term:`WSGI` app with help from the
:func:`pyramid.wsgi.wsgiapp2` decorator), these variables are
managed in a *stack* during normal system operations.  The stack
instance itself is a `threading.local
<http://docs.python.org/library/threading.html#threading.local>`_.

During normal operations, the thread locals stack is managed by a
:term:`Router` object.  At the beginning of a request, the Router
pushes the application's registry and the request on to the stack.  At
the end of a request, the stack is popped.  The topmost request and
registry on the stack are considered "current".  Therefore, when the
system is operating normally, the very definition of "current" is
defined entirely by the behavior of a pyramid :term:`Router`.

However, during unit testing, no Router code is ever invoked, and the
definition of "current" is defined by the boundary between calls to
the :meth:`pyramid.config.Configurator.begin` and
:meth:`pyramid.config.Configurator.end` methods (or between
calls to the :func:`pyramid.testing.setUp` and
:func:`pyramid.testing.tearDown` functions).  These functions push
and pop the threadlocal stack when the system is under test.  See
:ref:`test_setup_and_teardown` for the definitions of these functions.

Scripts which use :app:`Pyramid` machinery but never actually start
a WSGI server or receive requests via HTTP such as scripts which use
the :mod:`pyramid.scripting` API will never cause any Router code
to be executed.  However, the :mod:`pyramid.scripting` APIs also
push some values on to the thread locals stack as a matter of course.
Such scripts should expect the
:func:`~pyramid.threadlocal.get_current_request` function to always
return ``None``, and should expect the
:func:`~pyramid.threadlocal.get_current_registry` function to return
exactly the same :term:`application registry` for every request.

Why You Shouldn't Abuse Thread Locals
-------------------------------------

You probably should almost never use the
:func:`~pyramid.threadlocal.get_current_request` or
:func:`~pyramid.threadlocal.get_current_registry` functions, except
perhaps in tests.  In particular, it's almost always a mistake to use
``get_current_request`` or ``get_current_registry`` in application
code because its usage makes it possible to write code that can be
neither easily tested nor scripted.  Inappropriate usage is defined as
follows:

- ``get_current_request`` should never be called within the body of a
  :term:`view callable`, or within code called by a view callable.
  View callables already have access to the request (it's passed in to
  each as ``request``).

- ``get_current_request`` should never be called in :term:`resource` code.
  If a resource needs access to the request, it should be passed the request
  by a :term:`view callable`.

- ``get_current_request`` function should never be called because it's
  "easier" or "more elegant" to think about calling it than to pass a
  request through a series of function calls when creating some API
  design.  Your application should instead almost certainly pass data
  derived from the request around rather than relying on being able to
  call this function to obtain the request in places that actually
  have no business knowing about it.  Parameters are *meant* to be
  passed around as function arguments, this is why they exist.  Don't
  try to "save typing" or create "nicer APIs" by using this function
  in the place where a request is required; this will only lead to
  sadness later.

- Neither ``get_current_request`` nor ``get_current_registry`` should
  ever be called within application-specific forks of third-party
  library code.  The library you've forked almost certainly has
  nothing to do with :app:`Pyramid`, and making it dependent on
  :app:`Pyramid` (rather than making your :mod:`pyramid`
  application depend upon it) means you're forming a dependency in the
  wrong direction.

Use of the :func:`~pyramid.threadlocal.get_current_request` function
in application code *is* still useful in very limited circumstances.
As a rule of thumb, usage of ``get_current_request`` is useful
**within code which is meant to eventually be removed**.  For
instance, you may find yourself wanting to deprecate some API that
expects to be passed a request object in favor of one that does not
expect to be passed a request object.  But you need to keep
implementations of the old API working for some period of time while
you deprecate the older API.  So you write a "facade" implementation
of the new API which calls into the code which implements the older
API.  Since the new API does not require the request, your facade
implementation doesn't have local access to the request when it needs
to pass it into the older API implementation.  After some period of
time, the older implementation code is disused and the hack that uses
``get_current_request`` is removed.  This would be an appropriate
place to use the ``get_current_request``.

Use of the :func:`~pyramid.threadlocal.get_current_registry`
function should be limited to testing scenarios.  The registry made
current by use of the
:meth:`pyramid.config.Configurator.begin` method during a
test (or via :func:`pyramid.testing.setUp`) when you do not pass
one in is available to you via this API.

