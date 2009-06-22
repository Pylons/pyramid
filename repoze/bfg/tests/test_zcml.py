import unittest

from repoze.bfg.testing import cleanUp

class TestViewDirective(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import view
        return view(*arg, **kw)

    def test_no_view(self):
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, self._callFUT, context,
                          'repoze.view', None)

    def test_view_as_function(self):
        context = DummyContext()
        class IFoo:
            pass
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 2)

        permission = actions[0]
        permission_discriminator = ('permission', IFoo, '', IRequest,
                                    IViewPermission)
        self.assertEqual(permission['discriminator'], permission_discriminator)
        self.assertEqual(permission['callable'], handler)
        self.assertEqual(permission['args'][0], 'registerAdapter')
        self.failUnless(isinstance(permission['args'][1],ViewPermissionFactory))
        self.assertEqual(permission['args'][1].permission_name, 'repoze.view')
        self.assertEqual(permission['args'][2], (IFoo, IRequest))
        self.assertEqual(permission['args'][3], IViewPermission)
        self.assertEqual(permission['args'][4], '')
        self.assertEqual(permission['args'][5], None)
        
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IRequest, IView)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1], view)
        self.assertEqual(regadapt['args'][2], (IFoo, IRequest))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_view_as_function_requestonly(self):
        context = DummyContext()

        def view(request):
            return 'OK'
        class IFoo:
            pass
        
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 2)

        permission = actions[0]
        permission_discriminator = ('permission', IFoo, '', IRequest,
                                    IViewPermission)
        self.assertEqual(permission['discriminator'], permission_discriminator)
        self.assertEqual(permission['callable'], handler)
        self.assertEqual(permission['args'][0], 'registerAdapter')
        self.failUnless(isinstance(permission['args'][1],ViewPermissionFactory))
        self.assertEqual(permission['args'][1].permission_name, 'repoze.view')
        self.assertEqual(permission['args'][2], (IFoo, IRequest))
        self.assertEqual(permission['args'][3], IViewPermission)
        self.assertEqual(permission['args'][4], '')
        self.assertEqual(permission['args'][5], None)
        
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IRequest, IView)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        wrapper = regadapt['args'][1]
        self.failIfEqual(wrapper, view)
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')
        self.assertEqual(regadapt['args'][2], (IFoo, IRequest))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_view_as_instance(self):
        context = DummyContext()
        class AView:
            def __call__(self, context, request):
                """ """
        view = AView()
        class IFoo:
            pass
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 2)

        permission = actions[0]
        permission_discriminator = ('permission', IFoo, '', IRequest,
                                    IViewPermission)
        self.assertEqual(permission['discriminator'], permission_discriminator)
        self.assertEqual(permission['callable'], handler)
        self.assertEqual(permission['args'][0], 'registerAdapter')
        self.failUnless(isinstance(permission['args'][1],ViewPermissionFactory))
        self.assertEqual(permission['args'][1].permission_name, 'repoze.view')
        self.assertEqual(permission['args'][2], (IFoo, IRequest))
        self.assertEqual(permission['args'][3], IViewPermission)
        self.assertEqual(permission['args'][4], '')
        self.assertEqual(permission['args'][5], None)
        
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IRequest, IView)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1], view)
        self.assertEqual(regadapt['args'][2], (IFoo, IRequest))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_view_as_instance_requestonly(self):
        context = DummyContext()
        class AView:
            def __call__(self, request):
                return 'OK'
        view = AView()
        class IFoo:
            pass
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 2)

        permission = actions[0]
        permission_discriminator = ('permission', IFoo, '', IRequest,
                                    IViewPermission)
        self.assertEqual(permission['discriminator'], permission_discriminator)
        self.assertEqual(permission['callable'], handler)
        self.assertEqual(permission['args'][0], 'registerAdapter')
        self.failUnless(isinstance(permission['args'][1],ViewPermissionFactory))
        self.assertEqual(permission['args'][1].permission_name, 'repoze.view')
        self.assertEqual(permission['args'][2], (IFoo, IRequest))
        self.assertEqual(permission['args'][3], IViewPermission)
        self.assertEqual(permission['args'][4], '')
        self.assertEqual(permission['args'][5], None)
        
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IRequest, IView)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        wrapper = regadapt['args'][1]
        self.failIfEqual(wrapper, view)
        self.assertEqual(wrapper.__module__, view.__module__)
        self.failUnless('instance' in wrapper.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')
        self.assertEqual(regadapt['args'][2], (IFoo, IRequest))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_view_as_oldstyle_class(self):
        context = DummyContext()
        class IFoo:
            pass
        class view:
            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self):
                return self
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 2)

        permission = actions[0]
        permission_discriminator = ('permission', IFoo, '', IRequest,
                                    IViewPermission)
        self.assertEqual(permission['discriminator'], permission_discriminator)
        self.assertEqual(permission['callable'], handler)
        self.assertEqual(permission['args'][0], 'registerAdapter')
        self.failUnless(isinstance(permission['args'][1],ViewPermissionFactory))
        self.assertEqual(permission['args'][1].permission_name, 'repoze.view')
        self.assertEqual(permission['args'][2], (IFoo, IRequest))
        self.assertEqual(permission['args'][3], IViewPermission)
        self.assertEqual(permission['args'][4], '')
        self.assertEqual(permission['args'][5], None)
        
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IRequest, IView)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        wrapper = regadapt['args'][1]
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        result = wrapper(None, None)
        self.assertEqual(result.context, None)
        self.assertEqual(result.request, None)
        self.assertEqual(regadapt['args'][2], (IFoo, IRequest))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_view_as_oldstyle_class_requestonly(self):
        context = DummyContext()
        class IFoo:
            pass
        class view:
            def __init__(self, request):
                self.request = request

            def __call__(self):
                return self
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 2)

        permission = actions[0]
        permission_discriminator = ('permission', IFoo, '', IRequest,
                                    IViewPermission)
        self.assertEqual(permission['discriminator'], permission_discriminator)
        self.assertEqual(permission['callable'], handler)
        self.assertEqual(permission['args'][0], 'registerAdapter')
        self.failUnless(isinstance(permission['args'][1],ViewPermissionFactory))
        self.assertEqual(permission['args'][1].permission_name, 'repoze.view')
        self.assertEqual(permission['args'][2], (IFoo, IRequest))
        self.assertEqual(permission['args'][3], IViewPermission)
        self.assertEqual(permission['args'][4], '')
        self.assertEqual(permission['args'][5], None)
        
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IRequest, IView)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        wrapper = regadapt['args'][1]
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        result = wrapper(None, None)
        self.assertEqual(result.request, None)
        self.assertEqual(regadapt['args'][2], (IFoo, IRequest))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_view_as_newstyle_class(self):
        context = DummyContext()
        class IFoo:
            pass
        class view(object):
            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self):
                return self
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 2)

        permission = actions[0]
        permission_discriminator = ('permission', IFoo, '', IRequest,
                                    IViewPermission)
        self.assertEqual(permission['discriminator'], permission_discriminator)
        self.assertEqual(permission['callable'], handler)
        self.assertEqual(permission['args'][0], 'registerAdapter')
        self.failUnless(isinstance(permission['args'][1],ViewPermissionFactory))
        self.assertEqual(permission['args'][1].permission_name, 'repoze.view')
        self.assertEqual(permission['args'][2], (IFoo, IRequest))
        self.assertEqual(permission['args'][3], IViewPermission)
        self.assertEqual(permission['args'][4], '')
        self.assertEqual(permission['args'][5], None)
        
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IRequest, IView)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        wrapper = regadapt['args'][1]
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        result = wrapper(None, None)
        self.assertEqual(result.context, None)
        self.assertEqual(result.request, None)
        self.assertEqual(regadapt['args'][2], (IFoo, IRequest))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_view_as_newstyle_class_requestonly(self):
        context = DummyContext()
        class IFoo:
            pass
        class view(object):
            def __init__(self, request):
                self.request = request

            def __call__(self):
                return self
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 2)

        permission = actions[0]
        permission_discriminator = ('permission', IFoo, '', IRequest,
                                    IViewPermission)
        self.assertEqual(permission['discriminator'], permission_discriminator)
        self.assertEqual(permission['callable'], handler)
        self.assertEqual(permission['args'][0], 'registerAdapter')
        self.failUnless(isinstance(permission['args'][1],ViewPermissionFactory))
        self.assertEqual(permission['args'][1].permission_name, 'repoze.view')
        self.assertEqual(permission['args'][2], (IFoo, IRequest))
        self.assertEqual(permission['args'][3], IViewPermission)
        self.assertEqual(permission['args'][4], '')
        self.assertEqual(permission['args'][5], None)
        
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IRequest, IView)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        wrapper = regadapt['args'][1]
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        result = wrapper(None, None)
        self.assertEqual(result.request, None)
        self.assertEqual(regadapt['args'][2], (IFoo, IRequest))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_request_type_asinterface(self):
        context = DummyContext()
        class IFoo:
            pass
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view,
                      request_type=IDummy)
        actions = context.actions
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 2)

        permission = actions[0]
        permission_discriminator = ('permission', IFoo, '', IDummy,
                                    IViewPermission)
        self.assertEqual(permission['discriminator'], permission_discriminator)
        self.assertEqual(permission['callable'], handler)
        self.assertEqual(permission['args'][0], 'registerAdapter')
        self.failUnless(isinstance(permission['args'][1],ViewPermissionFactory))
        self.assertEqual(permission['args'][1].permission_name, 'repoze.view')
        self.assertEqual(permission['args'][2], (IFoo, IDummy))
        self.assertEqual(permission['args'][3], IViewPermission)
        self.assertEqual(permission['args'][4], '')
        self.assertEqual(permission['args'][5], None)
        
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IDummy, IView)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1], view)
        self.assertEqual(regadapt['args'][2], (IFoo, IDummy))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_request_type_ashttpmethod(self):
        context = DummyContext()
        class IFoo:
            pass
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view,
                      request_type='GET')
        actions = context.actions
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IGETRequest

        self.assertEqual(len(actions), 2)

        permission = actions[0]
        self.assertEqual(permission['args'][2], (IFoo, IGETRequest))
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IDummy, IView)
        self.assertEqual(regadapt['args'][2], (IFoo, IGETRequest))

    def test_request_type_asinterfacestring(self):
        context = DummyContext()
        class IFoo:
            pass
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view,
                      request_type='whatever')
        actions = context.actions
        from repoze.bfg.interfaces import IView
        self.assertEqual(len(actions), 2)

        permission = actions[0]
        self.assertEqual(permission['args'][2], (IFoo, IDummy))
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IDummy, IView)
        self.assertEqual(regadapt['args'][2], (IFoo, IDummy))

    def test_with_route_name(self):
        class IFoo:
            pass
        class IDummyRequest:
            pass
        context = DummyContext()
        context.request_factories = {'foo':{None:{'interface':IDummyRequest}}}
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view, route_name='foo')
        actions = context.actions
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 2)

        permission = actions[0]
        permission_discriminator = ('permission', IFoo, '', IDummyRequest,
                                    IViewPermission)
        self.assertEqual(permission['discriminator'], permission_discriminator)
        self.assertEqual(permission['callable'], handler)
        self.assertEqual(permission['args'][0], 'registerAdapter')
        self.failUnless(isinstance(permission['args'][1],ViewPermissionFactory))
        self.assertEqual(permission['args'][1].permission_name, 'repoze.view')
        self.assertEqual(permission['args'][2], (IFoo, IDummyRequest))
        self.assertEqual(permission['args'][3], IViewPermission)
        self.assertEqual(permission['args'][4], '')
        self.assertEqual(permission['args'][5], None)
        
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IDummyRequest, IView)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1], view)
        self.assertEqual(regadapt['args'][2], (IFoo, IDummyRequest))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_with_route_name_bad_order(self):
        context = DummyContext()
        context.request_factories = {}
        view = lambda *arg: None
        from zope.configuration.exceptions import ConfigurationError
        self.assertRaises(ConfigurationError, self._callFUT, context,
                          'repoze.view', None, view, '', None, 'foo')

