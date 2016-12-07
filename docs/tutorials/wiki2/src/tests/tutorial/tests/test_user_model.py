import unittest
import transaction

from pyramid import testing


class BaseTest(unittest.TestCase):

    def setUp(self):
        from ..models import get_tm_session
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('..models')
        self.config.include('..routes')

        session_factory = self.config.registry['dbsession_factory']
        self.session = get_tm_session(session_factory, transaction.manager)

        self.init_database()

    def init_database(self):
        from ..models.meta import Base
        session_factory = self.config.registry['dbsession_factory']
        engine = session_factory.kw['bind']
        Base.metadata.create_all(engine)

    def tearDown(self):
        testing.tearDown()
        transaction.abort()

    def makeUser(self, name, role):
        from ..models import User
        return User(name=name, role=role)


class TestSetPassword(BaseTest):

    def test_password_hash_saved(self):
        user = self.makeUser(name='foo', role='bar')
        self.assertFalse(user.password_hash)

        user.set_password('secret')
        self.assertTrue(user.password_hash)


class TestCheckPassword(BaseTest):

    def test_password_hash_not_set(self):
        user = self.makeUser(name='foo', role='bar')
        self.assertFalse(user.password_hash)

        self.assertFalse(user.check_password('secret'))

    def test_correct_password(self):
        user = self.makeUser(name='foo', role='bar')
        user.set_password('secret')
        self.assertTrue(user.password_hash)

        self.assertTrue(user.check_password('secret'))

    def test_incorrect_password(self):
        user = self.makeUser(name='foo', role='bar')
        user.set_password('secret')
        self.assertTrue(user.password_hash)

        self.assertFalse(user.check_password('incorrect'))
