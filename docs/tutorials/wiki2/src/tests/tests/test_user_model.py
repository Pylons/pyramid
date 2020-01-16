from tutorial import models


def test_password_hash_saved():
    user = models.User(name='foo', role='bar')
    assert user.password_hash is None

    user.set_password('secret')
    assert user.password_hash is not None

def test_password_hash_not_set():
    user = models.User(name='foo', role='bar')
    assert not user.check_password('secret')

def test_correct_password():
    user = models.User(name='foo', role='bar')
    user.set_password('secret')
    assert user.check_password('secret')

def test_incorrect_password():
    user = models.User(name='foo', role='bar')
    user.set_password('secret')
    assert not user.check_password('incorrect')
