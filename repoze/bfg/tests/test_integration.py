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
        actions = zcml_configure('configure.zcml', package)[-10:]
        actions.sort()

        action = actions[0]
        self.assertEqual(action[0][1], None)
        self.assertEqual(action[0][2], '')
        self.assertEqual(action[0][3], IRequest)
        self.assertEqual(action[0][4], IView)
        
        action = actions[1]
        self.assertEqual(action[0][1], None)
        self.assertEqual(action[0][2], '')
        self.assertEqual(action[0][3], IRequest)
        self.assertEqual(action[0][4], IView)

        action = actions[2]
        self.assertEqual(action[0][1], None)
        self.assertEqual(action[0][2], 'another')
        self.assertEqual(action[0][3], IRequest)
        self.assertEqual(action[0][4], IView)

        action = actions[3]
        self.assertEqual(action[0][1], None)
        self.assertEqual(action[0][2], 'another')
        self.assertEqual(action[0][3], IRequest)
        self.assertEqual(action[0][4], IView)

        action = actions[4]
        self.assertEqual(action[0][1], None)
        self.assertEqual(action[0][2], 'another_grokked_class')
        self.assertEqual(action[0][3], IRequest)
        self.assertEqual(action[0][4], IView)

        action = actions[5]
        self.assertEqual(action[0][1], None)
        self.assertEqual(action[0][2], 'another_grokked_instance')
        self.assertEqual(action[0][3], IRequest)
        self.assertEqual(action[0][4], IView)

        action = actions[6]
        self.assertEqual(action[0][1], None)
        self.assertEqual(action[0][2], 'another_oldstyle_grokked_class')
        self.assertEqual(action[0][3], IRequest)
        self.assertEqual(action[0][4], IView)

        action = actions[7]
        self.assertEqual(action[0][1], None)
        self.assertEqual(action[0][2], 'grokked_class')
        self.assertEqual(action[0][3], IRequest)
        self.assertEqual(action[0][4], IView)

        action = actions[8]
        self.assertEqual(action[0][1], None)
        self.assertEqual(action[0][2], 'grokked_instance')
        self.assertEqual(action[0][3], IRequest)
        self.assertEqual(action[0][4], IView)

        action = actions[9]
        self.assertEqual(action[0][1], None)
        self.assertEqual(action[0][2], 'oldstyle_grokked_class')
        self.assertEqual(action[0][3], IRequest)
        self.assertEqual(action[0][4], IView)

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
