import unittest

from pyramid import testing
from pyramid.exceptions import ConfigurationError

class TestDeriveView(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        self.config = None

    def _makeRequest(self):
        request = DummyRequest()
        request.registry = self.config.registry
        return request

    def _registerLogger(self):
        from pyramid.interfaces import IDebugLogger
        logger = DummyLogger()
        self.config.registry.registerUtility(logger, IDebugLogger)
        return logger

    def _registerSecurityPolicy(self, permissive):
        from pyramid.interfaces import IAuthenticationPolicy
        from pyramid.interfaces import IAuthorizationPolicy
        policy = DummySecurityPolicy(permissive)
        self.config.registry.registerUtility(policy, IAuthenticationPolicy)
        self.config.registry.registerUtility(policy, IAuthorizationPolicy)

    def test_function_returns_non_adaptable(self):
        def view(request):
            return None
        result = self.config.derive_view(view)
        self.assertFalse(result is view)
        try:
            result(None, None)
        except ValueError as e:
            self.assertEqual(
                e.args[0],
                'Could not convert return value of the view callable function '
                'pyramid.tests.test_config.test_derivations.view into a response '
                'object. The value returned was None. You may have forgotten '
                'to return a value from the view callable.'
                )
        else: # pragma: no cover
            raise AssertionError

    def test_function_returns_non_adaptable_dict(self):
        def view(request):
            return {'a':1}
        result = self.config.derive_view(view)
        self.assertFalse(result is view)
        try:
            result(None, None)
        except ValueError as e:
            self.assertEqual(
                e.args[0],
                "Could not convert return value of the view callable function "
                "pyramid.tests.test_config.test_derivations.view into a response "
                "object. The value returned was {'a': 1}. You may have "
                "forgotten to define a renderer in the view configuration."
                )
        else: # pragma: no cover
            raise AssertionError

    def test_instance_returns_non_adaptable(self):
        class AView(object):
            def __call__(self, request):
                return None
        view = AView()
        result = self.config.derive_view(view)
        self.assertFalse(result is view)
        try:
            result(None, None)
        except ValueError as e:
            msg = e.args[0]
            self.assertTrue(msg.startswith(
                'Could not convert return value of the view callable object '
                '<pyramid.tests.test_config.test_views.'))
            self.assertTrue(msg.endswith(
                '> into a response object. The value returned was None. You '
                'may have forgotten to return a value from the view callable.'))
        else: # pragma: no cover
            raise AssertionError

    def test_function_returns_true_Response_no_renderer(self):
        from pyramid.response import Response
        r = Response('Hello')
        def view(request):
            return r
        result = self.config.derive_view(view)
        self.assertFalse(result is view)
        response = result(None, None)
        self.assertEqual(response, r)

    def test_function_returns_true_Response_with_renderer(self):
        from pyramid.response import Response
        r = Response('Hello')
        def view(request):
            return r
        renderer = object()
        result = self.config.derive_view(view)
        self.assertFalse(result is view)
        response = result(None, None)
        self.assertEqual(response, r)

    def test_requestonly_default_method_returns_non_adaptable(self):
        request = DummyRequest()
        class AView(object):
            def __init__(self, request):
                pass
            def __call__(self):
                return None
        result = self.config.derive_view(AView)
        self.assertFalse(result is AView)
        try:
            result(None, request)
        except ValueError as e:
            self.assertEqual(
                e.args[0],
                'Could not convert return value of the view callable '
                'method __call__ of '
                'class pyramid.tests.test_config.test_derivations.AView into a '
                'response object. The value returned was None. You may have '
                'forgotten to return a value from the view callable.'
                )
        else: # pragma: no cover
            raise AssertionError

    def test_requestonly_nondefault_method_returns_non_adaptable(self):
        request = DummyRequest()
        class AView(object):
            def __init__(self, request):
                pass
            def theviewmethod(self):
                return None
        result = self.config.derive_view(AView)
        self.assertFalse(result is AView)
        try:
            result(None, request)
        except ValueError as e:
            self.assertEqual(
                e.args[0],
                'Could not convert return value of the view callable '
                'method theviewmethod of '
                'class pyramid.tests.test_config.test_views.AView into a '
                'response object. The value returned was None. You may have '
                'forgotten to return a value from the view callable.'
                )
        else: # pragma: no cover
            raise AssertionError

    def test_requestonly_function(self):
        response = DummyResponse()
        def view(request):
            return response
        result = self.config.derive_view(view)
        self.assertFalse(result is view)
        self.assertEqual(result(None, None), response)

    def test_requestonly_function_with_renderer(self):
        response = DummyResponse()
        class moo(object):
            def render_view(inself, req, resp, view_inst, ctx):
                self.assertEqual(req, request)
                self.assertEqual(resp, 'OK')
                self.assertEqual(view_inst, view)
                self.assertEqual(ctx, context)
                return response
            def clone(self):
                return self
        def view(request):
            return 'OK'
        result = self.config.derive_view(view)
        self.assertFalse(result.__wraps__ is view)
        request = self._makeRequest()
        context = testing.DummyResource()
        self.assertEqual(result(context, request), response)

    def test_requestonly_function_with_renderer_request_override(self):
        def moo(info):
            def inner(value, system):
                self.assertEqual(value, 'OK')
                self.assertEqual(system['request'], request)
                self.assertEqual(system['context'], context)
                return b'moo'
            return inner
        def view(request):
            return 'OK'
        self.config.add_renderer('moo', moo)
        result = self.config.derive_view(view, renderer='string')
        self.assertFalse(result is view)
        request = self._makeRequest()
        request.override_renderer = 'moo'
        context = testing.DummyResource()
        self.assertEqual(result(context, request).body, b'moo')

    def test_requestonly_function_with_renderer_request_has_view(self):
        response = DummyResponse()
        class moo(object):
            def render_view(inself, req, resp, view_inst, ctx):
                self.assertEqual(req, request)
                self.assertEqual(resp, 'OK')
                self.assertEqual(view_inst, 'view')
                self.assertEqual(ctx, context)
                return response
            def clone(self):
                return self
        def view(request):
            return 'OK'
        result = self.config.derive_view(view, renderer=moo())
        self.assertFalse(result.__wraps__ is view)
        request = self._makeRequest()
        request.__view__ = 'view'
        context = testing.DummyResource()
        r = result(context, request)
        self.assertEqual(r, response)
        self.assertFalse(hasattr(request, '__view__'))

    def test_class_without_attr(self):
        response = DummyResponse()
        class View(object):
            def __init__(self, request):
                pass
            def __call__(self):
                return response
        result = self.config.derive_view(View)
        request = self._makeRequest()
        self.assertEqual(result(None, request), response)
        self.assertEqual(request.__view__.__class__, View)

    def test_class_with_attr(self):
        response = DummyResponse()
        class View(object):
            def __init__(self, request):
                pass
            def another(self):
                return response
        result = self.config.derive_view(View, attr='another')
        request = self._makeRequest()
        self.assertEqual(result(None, request), response)
        self.assertEqual(request.__view__.__class__, View)

    def test_as_function_context_and_request(self):
        def view(context, request):
            return 'OK'
        result = self.config.derive_view(view)
        self.assertTrue(result.__wraps__ is view)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        self.assertEqual(view(None, None), 'OK')

    def test_as_function_requestonly(self):
        response = DummyResponse()
        def view(request):
            return response
        result = self.config.derive_view(view)
        self.assertFalse(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), response)

    def test_as_newstyle_class_context_and_request(self):
        response = DummyResponse()
        class view(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return response
        result = self.config.derive_view(view)
        self.assertFalse(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        request = self._makeRequest()
        self.assertEqual(result(None, request), response)
        self.assertEqual(request.__view__.__class__, view)

    def test_as_newstyle_class_requestonly(self):
        response = DummyResponse()
        class view(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return response
        result = self.config.derive_view(view)
        self.assertFalse(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        request = self._makeRequest()
        self.assertEqual(result(None, request), response)
        self.assertEqual(request.__view__.__class__, view)

    def test_as_oldstyle_class_context_and_request(self):
        response = DummyResponse()
        class view:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return response
        result = self.config.derive_view(view)
        self.assertFalse(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        request = self._makeRequest()
        self.assertEqual(result(None, request), response)
        self.assertEqual(request.__view__.__class__, view)

    def test_as_oldstyle_class_requestonly(self):
        response = DummyResponse()
        class view:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return response
        result = self.config.derive_view(view)
        self.assertFalse(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        request = self._makeRequest()
        self.assertEqual(result(None, request), response)
        self.assertEqual(request.__view__.__class__, view)

    def test_as_instance_context_and_request(self):
        response = DummyResponse()
        class View:
            def __call__(self, context, request):
                return response
        view = View()
        result = self.config.derive_view(view)
        self.assertTrue(result.__wraps__ is view)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), response)

    def test_as_instance_requestonly(self):
        response = DummyResponse()
        class View:
            def __call__(self, request):
                return response
        view = View()
        result = self.config.derive_view(view)
        self.assertFalse(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertTrue('test_views' in result.__name__)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), response)

    def test_with_debug_authorization_no_authpol(self):
        response = DummyResponse()
        view = lambda *arg: response
        self.config.registry.settings = dict(
            debug_authorization=True, reload_templates=True)
        logger = self._registerLogger()
        result = self.config._derive_view(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        request = self._makeRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), response)
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): Allowed "
                         "(no authorization policy in use)")

    def test_with_debug_authorization_authn_policy_no_authz_policy(self):
        response = DummyResponse()
        view = lambda *arg: response
        self.config.registry.settings = dict(debug_authorization=True)
        from pyramid.interfaces import IAuthenticationPolicy
        policy = DummySecurityPolicy(False)
        self.config.registry.registerUtility(policy, IAuthenticationPolicy)
        logger = self._registerLogger()
        result = self.config._derive_view(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        request = self._makeRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), response)
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): Allowed "
                         "(no authorization policy in use)")

    def test_with_debug_authorization_authz_policy_no_authn_policy(self):
        response = DummyResponse()
        view = lambda *arg: response
        self.config.registry.settings = dict(debug_authorization=True)
        from pyramid.interfaces import IAuthorizationPolicy
        policy = DummySecurityPolicy(False)
        self.config.registry.registerUtility(policy, IAuthorizationPolicy)
        logger = self._registerLogger()
        result = self.config._derive_view(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        request = self._makeRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), response)
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): Allowed "
                         "(no authorization policy in use)")

    def test_with_debug_authorization_no_permission(self):
        response = DummyResponse()
        view = lambda *arg: response
        self.config.registry.settings = dict(
            debug_authorization=True, reload_templates=True)
        self._registerSecurityPolicy(True)
        logger = self._registerLogger()
        result = self.config._derive_view(view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        request = self._makeRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), response)
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): Allowed ("
                         "no permission registered)")

    def test_debug_auth_permission_authpol_permitted(self):
        response = DummyResponse()
        view = lambda *arg: response
        self.config.registry.settings = dict(
            debug_authorization=True, reload_templates=True)
        logger = self._registerLogger()
        self._registerSecurityPolicy(True)
        result = self.config._derive_view(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result.__call_permissive__.__wraps__, view)
        request = self._makeRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), response)
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): True")

    def test_debug_auth_permission_authpol_permitted_no_request(self):
        response = DummyResponse()
        view = lambda *arg: response
        self.config.registry.settings = dict(
            debug_authorization=True, reload_templates=True)
        logger = self._registerLogger()
        self._registerSecurityPolicy(True)
        result = self.config._derive_view(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result.__call_permissive__.__wraps__, view)
        self.assertEqual(result(None, None), response)
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url None (view name "
                         "None against context None): True")

    def test_debug_auth_permission_authpol_denied(self):
        from pyramid.httpexceptions import HTTPForbidden
        response = DummyResponse()
        view = lambda *arg: response
        self.config.registry.settings = dict(
            debug_authorization=True, reload_templates=True)
        logger = self._registerLogger()
        self._registerSecurityPolicy(False)
        result = self.config._derive_view(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result.__call_permissive__.__wraps__, view)
        request = self._makeRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertRaises(HTTPForbidden, result, None, request)
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): False")

    def test_debug_auth_permission_authpol_denied2(self):
        view = lambda *arg: 'OK'
        self.config.registry.settings = dict(
            debug_authorization=True, reload_templates=True)
        self._registerLogger()
        self._registerSecurityPolicy(False)
        result = self.config._derive_view(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = self._makeRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        permitted = result.__permitted__(None, None)
        self.assertEqual(permitted, False)

    def test_debug_auth_permission_authpol_overridden(self):
        from pyramid.security import NO_PERMISSION_REQUIRED
        response = DummyResponse()
        view = lambda *arg: response
        self.config.registry.settings = dict(
            debug_authorization=True, reload_templates=True)
        logger = self._registerLogger()
        self._registerSecurityPolicy(False)
        result = self.config._derive_view(view, permission=NO_PERMISSION_REQUIRED)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        request = self._makeRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), response)
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): "
                         "Allowed (NO_PERMISSION_REQUIRED)")

    def test_secured_view_authn_policy_no_authz_policy(self):
        response = DummyResponse()
        view = lambda *arg: response
        self.config.registry.settings = {}
        from pyramid.interfaces import IAuthenticationPolicy
        policy = DummySecurityPolicy(False)
        self.config.registry.registerUtility(policy, IAuthenticationPolicy)
        result = self.config._derive_view(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        request = self._makeRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), response)

    def test_secured_view_authz_policy_no_authn_policy(self):
        response = DummyResponse()
        view = lambda *arg: response
        self.config.registry.settings = {}
        from pyramid.interfaces import IAuthorizationPolicy
        policy = DummySecurityPolicy(False)
        self.config.registry.registerUtility(policy, IAuthorizationPolicy)
        result = self.config._derive_view(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertFalse(hasattr(result, '__call_permissive__'))
        request = self._makeRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), response)

    def test_secured_view_raises_forbidden_no_name(self):
        from pyramid.interfaces import IAuthenticationPolicy
        from pyramid.interfaces import IAuthorizationPolicy
        from pyramid.httpexceptions import HTTPForbidden
        response = DummyResponse()
        view = lambda *arg: response
        self.config.registry.settings = {}
        policy = DummySecurityPolicy(False)
        self.config.registry.registerUtility(policy, IAuthenticationPolicy)
        self.config.registry.registerUtility(policy, IAuthorizationPolicy)
        result = self.config._derive_view(view, permission='view')
        request = self._makeRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        try:
            result(None, request)
        except HTTPForbidden as e:
            self.assertEqual(e.message,
                             'Unauthorized: <lambda> failed permission check')
        else: # pragma: no cover
            raise AssertionError

    def test_secured_view_raises_forbidden_with_name(self):
        from pyramid.interfaces import IAuthenticationPolicy
        from pyramid.interfaces import IAuthorizationPolicy
        from pyramid.httpexceptions import HTTPForbidden
        def myview(request): pass
        self.config.registry.settings = {}
        policy = DummySecurityPolicy(False)
        self.config.registry.registerUtility(policy, IAuthenticationPolicy)
        self.config.registry.registerUtility(policy, IAuthorizationPolicy)
        result = self.config._derive_view(myview, permission='view')
        request = self._makeRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        try:
            result(None, request)
        except HTTPForbidden as e:
            self.assertEqual(e.message,
                             'Unauthorized: myview failed permission check')
        else: # pragma: no cover
            raise AssertionError

    def test_predicate_mismatch_view_has_no_name(self):
        from pyramid.exceptions import PredicateMismatch
        response = DummyResponse()
        view = lambda *arg: response
        def predicate1(context, request):
            return False
        predicate1.text = lambda *arg: 'text'
        result = self.config._derive_view(view, predicates=[predicate1])
        request = self._makeRequest()
        request.method = 'POST'
        try:
            result(None, None)
        except PredicateMismatch as e:
            self.assertEqual(e.detail,
                             'predicate mismatch for view <lambda> (text)')
        else: # pragma: no cover
            raise AssertionError

    def test_predicate_mismatch_view_has_name(self):
        from pyramid.exceptions import PredicateMismatch
        def myview(request): pass
        def predicate1(context, request):
            return False
        predicate1.text = lambda *arg: 'text'
        result = self.config._derive_view(myview, predicates=[predicate1])
        request = self._makeRequest()
        request.method = 'POST'
        try:
            result(None, None)
        except PredicateMismatch as e:
            self.assertEqual(e.detail,
                             'predicate mismatch for view myview (text)')
        else: # pragma: no cover
            raise AssertionError

    def test_predicate_mismatch_exception_has_text_in_detail(self):
        from pyramid.exceptions import PredicateMismatch
        def myview(request): pass
        def predicate1(context, request):
            return True
        predicate1.text = lambda *arg: 'pred1'
        def predicate2(context, request):
            return False
        predicate2.text = lambda *arg: 'pred2'
        result = self.config._derive_view(myview, 
            predicates=[predicate1, predicate2])
        request = self._makeRequest()
        request.method = 'POST'
        try:
            result(None, None)
        except PredicateMismatch as e:
            self.assertEqual(e.detail,
                             'predicate mismatch for view myview (pred2)')
        else: # pragma: no cover
            raise AssertionError

    def test_with_predicates_all(self):
        response = DummyResponse()
        view = lambda *arg: response
        predicates = []
        def predicate1(context, request):
            predicates.append(True)
            return True
        def predicate2(context, request):
            predicates.append(True)
            return True
        result = self.config._derive_view(view, 
            predicates=[predicate1, predicate2])
        request = self._makeRequest()
        request.method = 'POST'
        next = result(None, None)
        self.assertEqual(next, response)
        self.assertEqual(predicates, [True, True])

    def test_with_predicates_checker(self):
        view = lambda *arg: 'OK'
        predicates = []
        def predicate1(context, request):
            predicates.append(True)
            return True
        def predicate2(context, request):
            predicates.append(True)
            return True
        result = self.config._derive_view(view, 
            predicates=[predicate1, predicate2])
        request = self._makeRequest()
        request.method = 'POST'
        next = result.__predicated__(None, None)
        self.assertEqual(next, True)
        self.assertEqual(predicates, [True, True])

    def test_with_predicates_notall(self):
        from pyramid.httpexceptions import HTTPNotFound
        view = lambda *arg: 'OK'
        predicates = []
        def predicate1(context, request):
            predicates.append(True)
            return True
        predicate1.text = lambda *arg: 'text'
        def predicate2(context, request):
            predicates.append(True)
            return False
        predicate2.text = lambda *arg: 'text'
        result = self.config._derive_view(view, 
            predicates=[predicate1, predicate2])
        request = self._makeRequest()
        request.method = 'POST'
        self.assertRaises(HTTPNotFound, result, None, None)
        self.assertEqual(predicates, [True, True])

    def test_with_wrapper_viewname(self):
        from pyramid.response import Response
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        inner_response = Response('OK')
        def inner_view(context, request):
            return inner_response
        def outer_view(context, request):
            self.assertEqual(request.wrapped_response, inner_response)
            self.assertEqual(request.wrapped_body, inner_response.body)
            self.assertEqual(request.wrapped_view.__original_view__,
                             inner_view)
            return Response(b'outer ' + request.wrapped_body)
        self.config.registry.registerAdapter(
            outer_view, (IViewClassifier, None, None), IView, 'owrap')
        result = self.config._derive_view(inner_view, viewname='inner',
                                wrapper_viewname='owrap')
        self.assertFalse(result is inner_view)
        self.assertEqual(inner_view.__module__, result.__module__)
        self.assertEqual(inner_view.__doc__, result.__doc__)
        request = self._makeRequest()
        response = result(None, request)
        self.assertEqual(response.body, b'outer OK')

    def test_with_wrapper_viewname_notfound(self):
        from pyramid.response import Response
        inner_response = Response('OK')
        def inner_view(context, request):
            return inner_response
        result = self.config._derive_view(inner_view, viewname='inner',
                                wrapper_viewname='owrap')
        request = self._makeRequest()
        self.assertRaises(ValueError, wrapped, None, request)

    def test_as_newstyle_class_context_and_request_attr_and_renderer(self):
        response = DummyResponse()
        class renderer(object):
            def render_view(inself, req, resp, view_inst, ctx):
                self.assertEqual(req, request)
                self.assertEqual(resp, {'a':'1'})
                self.assertEqual(view_inst.__class__, View)
                self.assertEqual(ctx, context)
                return response
            def clone(self):
                return self
        class View(object):
            def __init__(self, context, request):
                pass
            def index(self):
                return {'a':'1'}
        result = self.config._derive_view(View, 
            renderer=renderer(), attr='index')
        self.assertFalse(result is View)
        self.assertEqual(result.__module__, View.__module__)
        self.assertEqual(result.__doc__, View.__doc__)
        self.assertEqual(result.__name__, View.__name__)
        request = self._makeRequest()
        context = testing.DummyResource()
        self.assertEqual(result(context, request), response)

    def test_as_newstyle_class_requestonly_attr_and_renderer(self):
        response = DummyResponse()
        class renderer(object):
            def render_view(inself, req, resp, view_inst, ctx):
                self.assertEqual(req, request)
                self.assertEqual(resp, {'a':'1'})
                self.assertEqual(view_inst.__class__, View)
                self.assertEqual(ctx, context)
                return response
            def clone(self):
                return self
        class View(object):
            def __init__(self, request):
                pass
            def index(self):
                return {'a':'1'}
        result = self.config.derive_view(View, 
            renderer=renderer(), attr='index')
        self.assertFalse(result is View)
        self.assertEqual(result.__module__, View.__module__)
        self.assertEqual(result.__doc__, View.__doc__)
        self.assertEqual(result.__name__, View.__name__)
        request = self._makeRequest()
        context = testing.DummyResource()
        self.assertEqual(result(context, request), response)

    def test_as_oldstyle_cls_context_request_attr_and_renderer(self):
        response = DummyResponse()
        class renderer(object):
            def render_view(inself, req, resp, view_inst, ctx):
                self.assertEqual(req, request)
                self.assertEqual(resp, {'a':'1'})
                self.assertEqual(view_inst.__class__, View)
                self.assertEqual(ctx, context)
                return response
            def clone(self):
                return self
        class View:
            def __init__(self, context, request):
                pass
            def index(self):
                return {'a':'1'}
        result = self.config.derive_view(View, 
            renderer=renderer(), attr='index')
        self.assertFalse(result is View)
        self.assertEqual(result.__module__, View.__module__)
        self.assertEqual(result.__doc__, View.__doc__)
        self.assertEqual(result.__name__, View.__name__)
        request = self._makeRequest()
        context = testing.DummyResource()
        self.assertEqual(result(context, request), response)

    def test_as_oldstyle_cls_requestonly_attr_and_renderer(self):
        response = DummyResponse()
        class renderer(object):
            def render_view(inself, req, resp, view_inst, ctx):
                self.assertEqual(req, request)
                self.assertEqual(resp, {'a':'1'})
                self.assertEqual(view_inst.__class__, View)
                self.assertEqual(ctx, context)
                return response
            def clone(self):
                return self
        class View:
            def __init__(self, request):
                pass
            def index(self):
                return {'a':'1'}
        result = self.config.derive_view(View, 
            renderer=renderer(), attr='index')
        self.assertFalse(result is View)
        self.assertEqual(result.__module__, View.__module__)
        self.assertEqual(result.__doc__, View.__doc__)
        self.assertEqual(result.__name__, View.__name__)
        request = self._makeRequest()
        context = testing.DummyResource()
        self.assertEqual(result(context, request), response)

    def test_as_instance_context_and_request_attr_and_renderer(self):
        response = DummyResponse()
        class renderer(object):
            def render_view(inself, req, resp, view_inst, ctx):
                self.assertEqual(req, request)
                self.assertEqual(resp, {'a':'1'})
                self.assertEqual(view_inst, view)
                self.assertEqual(ctx, context)
                return response
            def clone(self):
                return self
        class View:
            def index(self, context, request):
                return {'a':'1'}
        view = View()
        result = self.config.derive_view(view, 
            renderer=renderer(), attr='index')
        self.assertFalse(result is view)
        self.assertEqual(result.__module__, view.__module__)
        self.assertEqual(result.__doc__, view.__doc__)
        request = self._makeRequest()
        context = testing.DummyResource()
        self.assertEqual(result(context, request), response)

    def test_as_instance_requestonly_attr_and_renderer(self):
        response = DummyResponse()
        class renderer(object):
            def render_view(inself, req, resp, view_inst, ctx):
                self.assertEqual(req, request)
                self.assertEqual(resp, {'a':'1'})
                self.assertEqual(view_inst, view)
                self.assertEqual(ctx, context)
                return response
            def clone(self):
                return self
        class View:
            def index(self, request):
                return {'a':'1'}
        view = View()
        result = self.config.derive_view(view, 
            renderer=renderer(), attr='index')
        self.assertFalse(result is view)
        self.assertEqual(result.__module__, view.__module__)
        self.assertEqual(result.__doc__, view.__doc__)
        request = self._makeRequest()
        context = testing.DummyResource()
        self.assertEqual(result(context, request), response)

    def test_with_view_mapper_config_specified(self):
        response = DummyResponse()
        class mapper(object):
            def __init__(self, **kw):
                self.kw = kw
            def __call__(self, view):
                def wrapped(context, request):
                    return response
                return wrapped
        def view(context, request): return 'NOTOK'
        result = self.config._derive_view(view, mapper=mapper)
        self.assertFalse(result.__wraps__ is view)
        self.assertEqual(result(None, None), response)

    def test_with_view_mapper_view_specified(self):
        from pyramid.response import Response
        response = Response()
        def mapper(**kw):
            def inner(view):
                def superinner(context, request):
                    self.assertEqual(request, None)
                    return response
                return superinner
            return inner
        def view(context, request): return 'NOTOK'
        view.__view_mapper__ = mapper
        result = self.config.derive_view(view)
        self.assertFalse(result.__wraps__ is view)
        self.assertEqual(result(None, None), response)

    def test_with_view_mapper_default_mapper_specified(self):
        from pyramid.response import Response
        response = Response()
        def mapper(**kw):
            def inner(view):
                def superinner(context, request):
                    self.assertEqual(request, None)
                    return  response
                return superinner
            return inner
        self.config.set_view_mapper(mapper)
        def view(context, request): return 'NOTOK'
        result = self.config.derive_view(view)
        self.assertFalse(result.__wraps__ is view)
        self.assertEqual(result(None, None), response)

    def test_attr_wrapped_view_branching_default_phash(self):
        from pyramid.config.util import DEFAULT_PHASH
        def view(context, request): pass
        result = self.config._derive_view(view, phash=DEFAULT_PHASH)
        self.assertEqual(result.__wraps__, view)

    def test_attr_wrapped_view_branching_nondefault_phash(self):
        def view(context, request): pass
        result = self.config._derive_view(view, phash='nondefault')
        self.assertNotEqual(result, view)

    def test_http_cached_view_integer(self):
        import datetime
        from pyramid.response import Response
        response = Response('OK')
        def inner_view(context, request):
            return response
        result = self.config._derive_view(inner_view, http_cache=3600)
        self.assertFalse(result is inner_view)
        self.assertEqual(inner_view.__module__, result.__module__)
        self.assertEqual(inner_view.__doc__, result.__doc__)
        request = self._makeRequest()
        when = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        result = result(None, request)
        self.assertEqual(result, response)
        headers = dict(result.headerlist)
        expires = parse_httpdate(headers['Expires'])
        assert_similar_datetime(expires, when)
        self.assertEqual(headers['Cache-Control'], 'max-age=3600')

    def test_http_cached_view_timedelta(self):
        import datetime
        from pyramid.response import Response
        response = Response('OK')
        def inner_view(context, request):
            return response
        result = self.config._derive_view(inner_view, 
            http_cache=datetime.timedelta(hours=1))
        self.assertFalse(result is inner_view)
        self.assertEqual(inner_view.__module__, result.__module__)
        self.assertEqual(inner_view.__doc__, result.__doc__)
        request = self._makeRequest()
        when = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        result = result(None, request)
        self.assertEqual(result, response)
        headers = dict(result.headerlist)
        expires = parse_httpdate(headers['Expires'])
        assert_similar_datetime(expires, when)
        self.assertEqual(headers['Cache-Control'], 'max-age=3600')

    def test_http_cached_view_tuple(self):
        import datetime
        from pyramid.response import Response
        response = Response('OK')
        def inner_view(context, request):
            return response
        result = self.config._derive_view(inner_view,
            http_cache=(3600, {'public':True}))
        self.assertFalse(result is inner_view)
        self.assertEqual(inner_view.__module__, result.__module__)
        self.assertEqual(inner_view.__doc__, result.__doc__)
        request = self._makeRequest()
        when = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        result = result(None, request)
        self.assertEqual(result, response)
        headers = dict(result.headerlist)
        expires = parse_httpdate(headers['Expires'])
        assert_similar_datetime(expires, when)
        self.assertEqual(headers['Cache-Control'], 'max-age=3600, public')

    def test_http_cached_view_tuple_seconds_None(self):
        from pyramid.response import Response
        response = Response('OK')
        def inner_view(context, request):
            return response
        result = self.config._derive_view(inner_view,
            http_cache=(None, {'public':True}))
        self.assertFalse(result is inner_view)
        self.assertEqual(inner_view.__module__, result.__module__)
        self.assertEqual(inner_view.__doc__, result.__doc__)
        request = self._makeRequest()
        result = result(None, request)
        self.assertEqual(result, response)
        headers = dict(result.headerlist)
        self.assertFalse('Expires' in headers)
        self.assertEqual(headers['Cache-Control'], 'public')

    def test_http_cached_view_prevent_auto_set(self):
        from pyramid.response import Response
        response = Response()
        response.cache_control.prevent_auto = True
        def inner_view(context, request):
            return response
        result = self.config._derive_view(inner_view, http_cache=3600)
        request = self._makeRequest()
        result = result(None, request)
        self.assertEqual(result, response) # doesn't blow up
        headers = dict(result.headerlist)
        self.assertFalse('Expires' in headers)
        self.assertFalse('Cache-Control' in headers)

    def test_http_cached_prevent_http_cache_in_settings(self):
        self.config.registry.settings['prevent_http_cache'] = True
        from pyramid.response import Response
        response = Response()
        def inner_view(context, request):
            return response
        result = self.config._derive_view(inner_view, http_cache=3600)
        request = self._makeRequest()
        result = result(None, request)
        self.assertEqual(result, response)
        headers = dict(result.headerlist)
        self.assertFalse('Expires' in headers)
        self.assertFalse('Cache-Control' in headers)

    def test_http_cached_view_bad_tuple(self):
        def view(request): pass
        self.assertRaises(ConfigurationError, self.config.derive_view, 
            view, http_cache=(None,))

from zope.interface import implementer
from pyramid.interfaces import (
    IResponse,
    IRequest,
    )

@implementer(IResponse)
class DummyResponse(object):
    content_type = None
    default_content_type = None
    body = None

class DummyRequest:
    subpath = ()
    matchdict = None
    request_iface  = IRequest

    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ
        self.params = {}
        self.cookies = {}
        self.response = DummyResponse()

class DummyLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(msg)
    warn = info
    debug = info

class DummySecurityPolicy:
    def __init__(self, permitted=True):
        self.permitted = permitted

    def effective_principals(self, request):
        return []

    def permits(self, context, principals, permission):
        return self.permitted

def parse_httpdate(s):
    import datetime
    # cannot use %Z, must use literal GMT; Jython honors timezone
    # but CPython does not
    return datetime.datetime.strptime(s, "%a, %d %b %Y %H:%M:%S GMT")

def assert_similar_datetime(one, two):
    for attr in ('year', 'month', 'day', 'hour', 'minute'):
        one_attr = getattr(one, attr)
        two_attr = getattr(two, attr)
        if not one_attr == two_attr: # pragma: no cover
            raise AssertionError('%r != %r in %s' % (one_attr, two_attr, attr))

