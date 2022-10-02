import os
import sys
import unittest

from . import dummy


class DummyIntrospector:
    def __init__(self):
        self.relations = {}
        self.introspectables = {}

    def get(self, name, discrim):
        pass


class TestPRoutesCommand(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.scripts.proutes import PRoutesCommand

        return PRoutesCommand

    def _makeOne(self):
        cmd = self._getTargetClass()([])
        cmd.bootstrap = dummy.DummyBootstrap()
        cmd.get_config_loader = dummy.DummyLoader()
        cmd.args.config_uri = '/foo/bar/myapp.ini#myapp'

        self._out_calls = []
        cmd.out = self._out

        return cmd

    def _makeRegistry(self):
        from pyramid.registry import Registry

        registry = Registry()
        registry.introspector = DummyIntrospector()
        return registry

    def _makeConfig(self, *arg, **kw):
        from pyramid.config import Configurator

        config = Configurator(*arg, **kw)
        return config

    def _out(self, msg, file=sys.stdout):  # pragma: no cover
        self._out_calls.append((msg, file))

    def test_good_args(self):
        command = self._makeOne()
        command.args.config_args = ('a=1',)
        route = dummy.DummyRoute('a', '/a')
        mapper = dummy.DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        registry = self._makeRegistry()
        command.bootstrap = dummy.DummyBootstrap(registry=registry)
        command.run()

        self.assertTrue(
            '<unknown>' in ''.join(msg for msg, file in self._out_calls)
        )

    def test_bad_args(self):
        command = self._makeOne()
        command.args.config_uri = '/foo/bar/myapp.ini#myapp'
        command.args.config_vars = ('a',)
        route = dummy.DummyRoute('a', '/a')
        mapper = dummy.DummyMapper(route)
        command._get_mapper = lambda *arg: mapper

        self.assertRaises(ValueError, command.run)

    def test_no_routes(self):
        command = self._makeOne()
        mapper = dummy.DummyMapper()
        command._get_mapper = lambda *arg: mapper
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(self._out_calls, [])

    def test_no_mapper(self):
        command = self._makeOne()
        command._get_mapper = lambda *arg: None
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(self._out_calls, [])

    def test_single_route_no_route_registered(self):
        command = self._makeOne()
        route = dummy.DummyRoute('a', '/a')
        mapper = dummy.DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        registry = self._makeRegistry()
        command.bootstrap = dummy.DummyBootstrap(registry=registry)

        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        self.assertEqual(
            self._out_calls[-1][0].split(), ['a', '/a', '<unknown>', '*']
        )

    def test_route_with_no_slash_prefix(self):
        command = self._makeOne()
        route = dummy.DummyRoute('a', 'a')
        mapper = dummy.DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        registry = self._makeRegistry()
        command.bootstrap = dummy.DummyBootstrap(registry=registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        self.assertEqual(
            self._out_calls[-1][0].split(), ['a', '/a', '<unknown>', '*']
        )

    def test_single_route_no_views_registered(self):
        from zope.interface import Interface

        from pyramid.interfaces import IRouteRequest

        registry = self._makeRegistry()

        def view():  # pragma: no cover
            pass

        class IMyRoute(Interface):
            pass

        registry.registerUtility(IMyRoute, IRouteRequest, name='a')
        command = self._makeOne()
        route = dummy.DummyRoute('a', '/a')
        mapper = dummy.DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        command.bootstrap = dummy.DummyBootstrap(registry=registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        self.assertEqual(
            self._out_calls[-1][0].split(), ['a', '/a', '<unknown>', '*']
        )

    def test_single_route_one_view_registered(self):
        from zope.interface import Interface

        from pyramid.interfaces import IRouteRequest, IView, IViewClassifier

        registry = self._makeRegistry()

        def view():  # pragma: no cover
            pass

        class IMyRoute(Interface):
            pass

        registry.registerAdapter(
            view, (IViewClassifier, IMyRoute, Interface), IView, ''
        )
        registry.registerUtility(IMyRoute, IRouteRequest, name='a')
        command = self._makeOne()
        route = dummy.DummyRoute('a', '/a')
        mapper = dummy.DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        command.bootstrap = dummy.DummyBootstrap(registry=registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()[:3]
        self.assertEqual(
            compare_to, ['a', '/a', 'tests.test_scripts.test_proutes.view']
        )

    def test_one_route_with_long_name_one_view_registered(self):
        from zope.interface import Interface

        from pyramid.interfaces import IRouteRequest, IView, IViewClassifier

        registry = self._makeRegistry()

        def view():  # pragma: no cover
            pass

        class IMyRoute(Interface):
            pass

        registry.registerAdapter(
            view, (IViewClassifier, IMyRoute, Interface), IView, ''
        )

        registry.registerUtility(
            IMyRoute, IRouteRequest, name='very_long_name_123'
        )

        command = self._makeOne()
        route = dummy.DummyRoute(
            'very_long_name_123', '/and_very_long_pattern_as_well'
        )
        mapper = dummy.DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        command.bootstrap = dummy.DummyBootstrap(registry=registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()[:3]
        self.assertEqual(
            compare_to,
            [
                'very_long_name_123',
                '/and_very_long_pattern_as_well',
                'tests.test_scripts.test_proutes.view',
            ],
        )

    def test_class_view(self):
        from pyramid.renderers import null_renderer as nr

        config = self._makeConfig(autocommit=True)
        config.add_route('foo', '/a/b')
        config.add_view(
            route_name='foo',
            view=dummy.DummyView,
            attr='view',
            renderer=nr,
            request_method='POST',
        )

        command = self._makeOne()
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = [
            'foo',
            '/a/b',
            'tests.test_scripts.dummy.DummyView.view',
            'POST',
        ]
        self.assertEqual(compare_to, expected)

    def test_single_route_one_view_registered_with_factory(self):
        from zope.interface import Interface

        from pyramid.interfaces import IRouteRequest, IView, IViewClassifier

        registry = self._makeRegistry()

        def view():  # pragma: no cover
            pass

        class IMyRoot(Interface):
            pass

        class IMyRoute(Interface):
            pass

        registry.registerAdapter(
            view, (IViewClassifier, IMyRoute, IMyRoot), IView, ''
        )
        registry.registerUtility(IMyRoute, IRouteRequest, name='a')
        command = self._makeOne()

        def factory(request):  # pragma: no cover
            pass

        route = dummy.DummyRoute('a', '/a', factory=factory)
        mapper = dummy.DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        command.bootstrap = dummy.DummyBootstrap(registry=registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        self.assertEqual(
            self._out_calls[-1][0].split()[:3], ['a', '/a', '<unknown>']
        )

    def test_single_route_multiview_registered(self):
        from zope.interface import Interface

        from pyramid.interfaces import (
            IMultiView,
            IRouteRequest,
            IViewClassifier,
        )

        registry = self._makeRegistry()

        def view():  # pragma: no cover
            pass

        class IMyRoute(Interface):
            pass

        multiview1 = dummy.DummyMultiView(
            view, context='context', view_name='a1'
        )

        registry.registerAdapter(
            multiview1, (IViewClassifier, IMyRoute, Interface), IMultiView, ''
        )
        registry.registerUtility(IMyRoute, IRouteRequest, name='a')
        command = self._makeOne()
        route = dummy.DummyRoute('a', '/a')
        mapper = dummy.DummyMapper(route)
        command._get_mapper = lambda *arg: mapper
        command.bootstrap = dummy.DummyBootstrap(registry=registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()[:3]
        view_module = 'tests.test_scripts.dummy'
        view_str = '<tests.test_scripts.dummy.DummyMultiView'
        final = f'{view_module}.{view_str}'

        self.assertEqual(compare_to, ['a', '/a', final])

    def test__get_mapper(self):
        from pyramid.urldispatch import RoutesMapper

        command = self._makeOne()
        registry = self._makeRegistry()

        result = command._get_mapper(registry)
        self.assertEqual(result.__class__, RoutesMapper)

    def test_one_route_all_methods_view_only_post(self):
        from pyramid.renderers import null_renderer as nr

        def view1(context, request):  # pragma: no cover
            return 'view1'

        config = self._makeConfig(autocommit=True)
        config.add_route('foo', '/a/b')
        config.add_view(
            route_name='foo', view=view1, renderer=nr, request_method='POST'
        )

        command = self._makeOne()
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = [
            'foo',
            '/a/b',
            'tests.test_scripts.test_proutes.view1',
            'POST',
        ]
        self.assertEqual(compare_to, expected)

    def test_one_route_only_post_view_all_methods(self):
        from pyramid.renderers import null_renderer as nr

        def view1(context, request):  # pragma: no cover
            return 'view1'

        config = self._makeConfig(autocommit=True)
        config.add_route('foo', '/a/b', request_method='POST')
        config.add_view(route_name='foo', view=view1, renderer=nr)

        command = self._makeOne()
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = [
            'foo',
            '/a/b',
            'tests.test_scripts.test_proutes.view1',
            'POST',
        ]
        self.assertEqual(compare_to, expected)

    def test_one_route_only_post_view_post_and_get(self):
        from pyramid.renderers import null_renderer as nr

        def view1(context, request):  # pragma: no cover
            return 'view1'

        config = self._makeConfig(autocommit=True)
        config.add_route('foo', '/a/b', request_method='POST')
        config.add_view(
            route_name='foo',
            view=view1,
            renderer=nr,
            request_method=('POST', 'GET'),
        )

        command = self._makeOne()
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = [
            'foo',
            '/a/b',
            'tests.test_scripts.test_proutes.view1',
            'POST',
        ]
        self.assertEqual(compare_to, expected)

    def test_route_request_method_mismatch(self):
        from pyramid.renderers import null_renderer as nr

        def view1(context, request):  # pragma: no cover
            return 'view1'

        config = self._makeConfig(autocommit=True)
        config.add_route('foo', '/a/b', request_method='POST')
        config.add_view(
            route_name='foo', view=view1, renderer=nr, request_method='GET'
        )

        command = self._makeOne()
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = [
            'foo',
            '/a/b',
            'tests.test_scripts.test_proutes.view1',
            '<route',
            'mismatch>',
        ]
        self.assertEqual(compare_to, expected)

    def test_route_static_views(self):
        config = self._makeConfig(autocommit=True)
        config.add_static_view('static', 'static', cache_max_age=3600)
        path2 = os.path.normpath('/var/www/static')
        config.add_static_view(name='static2', path=path2)
        config.add_static_view(
            name='pyramid_scaffold',
            path='pyramid:scaffolds/starter/+package+/static',
        )

        command = self._makeOne()
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 5)

        expected = [
            [
                '__static/',
                '/static/*subpath',
                'tests.test_scripts:static/',
                '*',
            ],
            ['__static2/', '/static2/*subpath', path2 + os.sep, '*'],
            [
                '__pyramid_scaffold/',
                '/pyramid_scaffold/*subpath',
                'pyramid:scaffolds/starter/+package+/static/',
                '*',
            ],
        ]

        for index, (line, file) in enumerate(self._out_calls[2:]):
            data = line.split()
            self.assertEqual(data, expected[index])

    def test_route_no_view(self):
        config = self._makeConfig(autocommit=True)
        config.add_route('foo', '/a/b', request_method='POST')

        command = self._makeOne()
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = ['foo', '/a/b', '<unknown>', 'POST']
        self.assertEqual(compare_to, expected)

    def test_route_as_wsgiapp(self):
        from pyramid.wsgi import wsgiapp2

        config1 = self._makeConfig(autocommit=True)

        def view1(context, request):  # pragma: no cover
            return 'view1'

        config1.add_route('foo', '/a/b', request_method='POST')
        config1.add_view(view=view1, route_name='foo')

        config2 = self._makeConfig(autocommit=True)
        config2.add_route('foo', '/a/b', request_method='POST')
        config2.add_view(wsgiapp2(config1.make_wsgi_app()), route_name='foo')

        command = self._makeOne()
        command.bootstrap = dummy.DummyBootstrap(registry=config2.registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = ['foo', '/a/b', '<wsgiapp>', 'POST']
        self.assertEqual(compare_to, expected)

    def test_route_is_get_view_request_method_not_post(self):
        from pyramid.config import not_
        from pyramid.renderers import null_renderer as nr

        def view1(context, request):  # pragma: no cover
            return 'view1'

        config = self._makeConfig(autocommit=True)
        config.add_route('foo', '/a/b', request_method='GET')
        config.add_view(
            route_name='foo',
            view=view1,
            renderer=nr,
            request_method=not_('POST'),
        )

        command = self._makeOne()
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = [
            'foo',
            '/a/b',
            'tests.test_scripts.test_proutes.view1',
            'GET',
        ]
        self.assertEqual(compare_to, expected)

    def test_view_request_method_not_post(self):
        from pyramid.config import not_
        from pyramid.renderers import null_renderer as nr

        def view1(context, request):  # pragma: no cover
            return 'view1'

        config = self._makeConfig(autocommit=True)
        config.add_route('foo', '/a/b')
        config.add_view(
            route_name='foo',
            view=view1,
            renderer=nr,
            request_method=not_('POST'),
        )

        command = self._makeOne()
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = [
            'foo',
            '/a/b',
            'tests.test_scripts.test_proutes.view1',
            '!POST,*',
        ]
        self.assertEqual(compare_to, expected)

    def test_view_glob(self):
        from pyramid.config import not_
        from pyramid.renderers import null_renderer as nr

        def view1(context, request):  # pragma: no cover
            return 'view1'

        def view2(context, request):  # pragma: no cover
            return 'view2'

        config = self._makeConfig(autocommit=True)
        config.add_route('foo', '/a/b')
        config.add_view(
            route_name='foo',
            view=view1,
            renderer=nr,
            request_method=not_('POST'),
        )

        config.add_route('bar', '/b/a')
        config.add_view(
            route_name='bar',
            view=view2,
            renderer=nr,
            request_method=not_('POST'),
        )

        command = self._makeOne()
        command.args.glob = '*foo*'
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = [
            'foo',
            '/a/b',
            'tests.test_scripts.test_proutes.view1',
            '!POST,*',
        ]
        self.assertEqual(compare_to, expected)

    def test_good_format(self):
        from pyramid.config import not_
        from pyramid.renderers import null_renderer as nr

        def view1(context, request):  # pragma: no cover
            return 'view1'

        config = self._makeConfig(autocommit=True)
        config.add_route('foo', '/a/b')
        config.add_view(
            route_name='foo',
            view=view1,
            renderer=nr,
            request_method=not_('POST'),
        )

        command = self._makeOne()
        command.args.glob = '*foo*'
        command.args.format = 'method,name'
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = ['!POST,*', 'foo']

        self.assertEqual(compare_to, expected)
        self.assertEqual(self._out_calls[0][0].split(), ['Method', 'Name'])

    def test_bad_format(self):
        from pyramid.config import not_
        from pyramid.renderers import null_renderer as nr

        def view1(context, request):  # pragma: no cover
            return 'view1'

        config = self._makeConfig(autocommit=True)
        config.add_route('foo', '/a/b')
        config.add_view(
            route_name='foo',
            view=view1,
            renderer=nr,
            request_method=not_('POST'),
        )

        command = self._makeOne()
        command.args.glob = '*foo*'
        command.args.format = 'predicates,name,pattern'
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        expected = (
            "You provided invalid formats ['predicates']. "
            "Available formats are ['name', 'pattern', 'view', 'method']",
            sys.stderr,
        )
        result = command.run()
        self.assertEqual(result, 2)
        self.assertEqual(self._out_calls[0], expected)

    def test_config_format_ini_newlines(self):
        from pyramid.config import not_
        from pyramid.renderers import null_renderer as nr

        def view1(context, request):  # pragma: no cover
            return 'view1'

        config = self._makeConfig(autocommit=True)
        config.add_route('foo', '/a/b')
        config.add_view(
            route_name='foo',
            view=view1,
            renderer=nr,
            request_method=not_('POST'),
        )

        command = self._makeOne()
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        command.get_config_loader = dummy.DummyLoader(
            {'proutes': {'format': 'method\nname'}}
        )

        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = ['!POST,*', 'foo']

        self.assertEqual(compare_to, expected)
        self.assertEqual(self._out_calls[0][0].split(), ['Method', 'Name'])

    def test_config_format_ini_spaces(self):
        from pyramid.config import not_
        from pyramid.renderers import null_renderer as nr

        def view1(context, request):  # pragma: no cover
            return 'view1'

        config = self._makeConfig(autocommit=True)
        config.add_route('foo', '/a/b')
        config.add_view(
            route_name='foo',
            view=view1,
            renderer=nr,
            request_method=not_('POST'),
        )

        command = self._makeOne()
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        command.get_config_loader = dummy.DummyLoader(
            {'proutes': {'format': 'method name'}}
        )

        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = ['!POST,*', 'foo']

        self.assertEqual(compare_to, expected)
        self.assertEqual(self._out_calls[0][0].split(), ['Method', 'Name'])

    def test_config_format_ini_commas(self):
        from pyramid.config import not_
        from pyramid.renderers import null_renderer as nr

        def view1(context, request):  # pragma: no cover
            return 'view1'

        config = self._makeConfig(autocommit=True)
        config.add_route('foo', '/a/b')
        config.add_view(
            route_name='foo',
            view=view1,
            renderer=nr,
            request_method=not_('POST'),
        )

        command = self._makeOne()

        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        command.get_config_loader = dummy.DummyLoader(
            {'proutes': {'format': 'method,name'}}
        )

        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = ['!POST,*', 'foo']

        self.assertEqual(compare_to, expected)
        self.assertEqual(self._out_calls[0][0].split(), ['Method', 'Name'])

    def test_static_routes_included_in_list(self):
        config = self._makeConfig(autocommit=True)
        config.add_route('foo', 'http://example.com/bar.aspx', static=True)

        command = self._makeOne()
        command.bootstrap = dummy.DummyBootstrap(registry=config.registry)
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(self._out_calls), 3)
        compare_to = self._out_calls[-1][0].split()
        expected = ['foo', 'http://example.com/bar.aspx', '<unknown>', '*']
        self.assertEqual(compare_to, expected)


class Test_main(unittest.TestCase):
    def _callFUT(self, argv):
        from pyramid.scripts.proutes import main

        return main(argv, quiet=True)

    def test_it(self):
        result = self._callFUT(['proutes'])
        self.assertEqual(result, 2)
