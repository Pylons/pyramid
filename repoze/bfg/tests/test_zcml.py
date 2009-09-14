import logging

logging.basicConfig()

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
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        context = DummyContext()
        class IFoo(Interface):
            pass
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions

        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        sm = getSiteManager()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        self.failUnless(wrapper)
        self.failIf(hasattr(wrapper, '__call_permissive__'))

        perm = sm.adapters.lookup((IFoo, IRequest), IViewPermission, name='')
        self.assertEqual(perm, None)

    def test_view_as_function_requestonly(self):
        from zope.interface import Interface
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission

        context = DummyContext()

        def view(request):
            return 'OK'
        class IFoo(Interface):
            pass
        
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        sm = getSiteManager()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        self.failIfEqual(wrapper, view)
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')
        self.failIf(hasattr(wrapper, '__call_permissive__'))

        perm = sm.adapters.lookup((IFoo, IRequest), IViewPermission, name='')
        self.assertEqual(perm, None)

    def test_view_as_instance(self):
        from zope.interface import Interface
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission

        context = DummyContext()
        class AView:
            def __call__(self, context, request):
                """ """
        view = AView()
        class IFoo(Interface):
            pass
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        sm = getSiteManager()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        self.failUnless(wrapper)
        self.failIf(hasattr(wrapper, '__call_permissive__'))

        perm = sm.adapters.lookup((IFoo, IRequest), IViewPermission, name='')
        self.assertEqual(perm, None)

    def test_view_as_instance_requestonly(self):
        from zope.interface import Interface
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission

        context = DummyContext()
        class AView:
            def __call__(self, request):
                return 'OK'
        view = AView()
        class IFoo(Interface):
            pass
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        sm = getSiteManager()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        self.failIfEqual(wrapper, view)
        self.assertEqual(wrapper.__module__, view.__module__)
        self.failUnless('instance' in wrapper.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')
        self.failIf(hasattr(wrapper, '__call_permissive__'))

        perm = sm.adapters.lookup((IFoo, IRequest), IViewPermission, name='')
        self.assertEqual(perm, None)

    def test_view_as_oldstyle_class(self):
        from zope.interface import Interface
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        context = DummyContext()
        class IFoo(Interface):
            pass
        class view:
            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self):
                return self
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions

        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        sm = getSiteManager()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        result = wrapper(None, None)
        self.assertEqual(result.context, None)
        self.assertEqual(result.request, None)
        self.failIf(hasattr(wrapper, '__call_permissive__'))

        perm = sm.adapters.lookup((IFoo, IRequest), IViewPermission, name='')
        self.assertEqual(perm, None)

    def test_view_as_oldstyle_class_requestonly(self):
        from zope.interface import Interface
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission

        context = DummyContext()
        class IFoo(Interface):
            pass
        class view:
            def __init__(self, request):
                self.request = request

            def __call__(self):
                return self
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        sm = getSiteManager()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        result = wrapper(None, None)
        self.assertEqual(result.request, None)
        self.failIf(hasattr(wrapper, '__call_permissive__'))

        perm = sm.adapters.lookup((IFoo, IRequest), IViewPermission, name='')
        self.assertEqual(perm, None)


    def test_view_as_newstyle_class(self):
        from zope.interface import Interface
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission

        context = DummyContext()
        class IFoo(Interface):
            pass
        class view(object):
            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self):
                return self
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        sm = getSiteManager()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        result = wrapper(None, None)
        self.assertEqual(result.context, None)
        self.assertEqual(result.request, None)
        self.failIf(hasattr(wrapper, '__call_permissive__'))

        perm = sm.adapters.lookup((IFoo, IRequest), IViewPermission, name='')
        self.assertEqual(perm, None)

    def test_view_as_newstyle_class_requestonly(self):
        from zope.interface import Interface
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission

        context = DummyContext()
        class IFoo(Interface):
            pass
        class view(object):
            def __init__(self, request):
                self.request = request

            def __call__(self):
                return self
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        sm = getSiteManager()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        result = wrapper(None, None)
        self.assertEqual(result.request, None)
        self.failIf(hasattr(wrapper, '__call_permissive__'))

        perm = sm.adapters.lookup((IFoo, IRequest), IViewPermission, name='')
        self.assertEqual(perm, None)

    def test_with_reltemplate(self):
        from zope.interface import Interface
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission

        import repoze.bfg.tests

        context = DummyContext(repoze.bfg.tests)
        class IFoo(Interface):
            pass
        class view(object):
            def __init__(self, context, request):
                self.request = request
                self.context = context

            def __call__(self):
                return {'a':'1'}

        import os
        fixture = 'fixtures/minimal.txt'
        self._callFUT(context, 'repoze.view', IFoo, view=view, template=fixture)
        actions = context.actions
        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        sm = getSiteManager()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        result = wrapper(None, None)
        self.assertEqual(result.body, 'Hello.\n')

    def test_request_type_asinterface(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        class IRequest(Interface):
            pass
        class IFoo(Interface):
            pass
        context = DummyContext(IRequest)
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view,
                      request_type=IDummy)
        actions = context.actions

        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', IDummy, IView, None, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        sm = getSiteManager()
        wrapper = sm.adapters.lookup((IFoo, IDummy), IView, name='')
        self.failUnless(wrapper)
        self.failIf(hasattr(wrapper, '__call_permissive__'))

        perm = sm.adapters.lookup((IFoo, IRequest), IViewPermission, name='')
        self.assertEqual(perm, None)

    def test_request_type_as_noninterface(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IView
        class IFoo(Interface):
            pass
        class Dummy:
            pass
        context = DummyContext(Dummy)
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view,
                      request_type=Dummy)
        actions = context.actions

        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', Dummy, IView, None, None, None, None, None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        sm = getSiteManager()
        iface = implementedBy(Dummy)
        wrapper = sm.adapters.lookup((IFoo, iface), IView, name='')
        self.failUnless(wrapper)
        self.failIf(hasattr(wrapper, '__call_permissive__'))

    def test_request_type_ashttpmethod(self):
        from zope.interface import Interface
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        class IFoo(Interface):
            pass
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view,
                      request_type='GET')
        actions = context.actions

        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, 'GET', None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        sm = getSiteManager()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.method = 'GET'
        self.assertEqual(wrapper.__predicated__(None, request), True)
        request.method = 'POST'
        self.assertEqual(wrapper.__predicated__(None, request), False)
        

    def test_request_type_asinterfacestring(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        class IFoo(Interface):
            pass
        class IRequest(Interface):
            pass
        context = DummyContext(IRequest)
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view,
                      request_type='whatever')
        actions = context.actions
        self.assertEqual(len(actions), 1)

        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None)
        self.assertEqual(actions[0]['discriminator'], discrim)
        register = actions[0]['callable']
        register()
        sm = getSiteManager()
        regview = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        self.assertEqual(view, regview)
        self.failIf(hasattr(view, '__call_permissive__'))

        perm = sm.adapters.lookup((IFoo, IRequest), IViewPermission, name='')
        self.assertEqual(perm, None)

    def test_with_route_name(self):
        from zope.interface import Interface
        from zope.interface import implementedBy
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        class IFoo(Interface):
            pass
        context = DummyContext()
        view = lambda *arg: '123'
        self._callFUT(context, 'repoze.view', IFoo, view=view, route_name='foo')
        actions = context.actions

        self.assertEqual(len(actions), 1)

        action = actions[0]
        register = action['callable']
        register()
        sm = getSiteManager() 
        factory = sm.getUtility(IRouteRequest, 'foo')
        request_type = implementedBy(factory)
        discrim = ('view', IFoo, '', request_type, IView, None, None, None,
                   'foo', None)
        self.assertEqual(action['discriminator'], discrim)
        the_view = sm.adapters.lookup((IFoo, request_type), IView, name='')
        request = factory({})
        self.assertEqual(the_view(None, request), '123')

    def test_with_request_method_true(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        context = DummyContext()
        class IFoo(Interface):
            pass
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            return '123'
        self._callFUT(context, None, IFoo, view=view, request_method='POST')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, 'POST', None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.method = 'POST'
        self.assertEqual(wrapper(None, request), '123')

    def test_with_request_method_false(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.view import NotFound
        context = DummyContext()
        class IFoo(Interface):
            pass
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            """ """
        self._callFUT(context, None, IFoo, view=view, request_method='POST')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, 'POST', None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.method = 'GET'
        self.assertRaises(NotFound, wrapper, None, request)

    def test_with_request_param_noval_true(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        context = DummyContext()
        class IFoo(Interface):
            pass
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            return '123'
        self._callFUT(context, None, IFoo, view=view, request_param='abc')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, 'abc', None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.params = {'abc':''}
        self.assertEqual(wrapper(None, request), '123')

    def test_with_request_param_noval_false(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.view import NotFound
        context = DummyContext()
        class IFoo(Interface):
            pass
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            """ """
        self._callFUT(context, None, IFoo, view=view, request_param='abc')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, 'abc', None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.params = {}
        self.assertRaises(NotFound, wrapper, None, request)

    def test_with_request_paramoval_true(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        context = DummyContext()
        class IFoo(Interface):
            pass
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            return '123'
        self._callFUT(context, None, IFoo, view=view, request_param='abc=123')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, 'abc', None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.params = {'abc':'123'}
        self.assertEqual(wrapper(None, request), '123')

    def test_with_request_param_val_false(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.view import NotFound
        context = DummyContext()
        class IFoo(Interface):
            pass
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            """ """
        self._callFUT(context, None, IFoo, view=view, request_param='abc=123')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, 'abc', None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.params = {'abc':'456'}
        self.assertRaises(NotFound, wrapper, None, request)

    def test_with_containment_true(self):
        from zope.component import getSiteManager
        from zope.interface import directlyProvides
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        context = DummyContext()
        class IFoo(Interface):
            pass
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            return '123'
        sm.registerAdapter(view, (IFoo, IRequest), IView, name='')
        self._callFUT(context, None, IFoo, view=view, containment=IFoo)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, IFoo, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        context = Dummy()
        directlyProvides(context, IFoo)
        self.assertEqual(wrapper(context, request), '123')

    def test_with_containment_false(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.view import NotFound
        context = DummyContext()
        class IFoo(Interface):
            pass
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            """ """
        self._callFUT(context, None, IFoo, view=view, containment=IFoo)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, IFoo, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        context = Dummy()
        self.assertRaises(NotFound, wrapper, context, request)

    def test_multiview_replaces_traditional_view(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IMultiView
        from repoze.bfg.interfaces import IViewPermission
        context = DummyContext()
        class IFoo(Interface):
            pass
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            return '123'
        sm.registerAdapter(view, (IFoo, IRequest), IView, name='')
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        self.failUnless(IMultiView.providedBy(wrapper))
        perm = sm.adapters.lookup((IFoo, IRequest), IViewPermission, name='')
        self.assertEqual(perm, wrapper.__permitted__)
        self.assertEqual(wrapper(None, None), '123')

    def test_multiview_replaces_multiview(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from zope.interface import implements
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IMultiView
        from repoze.bfg.interfaces import IViewPermission
        context = DummyContext()
        class IFoo(Interface):
            pass
        view = lambda *arg: None
        sm = getSiteManager()
        class DummyMultiView:
            implements(IMultiView)
            def __init__(self):
                self.views = []
                self.name = 'name'
            def add(self, view, score):
                self.views.append(view)
            def __call__(self, context, request):
                return '123'
            def __permitted__(self, context, request):
                """ """
        view = DummyMultiView()
        sm.registerAdapter(view, (IFoo, IRequest), IMultiView, name='')
        def view2(context, request):
            """ """
        self._callFUT(context, None, IFoo, view=view2)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        perm = sm.adapters.lookup((IFoo, IRequest), IViewPermission, name='')
        self.assertEqual(perm, wrapper.__permitted__)
        self.failUnless(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper(None, None), '123')
        self.assertEqual(wrapper.views, [view2])

    def test_for_as_class(self):
        from zope.component import getSiteManager
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        context = DummyContext()
        class Foo:
            pass
        sm = getSiteManager()
        def view(context, request):
            """ """
        self._callFUT(context, 'repoze.view', Foo, view=view)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', Foo, '', IRequest, IView, None, None, None, None,
                   None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        foo = implementedBy(Foo)
        wrapper = sm.adapters.lookup((foo, IRequest), IView, name='')
        self.assertEqual(wrapper, view)

class TestNotFoundDirective(unittest.TestCase):
    def _callFUT(self, context, view):
        from repoze.bfg.zcml import notfound
        return notfound(context, view)
    
    def test_it(self):
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import INotFoundView

        context = DummyContext()
        def view(request):
            return 'OK'
        self._callFUT(context, view)
        actions = context.actions
        self.assertEqual(len(actions), 1)

        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], INotFoundView)
        register = regadapt['callable']
        register()
        sm = getSiteManager()
        derived_view = sm.getUtility(INotFoundView)
        self.assertEqual(derived_view(None, None), 'OK')
        self.assertEqual(derived_view.__name__, view.__name__)

class TestForbiddenDirective(unittest.TestCase):
    def _callFUT(self, context, view):
        from repoze.bfg.zcml import forbidden
        return forbidden(context, view)
    
    def test_it(self):
        from zope.component import getSiteManager
        context = DummyContext()
        def view(request):
            return 'OK'
        self._callFUT(context, view)
        actions = context.actions
        from repoze.bfg.interfaces import IForbiddenView

        self.assertEqual(len(actions), 1)

        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IForbiddenView)
        register = regadapt['callable']
        register()
        sm = getSiteManager()
        derived_view = sm.getUtility(IForbiddenView)
        self.assertEqual(derived_view(None, None), 'OK')
        self.assertEqual(derived_view.__name__, view.__name__)

class TestRepozeWho1AuthenticationPolicyDirective(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, context, **kw):
        from repoze.bfg.zcml import repozewho1authenticationpolicy
        return repozewho1authenticationpolicy(context, **kw)

    def test_it_defaults(self):
        from zope.component import getUtility
        from repoze.bfg.interfaces import IAuthenticationPolicy
        context = DummyContext()
        self._callFUT(context)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.callback, None)
        self.assertEqual(policy.identifier_name, 'auth_tkt')
    
    def test_it(self):
        from zope.component import getUtility
        from repoze.bfg.interfaces import IAuthenticationPolicy
        context = DummyContext()
        def callback(identity, request):
            """ """
        self._callFUT(context, identifier_name='something', callback=callback)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.callback, callback)
        self.assertEqual(policy.identifier_name, 'something')

class TestRemoteUserAuthenticationPolicyDirective(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, context, **kw):
        from repoze.bfg.zcml import remoteuserauthenticationpolicy
        return remoteuserauthenticationpolicy(context, **kw)

    def test_defaults(self):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from zope.component import getUtility
        context = DummyContext()
        def callback(identity, request):
            """ """
        self._callFUT(context)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        regadapt_discriminator = 'authentication_policy'
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.environ_key, 'REMOTE_USER')
        self.assertEqual(policy.callback, None)

    def test_it(self):
        from zope.component import getUtility
        from repoze.bfg.interfaces import IAuthenticationPolicy
        context = DummyContext()
        def callback(identity, request):
            """ """
        self._callFUT(context, environ_key='BLAH', callback=callback)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.environ_key, 'BLAH')
        self.assertEqual(policy.callback, callback)

class TestAuthTktAuthenticationPolicyDirective(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, context, secret, **kw):
        from repoze.bfg.zcml import authtktauthenticationpolicy
        return authtktauthenticationpolicy(context, secret, **kw)

    def test_it_defaults(self):
        from zope.component import getUtility
        from repoze.bfg.interfaces import IAuthenticationPolicy
        context = DummyContext()
        self._callFUT(context, 'sosecret')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.cookie.secret, 'sosecret')
        self.assertEqual(policy.callback, None)

    def test_it_noconfigerror(self):
        from zope.component import getUtility
        from repoze.bfg.interfaces import IAuthenticationPolicy
        context = DummyContext()
        def callback(identity, request):
            """ """
        self._callFUT(context, 'sosecret', callback=callback,
                      cookie_name='repoze.bfg.auth_tkt',
                      secure=True, include_ip=True, timeout=100,
                      reissue_time=60)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.cookie.secret, 'sosecret')
        self.assertEqual(policy.callback, callback)

    def test_it_configerror(self):
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        def callback(identity, request):
            """ """
        self.assertRaises(ConfigurationError,
                          self._callFUT,
                          context, 'sosecret', callback=callback,
                          cookie_name='repoze.bfg.auth_tkt',
                          secure=True, include_ip=True, timeout=100,
                          reissue_time=500)

