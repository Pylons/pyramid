viewer_login = (
    '/login?login=viewer&password=viewer'
    '&came_from=FrontPage&form.submitted=Login'
)
viewer_wrong_login = (
    '/login?login=viewer&password=incorrect'
    '&came_from=FrontPage&form.submitted=Login'
)
editor_login = (
    '/login?login=editor&password=editor'
    '&came_from=FrontPage&form.submitted=Login'
)

def test_root(testapp):
    res = testapp.get('/', status=303)
    assert res.location == 'http://example.com/FrontPage'

def test_FrontPage(testapp):
    res = testapp.get('/FrontPage', status=200)
    assert b'FrontPage' in res.body

def test_missing_page(testapp):
    res = testapp.get('/SomePage', status=404)
    assert b'Not Found' in res.body

def test_referrer_is_login(testapp):
    res = testapp.get('/login', status=200)
    assert b'name="came_from" value="/"' in res.body

def test_successful_log_in(testapp):
    res = testapp.get(viewer_login, status=303)
    assert res.location == 'http://example.com/FrontPage'

def test_failed_log_in(testapp):
    res = testapp.get(viewer_wrong_login, status=400)
    assert b'login' in res.body

def test_logout_link_present_when_logged_in(testapp):
    res = testapp.get(viewer_login, status=303)
    res = testapp.get('/FrontPage', status=200)
    assert b'Logout' in res.body

def test_logout_link_not_present_after_logged_out(testapp):
    res = testapp.get(viewer_login, status=303)
    res = testapp.get('/FrontPage', status=200)
    res = testapp.get('/logout', status=303)
    assert b'Logout' not in res.body

def test_anonymous_user_cannot_edit(testapp):
    res = testapp.get('/FrontPage/edit_page', status=200)
    assert b'Login' in res.body

def test_anonymous_user_cannot_add(testapp):
    res = testapp.get('/add_page/NewPage', status=200)
    assert b'Login' in res.body

def test_viewer_user_cannot_edit(testapp):
    res = testapp.get(viewer_login, status=303)
    res = testapp.get('/FrontPage/edit_page', status=200)
    assert b'Login' in res.body

def test_viewer_user_cannot_add(testapp):
    res = testapp.get(viewer_login, status=303)
    res = testapp.get('/add_page/NewPage', status=200)
    assert b'Login' in res.body

def test_editors_member_user_can_edit(testapp):
    res = testapp.get(editor_login, status=303)
    res = testapp.get('/FrontPage/edit_page', status=200)
    assert b'Editing' in res.body

def test_editors_member_user_can_add(testapp):
    res = testapp.get(editor_login, status=303)
    res = testapp.get('/add_page/NewPage', status=200)
    assert b'Editing' in res.body

def test_editors_member_user_can_view(testapp):
    res = testapp.get(editor_login, status=303)
    res = testapp.get('/FrontPage', status=200)
    assert b'FrontPage' in res.body
