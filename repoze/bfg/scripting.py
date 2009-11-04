from repoze.bfg.request import FakeRequest

def get_root(app, request=None):
    """ Return a tuple composed of ``(root, closer)`` when provided a
    ``repoze.bfg.router.Router`` instance as the ``app`` argument.
    The ``root`` returned is the application root object.  The
    ``closer`` returned is a callable (accepting no arguments) that
    should be called when your scripting application is finished using
    the root.  If ``request`` is not None, it is used as the request
    passed to the BFG application root factory.  A faux request is
    constructed and passed to the root factory if ``request`` is None."""
    if request is None:
        request = FakeRequest({})
    registry = app.registry
    threadlocals = {'registry':registry, 'request':request}
    app.threadlocal_manager.push(threadlocals)
    def closer(request=request): # keep request alive via this function default
        app.threadlocal_manager.pop()
    root = app.root_factory(request)
    return root, closer

