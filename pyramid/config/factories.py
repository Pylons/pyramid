from pyramid.config.util import action_method

from pyramid.interfaces import (
    IDefaultRootFactory,
    IRequestFactory,
    IRootFactory,
    ISessionFactory,
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

