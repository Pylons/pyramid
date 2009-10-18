import os
import unittest

from repoze.bfg.wsgi import wsgiapp
from repoze.bfg.view import bfg_view
from repoze.bfg.view import static

from zope.interface import Interface

from repoze.bfg.testing import cleanUp

class INothing(Interface):
    pass

@bfg_view(for_=INothing)
@wsgiapp
def wsgiapptest(environ, start_response):
    """ """
    return '123'

class WGSIAppPlusBFGViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_it(self):
        import types
        self.failUnless(wsgiapptest.__bfg_view_settings__)
        self.failUnless(type(wsgiapptest) is types.FunctionType)
        context = DummyContext()
        request = DummyRequest()
        result = wsgiapptest(context, request)
        self.assertEqual(result, '123')

    def test_scanned(self):
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.zcml import scan
        context = DummyZCMLContext()
        from repoze.bfg.tests import test_integration
        scan(context, test_integration)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        register = action['callable']
        register()
        sm = getSiteManager()
        view = sm.adapters.lookup((INothing, IRequest), IView, name='')
        self.assertEqual(view, wsgiapptest)

here = os.path.dirname(__file__)
staticapp = static(os.path.join(here, 'fixtures'))

class TestStaticApp(unittest.TestCase):
    def test_it(self):
        from webob import Request
        context = DummyContext()
        from StringIO import StringIO
        request = Request({'PATH_INFO':'',
                           'SCRIPT_NAME':'',
                           'SERVER_NAME':'localhost',
                           'SERVER_PORT':'80',
                           'REQUEST_METHOD':'GET',
                           'wsgi.version':(1,0),
                           'wsgi.url_scheme':'http',
                           'wsgi.input':StringIO()})
        request.subpath = ['minimal.pt']
        result = staticapp(context, request)
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(
            result.body,
            open(os.path.join(here, 'fixtures/minimal.pt'), 'r').read())

class TestFixtureApp(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_execute_actions(self):
        import repoze.bfg.tests.fixtureapp as package
        from zope.configuration import config
        from zope.configuration import xmlconfig
        context = config.ConfigurationMachine()
        xmlconfig.registerCommonDirectives(context)
        context.package = package
        xmlconfig.include(context, 'configure.zcml', package)
        context.execute_actions(clear=False)

class TestGrokkedApp(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_it(self):
        from repoze.bfg.view import render_view_to_response
        from zope.interface import directlyProvides
        from repoze.bfg.zcml import zcml_configure
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRequest
        import repoze.bfg.tests.grokkedapp as package
        
        actions = zcml_configure('configure.zcml', package)
        actions.sort()

        num = 23

        action_types = [(actions[x][0][1],
                         actions[x][0][3],
                         actions[x][0][4]) for x in range(len(actions[:num]))]

        for typ in action_types:
            self.assertEqual(typ, (None, IRequest, IView))

        action_names = [actions[x][0][2] for x in range(len(actions[:num]))]
        action_names.sort()

        self.assertEqual(
            action_names, [
                '',
                '',
                'another',
                'another',
                'another_grokked_class',
                'another_grokked_instance',
                'another_oldstyle_grokked_class',
                'another_stacked1',
                'another_stacked2',
                'another_stacked_class1',
                'another_stacked_class2',
                'basemethod',
                'grokked_class',
                'grokked_instance',
                'method1',
                'method2',
                'oldstyle_grokked_class',
                'stacked1',
                'stacked2',
                'stacked_class1',
                'stacked_class2',
                'stacked_method1',
                'stacked_method2',
                ]
            )


        ctx = DummyContext()
        req = DummyRequest()
        directlyProvides(req, IRequest)

        req.method = 'GET'
        result = render_view_to_response(ctx, req, '')
        self.assertEqual(result, 'grokked')

        req.method = 'POST'
        result = render_view_to_response(ctx, req, '')
        self.assertEqual(result, 'grokked_post')

        result= render_view_to_response(ctx, req, 'grokked_class')
        self.assertEqual(result, 'grokked_class')

        result= render_view_to_response(ctx, req, 'grokked_instance')
        self.assertEqual(result, 'grokked_instance')

        result= render_view_to_response(ctx, req, 'oldstyle_grokked_class')
        self.assertEqual(result, 'oldstyle_grokked_class')

        req.method = 'GET'
        result = render_view_to_response(ctx, req, 'another')
        self.assertEqual(result, 'another_grokked')

        req.method = 'POST'
        result = render_view_to_response(ctx, req, 'another')
        self.assertEqual(result, 'another_grokked_post')

        result= render_view_to_response(ctx, req, 'another_grokked_class')
        self.assertEqual(result, 'another_grokked_class')

        result= render_view_to_response(ctx, req, 'another_grokked_instance')
        self.assertEqual(result, 'another_grokked_instance')

        result= render_view_to_response(ctx, req,
                                        'another_oldstyle_grokked_class')
        self.assertEqual(result, 'another_oldstyle_grokked_class')

        result = render_view_to_response(ctx, req, 'stacked1')
        self.assertEqual(result, 'stacked')

        result = render_view_to_response(ctx, req, 'stacked2')
        self.assertEqual(result, 'stacked')

        result = render_view_to_response(ctx, req, 'another_stacked1')
        self.assertEqual(result, 'another_stacked')

        result = render_view_to_response(ctx, req, 'another_stacked2')
        self.assertEqual(result, 'another_stacked')

        result = render_view_to_response(ctx, req, 'stacked_class1')
        self.assertEqual(result, 'stacked_class')

        result = render_view_to_response(ctx, req, 'stacked_class2')
        self.assertEqual(result, 'stacked_class')

        result = render_view_to_response(ctx, req, 'another_stacked_class1')
        self.assertEqual(result, 'another_stacked_class')

        result = render_view_to_response(ctx, req, 'another_stacked_class2')
        self.assertEqual(result, 'another_stacked_class')

        self.assertRaises(TypeError,
                          render_view_to_response, ctx, req, 'basemethod')

        result = render_view_to_response(ctx, req, 'method1')
        self.assertEqual(result, 'method1')

        result = render_view_to_response(ctx, req, 'method2')
        self.assertEqual(result, 'method2')

        result = render_view_to_response(ctx, req, 'stacked_method1')
        self.assertEqual(result, 'stacked_method')

        result = render_view_to_response(ctx, req, 'stacked_method2')
        self.assertEqual(result, 'stacked_method')

class DummyContext(object):
    pass

class DummyRequest:
    subpath = ('__init__.py',)
    traversed = None
    environ = {'REQUEST_METHOD':'GET', 'wsgi.version':(1,0)}
    def get_response(self, application):
        return application(None, None)

class DummyZCMLContext:
    def __init__(self):
        self.actions = []
        self.info = None

    def action(self, discriminator, callable, args):
        self.actions.append(
            {'discriminator':discriminator,
             'callable':callable,
             'args':args}
            )
