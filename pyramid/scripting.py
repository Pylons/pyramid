from pyramid.config import global_registries
from pyramid.request import Request
from pyramid.interfaces import IRequestFactory
from pyramid.interfaces import IRootFactory
from pyramid.threadlocal import manager as threadlocal_manager
from pyramid.traversal import DefaultRootFactory

def get_root(app, request=None):
    """ Return a tuple composed of ``(root, closer)`` when provided a
    :term:`router` instance as the ``app`` argument.  The ``root``
    returned is the application root object.  The ``closer`` returned
    is a callable (accepting no arguments) that should be called when
    your scripting application is finished using the root.

    If ``request`` is not None, it is used as the request passed to the
    :app:`Pyramid` application root factory. A request is constructed
    using :meth:`pyramid.scripting.make_request` and passed to the root
    factory if ``request`` is None."""
    registry = app.registry
    if request is None:
        request = make_request('/', registry)
    threadlocals = {'registry':registry, 'request':request}
    app.threadlocal_manager.push(threadlocals)
    def closer(request=request): # keep request alive via this function default
        app.threadlocal_manager.pop()
    root = app.root_factory(request)
    return root, closer

def get_root2(request=None, registry=None):
    """ Return a tuple composed of ``(root, closer)``.  The ``root``
    returned is the application's root object.  The ``closer`` returned
    is a callable (accepting no arguments) that should be called when
    your scripting application is finished using the root.

    If ``request`` is None, a default one is constructed using
    :meth:`pyramid.scripting.make_request`. It is used as the request
    passed to the :app:`Pyramid` application root factory.

    If ``registry`` is not supplied, the last registry loaded from
    :attr:`pyramid.config.global_registries` will be used. If you have
    loaded more than one :app:`Pyramid` application in the current
    process, you may not want to use the last registry loaded, thus
    you can search the ``global_registries`` and supply the appropriate
    one based on your own criteria.
    """
    if registry is None:
        registry = getattr(request, 'registry', global_registries.last)
    if request is None:
        request = make_request('/', registry)
    request.registry = registry
    threadlocals = {'registry':registry, 'request':request}
    threadlocal_manager.push(threadlocals)
    def closer(request=request): # keep request alive via this function default
        threadlocal_manager.pop()
    q = registry.queryUtility
    root_factory = registry.queryUtility(IRootFactory,
                                         default=DefaultRootFactory)
    root = root_factory(request)
    return root, closer

def make_request(path, registry=None):
    """ Return a :meth:`pyramid.request.Request` object anchored at a
    given path. The object returned will be generated from the supplied
    registry's :term:`Request Factory` using the
    :meth:`pyramid.interfaces.IRequestFactory.blank` method.

    This request object can be passed to
    :meth:`pyramid.scripting.get_root` to initialize an application in
    preparation for executing a script with a proper environment setup.
    URLs can then be generated with the object, as well as rendering
    templates.

    If ``registry`` is not supplied, the last registry loaded from
    :attr:`pyramid.config.global_registries` will be used. If you have
    loaded more than one :app:`Pyramid` application in the current
    process, you may not want to use the last registry loaded, thus
    you can search the ``global_registries`` and supply the appropriate
    one based on your own criteria.
    """
    if registry is None:
        registry = global_registries.last
    request_factory = registry.queryUtility(IRequestFactory, default=Request)
    request = request_factory.blank(path)
    request.registry = registry
    return request
