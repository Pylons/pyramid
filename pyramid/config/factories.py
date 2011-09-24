from pyramid.config.util import action_method

from pyramid.interfaces import IDefaultRootFactory
from pyramid.interfaces import IRequestFactory
from pyramid.interfaces import IRootFactory
from pyramid.interfaces import ISessionFactory

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
        self.action(IRootFactory, register)

    _set_root_factory = set_root_factory # bw compat

    @action_method
    def set_session_factory(self, session_factory):
        """
        Configure the application with a :term:`session factory`.  If this
        method is called, the ``session_factory`` argument must be a session
        factory callable or a :term:`dotted Python name` to that factory.

        .. note::

           Using the ``session_factory`` argument to the
           :class:`pyramid.config.Configurator` constructor can be used to
           achieve the same purpose.
        """
        session_factory = self.maybe_dotted(session_factory)
        def register():
            self.registry.registerUtility(session_factory, ISessionFactory)
        self.action(ISessionFactory, register)

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
        self.action(IRequestFactory, register)