class TestACLAuthorizationPolicyDirective(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, context, **kw):
        from repoze.bfg.zcml import aclauthorizationpolicy
        return aclauthorizationpolicy(context, **kw)
    
    def test_it(self):
        from zope.component import getUtility
        from repoze.bfg.authorization import ACLAuthorizationPolicy
        from repoze.bfg.interfaces import IAuthorizationPolicy
        context = DummyContext()
        def callback(identity, request):
            """ """
        self._callFUT(context)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthorizationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = getUtility(IAuthorizationPolicy)
        self.assertEqual(policy.__class__, ACLAuthorizationPolicy)

class TestDeriveView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, view, *arg, **kw):
        from repoze.bfg.zcml import derive_view
        return derive_view(view, *arg, **kw)

    def _registerLogger(self):
        from repoze.bfg.interfaces import ILogger
        from zope.component import getSiteManager
        logger = DummyLogger()
        sm = getSiteManager()
        sm.registerUtility(logger, ILogger, 'repoze.bfg.debug')
        return logger

    def _registerSettings(self, **d):
        from repoze.bfg.interfaces import ISettings
        from zope.component import getSiteManager
        settings = DummySettings(d)
        sm = getSiteManager()
        sm.registerUtility(settings, ISettings)

    def _registerSecurityPolicy(self, permissive):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.interfaces import IAuthorizationPolicy
        from zope.component import getSiteManager
        policy = DummySecurityPolicy(permissive)
        sm = getSiteManager()
        sm.registerUtility(policy, IAuthenticationPolicy)
        sm.registerUtility(policy, IAuthorizationPolicy)
    
    def test_view_as_function_context_and_request(self):
        def view(context, request):
            return 'OK'
        result = self._callFUT(view)
        self.failUnless(result is view)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(view(None, None), 'OK')
        
    def test_view_as_function_requestonly(self):
        def view(request):
            return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
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
        self.failIf(hasattr(result, '__call_permissive__'))
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
        self.failIf(hasattr(result, '__call_permissive__'))
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
        self.failIf(hasattr(result, '__call_permissive__'))
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
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')

    def test_view_as_instance_context_and_request(self):
        class View:
            def __call__(self, context, request):
                return 'OK'
        view = View()
        result = self._callFUT(view)
        self.failUnless(result is view)
        self.failIf(hasattr(result, '__call_permissive__'))
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
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')

    def test_view_with_debug_authorization_no_authpol(self):
        def view(context, request):
            return 'OK'
        self._registerSettings(debug_authorization=True, reload_templates=True)
        logger = self._registerLogger()
        result = self._callFUT(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        request = DummyRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), 'OK')
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): Allowed "
                         "(no authorization policy in use)")

    def test_view_with_debug_authorization_no_permission(self):
        def view(context, request):
            return 'OK'
        self._registerSettings(debug_authorization=True, reload_templates=True)
        self._registerSecurityPolicy(True)
        logger = self._registerLogger()
        result = self._callFUT(view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        request = DummyRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), 'OK')
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): Allowed ("
                         "no permission registered)")

    def test_view_with_debug_authorization_permission_authpol_permitted(self):
        def view(context, request):
            return 'OK'
        self._registerSettings(debug_authorization=True, reload_templates=True)
        logger = self._registerLogger()
        self._registerSecurityPolicy(True)
        result = self._callFUT(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result.__call_permissive__, view)
        request = DummyRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), 'OK')
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): True")
        
    def test_view_with_debug_authorization_permission_authpol_denied(self):
        from repoze.bfg.security import Unauthorized
        def view(context, request):
            """ """
        self._registerSettings(debug_authorization=True, reload_templates=True)
        logger = self._registerLogger()
        self._registerSecurityPolicy(False)
        result = self._callFUT(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result.__call_permissive__, view)
        request = DummyRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertRaises(Unauthorized, result, None, request)
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): False")

    def test_view_with_debug_authorization_permission_authpol_denied2(self):
        def view(context, request):
            """ """
        self._registerSettings(debug_authorization=True, reload_templates=True)
        logger = self._registerLogger()
        self._registerSecurityPolicy(False)
        result = self._callFUT(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        request.view_name = 'view_name'
        request.url = 'url'
        permitted = result.__permitted__(None, None)
        self.assertEqual(permitted, False)

    def test_view_with_predicates_all(self):
        def view(context, request):
            return '123'
        predicates = []
        def predicate1(context, request):
            predicates.append(True)
            return True
        def predicate2(context, request):
            predicates.append(True)
            return True
        result = self._callFUT(view, predicates=[predicate1, predicate2])
        request = DummyRequest()
        request.method = 'POST'
        next = result(None, None)
        self.assertEqual(next, '123')
        self.assertEqual(predicates, [True, True])

    def test_view_with_predicates_notall(self):
        from repoze.bfg.view import NotFound
        def view(context, request):
            """ """
        predicates = []
        def predicate1(context, request):
            predicates.append(True)
            return True
        def predicate2(context, request):
            predicates.append(True)
            return False
        result = self._callFUT(view, predicates=[predicate1, predicate2])
        request = DummyRequest()
        request.method = 'POST'
        self.assertRaises(NotFound, result, None, None)
        self.assertEqual(predicates, [True, True])

    def test_view_with_predicates_checker(self):
        def view(context, request):
            """ """
        predicates = []
        def predicate1(context, request):
            predicates.append(True)
            return True
        def predicate2(context, request):
            predicates.append(True)
            return True
        result = self._callFUT(view, predicates=[predicate1, predicate2])
        request = DummyRequest()
        request.method = 'POST'
        next = result.__predicated__(None, None)
        self.assertEqual(next, True)
        self.assertEqual(predicates, [True, True])

    def test_view_with_wrapper_viewname(self):
        from webob import Response
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IView
        inner_response = Response('OK')
        def inner_view(context, request):
            return inner_response
        def outer_view(context, request):
            self.assertEqual(request.wrapped_response, inner_response)
            self.assertEqual(request.wrapped_body, inner_response.body)
            self.assertEqual(request.wrapped_view, inner_view)
            return Response('outer ' + request.wrapped_body)
        sm = getSiteManager()
        sm.registerAdapter(outer_view, (None, None), IView, 'owrap')
        result = self._callFUT(inner_view, wrapper_viewname='owrap')
        self.failIf(result is inner_view)
        self.assertEqual(inner_view.__module__, result.__module__)
        self.assertEqual(inner_view.__doc__, result.__doc__)
        request = DummyRequest()
        response = result(None, request)
        self.assertEqual(response.body, 'outer OK')

class TestConnectRouteFunction(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, path, name, factory):
        from repoze.bfg.zcml import connect_route
        return connect_route(path, name, factory)

    def _registerRoutesMapper(self):
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        mapper = DummyMapper()
        from repoze.bfg.interfaces import IRoutesMapper
        gsm.registerUtility(mapper, IRoutesMapper)
        return mapper

    def test_defaults(self):
        mapper = self._registerRoutesMapper()
        self._callFUT('path', 'name', 'factory')
        self.assertEqual(mapper.connections, [('path', 'name', 'factory')])

class TestRouteDirective(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import route
        return route(*arg, **kw)

    def test_defaults(self):
        from repoze.bfg.zcml import connect_route
        context = DummyContext()
        self._callFUT(context, 'name', 'path')
        actions = context.actions
        self.assertEqual(len(actions), 1)

        route_action = actions[0]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(len(route_discriminator), 2)
        self.assertEqual(route_discriminator[0], 'route')
        self.assertEqual(route_discriminator[1], 'name')
        self.assertEqual(route_args, ('path', 'name', None))

    def test_with_view(self):
        from zope.interface import Interface
        from zope.interface import implementedBy
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRouteRequest
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        
        context = DummyContext()
        def view(context, request):
            return '123'
        self._callFUT(context, 'name', 'path', view=view)
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_factory = sm.getUtility(IRouteRequest, 'name')
        request_type = implementedBy(request_factory)
        view_discriminator = view_action['discriminator']
        self.assertEqual(len(view_discriminator), 10)
        self.assertEqual(view_discriminator[0], 'view')
        self.assertEqual(view_discriminator[1], None)
        self.assertEqual(view_discriminator[2],'')
        self.assertEqual(view_discriminator[3], request_type)
        self.assertEqual(view_discriminator[4], IView)
        self.assertEqual(view_discriminator[5], None)
        self.assertEqual(view_discriminator[6], None)
        self.assertEqual(view_discriminator[7], None)
        self.assertEqual(view_discriminator[8], 'name')
        self.assertEqual(view_discriminator[9], None)
        register = view_action['callable']
        register()
        sm = getSiteManager()
        wrapped = sm.adapters.lookup((Interface, request_type), IView, name='')
        request = DummyRequest()
        self.assertEqual(wrapped(None, request), '123')
        
        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(len(route_discriminator), 2)
        self.assertEqual(route_discriminator[0], 'route')
        self.assertEqual(route_discriminator[1], 'name')
        self.assertEqual(route_args, ('path', 'name', None))

    def test_with_view_and_view_for(self):
        from zope.component import getSiteManager
        from zope.interface import implementedBy
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            return '123'
        self._callFUT(context, 'name', 'path', view=view, view_for=IDummy)
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_factory = sm.getUtility(IRouteRequest, 'name')
        request_type = implementedBy(request_factory)
        view_discriminator = view_action['discriminator']
        self.assertEqual(len(view_discriminator), 10)
        self.assertEqual(view_discriminator[0], 'view')
        self.assertEqual(view_discriminator[1], IDummy)
        self.assertEqual(view_discriminator[2],'')
        self.assertEqual(view_discriminator[3], request_type)
        self.assertEqual(view_discriminator[4], IView) 
        self.assertEqual(view_discriminator[5], None)
        self.assertEqual(view_discriminator[6], None)
        self.assertEqual(view_discriminator[7], None)
        self.assertEqual(view_discriminator[8], 'name')
        self.assertEqual(view_discriminator[9], None)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        request = DummyRequest()
        self.assertEqual(wrapped(None, request), '123')
        
        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(len(route_discriminator), 2)
        self.assertEqual(route_discriminator[0], 'route')
        self.assertEqual(route_discriminator[1], 'name')
        self.assertEqual(route_args, ('path', 'name', None,))

    def test_without_view(self):
        from repoze.bfg.zcml import connect_route
        context = DummyContext()
        self._callFUT(context, 'name', 'path')
        actions = context.actions
        self.assertEqual(len(actions), 1)

        route_action = actions[0]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(len(route_discriminator), 2)
        self.assertEqual(route_discriminator[0], 'route')
        self.assertEqual(route_discriminator[1], 'name')
        self.assertEqual(route_args, ('path', 'name', None))

    def test_with_view_request_type(self):
        from zope.component import getSiteManager
        from zope.interface import implementedBy
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view,
                      view_request_type="GET")
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_factory = sm.getUtility(IRouteRequest, 'name')
        request_type = implementedBy(request_factory)
        view_discriminator = view_action['discriminator']
        self.assertEqual(len(view_discriminator), 10)
        self.assertEqual(view_discriminator[0], 'view')
        self.assertEqual(view_discriminator[1], None)
        self.assertEqual(view_discriminator[2],'')
        self.assertEqual(view_discriminator[3], request_type)
        self.assertEqual(view_discriminator[4], IView) 
        self.assertEqual(view_discriminator[5], None)
        self.assertEqual(view_discriminator[6], None)
        self.assertEqual(view_discriminator[7], 'GET')
        self.assertEqual(view_discriminator[8], 'name')
        self.assertEqual(view_discriminator[9], None)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(len(route_discriminator), 2)
        self.assertEqual(route_discriminator[0], 'route')
        self.assertEqual(route_discriminator[1], 'name')
        self.assertEqual(route_args, ('path', 'name', None))

    def test_with_view_request_type_alias(self):
        from zope.component import getSiteManager
        from zope.interface import implementedBy
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view, request_type="GET")
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_factory = sm.getUtility(IRouteRequest, 'name')
        request_type = implementedBy(request_factory)
        view_discriminator = view_action['discriminator']
        self.assertEqual(len(view_discriminator), 10)
        self.assertEqual(view_discriminator[0], 'view')
        self.assertEqual(view_discriminator[1], None)
        self.assertEqual(view_discriminator[2],'')
        self.assertEqual(view_discriminator[3], request_type)
        self.assertEqual(view_discriminator[4], IView) 
        self.assertEqual(view_discriminator[5], None)
        self.assertEqual(view_discriminator[6], None)
        self.assertEqual(view_discriminator[7], 'GET')
        self.assertEqual(view_discriminator[8], 'name')
        self.assertEqual(view_discriminator[9], None)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(len(route_discriminator), 2)
        self.assertEqual(route_discriminator[0], 'route')
        self.assertEqual(route_discriminator[1], 'name')
        self.assertEqual(route_args, ('path', 'name', None))

    def test_with_view_request_method(self):
        from zope.component import getSiteManager
        from zope.interface import implementedBy
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view,
                      view_request_method="GET")
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_factory = sm.getUtility(IRouteRequest, 'name')
        request_type = implementedBy(request_factory)
        view_discriminator = view_action['discriminator']
        self.assertEqual(len(view_discriminator), 10)
        self.assertEqual(view_discriminator[0], 'view')
        self.assertEqual(view_discriminator[1], None)
        self.assertEqual(view_discriminator[2],'')
        self.assertEqual(view_discriminator[3], request_type)
        self.assertEqual(view_discriminator[4], IView) 
        self.assertEqual(view_discriminator[5], None)
        self.assertEqual(view_discriminator[6], None)
        self.assertEqual(view_discriminator[7], 'GET')
        self.assertEqual(view_discriminator[8], 'name')
        self.assertEqual(view_discriminator[9], None)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(len(route_discriminator), 2)
        self.assertEqual(route_discriminator[0], 'route')
        self.assertEqual(route_discriminator[1], 'name')
        self.assertEqual(route_args, ('path', 'name', None))

    def test_with_view_request_method_alias(self):
        from zope.component import getSiteManager
        from zope.interface import implementedBy
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view, request_method="GET")
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_factory = sm.getUtility(IRouteRequest, 'name')
        request_type = implementedBy(request_factory)
        view_discriminator = view_action['discriminator']
        self.assertEqual(len(view_discriminator), 10)
        self.assertEqual(view_discriminator[0], 'view')
        self.assertEqual(view_discriminator[1], None)
        self.assertEqual(view_discriminator[2],'')
        self.assertEqual(view_discriminator[3], request_type)
        self.assertEqual(view_discriminator[4], IView) 
        self.assertEqual(view_discriminator[5], None)
        self.assertEqual(view_discriminator[6], None)
        self.assertEqual(view_discriminator[7], 'GET')
        self.assertEqual(view_discriminator[8], 'name')
        self.assertEqual(view_discriminator[9], None)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(len(route_discriminator), 2)
        self.assertEqual(route_discriminator[0], 'route')
        self.assertEqual(route_discriminator[1], 'name')
        self.assertEqual(route_args, ('path', 'name', None))

    def test_with_view_containment(self):
        from zope.component import getSiteManager
        from zope.interface import implementedBy
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view, view_containment=True)
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_factory = sm.getUtility(IRouteRequest, 'name')
        request_type = implementedBy(request_factory)
        view_discriminator = view_action['discriminator']
        self.assertEqual(len(view_discriminator), 10)
        self.assertEqual(view_discriminator[0], 'view')
        self.assertEqual(view_discriminator[1], None)
        self.assertEqual(view_discriminator[2],'')
        self.assertEqual(view_discriminator[3], request_type)
        self.assertEqual(view_discriminator[4], IView) 
        self.assertEqual(view_discriminator[5], True)
        self.assertEqual(view_discriminator[6], None)
        self.assertEqual(view_discriminator[7], None)
        self.assertEqual(view_discriminator[8], 'name')
        self.assertEqual(view_discriminator[9], None)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(len(route_discriminator), 2)
        self.assertEqual(route_discriminator[0], 'route')
        self.assertEqual(route_discriminator[1], 'name')
        self.assertEqual(route_args, ('path', 'name', None))

    def test_with_view_containment_alias(self):
        from zope.component import getSiteManager
        from zope.interface import implementedBy
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view, containment=True)
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_factory = sm.getUtility(IRouteRequest, 'name')
        request_type = implementedBy(request_factory)
        view_discriminator = view_action['discriminator']
        self.assertEqual(len(view_discriminator), 10)
        self.assertEqual(view_discriminator[0], 'view')
        self.assertEqual(view_discriminator[1], None)
        self.assertEqual(view_discriminator[2],'')
        self.assertEqual(view_discriminator[3], request_type)
        self.assertEqual(view_discriminator[4], IView) 
        self.assertEqual(view_discriminator[5], True)
        self.assertEqual(view_discriminator[6], None)
        self.assertEqual(view_discriminator[7], None)
        self.assertEqual(view_discriminator[8], 'name')
        self.assertEqual(view_discriminator[9], None)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(len(route_discriminator), 2)
        self.assertEqual(route_discriminator[0], 'route')
        self.assertEqual(route_discriminator[1], 'name')
        self.assertEqual(route_args, ('path', 'name', None))

