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
                   None, False, None, None, None)
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
                   None, False, None, None, None)
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
                   None, False, None, None, None)
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
                   None, False, None, None, None)
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
                   None, False, None, None, None)
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
                   None, False, None, None, None)
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
                   None, False, None, None, None)
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
                   None, False, None, None, None)
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
        from repoze.bfg.interfaces import IRendererFactory
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

        class Renderer:
            def __call__(self, path):
                self.path = path
                return lambda *arg: 'Hello!'

        renderer = Renderer()
        sm = getSiteManager()
        sm.registerUtility(renderer, IRendererFactory, name='.txt')

        fixture = 'fixtures/minimal.txt'
        self._callFUT(context, 'repoze.view', IFoo, view=view, renderer=fixture)
        actions = context.actions
        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None, False, None, None, None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        request = DummyRequest()
        result = wrapper(None, request)
        self.assertEqual(result.body, 'Hello!')
        self.assertEqual(renderer.path, 'repoze.bfg.tests:fixtures/minimal.txt')

    def test_with_template_no_view_callable(self):
        from zope.interface import Interface
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRendererFactory

        import repoze.bfg.tests

        context = DummyContext(repoze.bfg.tests)
        class IFoo(Interface):
            pass
        sm = getSiteManager()
        def renderer_factory(path):
            return lambda *arg: 'Hello!'
        sm.registerUtility(renderer_factory, IRendererFactory, name='.txt')

        self._callFUT(context, 'repoze.view', IFoo, renderer='foo.txt')
        actions = context.actions
        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None, False, None, None, None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.environ = {}
        result = wrapper(None, request)
        self.assertEqual(result.body, 'Hello!')

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
                   None, False, None, None, None)
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
        discrim = ('view', IFoo, '', Dummy, IView, None, None, None, None,
                   None, False, None, None, None)
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
                   None, False, None, None, None)
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
                   None, False, None, None, None)
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
        request_type = sm.getUtility(IRouteRequest, 'foo')
        discrim = ('view', IFoo, '', request_type, IView, None, None, None,
                   'foo', None, False, None, None, None)
        self.assertEqual(action['discriminator'], discrim)
        the_view = sm.adapters.lookup((IFoo, request_type), IView, name='')
        request = DummyRequest({})
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
                   None, False, None, None, None)
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
        from repoze.bfg.exceptions import NotFound
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
                   None, False, None, None, None)
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
                   None, False, None, None, None)
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
        from repoze.bfg.exceptions import NotFound
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
                   None, False, None, None, None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.params = {}
        self.assertRaises(NotFound, wrapper, None, request)

    def test_with_request_param_val_true(self):
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
        discrim = ('view', IFoo, '', IRequest, IView, None, 'abc=123', None,
                   None, None, False, None, None, None)
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
        from repoze.bfg.exceptions import NotFound
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
        discrim = ('view', IFoo, '', IRequest, IView, None, 'abc=123', None,
                   None, None, False, None, None, None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.params = {'abc':'456'}
        self.assertRaises(NotFound, wrapper, None, request)

    def test_with_xhr_true(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        class IFoo(Interface):
            pass
        context = DummyContext()
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            return '123'
        self._callFUT(context, None, IFoo, view=view, xhr=True)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None, True, None, None, None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), '123')

    def test_with_xhr_false(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.exceptions import NotFound
        class IFoo(Interface):
            pass
        context = DummyContext()
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            """ """
        self._callFUT(context, None, IFoo, view=view, xhr=True)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None, True, None, None, None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.is_xhr = False
        self.assertRaises(NotFound, wrapper, None, request)

    def test_with_header_badregex(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from zope.configuration.exceptions import ConfigurationError
        class IFoo(Interface):
            pass
        context = DummyContext()
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            """ """
        self.assertRaises(ConfigurationError, self._callFUT,
                          context, None, IFoo,
                          view=view, header='Host:a\\')

    def test_with_header_noval_match(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        class IFoo(Interface):
            pass
        context = DummyContext()
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            return '123'
        self._callFUT(context, None, IFoo, view=view, header='Host')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None, False, None, 'Host', None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.headers  = {'Host':'whatever'}
        self.assertEqual(wrapper(None, request), '123')

    def test_with_header_noval_nomatch(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.exceptions import NotFound
        class IFoo(Interface):
            pass
        context = DummyContext()
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            """ """
        self._callFUT(context, None, IFoo, view=view, header='Host')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None, False, None, 'Host', None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.headers  = {'NotHost':'whatever'}
        self.assertRaises(NotFound, wrapper, None, request)

    def test_with_header_val_match(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        class IFoo(Interface):
            pass
        context = DummyContext()
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            return '123'
        self._callFUT(context, None, IFoo, view=view, header=r'Host:\d')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None, False, None, r'Host:\d', None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.headers  = {'Host':'1'}
        self.assertEqual(wrapper(None, request), '123')

    def test_with_header_val_nomatch(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.exceptions import NotFound
        class IFoo(Interface):
            pass
        context = DummyContext()
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            """ """
        self._callFUT(context, None, IFoo, view=view, header=r'Host:\d')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None, False, None, r'Host:\d', None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.headers  = {'Host':'abc'}
        self.assertRaises(NotFound, wrapper, None, request)

    def test_with_accept_match(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        class IFoo(Interface):
            pass
        context = DummyContext()
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            return '123'
        self._callFUT(context, None, IFoo, view=view, accept='text/xml')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None, False, 'text/xml', None, None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.accept = ['text/xml']
        self.assertEqual(wrapper(None, request), '123')

    def test_with_accept_nomatch(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.exceptions import NotFound
        class IFoo(Interface):
            pass
        context = DummyContext()
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            """ """
        self._callFUT(context, None, IFoo, view=view, accept='text/xml')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None, False, 'text/xml', None, None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.accept = ['text/html']
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
                   None, False, None, None, None)
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
        from repoze.bfg.exceptions import NotFound
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
                   None, False, None, None, None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        context = Dummy()
        self.assertRaises(NotFound, wrapper, context, request)

    def test_with_path_info_badregex(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from zope.configuration.exceptions import ConfigurationError
        class IFoo(Interface):
            pass
        context = DummyContext()
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            """ """
        self.assertRaises(ConfigurationError, self._callFUT,
                          context, None, IFoo,
                          view=view, path_info='\\')

    def test_with_path_info_match(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        class IFoo(Interface):
            pass
        context = DummyContext()
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request):
            return '123'
        self._callFUT(context, None, IFoo, view=view, path_info='/foo')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None, False, None, None, '/foo')
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest({'PATH_INFO': '/foo'})
        self.assertEqual(wrapper(None, request), '123')

    def test_with_path_info_nomatch(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.exceptions import NotFound
        class IFoo(Interface):
            pass
        context = DummyContext()
        view = lambda *arg: None
        sm = getSiteManager()
        def view(context, request): pass
        self._callFUT(context, None, IFoo, view=view, path_info='/boo')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None, False, None, None, '/boo')
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest({'PATH_INFO': '/foo'})
        self.assertRaises(NotFound, wrapper, None, request)

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
        sm = getSiteManager()
        def view(context, request):
            return '123'
        sm.registerAdapter(view, (IFoo, IRequest), IView, name='')
        self._callFUT(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None, False, None, None, None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        self.failUnless(IMultiView.providedBy(wrapper))
        perm = sm.adapters.lookup((IFoo, IRequest), IViewPermission, name='')
        self.assertEqual(perm, wrapper.__permitted__)
        self.assertEqual(wrapper(None, None), '123')

    def test_multiview_call_ordering(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        context = DummyContext()
        class IFoo(Interface):
            pass
        def view1(context, request): return 'view1'
        def view2(context, request): return 'view2'
        def view3(context, request): return 'view3'
        def view4(context, request): return 'view4'
        def view5(context, request): return 'view5'
        def view6(context, request): return 'view6'
        def view7(context, request): return 'view7'
        def view8(context, request): return 'view8'
        self._callFUT(context, 'repoze.view', IFoo, view=view1)
        self._callFUT(context, 'repoze.view', IFoo, view=view2,
                      request_method='POST')
        self._callFUT(context, 'repoze.view', IFoo, view=view3,
                      request_param='param')
        self._callFUT(context, 'repoze.view', IFoo, view=view4,
                      containment=IFoo)
        self._callFUT(context, 'repoze.view', IFoo, view=view5,
                      request_method='POST', request_param='param')
        self._callFUT(context, 'repoze.view', IFoo, view=view6,
                      request_method='POST', containment=IFoo)
        self._callFUT(context, 'repoze.view', IFoo, view=view7,
                      request_param='param', containment=IFoo)
        self._callFUT(context, 'repoze.view', IFoo, view=view8,
                      request_type='POST', request_param='param',
                      containment=IFoo)
        for action in context.actions:
            register = action['callable']
            register()

        sm = getSiteManager()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')

        ctx = Dummy()
        request = DummyRequest()
        request.method = 'GET'
        request.params = {}
        self.assertEqual(wrapper(ctx, request), 'view1')

        ctx = Dummy()
        request = DummyRequest()
        request.params = {}
        request.method = 'POST'
        self.assertEqual(wrapper(ctx, request), 'view2')

        ctx = Dummy()
        request = DummyRequest()
        request.params = {'param':'1'}
        request.method = 'GET'
        self.assertEqual(wrapper(ctx, request), 'view3')

        ctx = Dummy()
        directlyProvides(ctx, IFoo)
        request = DummyRequest()
        request.method = 'GET'
        request.params = {}
        self.assertEqual(wrapper(ctx, request), 'view4')

        ctx = Dummy()
        request = DummyRequest()
        request.method = 'POST'
        request.params = {'param':'1'}
        self.assertEqual(wrapper(ctx, request), 'view5')

        ctx = Dummy()
        directlyProvides(ctx, IFoo)
        request = DummyRequest()
        request.params = {}
        request.method = 'POST'
        self.assertEqual(wrapper(ctx, request), 'view6')

        ctx = Dummy()
        directlyProvides(ctx, IFoo)
        request = DummyRequest()
        request.method = 'GET'
        request.params = {'param':'1'}
        self.assertEqual(wrapper(ctx, request), 'view7')

        ctx = Dummy()
        directlyProvides(ctx, IFoo)
        request = DummyRequest()
        request.method = 'POST'
        request.params = {'param':'1'}
        self.assertEqual(wrapper(ctx, request), 'view8')

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
                   None, False, None, None, None)
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
                   None, False, None, None, None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        foo = implementedBy(Foo)
        wrapper = sm.adapters.lookup((foo, IRequest), IView, name='')
        self.assertEqual(wrapper, view)

class TestNotFoundDirective(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
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
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
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

class TestViewUtility(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, context, view, attr, renderer, wrapper, iface):
        from repoze.bfg.zcml import view_utility
        return view_utility(context, view, attr, renderer, wrapper, iface)

    def test_no_view_no_renderer(self):
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, self._callFUT, context,
                          None, None, None, None, None)
    
    def test_no_view_with_renderer(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRendererFactory
        sm = getSiteManager()
        def renderer(path):
            return lambda *arg: 'OK'
        sm.registerUtility(renderer, IRendererFactory, name='dummy')
        class IDummy(Interface):
            pass
        context = DummyContext()
        self._callFUT(context, None, None, 'dummy', None, IDummy)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IDummy)
        register = regadapt['callable']
        register()
        derived_view = sm.getUtility(IDummy)
        request = DummyRequest()
        self.assertEqual(derived_view(None, request).body, 'OK')

    def test_template_renderer(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRendererFactory
        sm = getSiteManager()
        def renderer(path):
            return lambda *arg: 'OK'
        sm.registerUtility(renderer, IRendererFactory, name='.pt')
        class IDummy(Interface):
            pass
        context = DummyContext()
        self._callFUT(context, None, None, 'fixtures/minimal.pt', None, IDummy)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IDummy)
        register = regadapt['callable']
        register()
        derived_view = sm.getUtility(IDummy)
        request = DummyRequest()
        self.assertEqual(derived_view(None, request).body, 'OK')

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

class TestConnectRouteFunction(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, path, name, factory, predicates):
        from repoze.bfg.zcml import connect_route
        return connect_route(path, name, factory, predicates)

    def _registerRoutesMapper(self):
        from zope.component import getSiteManager
        sm = getSiteManager()
        mapper = DummyMapper()
        from repoze.bfg.interfaces import IRoutesMapper
        sm.registerUtility(mapper, IRoutesMapper)
        return mapper

    def test_defaults(self):
        mapper = self._registerRoutesMapper()
        self._callFUT('path', 'name', 'factory', 'predicates')
        self.assertEqual(mapper.connections, [('path', 'name', 'factory',
                                               'predicates')])

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
        self.assertEqual(
            route_discriminator,
            ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view(self):
        from zope.interface import Interface
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
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
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
        self.assertEqual(
            route_discriminator,
            ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_and_view_for(self):
        from zope.component import getSiteManager
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
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', IDummy, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        request = DummyRequest()
        self.assertEqual(wrapped(None, request), '123')
        
        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_and_view_for_alias(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            return '123'
        self._callFUT(context, 'name', 'path', view=view, for_=IDummy)
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', IDummy, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        request = DummyRequest()
        self.assertEqual(wrapped(None, request), '123')
        
        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

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
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(route_args, ('path', 'name', None, []))

    def test_with_view_request_type(self):
        from zope.component import getSiteManager
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
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, 'GET',
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_request_type_alias(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view,
                      request_type="GET")
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, 'GET',
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_request_method(self):
        from zope.component import getSiteManager
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
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, 'GET',
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_containment(self):
        from zope.component import getSiteManager
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
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, True, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None,None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_header(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view, view_header='Host')
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, None, 'Host', None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None,None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_path_info(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest

        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view, view_path_info='/foo')
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, '/foo')
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_xhr(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view, view_xhr=True)
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, True, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_accept(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view,
                      view_accept='text/xml')
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, 'text/xml', None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(
            route_discriminator,
            ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_renderer(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        from repoze.bfg.interfaces import IRendererFactory
        
        sm = getSiteManager()
        def renderer(name):
            return lambda *x: 'foo'
        sm.registerUtility(renderer, IRendererFactory, name='dummy')
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view,
                      view_renderer="dummy")
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_renderer_alias(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        from repoze.bfg.interfaces import IRendererFactory

        sm = getSiteManager()
        def renderer(name):
            return lambda *x: 'foo'
        sm.registerUtility(renderer, IRendererFactory, name='dummy')
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view,
                      renderer="dummy")
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_permission(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        sm = getSiteManager()
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view,
                      view_permission="edit")
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_permission_alias(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest

        sm = getSiteManager()
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view,
                      permission="edit")
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_for(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        sm = getSiteManager()

        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view,
                      view_for=IDummy)
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', IDummy, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_view_for_alias(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest

        sm = getSiteManager()
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view,
                      for_=IDummy)
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', IDummy, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    def test_with_request_type_GET(self):
        from zope.component import getSiteManager
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
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, 'GET',
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 0)

    # route predicates

    def test_with_xhr(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view, xhr=True)
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', True, None, None, None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 1)
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(predicates[0](None, request), True)

    def test_with_request_method(self):
        from zope.component import getSiteManager
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
        request_type = sm.getUtility(IRouteRequest, 'name')

        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, 'GET',None, None, None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 1)
        request = DummyRequest()
        request.method = 'GET'
        self.assertEqual(predicates[0](None, request), True)

    def test_with_path_info(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest

        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view, path_info='/foo')
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, '/foo',None,None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 1)
        request = DummyRequest()
        request.path_info = '/foo'
        self.assertEqual(predicates[0](None, request), True)

    def test_with_request_param(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view, request_param='abc')
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None,'abc', None, None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 1)
        request = DummyRequest()
        request.params = {'abc':'123'}
        self.assertEqual(predicates[0](None, request), True)

    def test_with_header(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view, header='Host')
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None,None,'Host', None))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 1)
        request = DummyRequest()
        request.headers = {'Host':'example.com'}
        self.assertEqual(predicates[0](None, request), True)

    def test_with_accept(self):
        from zope.component import getSiteManager
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        
        context = DummyContext()
        def view(context, request):
            """ """
        self._callFUT(context, 'name', 'path', view=view, accept='text/xml')
        actions = context.actions
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        register = view_action['callable']
        register()
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')

        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((IDummy, request_type), IView, name='')
        self.failUnless(wrapped)

        route_action = actions[1]
        route_callable = route_action['callable']
        route_discriminator = route_action['discriminator']
        route_args = route_action['args']
        self.assertEqual(route_callable, connect_route)
        self.assertEqual(
            route_discriminator,
            ('route', 'name', False, None, None, None, None, 'text/xml'))
        self.assertEqual(route_args[:3], ('path', 'name', None))
        predicates = route_args[3]
        self.assertEqual(len(predicates), 1)
        request = DummyRequest()
        request.accept = ['text/xml']
        self.assertEqual(predicates[0](None, request), True)

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
        from repoze.bfg.static import StaticRootFactory
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
        request_type = sm.getUtility(IRouteRequest, 'name')
        wrapped = sm.adapters.lookup((iface, request_type), IView, name='')
        request = DummyRequest()
        self.assertEqual(wrapped(None, request).__class__, StaticURLParser)

        action = actions[1]
        callable = action['callable']
        discriminator = action['discriminator']
        args = action['args']
        self.assertEqual(callable, connect_route)
        self.assertEqual(discriminator,
                         ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(args[0], 'name*subpath')

    def test_package_relative(self):
        from repoze.bfg.static import PackageURLParser
        from zope.component import getSiteManager
        from zope.interface import implementedBy
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.static import StaticRootFactory
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
        request_type = sm.getUtility(IRouteRequest, 'name')
        view = sm.adapters.lookup((iface, request_type), IView, name='')
        request = DummyRequest()
        self.assertEqual(view(None, request).__class__, PackageURLParser)

        action = actions[1]
        callable = action['callable']
        discriminator = action['discriminator']
        args = action['args']
        self.assertEqual(callable, connect_route)
        self.assertEqual(discriminator,
                         ('route', 'name', False, None, None, None, None, None))
        self.assertEqual(args[0], 'name*subpath')

    def test_here_relative(self):
        from repoze.bfg.static import PackageURLParser
        from zope.component import getSiteManager
        from zope.interface import implementedBy
        from repoze.bfg.zcml import connect_route
        from repoze.bfg.static import StaticRootFactory
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
        request_type = sm.getUtility(IRouteRequest, 'name')
        wrapped = sm.adapters.lookup((iface, request_type), IView, name='')
        request = DummyRequest()
        self.assertEqual(wrapped(None, request).__class__, PackageURLParser)

        action = actions[1]
        callable = action['callable']
        discriminator = action['discriminator']
        args = action['args']
        self.assertEqual(callable, connect_route)
        self.assertEqual(discriminator,
                         ('route', 'name', False, None, None, None, None, None))
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

class TestBFGViewGrokker(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.zcml import BFGViewGrokker
        return BFGViewGrokker

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
        settings = dict(permission='foo', for_=Interface, name='foo.html',
                        request_type=IRequest, route_name=None,
                        request_method=None, request_param=None,
                        containment=None, attr=None, renderer=None,
                        wrapper=None, xhr=False, header=None,
                        accept=None)
        obj.__bfg_view_settings__ = [settings]
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
        from repoze.bfg.zcml import BFGMultiGrokker
        from repoze.bfg.zcml import exclude
        martian = DummyMartianModule()
        module_grokker = DummyModuleGrokker()
        dummy_module = DummyModule()
        self._callFUT(None, dummy_module, martian)
        self.assertEqual(martian.name, 'dummy')
        multi_grokker = martian.module_grokker.multi_grokker
        self.assertEqual(multi_grokker.__class__, BFGMultiGrokker)
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

class DummyModule:
    __path__ = "foo"
    __name__ = "dummy"
    __file__ = ''

class DummyModuleGrokker:
    def __init__(self, grokker=None):
        self.multi_grokker = grokker
        
class DummyMartianModule:
    def grok_dotted_name(self, name, grokker, context, exclude_filter=None):
        self.name = name
        self.context = context
        self.exclude_filter = exclude_filter
        return True

    def ModuleGrokker(self, grokker=None):
        self.module_grokker = DummyModuleGrokker(grokker)
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

    def connect(self, path, name, factory, predicates=()):
        self.connections.append((path, name, factory, predicates))

class DummyRoute:
    pass

from zope.interface import Interface
class IDummy(Interface):
    pass

class DummyRequest:
    subpath = ()
    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ
        self.path_info = environ.get('PATH_INFO', None)

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
        
