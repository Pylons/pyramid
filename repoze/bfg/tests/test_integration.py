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

def _getRequestInterface(name_or_iface=None):
    from repoze.bfg.request import DEFAULT_REQUEST_FACTORIES
    return DEFAULT_REQUEST_FACTORIES[name_or_iface]['interface']

class WGSIAppPlusBFGViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_it(self):
        import types
        self.assertEqual(wsgiapptest.__is_bfg_view__, True)
        self.failUnless(type(wsgiapptest) is types.FunctionType)
        context = DummyContext()
        request = DummyRequest()
        result = wsgiapptest(context, request)
        self.assertEqual(result, '123')

    def test_scanned(self):
        IRequest = _getRequestInterface()
        from repoze.bfg.interfaces import IView
        from repoze.bfg.zcml import scan
        context = DummyContext()
        from repoze.bfg.tests import test_integration
        scan(context, test_integration)
        actions = context.actions
        self.assertEqual(len(actions), 2)
        action = actions[1]
        self.assertEqual(action['args'],
                         ('registerAdapter',
                          wsgiapptest, (INothing, IRequest), IView, '', None))

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
        import inspect
        from repoze.bfg.interfaces import IPOSTRequest
        from repoze.bfg.interfaces import IView
        import repoze.bfg.tests.grokkedapp as package
        from zope.configuration import config
        from zope.configuration import xmlconfig
        context = config.ConfigurationMachine()
        xmlconfig.registerCommonDirectives(context)
        context.package = package
        xmlconfig.include(context, 'configure.zcml', package)
        actions = context.actions

        post_iface = _getRequestInterface(IPOSTRequest)
        request_iface = _getRequestInterface()

        postview = actions[-1]
        self.assertEqual(postview[0][1], None)
        self.assertEqual(postview[0][2], '')
        self.assertEqual(postview[0][3], post_iface)
        self.assertEqual(postview[0][4], IView)
        self.assertEqual(postview[2][1], package.grokked_post)
        self.assertEqual(postview[2][2], (None, post_iface))
        self.assertEqual(postview[2][3], IView)
        
        klassview = actions[-2]
        self.assertEqual(klassview[0][1], None)
        self.assertEqual(klassview[0][2], 'grokked_klass')
        self.assertEqual(klassview[0][3], request_iface)
        self.assertEqual(klassview[0][4], IView)
        self.assertEqual(klassview[2][1], package.grokked_klass)
        self.assertEqual(klassview[2][2], (None, request_iface))
        self.assertEqual(klassview[2][3], IView)
        self.failUnless(inspect.isfunction(package.grokked_klass))
        self.assertEqual(package.grokked_klass(None, None), None)

        funcview = actions[-3]
        self.assertEqual(funcview[0][1], None)
        self.assertEqual(funcview[0][2], '')
        self.assertEqual(funcview[0][3], request_iface)
        self.assertEqual(funcview[0][4], IView)
        self.assertEqual(funcview[2][1], package.grokked)
        self.assertEqual(funcview[2][2], (None, request_iface))
        self.assertEqual(funcview[2][3], IView)

class DummyContext:
    pass

class DummyRequest:
    subpath = ('__init__.py',)
    traversed = None
    environ = {'REQUEST_METHOD':'GET', 'wsgi.version':(1,0)}
    def get_response(self, application):
        return application(None, None)

class DummyContext:
    def __init__(self):
        self.actions = []
        self.info = None

    def action(self, discriminator, callable, args):
        self.actions.append(
            {'discriminator':discriminator,
             'callable':callable,
             'args':args}
            )
