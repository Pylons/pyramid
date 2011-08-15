import unittest

from pyramid import testing

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

    def test_it(self):
        root = {}
        self._callFUT(root)
        self.assertEqual(root['app_root']['FrontPage'].data,
                         'This is the front page')

class ViewWikiTests(unittest.TestCase):
    def test_it(self):
        from tutorial.views import view_wiki
        context = testing.DummyResource()
        request = testing.DummyRequest()
        response = view_wiki(context, request)
        self.assertEqual(response.location, 'http://example.com/FrontPage')

class ViewPageTests(unittest.TestCase):
    def _callFUT(self, context, request):
        from tutorial.views import view_page
        return view_page(context, request)

    def test_it(self):
        wiki = testing.DummyResource()
        wiki['IDoExist'] = testing.DummyResource()
        context = testing.DummyResource(data='Hello CruelWorld IDoExist')
        context.__parent__ = wiki
        context.__name__ = 'thepage'
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['page'], context)
        self.assertEqual(
            info['content'],
            '<div class="document">\n'
            '<p>Hello <a href="http://example.com/add_page/CruelWorld">'
            'CruelWorld</a> '
            '<a href="http://example.com/IDoExist/">'
            'IDoExist</a>'
            '</p>\n</div>\n')
        self.assertEqual(info['edit_url'],
                         'http://example.com/thepage/edit_page')


class AddPageTests(unittest.TestCase):
    def _callFUT(self, context, request):
        from tutorial.views import add_page
        return add_page(context, request)

    def test_it_notsubmitted(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.subpath = ['AnotherPage']
        info = self._callFUT(context, request)
        self.assertEqual(info['page'].data,'')
        self.assertEqual(
            info['save_url'],
            request.resource_url(context, 'add_page', 'AnotherPage'))

    def test_it_submitted(self):
        context = testing.DummyResource()
        request = testing.DummyRequest({'form.submitted':True,
                                        'body':'Hello yo!'})
        request.subpath = ['AnotherPage']
        self._callFUT(context, request)
        page = context['AnotherPage']
        self.assertEqual(page.data, 'Hello yo!')
        self.assertEqual(page.__name__, 'AnotherPage')
        self.assertEqual(page.__parent__, context)

class EditPageTests(unittest.TestCase):
    def _callFUT(self, context, request):
        from tutorial.views import edit_page
        return edit_page(context, request)

    def test_it_notsubmitted(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['page'], context)
        self.assertEqual(info['save_url'],
                         request.resource_url(context, 'edit_page'))

    def test_it_submitted(self):
        context = testing.DummyResource()
        request = testing.DummyRequest({'form.submitted':True,
                                        'body':'Hello yo!'})
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')
        self.assertEqual(context.data, 'Hello yo!')

class FunctionalTests(unittest.TestCase):

    viewer_login = '/login?login=viewer&password=viewer' \
                   '&came_from=FrontPage&form.submitted=Login'
    viewer_wrong_login = '/login?login=viewer&password=incorrect' \
                   '&came_from=FrontPage&form.submitted=Login'
    editor_login = '/login?login=editor&password=editor' \
                   '&came_from=FrontPage&form.submitted=Login'

    def setUp(self):
        import tempfile
        import os.path
        from tutorial import main
        self.tmpdir = tempfile.mkdtemp()

        dbpath = os.path.join( self.tmpdir, 'test.db')
        uri = 'file://' + dbpath
        settings = { 'zodbconn.uri' : uri ,
                     'pyramid.includes': ['pyramid_zodbconn', 'pyramid_tm'] }

        app = main({}, **settings)
        self.db = app.registry.zodb_database
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        import shutil
        self.db.close()
        shutil.rmtree( self.tmpdir )

    def test_root(self):
        res = self.testapp.get('/', status=302)
        self.assertEqual(res.location, 'http://localhost/FrontPage')

    def test_FrontPage(self):
        res = self.testapp.get('/FrontPage', status=200)
        self.assertTrue('FrontPage' in res.body)

    def test_unexisting_page(self):
        res = self.testapp.get('/SomePage', status=404)
        self.assertTrue('Not Found' in res.body)

    def test_successful_log_in(self):
        res = self.testapp.get( self.viewer_login, status=302)
        self.assertEqual(res.location, 'http://localhost/FrontPage')

    def test_failed_log_in(self):
        res = self.testapp.get( self.viewer_wrong_login, status=200)
        self.assertTrue('login' in res.body)

    def test_logout_link_present_when_logged_in(self):
        res = self.testapp.get( self.viewer_login, status=302)
        res = self.testapp.get('/FrontPage', status=200)
        self.assertTrue('Logout' in res.body)

    def test_logout_link_not_present_after_logged_out(self):
        res = self.testapp.get( self.viewer_login, status=302)
        res = self.testapp.get('/FrontPage', status=200)
        res = self.testapp.get('/logout', status=302)
        self.assertTrue('Logout' not in res.body)

    def test_anonymous_user_cannot_edit(self):
        res = self.testapp.get('/FrontPage/edit_page', status=200)
        self.assertTrue('Login' in res.body)

    def test_anonymous_user_cannot_add(self):
        res = self.testapp.get('/add_page/NewPage', status=200)
        self.assertTrue('Login' in res.body)

    def test_viewer_user_cannot_edit(self):
        res = self.testapp.get( self.viewer_login, status=302)
        res = self.testapp.get('/FrontPage/edit_page', status=200)
        self.assertTrue('Login' in res.body)

    def test_viewer_user_cannot_add(self):
        res = self.testapp.get( self.viewer_login, status=302)
        res = self.testapp.get('/add_page/NewPage', status=200)
        self.assertTrue('Login' in res.body)

    def test_editors_member_user_can_edit(self):
        res = self.testapp.get( self.editor_login, status=302)
        res = self.testapp.get('/FrontPage/edit_page', status=200)
        self.assertTrue('Editing' in res.body)

    def test_editors_member_user_can_add(self):
        res = self.testapp.get( self.editor_login, status=302)
        res = self.testapp.get('/add_page/NewPage', status=200)
        self.assertTrue('Editing' in res.body)

    def test_editors_member_user_can_view(self):
        res = self.testapp.get( self.editor_login, status=302)
        res = self.testapp.get('/FrontPage', status=200)
        self.assertTrue('FrontPage' in res.body)