class TestNotFoundDirective(unittest.TestCase):
    def _callFUT(self, context, view):
        from repoze.bfg.zcml import notfound
        return notfound(context, view)
    
    def test_it(self):
        context = DummyContext()
        def view(request):
            return 'OK'
        self._callFUT(context, view)
        actions = context.actions
        from repoze.bfg.interfaces import INotFoundView
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 1)

        regadapt = actions[0]
        regadapt_discriminator = ('notfound_view',)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerUtility')
        derived_view = regadapt['args'][1]
        self.assertEqual(derived_view(None, None), 'OK')
        self.assertEqual(derived_view.__name__, view.__name__)
        self.assertEqual(regadapt['args'][2], INotFoundView)
        self.assertEqual(regadapt['args'][3], '')
        self.assertEqual(regadapt['args'][4], None)

class TestForbiddenDirective(unittest.TestCase):
    def _callFUT(self, context, view):
        from repoze.bfg.zcml import forbidden
        return forbidden(context, view)
    
    def test_it(self):
        context = DummyContext()
        def view(request):
            return 'OK'
        self._callFUT(context, view)
        actions = context.actions
        from repoze.bfg.interfaces import IForbiddenView
        from repoze.bfg.zcml import handler

        self.assertEqual(len(actions), 1)

        regadapt = actions[0]
        regadapt_discriminator = ('notfound_view',)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerUtility')
        derived_view = regadapt['args'][1]
        self.assertEqual(derived_view(None, None), 'OK')
        self.assertEqual(derived_view.__name__, view.__name__)
        self.assertEqual(regadapt['args'][2], IForbiddenView)
        self.assertEqual(regadapt['args'][3], '')
        self.assertEqual(regadapt['args'][4], None)
        
