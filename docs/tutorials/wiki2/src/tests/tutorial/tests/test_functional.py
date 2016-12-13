import transaction
import unittest
import webtest


class FunctionalTests(unittest.TestCase):

    basic_login = (
        '/login?login=basic&password=basic'
        '&next=FrontPage&form.submitted=Login')
    basic_wrong_login = (
        '/login?login=basic&password=incorrect'
        '&next=FrontPage&form.submitted=Login')
    basic_login_no_next = (
        '/login?login=basic&password=basic'
        '&form.submitted=Login')
    editor_login = (
        '/login?login=editor&password=editor'
        '&next=FrontPage&form.submitted=Login')

    @classmethod
    def setUpClass(cls):
        from tutorial.models.meta import Base
        from tutorial.models import (
            User,
            Page,
            get_tm_session,
        )
        from tutorial import main

        settings = {
            'sqlalchemy.url': 'sqlite://',
            'auth.secret': 'seekrit',
        }
        app = main({}, **settings)
        cls.testapp = webtest.TestApp(app)

        session_factory = app.registry['dbsession_factory']
        cls.engine = session_factory.kw['bind']
        Base.metadata.create_all(bind=cls.engine)

        with transaction.manager:
            dbsession = get_tm_session(session_factory, transaction.manager)
            editor = User(name='editor', role='editor')
            editor.set_password('editor')
            basic = User(name='basic', role='basic')
            basic.set_password('basic')
            page1 = Page(name='FrontPage', data='This is the front page')
            page1.creator = editor
            page2 = Page(name='BackPage', data='This is the back page')
            page2.creator = basic
            dbsession.add_all([basic, editor, page1, page2])

    @classmethod
    def tearDownClass(cls):
        from tutorial.models.meta import Base
        Base.metadata.drop_all(bind=cls.engine)

    def test_root(self):
        res = self.testapp.get('/', status=302)
        self.assertEqual(res.location, 'http://localhost/FrontPage')

    def test_FrontPage(self):
        res = self.testapp.get('/FrontPage', status=200)
        self.assertTrue(b'FrontPage' in res.body)

    def test_unexisting_page(self):
        self.testapp.get('/SomePage', status=404)

    def test_successful_log_in(self):
        res = self.testapp.get(self.basic_login, status=302)
        self.assertEqual(res.location, 'http://localhost/FrontPage')

    def test_successful_log_in_no_next(self):
        res = self.testapp.get(self.basic_login_no_next, status=302)
        self.assertEqual(res.location, 'http://localhost/')

    def test_failed_log_in(self):
        res = self.testapp.get(self.basic_wrong_login, status=200)
        self.assertTrue(b'login' in res.body)

    def test_logout_link_present_when_logged_in(self):
        self.testapp.get(self.basic_login, status=302)
        res = self.testapp.get('/FrontPage', status=200)
        self.assertTrue(b'Logout' in res.body)

    def test_logout_link_not_present_after_logged_out(self):
        self.testapp.get(self.basic_login, status=302)
        self.testapp.get('/FrontPage', status=200)
        res = self.testapp.get('/logout', status=302)
        self.assertTrue(b'Logout' not in res.body)

    def test_anonymous_user_cannot_edit(self):
        res = self.testapp.get('/FrontPage/edit_page', status=302).follow()
        self.assertTrue(b'Login' in res.body)

    def test_anonymous_user_cannot_add(self):
        res = self.testapp.get('/add_page/NewPage', status=302).follow()
        self.assertTrue(b'Login' in res.body)

    def test_basic_user_cannot_edit_front(self):
        self.testapp.get(self.basic_login, status=302)
        res = self.testapp.get('/FrontPage/edit_page', status=302).follow()
        self.assertTrue(b'Login' in res.body)

    def test_basic_user_can_edit_back(self):
        self.testapp.get(self.basic_login, status=302)
        res = self.testapp.get('/BackPage/edit_page', status=200)
        self.assertTrue(b'Editing' in res.body)

    def test_basic_user_can_add(self):
        self.testapp.get(self.basic_login, status=302)
        res = self.testapp.get('/add_page/NewPage', status=200)
        self.assertTrue(b'Editing' in res.body)

    def test_editors_member_user_can_edit(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/FrontPage/edit_page', status=200)
        self.assertTrue(b'Editing' in res.body)

    def test_editors_member_user_can_add(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/add_page/NewPage', status=200)
        self.assertTrue(b'Editing' in res.body)

    def test_editors_member_user_can_view(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/FrontPage', status=200)
        self.assertTrue(b'FrontPage' in res.body)

    def test_redirect_to_edit_for_existing_page(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/add_page/FrontPage', status=302)
        self.assertTrue(b'FrontPage' in res.body)
