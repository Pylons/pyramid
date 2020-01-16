import pytest
import transaction

from tutorial import models


basic_login = dict(login='basic', password='basic')
editor_login = dict(login='editor', password='editor')

@pytest.fixture(scope='session', autouse=True)
def dummy_data(app):
    """
    Add some dummy data to the database.

    Note that this is a session fixture that commits data to the database.
    Think about it similarly to running the ``initialize_db`` script at the
    start of the test suite.

    This data should not conflict with any other data added throughout the
    test suite or there will be issues - so be careful with this pattern!

    """
    tm = transaction.TransactionManager(explicit=True)
    with tm:
        dbsession = models.get_tm_session(app.registry['dbsession_factory'], tm)
        editor = models.User(name='editor', role='editor')
        editor.set_password('editor')
        basic = models.User(name='basic', role='basic')
        basic.set_password('basic')
        page1 = models.Page(name='FrontPage', data='This is the front page')
        page1.creator = editor
        page2 = models.Page(name='BackPage', data='This is the back page')
        page2.creator = basic
        dbsession.add_all([basic, editor, page1, page2])

def test_root(testapp):
    res = testapp.get('/', status=303)
    assert res.location == 'http://example.com/FrontPage'

def test_FrontPage(testapp):
    res = testapp.get('/FrontPage', status=200)
    assert b'FrontPage' in res.body

def test_missing_page(testapp):
    res = testapp.get('/SomePage', status=404)
    assert b'404' in res.body

def test_successful_log_in(testapp):
    params = dict(
        **basic_login,
        csrf_token=testapp.get_csrf_token(),
    )
    res = testapp.post('/login', params, status=303)
    assert res.location == 'http://example.com/'

def test_successful_log_with_next(testapp):
    params = dict(
        **basic_login,
        next='WikiPage',
        csrf_token=testapp.get_csrf_token(),
    )
    res = testapp.post('/login', params, status=303)
    assert res.location == 'http://example.com/WikiPage'

def test_failed_log_in(testapp):
    params = dict(
        login='basic',
        password='incorrect',
        csrf_token=testapp.get_csrf_token(),
    )
    res = testapp.post('/login', params, status=400)
    assert b'login' in res.body

def test_logout_link_present_when_logged_in(testapp):
    testapp.login(basic_login)
    res = testapp.get('/FrontPage', status=200)
    assert b'Logout' in res.body

def test_logout_link_not_present_after_logged_out(testapp):
    testapp.login(basic_login)
    testapp.get('/FrontPage', status=200)
    params = dict(csrf_token=testapp.get_csrf_token())
    res = testapp.post('/logout', params, status=303)
    assert b'Logout' not in res.body

def test_anonymous_user_cannot_edit(testapp):
    res = testapp.get('/FrontPage/edit_page', status=303).follow()
    assert b'Login' in res.body

def test_anonymous_user_cannot_add(testapp):
    res = testapp.get('/add_page/NewPage', status=303).follow()
    assert b'Login' in res.body

def test_basic_user_cannot_edit_front(testapp):
    testapp.login(basic_login)
    res = testapp.get('/FrontPage/edit_page', status=403)
    assert b'403' in res.body

def test_basic_user_can_edit_back(testapp):
    testapp.login(basic_login)
    res = testapp.get('/BackPage/edit_page', status=200)
    assert b'Editing' in res.body

def test_basic_user_can_add(testapp):
    testapp.login(basic_login)
    res = testapp.get('/add_page/NewPage', status=200)
    assert b'Editing' in res.body

def test_editors_member_user_can_edit(testapp):
    testapp.login(editor_login)
    res = testapp.get('/FrontPage/edit_page', status=200)
    assert b'Editing' in res.body

def test_editors_member_user_can_add(testapp):
    testapp.login(editor_login)
    res = testapp.get('/add_page/NewPage', status=200)
    assert b'Editing' in res.body

def test_editors_member_user_can_view(testapp):
    testapp.login(editor_login)
    res = testapp.get('/FrontPage', status=200)
    assert b'FrontPage' in res.body

def test_redirect_to_edit_for_existing_page(testapp):
    testapp.login(editor_login)
    res = testapp.get('/add_page/FrontPage', status=303)
    assert b'FrontPage' in res.body