class TestStaticDirective(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import static
        return static(*arg, **kw)

    def test_absolute(self):
        from paste.urlparser import StaticURLParser
        from zope.interface import implementedBy
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.zcml import StaticRootFactory
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        import os
        here = os.path.dirname(__file__)
        static_path = os.path.join(here, 'fixtures', 'static')
        context = DummyContext()
        self._callFUT(context, 'name', static_path)
        actions = context.actions
        self.assertEqual(len(actions), 2)

        action = actions[0]
        discriminator = action['discriminator']
        self.assertEqual(discriminator[:3], ('view', StaticRootFactory, ''))
        self.assertEqual(discriminator[4], IView)
        sm = getSiteManager()
        register = action['callable']
        register()
        sm = getSiteManager()
        iface = implementedBy(StaticRootFactory)
        request_factory = sm.getUtility(IRouteRequest, 'name')
        request_type = implementedBy(request_factory)
        wrapped = sm.adapters.lookup((iface, request_type), IView, name='')
        request = DummyRequest()
        self.assertEqual(wrapped(None, request).__class__, StaticURLParser)

        action = actions[1]
        callable = action['callable']
        discriminator = action['discriminator']
        args = action['args']
        self.assertEqual(callable, connect_route)
        self.assertEqual(discriminator, ('route', 'name'))
        self.assertEqual(args[0], 'name*subpath')

    def test_package_relative(self):
        from repoze.bfg.static import PackageURLParser
        from zope.component import getSiteManager
        from zope.interface import implementedBy
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.zcml import StaticRootFactory
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        context = DummyContext()
        self._callFUT(context, 'name', 'repoze.bfg.tests:fixtures/static')
        actions = context.actions
        self.assertEqual(len(actions), 2)

        action = actions[0]
        discriminator = action['discriminator']
        self.assertEqual(discriminator[:3], ('view', StaticRootFactory, ''))
        self.assertEqual(discriminator[4], IView)
        register = action['callable']
        register()
        sm = getSiteManager()
        iface = implementedBy(StaticRootFactory)
        request_factory = sm.getUtility(IRouteRequest, 'name')
        request_type = implementedBy(request_factory)
        view = sm.adapters.lookup((iface, request_type), IView, name='')
        request = DummyRequest()
        self.assertEqual(view(None, request).__class__, PackageURLParser)

        action = actions[1]
        callable = action['callable']
        discriminator = action['discriminator']
        args = action['args']
        self.assertEqual(callable, connect_route)
        self.assertEqual(discriminator, ('route', 'name'))
        self.assertEqual(args[0], 'name*subpath')

    def test_here_relative(self):
        from repoze.bfg.static import PackageURLParser
        from zope.component import getSiteManager
        from zope.interface import implementedBy
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.zcml import StaticRootFactory
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        import repoze.bfg.tests
        context = DummyContext(repoze.bfg.tests)
        self._callFUT(context, 'name', 'fixtures/static')
        actions = context.actions
        self.assertEqual(len(actions), 2)

        action = actions[0]
        discriminator = action['discriminator']
        self.assertEqual(discriminator[:3], ('view', StaticRootFactory, ''))
        self.assertEqual(discriminator[4], IView)
        register = action['callable']
        register()
        sm = getSiteManager()
        iface = implementedBy(StaticRootFactory)
        request_factory = sm.getUtility(IRouteRequest, 'name')
        request_type = implementedBy(request_factory)
        wrapped = sm.adapters.lookup((iface, request_type), IView, name='')
        request = DummyRequest()
        self.assertEqual(wrapped(None, request).__class__, PackageURLParser)

        action = actions[1]
        callable = action['callable']
        discriminator = action['discriminator']
        args = action['args']
        self.assertEqual(callable, connect_route)
        self.assertEqual(discriminator, ('route', 'name'))
        self.assertEqual(args[0], 'name*subpath')

class TestResourceDirective(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import resource
        return resource(*arg, **kw)

    def test_samename(self):
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, self._callFUT, context, 'a', 'a')

    def test_override_directory_with_file(self):
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, self._callFUT, context,
                          'a:foo/', 'a:foo.pt')

    def test_override_file_with_directory(self):
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, self._callFUT, context,
                          'a:foo.pt', 'a:foo/')

    def test_no_colons(self):
        from repoze.bfg.zcml import _override
        context = DummyContext()
        self._callFUT(context, 'a', 'b')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action['callable'], _override)
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['args'],
                         (DummyModule, '', DummyModule, ''))

    def test_with_colons(self):
        from repoze.bfg.zcml import _override
        context = DummyContext()
        self._callFUT(context, 'a:foo.pt', 'b:foo.pt')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action['callable'], _override)
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['args'],
                         (DummyModule, 'foo.pt', DummyModule, 'foo.pt'))

    def test_override_module_with_directory(self):
        from repoze.bfg.zcml import _override
        context = DummyContext()
        self._callFUT(context, 'a', 'b:foo/')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action['callable'], _override)
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['args'],
                         (DummyModule, '', DummyModule, 'foo/'))

    def test_override_directory_with_module(self):
        from repoze.bfg.zcml import _override
        context = DummyContext()
        self._callFUT(context, 'a:foo/', 'b')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action['callable'], _override)
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['args'],
                         (DummyModule, 'foo/', DummyModule, ''))

    def test_override_module_with_module(self):
        from repoze.bfg.zcml import _override
        context = DummyContext()
        self._callFUT(context, 'a', 'b')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action['callable'], _override)
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['args'],
                         (DummyModule, '', DummyModule, ''))

