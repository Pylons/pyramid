import warnings

from pyramid.interfaces import IRendererFactory
from pyramid.interfaces import IRendererGlobalsFactory
from pyramid.interfaces import PHASE1_CONFIG

from pyramid.config.util import action_method

from pyramid import renderers
from pyramid import chameleon_text
from pyramid import chameleon_zpt
from pyramid.mako_templating import renderer_factory as mako_renderer_factory

DEFAULT_RENDERERS = (
    ('.txt', chameleon_text.renderer_factory),
    ('.pt', chameleon_zpt.renderer_factory),
    ('.mak', mako_renderer_factory),
    ('.mako', mako_renderer_factory),
    ('json', renderers.json_renderer_factory),
    ('string', renderers.string_renderer_factory),
    )

class RenderingConfiguratorMixin(object):
    @action_method
    def add_renderer(self, name, factory):
        """
        Add a :app:`Pyramid` :term:`renderer` factory to the
        current configuration state.

        The ``name`` argument is the renderer name.  Use ``None`` to
        represent the default renderer (a renderer which will be used for all
        views unless they name another renderer specifically).

        The ``factory`` argument is Python reference to an
        implementation of a :term:`renderer` factory or a
        :term:`dotted Python name` to same.
        """
        factory = self.maybe_dotted(factory)
        # if name is None or the empty string, we're trying to register
        # a default renderer, but registerUtility is too dumb to accept None
        # as a name
        if not name:
            name = ''
        def register():
            self.registry.registerUtility(factory, IRendererFactory, name=name)
        # we need to register renderers early (in phase 1) because they are
        # used during view configuration (which happens in phase 3)
        self.action((IRendererFactory, name), register, order=PHASE1_CONFIG)

    @action_method
    def set_renderer_globals_factory(self, factory, warn=True):
        """ The object passed as ``factory`` should be an callable (or
        a :term:`dotted Python name` which refers to an callable) that
        will be used by the :app:`Pyramid` rendering machinery as a
        renderers global factory (see :ref:`adding_renderer_globals`).

        The ``factory`` callable must accept a single argument named
        ``system`` (which will be a dictionary) and it must return a
        dictionary.  When an application uses a renderer, the
        factory's return dictionary will be merged into the ``system``
        dictionary, and therefore will be made available to the code
        which uses the renderer.

        .. warning::

           This method is deprecated as of Pyramid 1.1.

        .. note::

           Using the ``renderer_globals_factory`` argument
           to the :class:`pyramid.config.Configurator` constructor
           can be used to achieve the same purpose.
        """
        if warn:
            warnings.warn(
                'Calling the ``set_renderer_globals`` method of a Configurator '
                'is deprecated as of Pyramid 1.1. Use a BeforeRender event '
                'subscriber as documented in the "Hooks" chapter of the '
                'Pyramid narrative documentation instead',
                DeprecationWarning,
                3)

        factory = self.maybe_dotted(factory)
        def register():
            self.registry.registerUtility(factory, IRendererGlobalsFactory)
        self.action(IRendererGlobalsFactory, register)
