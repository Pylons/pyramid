.. _threadlocals_chapter:

Thread Locals
=============

When a request is processed, :mod:`repoze.bfg` makes two "thread
local" variables available to the application: a "registry" and a
"request".

A thread local variable is a variable that appears to be a "global"
variable to an application which uses it.  However, unlike a true
global variable, one thread or process serving the application may
receive a different value than another thread or process when that
variable is "thread local".

How is this beneficial?  Well, usually it's decidedly **not**.  Using
a global or a thread local variable in any application usually makes
it a lot harder to understand for a casual reader.  Use of a thread
local or a global is usually just a way to avoid passing some value
around between functions, which is itself usually a very bad idea.

However, for historical reasons, thread local variables are indeed
consulted by various :mod:`repoze.bfg` API functions.  Two API
functions exist for this purpose:
``repoze.bfg.threadlocal.get_current_request`` and
``repoze.bfg.threadlocal.get_current_registry``.  The former returns
the "current" request; the latter returns the "current" registry.
Both ``get_current_*`` functions retrieve an object from a
thread-local stack.  These API functions are documented in
:ref:`threadlocal_module`.

During normal operations, the thread local stack is managed by a
:term:`Router` object.  Therefore, when the system is operating
normally, the very definition of "current" is defined entirely by the
behavior of a repoze.bfg :term:`Router`.  However, during unit or
functional testing, the definition of "current" is defined by the
boundary between calls to the ``repoze.bfg.testing.setUp`` and
``repoze.bfg.testing.tearDown``.  See :ref:`test_setup_and_teardown`
for the definitions of these functions.

Scripts which use :mod:`repoze.bfg` machinery but never actually start
a WSGI server or receive requests via HTTP (such as scripts which use
the :mod:`repoze.bfg.scripting`` API) will never cause any Router code
to be executed.  Such scripts should expect the
``get_current_request`` function to always return ``None``, and should
expect the ``get_current_registry`` function to return exactly the
same :term:`application registry` for every request.

Why You Shouldn't Use These Functions
-------------------------------------

You probably should almost never use the ``get_current_request`` or
``get_current_registry`` functions, except perhaps in tests.  In
particular, it's almost always usually a mistake to use
``get_current_request`` or ``get_current_registry`` in application
code because its usage makes it possible to write code that can be
neither easily tested nor scripted.  Inappropriate usage is defined as
follows:

- ``get_current_request`` should never be called within :term:`view`
  code, or code called by view code.  View code already has access to
  the request (it's passed in).

- ``get_current_request`` should never be called in :term:`model`
  code.  Model code should never require any access to the request; if
  your model code requires access to a request object, you've almost
  certainly factored something wrong, and you should change your code
  rather than using this function.

- The ``get_current_request`` function should never be called because
  it's "easier" or "more elegant" to think about calling it than to
  pass a request through a series of function calls when creating some
  API design.  Your application should instead almost certainly pass
  data derived from the request around rather than relying on being
  able to call this function to obtain the request in places that
  actually have no business knowing about it.  Parameters are *meant*
  to be passed around as function arguments, this is why they exist.
  Don't try to "save typing" or create "nicer APIs" by using this
  function in the place where a request is required; this will only
  lead to sadness later.

- Neither ``get_current_request`` nor ``get_current_registry`` should
  never be called within application-specific forks of third-party
  library code.  The library you've forked almost certainly has
  nothing to do with :mod:`repoze.bfg`, and making it dependent on
  repoze.bfg (rather than making your :mod:`repoze.bfg` application
  depend upon it) means you're forming a dependency in the wrong
  direction.

Use of the ``get_current_request`` function in application code *is*
still useful in very limited circumstances.  As a rule of thumb, usage
of ``get_current_request`` is useful **within code which is meant to
eventually be removed**.  For instance, you may find yourself wanting
to deprecate some API that expects to be passed a request object in
favor of one that does not expect to be passed a request object.  But
you need to keep implementations of the old API working for some
period of time while you deprecate the older API.  So you write a
"facade" implementation of the new API which calls into the code which
implements the older API.  Since the new API does not require the
request, your facade implementation doesn't have local access to the
request when it needs to pass it into the older API implementaton.
After some period of time, the older implementation code is disused
and the hack that uses ``get_current_request`` is removed.  This would
be an appropriate place to use the ``get_current_request`` function.

Use of the ``get_current_registry`` function should be limited to
testing scenarios.  The registry created by
``repoze.bfg.testing.setUp`` when you do not pass one in is available
to you via this API.

