import unittest
import transaction
from pyramid import testing

def _initTestingDB():
    from sqlalchemy import create_engine
    from tutorial.models import (
        DBSession,
        Page,
        Base
        )
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    with transaction.manager:
        model = Page('FrontPage', 'This is the front page')
        DBSession.add(model)
    return DBSession

def _registerRoutes(config):
    config.add_route('view_page', '{pagename}')
    config.add_route('edit_page', '{pagename}/edit_page')
    config.add_route('add_page', 'add_page/{pagename}')


class PageModelTests(unittest.TestCase):

    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        self.session.remove()

    def _getTargetClass(self):
        from tutorial.models import Page
        return Page

    def _makeOne(self, name='SomeName', data='some data'):
        return self._getTargetClass()(name, data)

    def test_constructor(self):
        instance = self._makeOne()
        self.assertEqual(instance.name, 'SomeName')
        self.assertEqual(instance.data, 'some data')

class ViewWikiTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, request):
        from tutorial.views import view_wiki
        return view_wiki(request)

    def test_it(self):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        response = self._callFUT(request)
        self.assertEqual(response.location, 'http://example.com/FrontPage')

class ViewPageTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def _callFUT(self, request):
        from tutorial.views import view_page
        return view_page(request)

    def test_it(self):
        from tutorial.models import Page
        request = testing.DummyRequest()
        request.matchdict['pagename'] = 'IDoExist'
        page = Page('IDoExist', 'Hello CruelWorld IDoExist')
        self.session.add(page)
        _registerRoutes(self.config)
        info = self._callFUT(request)
        self.assertEqual(info['page'], page)
        self.assertEqual(
            info['content'],
            '<div class="document">\n'
            '<p>Hello <a href="http://example.com/add_page/CruelWorld">'
            'CruelWorld</a> '
            '<a href="http://example.com/IDoExist">'
            'IDoExist</a>'
            '</p>\n</div>\n')
        self.assertEqual(info['edit_url'],
            'http://example.com/IDoExist/edit_page')

class AddPageTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def _callFUT(self, request):
        from tutorial.views import add_page
        return add_page(request)

    def test_it_notsubmitted(self):
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        request.matchdict = {'pagename':'AnotherPage'}
        info = self._callFUT(request)
        self.assertEqual(info['page'].data,'')
        self.assertEqual(info['save_url'],
                         'http://example.com/add_page/AnotherPage')

    def test_it_submitted(self):
        from tutorial.models import Page
        _registerRoutes(self.config)
        request = testing.DummyRequest({'form.submitted':True,
                                        'body':'Hello yo!'})
        request.matchdict = {'pagename':'AnotherPage'}
        self._callFUT(request)
        page = self.session.query(Page).filter_by(name='AnotherPage').one()
        self.assertEqual(page.data, 'Hello yo!')

class EditPageTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def _callFUT(self, request):
        from tutorial.views import edit_page
        return edit_page(request)

    def test_it_notsubmitted(self):
        from tutorial.models import Page
        _registerRoutes(self.config)
        request = testing.DummyRequest()
        request.matchdict = {'pagename':'abc'}
        page = Page('abc', 'hello')
        self.session.add(page)
        info = self._callFUT(request)
        self.assertEqual(info['page'], page)
        self.assertEqual(info['save_url'],
            'http://example.com/abc/edit_page')

    def test_it_submitted(self):
        from tutorial.models import Page
        _registerRoutes(self.config)
        request = testing.DummyRequest({'form.submitted':True,
            'body':'Hello yo!'})
        request.matchdict = {'pagename':'abc'}
        page = Page('abc', 'hello')
        self.session.add(page)
        response = self._callFUT(request)
        self.assertEqual(response.location, 'http://example.com/abc')
        self.assertEqual(page.data, 'Hello yo!')

class FunctionalTests(unittest.TestCase):

    viewer_login = '/login?login=viewer&password=viewer' \
                   '&came_from=FrontPage&form.submitted=Login'
    viewer_wrong_login = '/login?login=viewer&password=incorrect' \
                   '&came_from=FrontPage&form.submitted=Login'
    editor_login = '/login?login=editor&password=editor' \
                   '&came_from=FrontPage&form.submitted=Login'

    def setUp(self):
        from tutorial import main
        settings = { 'sqlalchemy.url': 'sqlite://'}
        app = main({}, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
        _initTestingDB()

    def tearDown(self):
        del self.testapp
        from tutorial.models import DBSession
        DBSession.remove()

    def test_root(self):
        res = self.testapp.get('/', status=302)
        self.assertEqual(res.location, 'http://localhost/FrontPage')

    def test_FrontPage(self):
        res = self.testapp.get('/FrontPage', status=200)
        self.assertTrue('FrontPage' in res.body)

    def test_unexisting_page(self):
        self.testapp.get('/SomePage', status=404)

    def test_successful_log_in(self):
        res = self.testapp.get(self.viewer_login, status=302)
        self.assertEqual(res.location, 'http://localhost/FrontPage')

    def test_failed_log_in(self):
        res = self.testapp.get(self.viewer_wrong_login, status=200)
        self.assertTrue('login' in res.body)

    def test_logout_link_present_when_logged_in(self):
        self.testapp.get(self.viewer_login, status=302)
        res = self.testapp.get('/FrontPage', status=200)
        self.assertTrue('Logout' in res.body)

    def test_logout_link_not_present_after_logged_out(self):
        self.testapp.get(self.viewer_login, status=302)
        self.testapp.get('/FrontPage', status=200)
        res = self.testapp.get('/logout', status=302)
        self.assertTrue('Logout' not in res.body)

    def test_anonymous_user_cannot_edit(self):
        res = self.testapp.get('/FrontPage/edit_page', status=200)
        self.assertTrue('Login' in res.body)

    def test_anonymous_user_cannot_add(self):
        res = self.testapp.get('/add_page/NewPage', status=200)
        self.assertTrue('Login' in res.body)

    def test_viewer_user_cannot_edit(self):
        self.testapp.get(self.viewer_login, status=302)
        res = self.testapp.get('/FrontPage/edit_page', status=200)
        self.assertTrue('Login' in res.body)

    def test_viewer_user_cannot_add(self):
        self.testapp.get(self.viewer_login, status=302)
        res = self.testapp.get('/add_page/NewPage', status=200)
        self.assertTrue('Login' in res.body)

    def test_editors_member_user_can_edit(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/FrontPage/edit_page', status=200)
        self.assertTrue('Editing' in res.body)

    def test_editors_member_user_can_add(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/add_page/NewPage', status=200)
        self.assertTrue('Editing' in res.body)

    def test_editors_member_user_can_view(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/FrontPage', status=200)
        self.assertTrue('FrontPage' in res.body)

class Test_populate(unittest.TestCase):
    def setUp(self):
        from tutorial.models import DBSession
        DBSession.remove()

    def tearDown(self):
        from tutorial.models import DBSession
        DBSession.remove()

    def _callFUT(self, settings):
        from tutorial.scripts.populate import main
        main(['foo', 'development.ini'], settings)

    def test_it(self):
        self._callFUT({'sqlalchemy.url':'sqlite://'})
        from tutorial.models import DBSession, Page
        self.assertEqual(DBSession.query(Page).one().data,
            'This is the front page')

