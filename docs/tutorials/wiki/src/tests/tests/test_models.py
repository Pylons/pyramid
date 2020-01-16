from tutorial import models

def test_page_model():
    instance = models.Page(data='some data')
    assert instance.data == 'some data'

def test_wiki_model():
    wiki = models.Wiki()
    assert wiki.__parent__ is None
    assert wiki.__name__ is None

def test_appmaker():
    root = {}
    models.appmaker(root)
    assert root['app_root']['FrontPage'].data == 'This is the front page'

def test_password_hashing():
    from tutorial.security import hash_password, check_password

    password = 'secretpassword'
    hashed_password = hash_password(password)
    assert check_password(hashed_password, password)
    assert not check_password(hashed_password, 'attackerpassword')
    assert not check_password(None, password)