class TestDeriveView(unittest.TestCase):
    def _callFUT(self, view):
        from repoze.bfg.zcml import derive_view
        return derive_view(view)
    
    def test_view_as_function_context_and_request(self):
        def view(context, request):
            return 'OK'
        result = self._callFUT(view)
        self.failUnless(result is view)
        self.assertEqual(view(None, None), 'OK')
        
    def test_view_as_function_requestonly(self):
        def view(request):
            return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_newstyle_class_context_and_request(self):
        class view(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')
        
    def test_view_as_newstyle_class_requestonly(self):
        class view(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_oldstyle_class_context_and_request(self):
        class view:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')
        
    def test_view_as_oldstyle_class_requestonly(self):
        class view:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_instance_context_and_request(self):
        class View:
            def __call__(self, context, request):
                return 'OK'
        view = View()
        result = self._callFUT(view)
        self.failUnless(result is view)
        self.assertEqual(result(None, None), 'OK')
        
    def test_view_as_instance_requestonly(self):
        class View:
            def __call__(self, request):
                return 'OK'
        view = View()
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        self.assertEqual(result(None, None), 'OK')

class TestRouteRequirementFunction(unittest.TestCase):
    def _callFUT(self, context, attr, expr):
        from repoze.bfg.zcml import route_requirement
        return route_requirement(context, attr, expr)

    def test_it(self):
        context = DummyContext()
        context.context = DummyContext()
        context.context.requirements = {}
        self._callFUT(context, 'a', 'b')
        self.assertEqual(context.context.requirements['a'], 'b')
        self.assertRaises(ValueError, self._callFUT, context, 'a', 'b')

class TestConnectRouteFunction(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, directive):
        from repoze.bfg.zcml import connect_route
        return connect_route(directive)

    def _registerRoutesMapper(self):
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        mapper = DummyMapper()
        from repoze.bfg.interfaces import IRoutesMapper
        gsm.registerUtility(mapper, IRoutesMapper)
        return mapper

    def test_no_mapper(self):
        directive = DummyRouteDirective()
        self._callFUT(directive) # doesn't blow up when no routes mapper reg'd

    def test_defaults(self):
        mapper = self._registerRoutesMapper()
        directive = DummyRouteDirective()
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][0], ('name', 'path'))
        self.assertEqual(mapper.connections[0][1], {'requirements': {}})

    def test_name_and_path(self):
        mapper = self._registerRoutesMapper()
        directive = DummyRouteDirective(name='abc', path='thepath')
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][0], ('abc', 'thepath',))
        self.assertEqual(mapper.connections[0][1], {'requirements': {}})

    def test_all_directives(self):
        mapper = self._registerRoutesMapper()
        def foo():
            """ """
        directive = DummyRouteDirective(
            minimize=True, explicit=True, encoding='utf-8', static=True,
            filter=foo, absolute=True, member_name='m', collection_name='c',
            parent_member_name='p', parent_collection_name='c',
            condition_method='GET', condition_subdomain=True,
            condition_function=foo, subdomains=['a'],
            name='thename', path='thepath',
            factory=foo, view='view', permission='permission')
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][0], ('thename', 'thepath'))
        pr = {'member_name':'p', 'collection_name':'c'}
        c = {'method':'GET', 'sub_domain':['a'], 'function':foo}
        D = mapper.connections[0][1]
        
        self.assertEqual(D['requirements'], {})
        self.assertEqual(D['_minimize'],True)
        self.assertEqual(D['_explicit'],True)
        self.assertEqual(D['_encoding'],'utf-8')
        self.assertEqual(D['_static'],True)
        self.assertEqual(D['_filter'],foo)
        self.assertEqual(D['_absolute'],True)
        self.assertEqual(D['_member_name'], 'm')
        self.assertEqual(D['_collection_name'], 'c')
        self.assertEqual(D['_parent_resource'], pr)
        self.assertEqual(D['conditions'], c)
        route = mapper.matchlist[-1]
        self.assertEqual(route._factory, foo)
        self.assertEqual(route.request_factories,
                         directive.context.request_factories['thename'])
        

    def test_condition_subdomain_true(self):
        mapper = self._registerRoutesMapper()
        directive = DummyRouteDirective(static=True, explicit=True,
                                        condition_subdomain=True)
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][1],
                         {'requirements': {},
                          '_static':True,
                          '_explicit':True,
                          'conditions':{'sub_domain':True}
                          })

    def test_condition_function(self):
        mapper = self._registerRoutesMapper()
        def foo(e, r):
            """ """
        directive = DummyRouteDirective(static=True, explicit=True,
                                        condition_function=foo)
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][1],
                         {'requirements': {},
                          '_static':True,
                          '_explicit':True,
                          'conditions':{'function':foo}
                          })

    def test_condition_method(self):
        mapper = self._registerRoutesMapper()
        directive = DummyRouteDirective(static=True, explicit=True,
                                        condition_method='GET')
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][1],
                         {'requirements': {},
                          '_static':True,
                          '_explicit':True,
                          'conditions':{'method':'GET'}
                          })

    def test_request_type(self):
        mapper = self._registerRoutesMapper()
        directive = DummyRouteDirective(static=True, explicit=True,
                                        request_type='GET')
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][1],
                         {'requirements': {},
                          '_static':True,
                          '_explicit':True,
                          'conditions':{'method':'GET'}
                          })

    def test_condition_method_and_request_type(self):
        mapper = self._registerRoutesMapper()
        directive = DummyRouteDirective(static=True, explicit=True,
                                        request_type='GET',
                                        condition_method='POST')
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][1],
                         {'requirements': {},
                          '_static':True,
                          '_explicit':True,
                          'conditions':{'method':'POST'}
                          })


    def test_subdomains(self):
        mapper = self._registerRoutesMapper()
        directive = DummyRouteDirective(name='name',
                                        static=True, explicit=True,
                                        subdomains=['a', 'b'])
        self._callFUT(directive)
        self.assertEqual(len(mapper.connections), 1)
        self.assertEqual(mapper.connections[0][0], ('name', 'path'))
        self.assertEqual(mapper.connections[0][1],
                         {'requirements': {},
                          '_static':True,
                          '_explicit':True,
                          'conditions':{'sub_domain':['a', 'b']}
                          })

