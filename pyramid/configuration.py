from pyramid.config import Configurator as BaseConfigurator
from pyramid.exceptions import ConfigurationError # API
from pyramid.config import DEFAULT_RENDERERS
from pyramid.path import caller_package

from zope.deprecation import deprecated

ConfigurationError = ConfigurationError # pyflakes

deprecated(
    'ConfigurationError',
    'pyramid.configuration.ConfigurationError is deprecated as of '
    'Pyramid 1.0.  Use ``pyramid.config.ConfigurationError`` instead.')

class Configurator(BaseConfigurator):
    def __init__(self,
                 registry=None,
                 package=None,
                 settings=None,
                 root_factory=None,
                 authentication_policy=None,
                 authorization_policy=None,
                 renderers=DEFAULT_RENDERERS,
                 debug_logger=None,
                 locale_negotiator=None,
                 request_factory=None,
                 renderer_globals_factory=None,
                 default_permission=None,
                 session_factory=None,
                 autocommit=True,
                 route_prefix=None,
                 ):
        if package is None:
            package = caller_package()
        BaseConfigurator.__init__(
            self,
            registry=registry,
            package=package,
            settings=settings,
            root_factory=root_factory,
            authentication_policy=authentication_policy,
            authorization_policy=authorization_policy,
            renderers=renderers,
            debug_logger=debug_logger,
            locale_negotiator=locale_negotiator,
            request_factory=request_factory,
            renderer_globals_factory=renderer_globals_factory,
            default_permission=default_permission,
            session_factory=session_factory,
            autocommit=autocommit,
            route_prefix=route_prefix,
            )
            
deprecated(
    'Configurator',
    'pyramid.configuration.Configurator is deprecated as of Pyramid 1.0.  Use'
    '``pyramid.config.Configurator`` with ``autocommit=True`` instead.')

