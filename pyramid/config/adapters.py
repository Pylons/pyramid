from zope.interface import Interface

from pyramid.interfaces import (
    IResponse,
    ITraverser,
    IResourceURL,
    )

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

    @action_method
    def add_traverser(self, adapter, iface=None):
        """
        The superdefault :term:`traversal` algorithm that :app:`Pyramid` uses
        is explained in :ref:`traversal_algorithm`.  Though it is rarely
        necessary, this default algorithm can be swapped out selectively for
        a different traversal pattern via configuration.  The section
        entitled :ref:`changing_the_traverser` details how to create a
        traverser class.

        For example, to override the superdefault traverser used by Pyramid,
        you might do something like this:

        .. code-block:: python

           from myapp.traversal import MyCustomTraverser
           config.add_traverser(MyCustomTraverser)

        This would cause the Pyramid superdefault traverser to never be used;
        intead all traversal would be done using your ``MyCustomTraverser``
        class, no matter which object was returned by the :term:`root
        factory` of this application.  Note that we passed no arguments to
        the ``iface`` keyword parameter.  The default value of ``iface``,
        ``None`` represents that the registered traverser should be used when
        no other more specific traverser is available for the object returned
        by the root factory.

        However, more than one traversal algorithm can be active at the same
        time.  The traverser used can depend on the result of the :term:`root
        factory`.  For instance, if your root factory returns more than one
        type of object conditionally, you could claim that an alternate
        traverser adapter should be used agsinst one particular class or
        interface returned by that root factory.  When the root factory
        returned an object that implemented that class or interface, a custom
        traverser would be used.  Otherwise, the default traverser would be
        used.  The ``iface`` argument represents the class of the object that
        the root factory might return or an :term:`interface` that the object
        might implement.

        To use a particular traverser only when the root factory returns a
        particular class:

        .. code-block:: python

           config.add_traverser(MyCustomTraverser, MyRootClass)

        When more than one traverser is active, the "most specific" traverser
        will be used (the one that matches the class or interface of the
        value returned by the root factory most closely).

        Note that either ``adapter`` or ``iface`` can be a :term:`dotted
        Python name` or a Python object.

        See :ref:`changing_the_traverser` for more information.
        """
        iface = self.maybe_dotted(iface)
        adapter= self.maybe_dotted(adapter)
        def register(iface=iface):
            if iface is None:
                iface = Interface
            self.registry.registerAdapter(adapter, (iface,), ITraverser)
        discriminator = ('traverser', iface)
        intr = self.introspectable(
            'traversers', 
            discriminator,
            'traverser for %r' % iface,
            'traverser',
            )
        intr['adapter'] = adapter
        intr['iface'] = iface
        self.action(discriminator, register, introspectables=(intr,))

    @action_method
    def add_resource_url_adapter(self, adapter, resource_iface=None):
        """
        When you add a traverser as described in
        :ref:`changing_the_traverser`, it's convenient to continue to use the
        :meth:`pyramid.request.Request.resource_url` API.  However, since the
        way traversal is done may have been modified, the URLs that
        ``resource_url`` generates by default may be incorrect when resources
        are returned by a custom traverser.

        If you've added a traverser, you can change how
        :meth:`~pyramid.request.Request.resource_url` generates a URL for a
        specific type of resource by calling this method.

        The ``adapter`` argument represents a class that implements the
        :class:`~pyramid.interfaces.IResourceURL` interface.  The class
        constructor should accept two arguments in its constructor (the
        resource and the request) and the resulting instance should provide
        the attributes detailed in that interface (``virtual_path`` and
        ``physical_path``, in particular).

        The ``resource_iface`` argument represents a class or interface that
        the resource should possess for this url adapter to be used when
        :meth:`pyramid.request.Request.resource_url` looks up a resource url
        adapter.  If ``resource_iface`` is not passed, or it is passed as
        ``None``, the url adapter will be used for every type of resource.

        See :ref:`changing_resource_url` for more information.

        .. note::

           This API is new in Pyramid 1.3.
        """
        adapter = self.maybe_dotted(adapter)
        resource_iface = self.maybe_dotted(resource_iface)
        def register(resource_iface=resource_iface):
            if resource_iface is None:
                resource_iface = Interface
            self.registry.registerAdapter(
                adapter, 
                (resource_iface, Interface),
                IResourceURL,
                )
        discriminator = ('resource url adapter', resource_iface)
        intr = self.introspectable(
            'resource url adapters', 
            discriminator,
            'resource url adapter for resource iface %r' % resource_iface,
            'resource url adapter',
            )
        intr['adapter'] = adapter
        intr['resource_iface'] = resource_iface
        self.action(discriminator, register, introspectables=(intr,))

        
