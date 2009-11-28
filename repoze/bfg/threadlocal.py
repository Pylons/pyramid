import threading

from repoze.bfg.registry import global_registry

class ThreadLocalManager(threading.local):
    def __init__(self, default=None):
        # http://code.google.com/p/google-app-engine-django/issues/detail?id=119
        # we *must* use a keword argument for ``default`` here instead
        # of a positional argument to work around a bug in the
        # implementation of _threading_local.local in Python, which is
        # used by GAE instead of _thread.local
        self.stack = []
        self.default = default
        
    def push(self, info):
        self.stack.append(info)

    set = push # b/c

    def pop(self):
        if self.stack:
            return self.stack.pop()

    def get(self):
        try:
            return self.stack[-1]
        except IndexError:
            return self.default()

    def clear(self):
        self.stack[:] = []

def defaults():
    return {'request':None, 'registry':global_registry}

manager = ThreadLocalManager(default=defaults)

## **The below function ``get_current*`` functions should be used
## extremely sparingly.

## In particular, it's almost always usually a mistake to use
## ``get_current_request`` because its usage makes it possible to
## write code that can be neither easily tested nor scripted.
## Inappropriate usage is defined as follows:

## - ``get_current_request`` should never be called within
##   :term:`view` code, or code called by view code.  View code
##   already has access to the request (it's passed in).

## - ``get_current_request`` should never be called in :term:`model`
##   code.  Model code should never require any access to the
##   request; if your model code requires access to a request object,
##   you've almost certainly factored something wrong, and you should
##   change your code rather than using this function.

## - The ``get_current_request`` function should never be called
##   because it's 'easier' or 'more elegant' to think about calling
##   it than to pass a request through a series of function calls
##   when creating some API design.  Your application should instead
##   almost certainly pass data derived from the request around
##   rather than relying on being able to call this function to
##   obtain the request in places that actually have no business
##   knowing about it.  Parameters are meant to be passed around as
##   function arguments, not obtained from some pseudo-global.  Don't
##   try to 'save typing' or create 'nicer APIs' by using this
##   function in the place where a request is required; this will
##   only lead to sadness later.

## - Neither ``get_current_request`` nor ``get_current_registry``
##   should never be called within application-specific forks of
##   third-party library code.  The library you've forked almost
##   certainly has nothing to do with repoze.bfg, and making it
##   dependent on repoze.bfg (rather than making your repoze.bfg
##   application depend upon it) means you're forming a dependency in
##   the wrong direction.

## The ``get_current_request`` function *is* still useful in very
## limited circumstances.  As a rule of thumb, usage of
## ``get_current_request`` is useful **within code which is meant to
## eventually be removed**.  For instance, you may find yourself
## wanting to deprecate some API that expects to be passed a request
## object in favor of one that does not expect to be passed a request
## object.  But you need to keep implementations of the old API
## working for some period of time while you deprecate the older API.
## So you write a 'facade' implementation of the new API which calls
## into the code which implements the older API.  Since the new API
## does not require the request, your facade implementation doesn't
## have local access to the request when it needs to pass it into the
## older API implementaton.  After some period of time, the older
## implementation code is disused and the hack that uses
## ``get_current_request`` is removed.  This would be an appropriate
## place to use the ``get_current_request`` function.

## ``get_current_request`` retrieves a request object from a
## thread-local stack that is managed by a :term:`Router` object.
## Therefore the very definition of 'current request' is defined
## entirely by the behavior of a repoze.bfg Router.  Scripts which
## use :mod:`repoze.bfg` machinery but never actually start a WSGI
## server or receive requests via HTTP (such as scripts which use the
## :mod:`repoze.bfg.scripting`` API) will never cause any Router code
## to be executed.  Such scripts should expect this function to
## always return ``None``.

def get_current_request():
    """Return the currently active request or ``None`` if no request
    is currently active.

    This function should be used *extremely sparingly*, usually only
    in unit testing code.  it's almost always usually a mistake to use
    ``get_current_request`` outside a testing context because its
    usage makes it possible to write code that can be neither easily
    tested nor scripted.
    """
    return manager.get()['request']

def get_current_registry(context=None): # context required by getSiteManager API
    """Return the currently active :term:`application registry` or the
    global application registry if no request is currently active.

    This function should be used *extremely sparingly*, usually only
    in unit testing code.  it's almost always usually a mistake to use
    ``get_current_registry`` outside a testing context because its
    usage makes it possible to write code that can be neither easily
    tested nor scripted.
    """
    return manager.get()['registry']

