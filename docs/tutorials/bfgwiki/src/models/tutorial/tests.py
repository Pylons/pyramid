import unittest

from repoze.bfg import testing

class PageModelTests(unittest.TestCase):

    def _getTargetClass(self):
        from tutorial.models import Page
        return Page

    def _makeOne(self, data=u'some data'):
        return self._getTargetClass()(data=data)

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.data, u'some data')
        
class WikiModelTests(unittest.TestCase):

    def _getTargetClass(self):
        from tutorial.models import Wiki
        return Wiki

    def _makeOne(self):
        return self._getTargetClass()()

    def test_it(self):
        wiki = self._makeOne()
        self.assertEqual(wiki.__parent__, None)
        self.assertEqual(wiki.__name__, None)

class AppmakerTests(unittest.TestCase):

    def _callFUT(self, zodb_root):
        from tutorial.models import appmaker
        return appmaker(zodb_root)

    def test_no_app_root(self):
        root = {}
        self._callFUT(root)
        self.assertEqual(root['app_root']['FrontPage'].data,
                         'This is the front page')

    def test_w_app_root(self):
        app_root = object()
        root = {'app_root': app_root}
        self._callFUT(root)
        self.failUnless(root['app_root'] is app_root)

class ViewTests(unittest.TestCase):

    """ These tests are unit tests for the view.  They test the
    functionality of *only* the view.  They register and use dummy
    implementations of repoze.bfg functionality to allow you to avoid
    testing 'too much'"""

    def setUp(self):
        """ cleanUp() is required to clear out the application registry
        between tests (done in setUp for good measure too)
        """
        testing.cleanUp()
        
    def tearDown(self):
        """ cleanUp() is required to clear out the application registry
        between tests
        """
        testing.cleanUp()

    def test_my_view(self):
        from tutorial.views import my_view
        context = testing.DummyModel()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/mytemplate.pt')
        response = my_view(context, request)
        renderer.assert_(project='tutorial')
