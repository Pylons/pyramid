from pyramid.request import Request
from pyramid.interfaces import IRequestFactory

def get_root(app, request=None):
    """ Return a tuple composed of ``(root, closer)`` when provided a
    :term:`router` instance as the ``app`` argument.  The ``root``
    returned is the application root object.  The ``closer`` returned
    is a callable (accepting no arguments) that should be called when
    your scripting application is finished using the root.  If
    ``request`` is not None, it is used as the request passed to the
    :app:`Pyramid` application root factory.  A request is
    constructed and passed to the root factory if ``request`` is None."""
    registry = app.registry
    if request is None:
        request_factory = registry.queryUtility(
            IRequestFactory, default=Request)
        request = request_factory.blank('/')
        request.registry = registry
    threadlocals = {'registry':registry, 'request':request}
    app.threadlocal_manager.push(threadlocals)
    def closer(request=request): # keep request alive via this function default
        app.threadlocal_manager.pop()
    root = app.root_factory(request)
    return root, closer

