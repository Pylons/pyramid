from zope.interface import Interface

from pyramid.config.util import action_method

from pyramid.interfaces import (
    IDefaultRootFactory,
    INewRequest,
    IRequestFactory,
    IRequestProperties,
    IRootFactory,
    ISessionFactory,
    ITraverser,
    )

from pyramid.traversal import DefaultRootFactory

class FactoriesConfiguratorMixin(object):
    @action_method
    def set_root_factory(self, factory):
        """ Add a :term:`root factory` to the current configuration
        state.  If the ``factory`` argument is ``None`` a default root
        factory will be registered.

        .. note::

           Using the ``root_factory`` argument to the
           :class:`pyramid.config.Configurator` constructor can be used to
           achieve the same purpose.
        """
        factory = self.maybe_dotted(factory)
        if factory is None:
            factory = DefaultRootFactory
        def register():
            self.registry.registerUtility(factory, IRootFactory)
            self.registry.registerUtility(factory, IDefaultRootFactory) # b/c

        intr = self.introspectable('root factories',
                                   None,
                                   self.object_description(factory),
                                   'root factory')
        intr['factory'] = factory
        self.action(IRootFactory, register, introspectables=(intr,))

    _set_root_factory = set_root_factory # bw compat

    @action_method
    def set_session_factory(self, factory):
        """
        Configure the application with a :term:`session factory`.  If this
        method is called, the ``factory`` argument must be a session
        factory callable or a :term:`dotted Python name` to that factory.

        .. note::

           Using the ``session_factory`` argument to the
           :class:`pyramid.config.Configurator` constructor can be used to
           achieve the same purpose.
        """
        factory = self.maybe_dotted(factory)
        def register():
            self.registry.registerUtility(factory, ISessionFactory)
        intr = self.introspectable('session factory', None,
                                   self.object_description(factory),
                                   'session factory')
        intr['factory'] = factory
        self.action(ISessionFactory, register, introspectables=(intr,))

    @action_method
    def set_request_factory(self, factory):
        """ The object passed as ``factory`` should be an object (or a
        :term:`dotted Python name` which refers to an object) which
        will be used by the :app:`Pyramid` router to create all
        request objects.  This factory object must have the same
        methods and attributes as the
        :class:`pyramid.request.Request` class (particularly
        ``__call__``, and ``blank``).

        See :meth:`pyramid.config.Configurator.set_request_property`
        for a less intrusive way to extend the request objects with
        custom properties.

        .. note::

           Using the ``request_factory`` argument to the
           :class:`pyramid.config.Configurator` constructor
           can be used to achieve the same purpose.
        """
        factory = self.maybe_dotted(factory)
        def register():
            self.registry.registerUtility(factory, IRequestFactory)
        intr = self.introspectable('request factory', None,
                                   self.object_description(factory),
                                   'request factory')
        intr['factory'] = factory
        self.action(IRequestFactory, register, introspectables=(intr,))

    @action_method
    def set_request_property(self, callable, name=None, reify=False):
        """ Add a property to the request object.

        ``callable`` can either be a callable that accepts the request
        as its single positional parameter, or it can be a property
        descriptor. It may also be a :term:`dotted Python name` which
        refers to either a callable or a property descriptor.

        If the ``callable`` is a property descriptor a ``ValueError``
        will be raised if ``name`` is ``None`` or ``reify`` is ``True``.

        If ``name`` is None, the name of the property will be computed
        from the name of the ``callable``.

        See :meth:`pyramid.request.Request.set_property` for more
        information on its usage.

        This is the recommended method for extending the request object
        and should be used in favor of providing a custom request
        factory via
        :meth:`pyramid.config.Configurator.set_request_factory`.

        .. versionadded:: 1.3
        """
        callable = self.maybe_dotted(callable)

        if name is None:
            name = callable.__name__

        def register():
            plist = self.registry.queryUtility(IRequestProperties)

            if plist is None:
                plist = []
                self.registry.registerUtility(plist, IRequestProperties)
                self.registry.registerHandler(_set_request_properties,
                                              (INewRequest,))

            plist.append((name, callable, reify))

        intr = self.introspectable('request properties', name,
                                   self.object_description(callable),
                                   'request property')
        intr['callable'] = callable
        intr['reify'] = reify
        self.action(('request properties', name), register,
                    introspectables=(intr,))

    def set_traverser(self, factory, iface=None):
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
           config.set_traverser(MyCustomTraverser)

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

           config.set_traverser(MyCustomTraverser, MyRootClass)

        When more than one traverser is active, the "most specific" traverser
        will be used (the one that matches the class or interface of the
        value returned by the root factory most closely).

        Note that either ``factory`` or ``iface`` can be a :term:`dotted
        Python name` or a Python object.

        See :ref:`changing_the_traverser` for more information.
        """
        iface = self.maybe_dotted(iface)
        factory = self.maybe_dotted(factory)
        def register(iface=iface):
            if iface is None:
                iface = Interface
            self.registry.registerAdapter(factory, (iface,), ITraverser)
        discriminator = ('traverser', iface)
        intr = self.introspectable(
            'traversers', 
            discriminator,
            'traverser for %r' % iface,
            'traverser',
            )
        intr['factory'] = factory
        intr['iface'] = iface
        self.action(('traverser', iface), register, introspectables=(intr,))

def _set_request_properties(event):
    request = event.request
    plist = request.registry.queryUtility(IRequestProperties)
    for prop in plist:
        name, callable, reify = prop
        request.set_property(callable, name=name, reify=reify)