class TestRouteDirective(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.zcml import Route
        return Route

    def _makeOne(self, context, path, name, **kw):
        return self._getTargetClass()(context, path, name, **kw)

    def test_defaults(self):
        context = DummyContext()
        route = self._makeOne(context, 'path', 'name')
        self.assertEqual(route.path, 'path')
        self.assertEqual(route.name, 'name')
        self.assertEqual(route.requirements, {})

    def test_parent_collection_name_missing(self):
        context = DummyContext()
        from zope.configuration.exceptions import ConfigurationError
        self.assertRaises(ConfigurationError, self._makeOne, context,
                          'path', 'name', parent_member_name='a')
        
    def test_parent_collection_name_present(self):
        context = DummyContext()
        route = self._makeOne(context, 'path', 'name',
                              parent_member_name='a',
                              parent_collection_name='p')
        self.assertEqual(route.parent_member_name, 'a')
        self.assertEqual(route.parent_collection_name, 'p')

    def test_after_with_view(self):
        from repoze.bfg.zcml import handler
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        
        context = DummyContext()
        view = Dummy()
        route = self._makeOne(context, 'path', 'name', view=view)
        route.after()
        actions = context.actions
        self.assertEqual(len(actions), 2)

        factories = context.request_factories
        request_iface = factories['name'][None]['interface']

        view_action = actions[0]
        view_callable = view_action['callable']
        view_discriminator = view_action['discriminator']
        view_args = view_action['args']
        self.assertEqual(view_callable, handler)
        self.assertEqual(len(view_discriminator), 5)
        self.assertEqual(view_discriminator[0], 'view')
        self.assertEqual(view_discriminator[1], None)
        self.assertEqual(view_discriminator[2],'')
        self.assertEqual(view_discriminator[3], request_iface)
        self.assertEqual(view_discriminator[4], IView)
        self.assertEqual(view_args, ('registerAdapter', view,
                                     (None, request_iface), IView,
                                     '', None))
        
        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(len(route_discriminator), 7)
        self.assertEqual(route_discriminator[0], 'route')
        self.assertEqual(route_discriminator[1], 'name')
        self.assertEqual(route_discriminator[2],'{}')
        self.assertEqual(route_discriminator[3], None)
        self.assertEqual(route_discriminator[4], None)
        self.assertEqual(route_discriminator[5], None)
        self.assertEqual(route_discriminator[6], None)
        self.assertEqual(route_args, (route,))

    def test_after_with_view_and_view_for(self):
        from repoze.bfg.zcml import handler
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        
        context = DummyContext()
        view = Dummy()
        route = self._makeOne(context, 'path', 'name', view=view,
                              view_for=IDummy)
        route.after()
        actions = context.actions
        self.assertEqual(len(actions), 2)

        factories = context.request_factories
        request_iface = factories['name'][None]['interface']

        view_action = actions[0]
        view_callable = view_action['callable']
        view_discriminator = view_action['discriminator']
        view_args = view_action['args']
        self.assertEqual(view_callable, handler)
        self.assertEqual(len(view_discriminator), 5)
        self.assertEqual(view_discriminator[0], 'view')
        self.assertEqual(view_discriminator[1], IDummy)
        self.assertEqual(view_discriminator[2],'')
        self.assertEqual(view_discriminator[3], request_iface)
        self.assertEqual(view_discriminator[4], IView)
        self.assertEqual(view_args, ('registerAdapter', view,
                                     (IDummy, request_iface), IView,
                                     '', None))
        
        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(len(route_discriminator), 7)
        self.assertEqual(route_discriminator[0], 'route')
        self.assertEqual(route_discriminator[1], 'name')
        self.assertEqual(route_discriminator[2],'{}')
        self.assertEqual(route_discriminator[3], None)
        self.assertEqual(route_discriminator[4], None)
        self.assertEqual(route_discriminator[5], None)
        self.assertEqual(route_discriminator[6], None)
        self.assertEqual(route_args, (route,))

    def test_after_without_view(self):
        from repoze.bfg.zcml import connect_route
        
        context = DummyContext()
        view = Dummy()
        route = self._makeOne(context, 'path', 'name')
        route.after()
        actions = context.actions
        self.assertEqual(len(actions), 1)

        route_action = actions[0]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(len(route_discriminator), 7)
        self.assertEqual(route_discriminator[0], 'route')
        self.assertEqual(route_discriminator[1], 'name')
        self.assertEqual(route_discriminator[2],'{}')
        self.assertEqual(route_discriminator[3], None)
        self.assertEqual(route_discriminator[4], None)
        self.assertEqual(route_discriminator[5], None)
        self.assertEqual(route_discriminator[6], None)
        self.assertEqual(route_args, (route,))

class TestZCMLConfigure(unittest.TestCase):
    i = 0
    def _callFUT(self, path, package):
        from repoze.bfg.zcml import zcml_configure
        return zcml_configure(path, package)
    
    def setUp(self):
        cleanUp()
        self.tempdir = None
        import sys
        import os
        import tempfile
        from repoze.bfg.path import package_path
        from repoze.bfg.tests import fixtureapp as package
        import shutil
        tempdir = tempfile.mkdtemp()
        modname = 'myfixture%s' % self.i
        self.i += 1
        self.packagepath = os.path.join(tempdir, modname)
        fixturedir = package_path(package)
        shutil.copytree(fixturedir, self.packagepath)
        sys.path.insert(0, tempdir)
        self.module = __import__(modname)
        self.tempdir = tempdir

    def tearDown(self):
        cleanUp()
        import sys
        import shutil
        if self.module is not None:
            del sys.modules[self.module.__name__]
        if self.tempdir is not None:
            sys.path.pop(0)
            shutil.rmtree(self.tempdir)

    def test_zcml_configure(self):
        actions = self._callFUT('configure.zcml', self.module)
        self.failUnless(actions)
        self.failUnless(isinstance(actions, list))

    def test_zcml_configure_nonexistent_configure_dot_zcml(self):
        import os
        os.remove(os.path.join(self.packagepath, 'configure.zcml'))
        self.assertRaises(IOError, self._callFUT, 'configure.zcml',
                          self.module)

    def test_secpol_BBB(self):
        from repoze.bfg.interfaces import IAuthorizationPolicy
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.interfaces import ISecurityPolicy
        from repoze.bfg.interfaces import ILogger
        secpol = DummySecurityPolicy()
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.registerUtility(secpol, ISecurityPolicy)
        logger = DummyLogger()
        gsm.registerUtility(logger, ILogger, name='repoze.bfg.debug')
        self._callFUT('configure.zcml', self.module)
        self.failUnless(gsm.queryUtility(IAuthenticationPolicy))
        self.failUnless(gsm.queryUtility(IAuthorizationPolicy))
        self.assertEqual(len(logger.messages), 1)
        self.failUnless('ISecurityPolicy' in logger.messages[0])

    def test_iunauthorized_appfactory_BBB(self):
        from repoze.bfg.interfaces import IUnauthorizedAppFactory
        from repoze.bfg.interfaces import IForbiddenView
        from zope.component import getGlobalSiteManager
        from repoze.bfg.interfaces import ILogger
        context = DummyContext()
        def factory():
            return 'yo'
        logger = DummyLogger()
        gsm = getGlobalSiteManager()
        gsm.registerUtility(factory, IUnauthorizedAppFactory)
        logger = DummyLogger()
        gsm.registerUtility(logger, ILogger, name='repoze.bfg.debug')
        self._callFUT('configure.zcml', self.module)
        self.assertEqual(len(logger.messages), 1)
        self.failUnless('forbidden' in logger.messages[0])
        forbidden = gsm.getUtility(IForbiddenView)
        self.assertEqual(forbidden(None, DummyRequest()), 'yo')

    def test_inotfound_appfactory_BBB(self):
        from repoze.bfg.interfaces import INotFoundAppFactory
        from repoze.bfg.interfaces import INotFoundView
        from zope.component import getGlobalSiteManager
        from repoze.bfg.interfaces import ILogger
        context = DummyContext()
        def factory():
            return 'yo'
        logger = DummyLogger()
        gsm = getGlobalSiteManager()
        gsm.registerUtility(factory, INotFoundAppFactory)
        logger = DummyLogger()
        gsm.registerUtility(logger, ILogger, name='repoze.bfg.debug')
        self._callFUT('configure.zcml', self.module)
        self.assertEqual(len(logger.messages), 1)
        self.failUnless('notfound' in logger.messages[0])
        notfound = gsm.getUtility(INotFoundView)
        self.assertEqual(notfound(None,DummyRequest()), 'yo')

class TestBFGViewFunctionGrokker(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.zcml import BFGViewFunctionGrokker
        return BFGViewFunctionGrokker

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_grok_is_bfg_view(self):
        from repoze.bfg.interfaces import IRequest
        from zope.interface import Interface
        grokker = self._makeOne()
        class obj:
            pass
        obj.__is_bfg_view__ = True
        obj.__permission__ = 'foo'
        obj.__for__ = Interface
        obj.__view_name__ = 'foo.html'
        obj.__request_type__ = IRequest
        obj.__route_name__ = None
        context = DummyContext()
        result = grokker.grok('name', obj, context=context)
        self.assertEqual(result, True)
        actions = context.actions
        self.assertEqual(len(actions), 2)

    def test_grok_is_not_bfg_view(self):
        grokker = self._makeOne()
        class obj:
            pass
        context = DummyContext()
        result = grokker.grok('name', obj, context=context)
        self.assertEqual(result, False)
        actions = context.actions
        self.assertEqual(len(actions), 0)

class TestZCMLScanDirective(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, package, martian):
        from repoze.bfg.zcml import scan
        return scan(context, package, martian)

    def test_it(self):
        martian = DummyMartianModule()
        module_grokker = DummyModuleGrokker()
        dummy_module = DummyModule()
        from repoze.bfg.zcml import exclude
        self._callFUT(None, dummy_module, martian)
        self.assertEqual(martian.name, 'dummy')
        self.assertEqual(len(martian.module_grokker.registered), 1)
        self.assertEqual(martian.context, None)
        self.assertEqual(martian.exclude_filter, exclude)

class TestExcludeFunction(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, name):
        from repoze.bfg.zcml import exclude
        return exclude(name)

    def test_it(self):
        self.assertEqual(self._callFUT('.foo'), True)
        self.assertEqual(self._callFUT('foo'), False)

class TestRequestOnly(unittest.TestCase):
    def _callFUT(self, arg):
        from repoze.bfg.zcml import requestonly
        return requestonly(arg)
    
    def test_newstyle_class_no_init(self):
        class foo(object):
            """ """
        self.assertFalse(self._callFUT(foo))

    def test_newstyle_class_init_toomanyargs(self):
        class foo(object):
            def __init__(self, context, request):
                """ """
        self.assertFalse(self._callFUT(foo))
        
    def test_newstyle_class_init_onearg_named_request(self):
        class foo(object):
            def __init__(self, request):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_newstyle_class_init_onearg_named_somethingelse(self):
        class foo(object):
            def __init__(self, req):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_newstyle_class_init_defaultargs_firstname_not_request(self):
        class foo(object):
            def __init__(self, context, request=None):
                """ """
        self.assertFalse(self._callFUT(foo))

    def test_newstyle_class_init_defaultargs_firstname_request(self):
        class foo(object):
            def __init__(self, request, foo=1, bar=2):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_newstyle_class_init_noargs(self):
        class foo(object):
            def __init__():
                """ """
        self.assertFalse(self._callFUT(foo))

    def test_oldstyle_class_no_init(self):
        class foo:
            """ """
        self.assertFalse(self._callFUT(foo))

    def test_oldstyle_class_init_toomanyargs(self):
        class foo:
            def __init__(self, context, request):
                """ """
        self.assertFalse(self._callFUT(foo))
        
    def test_oldstyle_class_init_onearg_named_request(self):
        class foo:
            def __init__(self, request):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_oldstyle_class_init_onearg_named_somethingelse(self):
        class foo:
            def __init__(self, req):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_oldstyle_class_init_defaultargs_firstname_not_request(self):
        class foo:
            def __init__(self, context, request=None):
                """ """
        self.assertFalse(self._callFUT(foo))

    def test_oldstyle_class_init_defaultargs_firstname_request(self):
        class foo:
            def __init__(self, request, foo=1, bar=2):
                """ """
        self.assertTrue(self._callFUT(foo), True)

    def test_oldstyle_class_init_noargs(self):
        class foo:
            def __init__():
                """ """
        self.assertFalse(self._callFUT(foo))

    def test_function_toomanyargs(self):
        def foo(context, request):
            """ """
        self.assertFalse(self._callFUT(foo))
        
    def test_function_onearg_named_request(self):
        def foo(request):
            """ """
        self.assertTrue(self._callFUT(foo))

    def test_function_onearg_named_somethingelse(self):
        def foo(req):
            """ """
        self.assertTrue(self._callFUT(foo))

    def test_function_defaultargs_firstname_not_request(self):
        def foo(context, request=None):
            """ """
        self.assertFalse(self._callFUT(foo))

    def test_function_defaultargs_firstname_request(self):
        def foo(request, foo=1, bar=2):
            """ """
        self.assertTrue(self._callFUT(foo), True)

    def test_instance_toomanyargs(self):
        class Foo:
            def __call__(self, context, request):
                """ """
        foo = Foo()
        self.assertFalse(self._callFUT(foo))
        
    def test_instance_defaultargs_onearg_named_request(self):
        class Foo:
            def __call__(self, request):
                """ """
        foo = Foo()
        self.assertTrue(self._callFUT(foo))

    def test_instance_defaultargs_onearg_named_somethingelse(self):
        class Foo:
            def __call__(self, req):
                """ """
        foo = Foo()
        self.assertTrue(self._callFUT(foo))

    def test_instance_defaultargs_firstname_not_request(self):
        class Foo:
            def __call__(self, context, request=None):
                """ """
        foo = Foo()
        self.assertFalse(self._callFUT(foo))

    def test_instance_defaultargs_firstname_request(self):
        class Foo:
            def __call__(self, request, foo=1, bar=2):
                """ """
        foo = Foo()
        self.assertTrue(self._callFUT(foo), True)

class DummyModule:
    __name__ = 'dummy'

class DummyModuleGrokker:
    def __init__(self):
        self.registered = []
        
    def register(self, other):
        self.registered.append(other)
        
class DummyMartianModule:
    def grok_dotted_name(self, name, grokker, context, exclude_filter=None):
        self.name = name
        self.context = context
        self.exclude_filter = exclude_filter
        return True

    def ModuleGrokker(self):
        self.module_grokker = DummyModuleGrokker()
        return self.module_grokker

class DummyContext:
    def __init__(self):
        self.actions = []
        self.info = None

    def action(self, discriminator, callable, args):
        self.actions.append(
            {'discriminator':discriminator,
             'callable':callable,
             'args':args}
            )

    def resolve(self, dottedname):
        return IDummy

class Dummy:
    pass

class DummyRouteDirective:
    path = 'path'
    name = 'name'
    view = None
    factory = None
    permission = None
    encoding = None
    static = False
    minimize = False
    explicit = False
    static = False
    filter = None
    absolute = False
    member_name = False
    collection_name = None
    parent_member_name = None
    parent_collection_name = None
    condition_method = None
    request_type = None
    condition_subdomain = None
    condition_function = None
    subdomains = None
    def __init__(self, **kw):
        if not 'requirements' in kw:
            kw['requirements'] = {}
        self.__dict__.update(kw)
        self.context = DummyContext()
        self.context.request_factories = {self.name:{}}

class DummyMapper:
    def __init__(self):
        self.connections = []
        self.matchlist = []

    def connect(self, *arg, **kw):
        self.connections.append((arg, kw))
        self.matchlist.append(DummyRoute())

class DummyRoute:
    pass

from zope.interface import Interface
class IDummy(Interface):
    pass

class DummySecurityPolicy:
    pass

class DummyLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(msg)
    warn = info
    debug = info

class DummyRequest:
    def get_response(self, app):
        return app
    
