def get_root(app, environ=None):
    """ Return a tuple composed of ``(root, closer)`` when provided a
    ``repoze.bfg.router.Router`` instance as the ``app`` argument.
    The ``root`` returned is the application root object.  The
    ``closer`` returned is a callable (accepting no arguments) that
    should be called when your scripting application is finished using
    the root.  If ``environ`` is not None, it is used as the
    environment passed to the BFG application root factory.  An empty
    environ is constructed and passed to the root factory if
    ``environ`` is None."""
    registry = app.registry
    threadlocals = {'registry':registry, 'request':None}
    app.threadlocal_manager.push(threadlocals)
    if environ is None:
        environ = {}
    def closer(environ=environ): # keep environ alive via this function default
        app.threadlocal_manager.pop()
    root = app.root_factory(environ)
    return root, closer