class Test_OverrideFunction(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import _override
        return _override(*arg, **kw)

    def _registerOverrides(self, overrides, package_name):
        from repoze.bfg.interfaces import IPackageOverrides
        from zope.component import getSiteManager
        sm = getSiteManager()
        sm.registerUtility(overrides, IPackageOverrides, name=package_name)

    def test_overrides_not_yet_registered(self):
        from zope.component import queryUtility
        from repoze.bfg.interfaces import IPackageOverrides
        package = DummyPackage('package')
        opackage = DummyPackage('opackage')
        self._callFUT(package, 'path', opackage, 'oprefix',
                      PackageOverrides=DummyOverrides)
        overrides = queryUtility(IPackageOverrides, name='package')
        self.assertEqual(overrides.package, package)
        self.assertEqual(overrides.inserted, [('path', 'opackage', 'oprefix')])

    def test_overrides_already_registered(self):
        package = DummyPackage('package')
        opackage = DummyPackage('opackage')
        overrides = DummyOverrides(package)
        self._registerOverrides(overrides, 'package')
        self._callFUT(package, 'path', opackage, 'oprefix')
        self.assertEqual(overrides.inserted, [('path', 'opackage', 'oprefix')])

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
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from zope.interface import Interface
        grokker = self._makeOne()
        class obj:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        obj.__is_bfg_view__ = True
        obj.__permission__ = 'foo'
        obj.__for__ = Interface
        obj.__view_name__ = 'foo.html'
        obj.__request_type__ = IRequest
        obj.__route_name__ = None
        obj.__request_method__ = None
        obj.__request_param__ = None
        obj.__containment__ = None
        obj.__attr__ = None
        obj.__template__ = None
        obj.__wrapper_viewname__ = None
        context = DummyContext()
        result = grokker.grok('name', obj, context=context)
        self.assertEqual(result, True)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        register = actions[0]['callable']
        register()
        sm = getSiteManager()
        wrapped = sm.adapters.lookup((Interface, IRequest), IView,
                                     name='foo.html')
        self.assertEqual(wrapped(None, None), 'OK')

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

class TestAll(unittest.TestCase):
    def test_it(self):
        from repoze.bfg.zcml import all
        self.assertEqual(all([True, True]), True)
        self.assertEqual(all([False, False]), False)
        self.assertEqual(all([False, True]), False)

class TestStaticRootFactory(unittest.TestCase):
    def test_it(self):
        from repoze.bfg.zcml import StaticRootFactory
        StaticRootFactory({}) # it just needs construction

class DummyModule:
    __path__ = "foo"
    __name__ = "dummy"
    __file__ = ''

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
    def __init__(self, resolved=DummyModule):
        self.actions = []
        self.info = None
        self.resolved = resolved

    def action(self, discriminator, callable=None, args=(), kw={}, order=0):
        self.actions.append(
            {'discriminator':discriminator,
             'callable':callable,
             'args':args}
            )

    def resolve(self, dottedname):
        return self.resolved

class Dummy:
    pass

class DummyMapper:
    def __init__(self):
        self.connections = []

    def connect(self, *args):
        self.connections.append(args)

class DummyRoute:
    pass

from zope.interface import Interface
class IDummy(Interface):
    pass

class DummyLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(msg)
    warn = info
    debug = info

class DummyRequest:
    subpath = ()
    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ
        
    def get_response(self, app):
        return app

    def copy(self):
        return self

class DummyOverrides:
    def __init__(self, package):
        self.package = package
        self.inserted = []

    def insert(self, path, package, prefix):
        self.inserted.append((path, package, prefix))
        
class DummyPackage:
    def __init__(self, name):
        self.__name__ = name
        
class DummySettings(dict):
    def __getattr__(self, name):
        return self[name]
    
class DummySecurityPolicy:
    def __init__(self, permitted=True):
        self.permitted = permitted

    def effective_principals(self, request):
        return []

    def permits(self, context, principals, permission):
        return self.permitted

