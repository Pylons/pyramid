class DummyTweens(object):
    def __init__(self, implicit, explicit):
        self._implicit = implicit
        self.explicit = explicit
        self.name_to_alias = {}
    def implicit(self):
        return self._implicit

class Dummy:
    pass

dummy_root = Dummy()

class DummyRegistry(object):
    settings = {}
    def queryUtility(self, iface, default=None, name=''):
        return default

dummy_registry = DummyRegistry()

class DummyShell(object):
    env = {}
    help = ''
    called = False

    def __call__(self, env, help):
        self.env = env
        self.help = help
        self.called = True

class DummyInteractor:
    def __call__(self, banner, local):
        self.banner = banner
        self.local = local

class DummyApp:
    def __init__(self):
        self.registry = dummy_registry

class DummyMapper(object):
    def __init__(self, *routes):
        self.routes = routes

    def get_routes(self, include_static=False):
        return self.routes

class DummyRoute(object):
    def __init__(self, name, pattern, factory=None,
                 matchdict=None, predicate=None):
        self.name = name
        self.path = pattern
        self.pattern = pattern
        self.factory = factory
        self.matchdict = matchdict
        self.predicates = []
        if predicate is not None:
            self.predicates = [predicate]

    def match(self, route):
        return self.matchdict

class DummyRequest:
    application_url = 'http://example.com:5432'
    script_name = ''
    def __init__(self, environ):
        self.environ = environ
        self.matchdict = {}

class DummyView(object):
    def __init__(self, **attrs):
        self.__request_attrs__ = attrs

    def view(context, request): pass

from zope.interface import implementer
from pyramid.interfaces import IMultiView
@implementer(IMultiView)
class DummyMultiView(object):

    def __init__(self, *views, **attrs):
        self.views = [(None, view, None) for view in views]
        self.__request_attrs__ = attrs

class DummyCloser(object):
    def __call__(self):
        self.called = True

class DummyBootstrap(object):
    def __init__(self, app=None, registry=None, request=None, root=None,
                 root_factory=None, closer=None):
        self.app = app or DummyApp()
        if registry is None:
            registry = DummyRegistry()
        self.registry = registry
        if request is None:
            request = DummyRequest({})
        self.request = request
        if root is None:
            root = Dummy()
        self.root = root
        if root_factory is None:
            root_factory = Dummy()
        self.root_factory = root_factory
        if closer is None:
            closer = DummyCloser()
        self.closer = closer

    def __call__(self, *a, **kw):
        self.a = a
        self.kw = kw
        registry = kw.get('registry', self.registry)
        request = kw.get('request', self.request)
        request.registry = registry
        return {
            'app': self.app,
            'registry': registry,
            'request': request,
            'root': self.root,
            'root_factory': self.root_factory,
            'closer': self.closer,
        }


class DummyEntryPoint(object):
    def __init__(self, name, module):
        self.name = name
        self.module = module

    def load(self):
        return self.module


class DummyPkgResources(object):
    def __init__(self, entry_point_values):
        self.entry_points = []

        for name, module in entry_point_values.items():
            self.entry_points.append(DummyEntryPoint(name, module))

    def iter_entry_points(self, name):
        return self.entry_points


class dummy_setup_logging(object):
    def __call__(self, config_uri, global_conf):
        self.config_uri = config_uri
        self.defaults = global_conf


class DummyLoader(object):
    def __init__(self, settings=None, app_settings=None, app=None, server=None):
        if not settings:
            settings = {}
        if not app_settings:
            app_settings = {}
        self.settings = settings
        self.app_settings = app_settings
        self.app = app
        self.server = server
        self.calls = []

    def __call__(self, uri):
        import plaster
        self.uri = plaster.parse_uri(uri)
        return self

    def add_call(self, op, name, defaults):
        self.calls.append({'op': op, 'name': name, 'defaults': defaults})

    def get_settings(self, name=None, defaults=None):
        self.add_call('settings', name, defaults)
        return self.settings.get(name, {})

    def get_wsgi_app(self, name=None, defaults=None):
        self.add_call('app', name, defaults)
        return self.app

    def get_wsgi_app_settings(self, name=None, defaults=None):
        self.add_call('app_settings', name, defaults)
        return self.app_settings

    def get_wsgi_server(self, name=None, defaults=None):
        self.add_call('server', name, defaults)
        return self.server

    def setup_logging(self, defaults):
        self.add_call('logging', None, defaults)
        self.defaults = defaults
