from zope.interface import Interface

from pyramid.interfaces import IResponse

from pyramid.config.util import action_method

class AdaptersConfiguratorMixin(object):
    @action_method
    def add_subscriber(self, subscriber, iface=None):
        """Add an event :term:`subscriber` for the event stream
        implied by the supplied ``iface`` interface.  The
        ``subscriber`` argument represents a callable object (or a
        :term:`dotted Python name` which identifies a callable); it
        will be called with a single object ``event`` whenever
        :app:`Pyramid` emits an :term:`event` associated with the
        ``iface``, which may be an :term:`interface` or a class or a
        :term:`dotted Python name` to a global object representing an
        interface or a class.  Using the default ``iface`` value,
        ``None`` will cause the subscriber to be registered for all
        event types. See :ref:`events_chapter` for more information
        about events and subscribers."""
        dotted = self.maybe_dotted
        subscriber, iface = dotted(subscriber), dotted(iface)
        if iface is None:
            iface = (Interface,)
        if not isinstance(iface, (tuple, list)):
            iface = (iface,)
        def register():
            self.registry.registerHandler(subscriber, iface)
        intr = self.introspectable('subscribers',
                                   id(subscriber),
                                   self.object_description(subscriber),
                                   'subscriber')
        intr['subscriber'] = subscriber
        intr['interfaces'] = iface
        self.action(None, register, introspectables=(intr,))
        return subscriber

    @action_method
    def add_response_adapter(self, adapter, type_or_iface):
        """ When an object of type (or interface) ``type_or_iface`` is
        returned from a view callable, Pyramid will use the adapter
        ``adapter`` to convert it into an object which implements the
        :class:`pyramid.interfaces.IResponse` interface.  If ``adapter`` is
        None, an object returned of type (or interface) ``type_or_iface``
        will itself be used as a response object.

        ``adapter`` and ``type_or_interface`` may be Python objects or
        strings representing dotted names to importable Python global
        objects.

        See :ref:`using_iresponse` for more information."""
        adapter = self.maybe_dotted(adapter)
        type_or_iface = self.maybe_dotted(type_or_iface)
        def register():
            reg = self.registry
            if adapter is None:
                reg.registerSelfAdapter((type_or_iface,), IResponse)
            else:
                reg.registerAdapter(adapter, (type_or_iface,), IResponse)
        discriminator = (IResponse, type_or_iface)
        intr = self.introspectable(
            'response adapters',
            discriminator,
            self.object_description(adapter),
            'response adapter')
        intr['adapter'] = adapter
        intr['type'] = type_or_iface
        self.action(discriminator, register, introspectables=(intr,))

    def _register_response_adapters(self):
        # cope with WebOb response objects that aren't decorated with IResponse
        from webob import Response as WebobResponse
        self.registry.registerSelfAdapter((WebobResponse,), IResponse)
