import unittest
import warnings

from pyramid.util import text_

from . import DummyContext, dummyfactory


class RoutesConfiguratorMixinTests(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid.config import Configurator

        config = Configurator(*arg, **kw)
        return config

    def _assertRoute(self, config, name, path, num_predicates=0):
        from pyramid.interfaces import IRoutesMapper

        mapper = config.registry.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        route = routes[0]
        self.assertEqual(len(routes), 1)
        self.assertEqual(route.name, name)
        self.assertEqual(route.path, path)
        self.assertEqual(len(routes[0].predicates), num_predicates)
        return route

    def _makeRequest(self, config):
        request = DummyRequest()
        request.registry = config.registry
        return request

    def test_get_routes_mapper_not_yet_registered(self):
        config = self._makeOne()
        mapper = config.get_routes_mapper()
        self.assertEqual(mapper.routelist, [])

    def test_get_routes_mapper_already_registered(self):
        from pyramid.interfaces import IRoutesMapper

        config = self._makeOne()
        mapper = object()
        config.registry.registerUtility(mapper, IRoutesMapper)
        result = config.get_routes_mapper()
        self.assertEqual(result, mapper)

    def test_add_route_defaults(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path')
        self._assertRoute(config, 'name', 'path')

    def test_add_route_with_route_prefix(self):
        config = self._makeOne(autocommit=True)
        config.route_prefix = 'root'
        config.add_route('name', 'path')
        self._assertRoute(config, 'name', 'root/path')

    def test_add_route_with_inherit_errors(self):
        from pyramid.exceptions import ConfigurationError

        config = self._makeOne(autocommit=True)
        self.assertRaises(
            ConfigurationError,
            config.add_route,
            'name',
            '/',
            inherit_slash=True,
        )

    def test_add_route_with_route_prefix_with_inherit_slash(self):
        config = self._makeOne(autocommit=True)
        config.route_prefix = 'root'
        config.add_route('name', '', inherit_slash=True)
        self._assertRoute(config, 'name', 'root')

    def test_add_route_with_root_slash_with_route_prefix(self):
        config = self._makeOne(autocommit=True)
        config.route_prefix = 'root'
        config.add_route('name', '/')
        self._assertRoute(config, 'name', 'root/')

    def test_add_route_discriminator(self):
        config = self._makeOne()
        config.add_route('name', 'path')
        self.assertEqual(
            config.action_state.actions[-1]['discriminator'], ('route', 'name')
        )

    def test_add_route_with_factory(self):
        config = self._makeOne(autocommit=True)
        factory = object()
        config.add_route('name', 'path', factory=factory)
        route = self._assertRoute(config, 'name', 'path')
        self.assertEqual(route.factory, factory)

    def test_add_route_with_static(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path/{foo}', static=True)
        mapper = config.get_routes_mapper()
        self.assertEqual(len(mapper.get_routes()), 0)
        self.assertEqual(mapper.generate('name', {"foo": "a"}), '/path/a')

    def test_add_route_with_factory_dottedname(self):
        config = self._makeOne(autocommit=True)
        config.add_route(
            'name', 'path', factory='tests.test_config.dummyfactory'
        )
        route = self._assertRoute(config, 'name', 'path')
        self.assertEqual(route.factory, dummyfactory)

    def test_add_route_with_xhr(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path', xhr=True)
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.is_xhr = True
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.is_xhr = False
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_request_method(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path', request_method='GET')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.method = 'GET'
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.method = 'POST'
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_path_info(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path', path_info='/foo')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.upath_info = '/foo'
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.upath_info = '/'
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_path_info_highorder(self):
        config = self._makeOne(autocommit=True)
        config.add_route(
            'name', 'path', path_info=text_(b'/La Pe\xc3\xb1a', 'utf-8')
        )
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.upath_info = text_(b'/La Pe\xc3\xb1a', 'utf-8')
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.upath_info = text_('/')
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_path_info_regex(self):
        config = self._makeOne(autocommit=True)
        config.add_route(
            'name', 'path', path_info=text_(br'/La Pe\w*', 'utf-8')
        )
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.upath_info = text_(b'/La Pe\xc3\xb1a', 'utf-8')
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.upath_info = text_('/')
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_request_param(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path', request_param='abc')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.params = {'abc': '123'}
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.params = {}
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_custom_predicates(self):
        import warnings

        config = self._makeOne(autocommit=True)

        def pred1(context, request):  # pragma: no cover
            pass

        def pred2(context, request):  # pragma: no cover
            pass

        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings('always')
            config.add_route('name', 'path', custom_predicates=(pred1, pred2))
            self.assertEqual(len(w), 1)
        route = self._assertRoute(config, 'name', 'path', 2)
        self.assertEqual(len(route.predicates), 2)

    def test_add_route_with_header(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path', header='Host')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.headers = {'Host': 'example.com'}
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.headers = {}
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_accept(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path', accept='text/xml')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.accept = DummyAccept('text/xml')
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.accept = DummyAccept('text/html')
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_accept_list(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path', accept=['text/xml', 'text/plain'])
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.accept = DummyAccept('text/xml')
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.accept = DummyAccept('text/plain')
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.accept = DummyAccept('text/html')
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_wildcard_accept_raises(self):
        config = self._makeOne(autocommit=True)
        self.assertRaises(
            ValueError,
            lambda: config.add_route('name', 'path', accept='text/*'),
        )

    def test_add_route_no_pattern_with_path(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', path='path')
        self._assertRoute(config, 'name', 'path')

    def test_add_route_no_path_no_pattern(self):
        from pyramid.exceptions import ConfigurationError

        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.add_route, 'name')

    def test_add_route_with_pregenerator(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'pattern', pregenerator='123')
        route = self._assertRoute(config, 'name', 'pattern')
        self.assertEqual(route.pregenerator, '123')

    def test_add_route_no_view_with_view_attr(self):
        config = self._makeOne(autocommit=True)
        from pyramid.exceptions import ConfigurationError

        try:
            config.add_route('name', '/pattern', view_attr='abc')
        except ConfigurationError:
            pass
        else:  # pragma: no cover
            raise AssertionError

    def test_add_route_no_view_with_view_context(self):
        config = self._makeOne(autocommit=True)
        from pyramid.exceptions import ConfigurationError

        try:
            config.add_route('name', '/pattern', view_context=DummyContext)
        except ConfigurationError:
            pass
        else:  # pragma: no cover
            raise AssertionError

    def test_add_route_no_view_with_view_permission(self):
        config = self._makeOne(autocommit=True)
        from pyramid.exceptions import ConfigurationError

        try:
            config.add_route('name', '/pattern', view_permission='edit')
        except ConfigurationError:
            pass
        else:  # pragma: no cover
            raise AssertionError

    def test_add_route_no_view_with_view_renderer(self):
        config = self._makeOne(autocommit=True)
        from pyramid.exceptions import ConfigurationError

        try:
            config.add_route('name', '/pattern', view_renderer='json')
        except ConfigurationError:
            pass
        else:  # pragma: no cover
            raise AssertionError

    def test_add_route_effective_principals_deprecated(self):
        config = self._makeOne(autocommit=True)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always', DeprecationWarning)
            config.add_route('foo', '/bar', effective_principals=['any'])
            self.assertIn(
                'deprecated effective_principals', str(w[-1].message)
            )


class DummyRequest:
    subpath = ()
    matchdict = None

    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ
        self.params = {}
        self.cookies = {}


class DummyAccept(object):
    def __init__(self, *matches, **kw):
        self.matches = list(matches)
        self.contains = kw.pop('contains', False)

    def acceptable_offers(self, offers):
        results = []
        for match in self.matches:
            if match in offers:
                results.append((match, 1.0))
        return results
