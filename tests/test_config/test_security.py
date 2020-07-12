import unittest

from pyramid.exceptions import ConfigurationError, ConfigurationExecutionError


class ConfiguratorSecurityMethodsTests(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid.config import Configurator

        config = Configurator(*arg, **kw)
        return config

    def test_set_security_policy(self):
        from pyramid.interfaces import ISecurityPolicy

        config = self._makeOne()
        policy = object()
        config.set_security_policy(policy)
        config.commit()
        self.assertEqual(config.registry.getUtility(ISecurityPolicy), policy)

    def test_set_authentication_policy_with_security_policy(self):
        from pyramid.interfaces import IAuthorizationPolicy, ISecurityPolicy

        config = self._makeOne()
        security_policy = object()
        authn_policy = object()
        authz_policy = object()
        config.registry.registerUtility(security_policy, ISecurityPolicy)
        config.registry.registerUtility(authz_policy, IAuthorizationPolicy)
        config.set_authentication_policy(authn_policy)
        self.assertRaises(ConfigurationError, config.commit)

    def test_set_authentication_policy_no_authz_policy(self):
        config = self._makeOne()
        policy = object()
        config.set_authentication_policy(policy)
        self.assertRaises(ConfigurationExecutionError, config.commit)

    def test_set_authentication_policy_no_authz_policy_autocommit(self):
        config = self._makeOne(autocommit=True)
        policy = object()
        self.assertRaises(
            ConfigurationError, config.set_authentication_policy, policy
        )

    def test_set_authentication_policy_with_authz_policy(self):
        from pyramid.interfaces import (
            IAuthenticationPolicy,
            IAuthorizationPolicy,
            ISecurityPolicy,
        )
        from pyramid.security import LegacySecurityPolicy

        config = self._makeOne()
        authn_policy = object()
        authz_policy = object()
        config.registry.registerUtility(authz_policy, IAuthorizationPolicy)
        config.set_authentication_policy(authn_policy)
        config.commit()
        self.assertEqual(
            config.registry.getUtility(IAuthenticationPolicy), authn_policy
        )
        self.assertIsInstance(
            config.registry.getUtility(ISecurityPolicy), LegacySecurityPolicy
        )

    def test_set_authentication_policy_with_authz_policy_autocommit(self):
        from pyramid.interfaces import (
            IAuthenticationPolicy,
            IAuthorizationPolicy,
            ISecurityPolicy,
        )
        from pyramid.security import LegacySecurityPolicy

        config = self._makeOne(autocommit=True)
        authn_policy = object()
        authz_policy = object()
        config.registry.registerUtility(authz_policy, IAuthorizationPolicy)
        config.set_authentication_policy(authn_policy)
        config.commit()
        self.assertEqual(
            config.registry.getUtility(IAuthenticationPolicy), authn_policy
        )
        self.assertIsInstance(
            config.registry.getUtility(ISecurityPolicy), LegacySecurityPolicy
        )

    def test_set_authorization_policy_no_authn_policy(self):
        config = self._makeOne()
        policy = object()
        config.set_authorization_policy(policy)
        self.assertRaises(ConfigurationExecutionError, config.commit)

    def test_set_authorization_policy_no_authn_policy_autocommit(self):
        from pyramid.interfaces import IAuthorizationPolicy

        config = self._makeOne(autocommit=True)
        policy = object()
        config.set_authorization_policy(policy)
        self.assertEqual(
            config.registry.getUtility(IAuthorizationPolicy), policy
        )

    def test_set_authorization_policy_with_authn_policy(self):
        from pyramid.interfaces import (
            IAuthenticationPolicy,
            IAuthorizationPolicy,
        )

        config = self._makeOne()
        authn_policy = object()
        authz_policy = object()
        config.registry.registerUtility(authn_policy, IAuthenticationPolicy)
        config.set_authorization_policy(authz_policy)
        config.commit()
        self.assertEqual(
            config.registry.getUtility(IAuthorizationPolicy), authz_policy
        )

    def test_set_authorization_policy_with_authn_policy_autocommit(self):
        from pyramid.interfaces import (
            IAuthenticationPolicy,
            IAuthorizationPolicy,
        )

        config = self._makeOne(autocommit=True)
        authn_policy = object()
        authz_policy = object()
        config.registry.registerUtility(authn_policy, IAuthenticationPolicy)
        config.set_authorization_policy(authz_policy)
        self.assertEqual(
            config.registry.getUtility(IAuthorizationPolicy), authz_policy
        )

    def test_set_default_permission(self):
        from pyramid.interfaces import IDefaultPermission

        config = self._makeOne(autocommit=True)
        config.set_default_permission('view')
        self.assertEqual(
            config.registry.getUtility(IDefaultPermission), 'view'
        )

    def test_add_permission(self):
        config = self._makeOne(autocommit=True)
        config.add_permission('perm')
        cat = config.registry.introspector.get_category('permissions')
        self.assertEqual(len(cat), 1)
        D = cat[0]
        intr = D['introspectable']
        self.assertEqual(intr['value'], 'perm')

    def test_set_default_csrf_options(self):
        from pyramid.interfaces import IDefaultCSRFOptions

        config = self._makeOne(autocommit=True)
        config.set_default_csrf_options()
        result = config.registry.getUtility(IDefaultCSRFOptions)
        self.assertEqual(result.require_csrf, True)
        self.assertEqual(result.token, 'csrf_token')
        self.assertEqual(result.header, 'X-CSRF-Token')
        self.assertEqual(
            list(sorted(result.safe_methods)),
            ['GET', 'HEAD', 'OPTIONS', 'TRACE'],
        )
        self.assertTrue(result.check_origin)
        self.assertFalse(result.allow_no_origin)
        self.assertTrue(result.callback is None)

    def test_changing_set_default_csrf_options(self):
        from pyramid.interfaces import IDefaultCSRFOptions

        config = self._makeOne(autocommit=True)

        def callback(request):  # pragma: no cover
            return True

        config.set_default_csrf_options(
            require_csrf=False,
            token='DUMMY',
            header=None,
            safe_methods=('PUT',),
            check_origin=False,
            allow_no_origin=False,
            callback=callback,
        )
        result = config.registry.getUtility(IDefaultCSRFOptions)
        self.assertEqual(result.require_csrf, False)
        self.assertEqual(result.token, 'DUMMY')
        self.assertEqual(result.header, None)
        self.assertEqual(list(sorted(result.safe_methods)), ['PUT'])
        self.assertFalse(result.check_origin)
        self.assertFalse(result.allow_no_origin)
        self.assertTrue(result.callback is callback)
