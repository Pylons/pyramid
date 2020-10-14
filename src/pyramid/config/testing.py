from zope.interface import Interface

from pyramid.config.actions import action_method
from pyramid.interfaces import IRendererFactory, ISecurityPolicy, ITraverser
from pyramid.renderers import RendererHelper
from pyramid.traversal import split_path_info


class TestingConfiguratorMixin:
    # testing API
    def testing_securitypolicy(
        self,
        userid=None,
        identity=None,
        permissive=True,
        remember_result=None,
        forget_result=None,
    ):
        """Unit/integration testing helper.  Registers a faux :term:`security
        policy`.

        This function is most useful when testing code that uses the security
        APIs, such as :meth:`pyramid.request.Request.identity`,
        :attr:`pyramid.request.Request.authenticated_userid`, or
        :meth:`pyramid.request.Request.has_permission`,

        The behavior of the registered :term:`security policy` depends on the
        arguments passed to this method.

        :param userid:  If provided, the policy's ``authenticated_userid``
            method will return this value.  As a result,
            :attr:`pyramid.request.Request.authenticated_userid` will have this
            value as well.
        :type userid:  str
        :param identity:  If provided, the policy's ``identity`` method will
            return this value.  As a result,
            :attr:`pyramid.request.Request.identity`` will have this value.
        :type identity:  object
        :param permissive:  If true, the policy will allow access to any user
            for any permission.  If false, the policy will deny all access.
        :type permissive:  bool
        :param remember_result:  If provided, the policy's ``remember`` method
            will return this value.  Otherwise, ``remember`` will return an
            empty list.
        :type remember_result:  list
        :param forget_result:  If provided, the policy's ``forget`` method will
            return this value.  Otherwise, ``forget`` will return an empty
            list.
        :type forget_result:  list

        .. versionadded:: 1.4
            The ``remember_result`` argument.

        .. versionadded:: 1.4
            The ``forget_result`` argument.

        .. versionchanged:: 2.0
            Removed ``groupids`` argument and add `identity` argument.

        """
        from pyramid.testing import DummySecurityPolicy

        policy = DummySecurityPolicy(
            userid, identity, permissive, remember_result, forget_result
        )
        self.registry.registerUtility(policy, ISecurityPolicy)
        return policy

    def testing_resources(self, resources):
        """Unit/integration testing helper: registers a dictionary of
        :term:`resource` objects that can be resolved via the
        :func:`pyramid.traversal.find_resource` API.

        The :func:`pyramid.traversal.find_resource` API is called with
        a path as one of its arguments.  If the dictionary you
        register when calling this method contains that path as a
        string key (e.g. ``/foo/bar`` or ``foo/bar``), the
        corresponding value will be returned to ``find_resource`` (and
        thus to your code) when
        :func:`pyramid.traversal.find_resource` is called with an
        equivalent path string or tuple.
        """

        class DummyTraverserFactory:
            def __init__(self, context):
                self.context = context

            def __call__(self, request):
                path = request.path_info
                ob = resources[path]
                traversed = split_path_info(path)
                return {
                    'context': ob,
                    'view_name': '',
                    'subpath': (),
                    'traversed': traversed,
                    'virtual_root': ob,
                    'virtual_root_path': (),
                    'root': ob,
                }

        self.registry.registerAdapter(
            DummyTraverserFactory, (Interface,), ITraverser
        )
        return resources

    testing_models = testing_resources  # b/w compat

    @action_method
    def testing_add_subscriber(self, event_iface=None):
        """Unit/integration testing helper: Registers a
        :term:`subscriber` which listens for events of the type
        ``event_iface``.  This method returns a list object which is
        appended to by the subscriber whenever an event is captured.

        When an event is dispatched that matches the value implied by
        the ``event_iface`` argument, that event will be appended to
        the list.  You can then compare the values in the list to
        expected event notifications.  This method is useful when
        testing code that wants to call
        :meth:`pyramid.registry.Registry.notify`,
        or :func:`zope.component.event.dispatch`.

        The default value of ``event_iface`` (``None``) implies a
        subscriber registered for *any* kind of event.
        """
        event_iface = self.maybe_dotted(event_iface)
        L = []

        def subscriber(*event):
            L.extend(event)

        self.add_subscriber(subscriber, event_iface)
        return L

    def testing_add_renderer(self, path, renderer=None):
        """Unit/integration testing helper: register a renderer at
        ``path`` (usually a relative filename ala ``templates/foo.pt``
        or an asset specification) and return the renderer object.
        If the ``renderer`` argument is None, a 'dummy' renderer will
        be used.  This function is useful when testing code that calls
        the :func:`pyramid.renderers.render` function or
        :func:`pyramid.renderers.render_to_response` function or
        any other ``render_*`` or ``get_*`` API of the
        :mod:`pyramid.renderers` module.

        Note that calling this method for with a ``path`` argument
        representing a renderer factory type (e.g. for ``foo.pt``
        usually implies the ``chameleon_zpt`` renderer factory)
        clobbers any existing renderer factory registered for that
        type.

        .. note:: This method is also available under the alias
           ``testing_add_template`` (an older name for it).

        """
        from pyramid.testing import DummyRendererFactory

        helper = RendererHelper(name=path, registry=self.registry)
        factory = self.registry.queryUtility(
            IRendererFactory, name=helper.type
        )
        if not isinstance(factory, DummyRendererFactory):
            factory = DummyRendererFactory(helper.type, factory)
            self.registry.registerUtility(
                factory, IRendererFactory, name=helper.type
            )

        from pyramid.testing import DummyTemplateRenderer

        if renderer is None:
            renderer = DummyTemplateRenderer()
        factory.add(path, renderer)
        return renderer

    testing_add_template = testing_add_renderer
