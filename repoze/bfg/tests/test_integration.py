import os
import unittest

from repoze.bfg.push import pushpage
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
        self.assertEqual(wsgiapptest.__is_bfg_view__, True)
        self.failUnless(type(wsgiapptest) is types.FunctionType)
        context = DummyContext()
        request = DummyRequest()
        result = wsgiapptest(context, request)
        self.assertEqual(result, '123')

    def test_scanned(self):
        from repoze.bfg.interfaces import IRequest
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

@bfg_view(for_=INothing)
@pushpage('fake.pt')
def pushtest(context, request):
    """ """
    return {'a':1}

class PushPagePlusBFGViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_it(self):
        import types
        import os
        from repoze.bfg.testing import registerDummyRenderer
        path = os.path.join(os.path.dirname(__file__), 'fake.pt')
        renderer = registerDummyRenderer(path)
        self.assertEqual(pushtest.__is_bfg_view__, True)
        self.failUnless(type(pushtest) is types.FunctionType)
        context = DummyContext()
        request = DummyRequest()
        result = pushtest(context, request)
        self.assertEqual(result.status, '200 OK')

    def test_scanned(self):
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.zcml import scan
        context = DummyContext()
        from repoze.bfg.tests import test_integration
        scan(context, test_integration)
        actions = context.actions
        self.assertEqual(len(actions), 2)
        action = actions[0]
        self.assertEqual(action['args'],
                         ('registerAdapter',
                          pushtest, (INothing, IRequest), IView, '', None))

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

    def test_registry_actions_can_be_pickled_and_unpickled(self):
        import repoze.bfg.tests.fixtureapp as package
        from zope.configuration import config
        from zope.configuration import xmlconfig
        context = config.ConfigurationMachine()
        xmlconfig.registerCommonDirectives(context)
        context.package = package
        xmlconfig.include(context, 'configure.zcml', package)
        context.execute_actions(clear=False)
        actions = context.actions
        import cPickle
        dumped = cPickle.dumps(actions, -1)
        new = cPickle.loads(dumped)
        self.assertEqual(len(actions), len(new))

class TestGrokkedApp(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_it(self):
        import repoze.bfg.tests.grokkedapp as package
        
        from zope.configuration import config
        from zope.configuration import xmlconfig
        context = config.ConfigurationMachine()
        xmlconfig.registerCommonDirectives(context)
        context.package = package
        xmlconfig.include(context, 'configure.zcml', package)
        actions = context.actions
        self.failUnless(actions)

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
