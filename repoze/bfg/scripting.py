_GET_ROOT_ENVIRON = {}

def get_root(router):
    """ Given a :mod:`repoze.bfg` Router application instance as its
    ``router`` argument, this callable returns the traversal root of
    graph as defined by the application's root factory.  It also has
    the effect of pushing a new registry and request on to the
    internal thread local stack managed by BFG so that registry
    lookups work properly.

    .. warning:: This function should never be called from *within* a
       BFG model or view, only from top-level scripts which wish to
       get the root of a graph to do offline processing."""
    registry = router.registry
    threadlocals = {'registry':registry, 'request':None}
    router.threadlocal_manager.push(threadlocals)
    return router.root_factory(_GET_ROOT_ENVIRON)

