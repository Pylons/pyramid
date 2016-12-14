import mock
import unittest


class TestMyAuthenticationPolicy(unittest.TestCase):

    def test_no_user(self):
        request = mock.Mock()
        request.user = None

        from ..security import MyAuthenticationPolicy
        policy = MyAuthenticationPolicy(None)
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_user(self):
        request = mock.Mock()
        request.user.id = 'foo'

        from ..security import MyAuthenticationPolicy
        policy = MyAuthenticationPolicy(None)
        self.assertEqual(policy.authenticated_userid(request), 'foo')
