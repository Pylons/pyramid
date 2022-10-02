import sys
import unittest

from . import dummy


class TestPViewsCommand(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.scripts.pviews import PViewsCommand

        return PViewsCommand

    def _makeOne(self, registry=None):
        cmd = self._getTargetClass()([])
        cmd.bootstrap = dummy.DummyBootstrap(registry=registry)
        cmd.setup_logging = dummy.dummy_setup_logging()
        cmd.args.config_uri = '/foo/bar/myapp.ini#myapp'

        self._out_calls = []
        cmd.out = self._out

        return cmd

    def _makeRequest(self, url, registry):
        from pyramid.request import Request

        request = Request.blank('/a')
        request.registry = registry
        return request

    def _register_mapper(self, registry, routes):
        from pyramid.interfaces import IRoutesMapper

        mapper = dummy.DummyMapper(*routes)
        registry.registerUtility(mapper, IRoutesMapper)

    def _out(self, msg, file=sys.stdout):
        self._out_calls.append((msg, file))

    def test__find_view_no_match(self):
        from pyramid.registry import Registry

        registry = Registry()
        self._register_mapper(registry, [])
        command = self._makeOne(registry)
        request = self._makeRequest('/a', registry)
        result = command._find_view(request)
        self.assertEqual(result, None)

    def test__find_view_no_match_multiview_registered(self):
        from zope.interface import implementer, providedBy

        from pyramid.interfaces import IMultiView, IRequest, IViewClassifier
        from pyramid.registry import Registry
        from pyramid.traversal import DefaultRootFactory

        registry = Registry()

        @implementer(IMultiView)
        class View1:
            pass

        request = dummy.DummyRequest()
        request.path_info = '/a'
        root = DefaultRootFactory(request)
        root_iface = providedBy(root)
        registry.registerAdapter(
            View1(), (IViewClassifier, IRequest, root_iface), IMultiView
        )
        self._register_mapper(registry, [])
        command = self._makeOne(registry=registry)
        request = self._makeRequest('/x', registry)
        result = command._find_view(request)
        self.assertEqual(result, None)

    def test__find_view_traversal(self):
        from zope.interface import providedBy

        from pyramid.interfaces import IRequest, IView, IViewClassifier
        from pyramid.registry import Registry
        from pyramid.traversal import DefaultRootFactory

        registry = Registry()

        def view1():  # pragma: no cover
            pass

        request = dummy.DummyRequest()
        request.path_info = '/a'
        root = DefaultRootFactory(request)
        root_iface = providedBy(root)
        registry.registerAdapter(
            view1, (IViewClassifier, IRequest, root_iface), IView, name='a'
        )
        self._register_mapper(registry, [])
        command = self._makeOne(registry=registry)
        request = self._makeRequest('/a', registry)
        result = command._find_view(request)
        self.assertEqual(result, view1)

    def test__find_view_traversal_multiview(self):
        from zope.interface import implementer, providedBy

        from pyramid.interfaces import IMultiView, IRequest, IViewClassifier
        from pyramid.registry import Registry
        from pyramid.traversal import DefaultRootFactory

        registry = Registry()

        @implementer(IMultiView)
        class View1:
            pass

        request = dummy.DummyRequest()
        request.path_info = '/a'
        root = DefaultRootFactory(request)
        root_iface = providedBy(root)
        view = View1()
        registry.registerAdapter(
            view, (IViewClassifier, IRequest, root_iface), IMultiView, name='a'
        )
        self._register_mapper(registry, [])
        command = self._makeOne(registry=registry)
        request = self._makeRequest('/a', registry)
        result = command._find_view(request)
        self.assertEqual(result, view)

    def test__find_view_route_no_multiview(self):
        from zope.interface import Interface, implementer

        from pyramid.interfaces import IRouteRequest, IView, IViewClassifier
        from pyramid.registry import Registry

        registry = Registry()

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

        @implementer(IMyRoot)
        class Factory:
            def __init__(self, request):
                pass

        routes = [
            dummy.DummyRoute('a', '/a', factory=Factory, matchdict={}),
            dummy.DummyRoute('b', '/b', factory=Factory),
        ]
        self._register_mapper(registry, routes)
        command = self._makeOne(registry=registry)
        request = self._makeRequest('/a', registry)
        result = command._find_view(request)
        self.assertEqual(result, view)

    def test__find_view_route_multiview_no_view_registered(self):
        from zope.interface import Interface, implementer

        from pyramid.interfaces import IMultiView, IRootFactory, IRouteRequest
        from pyramid.registry import Registry

        registry = Registry()

        def view1():  # pragma: no cover
            pass

        def view2():  # pragma: no cover
            pass

        class IMyRoot(Interface):
            pass

        class IMyRoute1(Interface):
            pass

        class IMyRoute2(Interface):
            pass

        registry.registerUtility(IMyRoute1, IRouteRequest, name='a')
        registry.registerUtility(IMyRoute2, IRouteRequest, name='b')

        @implementer(IMyRoot)
        class Factory:
            def __init__(self, request):
                pass

        registry.registerUtility(Factory, IRootFactory)
        routes = [
            dummy.DummyRoute('a', '/a', matchdict={}),
            dummy.DummyRoute('b', '/a', matchdict={}),
        ]
        self._register_mapper(registry, routes)
        command = self._makeOne(registry=registry)
        request = self._makeRequest('/a', registry)
        result = command._find_view(request)
        self.assertTrue(IMultiView.providedBy(result))

    def test__find_view_route_multiview(self):
        from zope.interface import Interface, implementer

        from pyramid.interfaces import (
            IMultiView,
            IRootFactory,
            IRouteRequest,
            IView,
            IViewClassifier,
        )
        from pyramid.registry import Registry

        registry = Registry()

        def view1():  # pragma: no cover
            pass

        def view2():  # pragma: no cover
            pass

        class IMyRoot(Interface):
            pass

        class IMyRoute1(Interface):
            pass

        class IMyRoute2(Interface):
            pass

        registry.registerAdapter(
            view1, (IViewClassifier, IMyRoute1, IMyRoot), IView, ''
        )
        registry.registerAdapter(
            view2, (IViewClassifier, IMyRoute2, IMyRoot), IView, ''
        )
        registry.registerUtility(IMyRoute1, IRouteRequest, name='a')
        registry.registerUtility(IMyRoute2, IRouteRequest, name='b')

        @implementer(IMyRoot)
        class Factory:
            def __init__(self, request):
                pass

        registry.registerUtility(Factory, IRootFactory)
        routes = [
            dummy.DummyRoute('a', '/a', matchdict={}),
            dummy.DummyRoute('b', '/a', matchdict={}),
        ]
        self._register_mapper(registry, routes)
        command = self._makeOne(registry=registry)
        request = self._makeRequest('/a', registry)
        result = command._find_view(request)
        self.assertTrue(IMultiView.providedBy(result))
        self.assertEqual(len(result.views), 2)
        self.assertTrue((None, view1, None) in result.views)
        self.assertTrue((None, view2, None) in result.views)

    def test__find_multi_routes_all_match(self):
        command = self._makeOne()

        def factory(request):  # pragma: no cover
            pass

        routes = [
            dummy.DummyRoute('a', '/a', factory=factory, matchdict={}),
            dummy.DummyRoute('b', '/a', factory=factory, matchdict={}),
        ]
        mapper = dummy.DummyMapper(*routes)
        request = dummy.DummyRequest()
        request.path_info = '/a'
        result = command._find_multi_routes(mapper, request)
        self.assertEqual(
            result,
            [
                {'match': {}, 'route': routes[0]},
                {'match': {}, 'route': routes[1]},
            ],
        )

    def test__find_multi_routes_some_match(self):
        command = self._makeOne()

        def factory(request):  # pragma: no cover
            pass

        routes = [
            dummy.DummyRoute('a', '/a', factory=factory),
            dummy.DummyRoute('b', '/a', factory=factory, matchdict={}),
        ]
        mapper = dummy.DummyMapper(*routes)
        request = dummy.DummyRequest()
        request.path_info = '/a'
        result = command._find_multi_routes(mapper, request)
        self.assertEqual(result, [{'match': {}, 'route': routes[1]}])

    def test__find_multi_routes_none_match(self):
        command = self._makeOne()

        def factory(request):  # pragma: no cover
            pass

        routes = [
            dummy.DummyRoute('a', '/a', factory=factory),
            dummy.DummyRoute('b', '/a', factory=factory),
        ]
        mapper = dummy.DummyMapper(*routes)
        request = dummy.DummyRequest()
        request.path_info = '/a'
        result = command._find_multi_routes(mapper, request)
        self.assertEqual(result, [])

    def test_views_command_not_found(self):
        from pyramid.registry import Registry

        registry = Registry()
        command = self._makeOne(registry=registry)
        command._find_view = lambda arg1: None
        command.args.config_uri = '/foo/bar/myapp.ini#myapp'
        command.args.url = '/a'
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(self._out_calls[1], ('URL = /a', sys.stdout))
        self.assertEqual(self._out_calls[3], ('    Not found.', sys.stdout))

    def test_views_command_not_found_url_starts_without_slash(self):
        from pyramid.registry import Registry

        registry = Registry()
        command = self._makeOne(registry=registry)
        command._find_view = lambda arg1: None
        command.args.config_uri = '/foo/bar/myapp.ini#myapp'
        command.args.url = 'a'
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(self._out_calls[1], ('URL = /a', sys.stdout))
        self.assertEqual(self._out_calls[3], ('    Not found.', sys.stdout))

    def test_views_command_single_view_traversal(self):
        from pyramid.registry import Registry

        registry = Registry()
        command = self._makeOne(registry=registry)
        view = dummy.DummyView(context='context', view_name='a')
        command._find_view = lambda arg1: view
        command.args.config_uri = '/foo/bar/myapp.ini#myapp'
        command.args.url = '/a'
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(self._out_calls[1], ('URL = /a', sys.stdout))
        self.assertEqual(
            self._out_calls[3], ('    context: context', sys.stdout)
        )
        self.assertEqual(self._out_calls[4], ('    view name: a', sys.stdout))
        self.assertEqual(
            self._out_calls[8],
            ('    tests.test_scripts.dummy.DummyView', sys.stdout),
        )

    def test_views_command_single_view_function_traversal(self):
        from pyramid.registry import Registry

        registry = Registry()
        command = self._makeOne(registry=registry)

        def view():  # pragma: no cover
            pass

        view.__request_attrs__ = {'context': 'context', 'view_name': 'a'}
        command._find_view = lambda arg1: view
        command.args.config_uri = '/foo/bar/myapp.ini#myapp'
        command.args.url = '/a'
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(self._out_calls[1], ('URL = /a', sys.stdout))
        self.assertEqual(
            self._out_calls[3], ('    context: context', sys.stdout)
        )
        self.assertEqual(self._out_calls[4], ('    view name: a', sys.stdout))
        self.assertEqual(
            self._out_calls[8],
            ('    tests.test_scripts.test_pviews.view', sys.stdout),
        )

    def test_views_command_single_view_traversal_with_permission(self):
        from pyramid.registry import Registry

        registry = Registry()
        command = self._makeOne(registry=registry)
        view = dummy.DummyView(context='context', view_name='a')
        view.__permission__ = 'test'
        command._find_view = lambda arg1: view
        command.args.config_uri = '/foo/bar/myapp.ini#myapp'
        command.args.url = '/a'
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(self._out_calls[1], ('URL = /a', sys.stdout))
        self.assertEqual(
            self._out_calls[3], ('    context: context', sys.stdout)
        )
        self.assertEqual(self._out_calls[4], ('    view name: a', sys.stdout))
        self.assertEqual(
            self._out_calls[8],
            ('    tests.test_scripts.dummy.DummyView', sys.stdout),
        )
        self.assertEqual(
            self._out_calls[9], ('    required permission = test', sys.stdout)
        )

    def test_views_command_single_view_traversal_with_predicates(self):
        from pyramid.registry import Registry

        registry = Registry()
        command = self._makeOne(registry=registry)

        def predicate():  # pragma: no cover
            pass

        predicate.text = lambda *arg: "predicate = x"
        view = dummy.DummyView(context='context', view_name='a')
        view.__predicates__ = [predicate]
        command._find_view = lambda arg1: view
        command.args.config_uri = '/foo/bar/myapp.ini#myapp'
        command.args.url = '/a'
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(self._out_calls[1], ('URL = /a', sys.stdout))
        self.assertEqual(
            self._out_calls[3], ('    context: context', sys.stdout)
        )
        self.assertEqual(self._out_calls[4], ('    view name: a', sys.stdout))
        self.assertEqual(
            self._out_calls[8],
            ('    tests.test_scripts.dummy.DummyView', sys.stdout),
        )
        self.assertEqual(
            self._out_calls[9],
            ('    view predicates (predicate = x)', sys.stdout),
        )

    def test_views_command_single_view_route(self):
        from pyramid.registry import Registry

        registry = Registry()
        command = self._makeOne(registry=registry)
        route = dummy.DummyRoute('a', '/a', matchdict={})
        view = dummy.DummyView(
            context='context', view_name='a', matched_route=route, subpath=''
        )
        command._find_view = lambda arg1: view
        command.args.config_uri = '/foo/bar/myapp.ini#myapp'
        command.args.url = '/a'
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(self._out_calls[1], ('URL = /a', sys.stdout))
        self.assertEqual(
            self._out_calls[3], ('    context: context', sys.stdout)
        )
        self.assertEqual(self._out_calls[4], ('    view name: a', sys.stdout))
        self.assertEqual(self._out_calls[6], ('    Route:', sys.stdout))
        self.assertEqual(self._out_calls[8], ('    route name: a', sys.stdout))
        self.assertEqual(
            self._out_calls[9], ('    route pattern: /a', sys.stdout)
        )
        self.assertEqual(
            self._out_calls[10], ('    route path: /a', sys.stdout)
        )
        self.assertEqual(self._out_calls[11], ('    subpath: ', sys.stdout))
        self.assertEqual(
            self._out_calls[15],
            ('        tests.test_scripts.dummy.DummyView', sys.stdout),
        )

    def test_views_command_multi_view_nested(self):
        from pyramid.registry import Registry

        registry = Registry()
        command = self._makeOne(registry=registry)
        view1 = dummy.DummyView(context='context', view_name='a1')
        view1.__name__ = 'view1'
        view1.__view_attr__ = 'call'
        multiview1 = dummy.DummyMultiView(
            view1, context='context', view_name='a1'
        )
        multiview2 = dummy.DummyMultiView(
            multiview1, context='context', view_name='a'
        )
        command._find_view = lambda arg1: multiview2
        command.args.config_uri = '/foo/bar/myapp.ini#myapp'
        command.args.url = '/a'
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(self._out_calls[1], ('URL = /a', sys.stdout))
        self.assertEqual(
            self._out_calls[3], ('    context: context', sys.stdout)
        )
        self.assertEqual(self._out_calls[4], ('    view name: a', sys.stdout))
        self.assertEqual(
            self._out_calls[8],
            ('    tests.test_scripts.dummy.DummyMultiView', sys.stdout),
        )
        self.assertEqual(
            self._out_calls[12],
            ('        tests.test_scripts.dummy.view1.call', sys.stdout),
        )

    def test_views_command_single_view_route_with_route_predicates(self):
        from pyramid.registry import Registry

        registry = Registry()
        command = self._makeOne(registry=registry)

        def predicate():  # pragma: no cover
            pass

        predicate.text = lambda *arg: "predicate = x"
        route = dummy.DummyRoute('a', '/a', matchdict={}, predicate=predicate)
        view = dummy.DummyView(
            context='context', view_name='a', matched_route=route, subpath=''
        )
        command._find_view = lambda arg1: view
        command.args.config_uri = '/foo/bar/myapp.ini#myapp'
        command.args.url = '/a'
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(self._out_calls[1], ('URL = /a', sys.stdout))
        self.assertEqual(
            self._out_calls[3], ('    context: context', sys.stdout)
        )
        self.assertEqual(self._out_calls[4], ('    view name: a', sys.stdout))
        self.assertEqual(self._out_calls[6], ('    Route:', sys.stdout))
        self.assertEqual(self._out_calls[8], ('    route name: a', sys.stdout))
        self.assertEqual(
            self._out_calls[9], ('    route pattern: /a', sys.stdout)
        )
        self.assertEqual(
            self._out_calls[10], ('    route path: /a', sys.stdout)
        )
        self.assertEqual(self._out_calls[11], ('    subpath: ', sys.stdout))
        self.assertEqual(
            self._out_calls[12],
            ('    route predicates (predicate = x)', sys.stdout),
        )
        self.assertEqual(
            self._out_calls[16],
            ('        tests.test_scripts.dummy.DummyView', sys.stdout),
        )

    def test_views_command_multiview(self):
        from pyramid.registry import Registry

        registry = Registry()
        command = self._makeOne(registry=registry)
        view = dummy.DummyView(context='context')
        view.__name__ = 'view'
        view.__view_attr__ = 'call'
        multiview = dummy.DummyMultiView(
            view, context='context', view_name='a'
        )
        command._find_view = lambda arg1: multiview
        command.args.config_uri = '/foo/bar/myapp.ini#myapp'
        command.args.url = '/a'
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(self._out_calls[1], ('URL = /a', sys.stdout))
        self.assertEqual(
            self._out_calls[3], ('    context: context', sys.stdout)
        )
        self.assertEqual(self._out_calls[4], ('    view name: a', sys.stdout))
        self.assertEqual(
            self._out_calls[8],
            ('    tests.test_scripts.dummy.view.call', sys.stdout),
        )

    def test_views_command_multiview_with_permission(self):
        from pyramid.registry import Registry

        registry = Registry()
        command = self._makeOne(registry=registry)
        view = dummy.DummyView(context='context')
        view.__name__ = 'view'
        view.__view_attr__ = 'call'
        view.__permission__ = 'test'
        multiview = dummy.DummyMultiView(
            view, context='context', view_name='a'
        )
        command._find_view = lambda arg1: multiview
        command.args.config_uri = '/foo/bar/myapp.ini#myapp'
        command.args.url = '/a'
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(self._out_calls[1], ('URL = /a', sys.stdout))
        self.assertEqual(
            self._out_calls[3], ('    context: context', sys.stdout)
        )
        self.assertEqual(self._out_calls[4], ('    view name: a', sys.stdout))
        self.assertEqual(
            self._out_calls[8],
            ('    tests.test_scripts.dummy.view.call', sys.stdout),
        )
        self.assertEqual(
            self._out_calls[9], ('    required permission = test', sys.stdout)
        )

    def test_views_command_multiview_with_predicates(self):
        from pyramid.registry import Registry

        registry = Registry()
        command = self._makeOne(registry=registry)

        def predicate():  # pragma: no cover
            pass

        predicate.text = lambda *arg: "predicate = x"
        view = dummy.DummyView(context='context')
        view.__name__ = 'view'
        view.__view_attr__ = 'call'
        view.__predicates__ = [predicate]
        multiview = dummy.DummyMultiView(
            view, context='context', view_name='a'
        )
        command._find_view = lambda arg1: multiview
        command.args.config_uri = '/foo/bar/myapp.ini#myapp'
        command.args.url = '/a'
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(self._out_calls[1], ('URL = /a', sys.stdout))
        self.assertEqual(
            self._out_calls[3], ('    context: context', sys.stdout)
        )
        self.assertEqual(self._out_calls[4], ('    view name: a', sys.stdout))
        self.assertEqual(
            self._out_calls[8],
            ('    tests.test_scripts.dummy.view.call', sys.stdout),
        )
        self.assertEqual(
            self._out_calls[9],
            ('    view predicates (predicate = x)', sys.stdout),
        )


class Test_main(unittest.TestCase):
    def _callFUT(self, argv):
        from pyramid.scripts.pviews import main

        return main(argv, quiet=True)

    def test_it(self):
        result = self._callFUT(['pviews'])
        self.assertEqual(result, 2)
