import unittest

from pyramid import testing

import os

here = os.path.dirname(__file__)
locale = os.path.abspath(
    os.path.join(here, '..', 'localeapp', 'locale'))
locale2 = os.path.abspath(
    os.path.join(here, '..', 'localeapp', 'locale2'))
locale3 = os.path.abspath(
    os.path.join(here, '..', 'localeapp', 'locale3'))

from pyramid.tests.test_config import dummy_tween_factory
from pyramid.tests.test_config import dummy_tween_factory2
from pyramid.tests.test_config import dummyfactory
from pyramid.tests.test_config import dummy_include
from pyramid.tests.test_config import dummy_view
from pyramid.tests.test_config import dummy_extend
from pyramid.tests.test_config import dummy_extend2
from pyramid.tests.test_config import IDummy

try:
    import __pypy__
except:
    __pypy__ = None

class ConfiguratorTests(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid.config import Configurator
        config = Configurator(*arg, **kw)
        return config

    def _registerRenderer(self, config, name='.txt'):
        from pyramid.interfaces import IRendererFactory
        from pyramid.interfaces import ITemplateRenderer
        from zope.interface import implements
        class Renderer:
            implements(ITemplateRenderer)
            def __init__(self, info):
                self.__class__.info = info
            def __call__(self, *arg):
                return 'Hello!'
        config.registry.registerUtility(Renderer, IRendererFactory, name=name)
        return Renderer

    def _getViewCallable(self, config, ctx_iface=None, request_iface=None,
                         name='', exception_view=False):
        from zope.interface import Interface
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        if exception_view:
            classifier = IExceptionViewClassifier
        else:
            classifier = IViewClassifier
        if ctx_iface is None:
            ctx_iface = Interface
        if request_iface is None:
            request_iface = IRequest
        return config.registry.adapters.lookup(
            (classifier, request_iface, ctx_iface), IView, name=name,
            default=None)

    def _getRouteRequestIface(self, config, name):
        from pyramid.interfaces import IRouteRequest
        iface = config.registry.getUtility(IRouteRequest, name)
        return iface

    def _assertNotFound(self, wrapper, *arg):
        from pyramid.httpexceptions import HTTPNotFound
        self.assertRaises(HTTPNotFound, wrapper, *arg)

    def _registerEventListener(self, config, event_iface=None):
        if event_iface is None: # pragma: no cover
            from zope.interface import Interface
            event_iface = Interface
        L = []
        def subscriber(*event):
            L.extend(event)
        config.registry.registerHandler(subscriber, (event_iface,))
        return L

    def _makeRequest(self, config):
        request = DummyRequest()
        request.registry = config.registry
        return request

    def _conflictFunctions(self, e):
        conflicts = e._conflicts.values()
        for conflict in conflicts:
            for confinst in conflict:
                yield confinst[2]

    def test_ctor_no_registry(self):
        import sys
        from pyramid.interfaces import ISettings
        from pyramid.config import Configurator
        from pyramid.interfaces import IRendererFactory
        config = Configurator()
        this_pkg = sys.modules['pyramid.tests.test_config']
        self.assertTrue(config.registry.getUtility(ISettings))
        self.assertEqual(config.package, this_pkg)
        self.assertTrue(config.registry.getUtility(IRendererFactory, 'json'))
        self.assertTrue(config.registry.getUtility(IRendererFactory, 'string'))
        if not __pypy__:
            self.assertTrue(config.registry.getUtility(IRendererFactory, '.pt'))
            self.assertTrue(config.registry.getUtility(IRendererFactory,'.txt'))
        self.assertTrue(config.registry.getUtility(IRendererFactory, '.mak'))
        self.assertTrue(config.registry.getUtility(IRendererFactory, '.mako'))

    def test__set_settings_as_None(self):
        config = self._makeOne()
        settings = config._set_settings(None)
        self.assertTrue(settings)

    def test__set_settings_as_dictwithvalues(self):
        config = self._makeOne()
        settings = config._set_settings({'a':'1'})
        self.assertEqual(settings['a'], '1')

    def test_begin(self):
        from pyramid.config import Configurator
        config = Configurator()
        manager = DummyThreadLocalManager()
        config.manager = manager
        config.begin()
        self.assertEqual(manager.pushed,
                         {'registry':config.registry, 'request':None})
        self.assertEqual(manager.popped, False)

    def test_begin_with_request(self):
        from pyramid.config import Configurator
        config = Configurator()
        request = object()
        manager = DummyThreadLocalManager()
        config.manager = manager
        config.begin(request=request)
        self.assertEqual(manager.pushed,
                         {'registry':config.registry, 'request':request})
        self.assertEqual(manager.popped, False)

    def test_end(self):
        from pyramid.config import Configurator
        config = Configurator()
        manager = DummyThreadLocalManager()
        config.manager = manager
        config.end()
        self.assertEqual(manager.pushed, None)
        self.assertEqual(manager.popped, True)

    def test_ctor_with_package_registry(self):
        import sys
        from pyramid.config import Configurator
        pkg = sys.modules['pyramid']
        config = Configurator(package=pkg)
        self.assertEqual(config.package, pkg)

    def test_ctor_noreg_custom_settings(self):
        from pyramid.interfaces import ISettings
        settings = {'reload_templates':True,
                    'mysetting':True}
        config = self._makeOne(settings=settings)
        settings = config.registry.getUtility(ISettings)
        self.assertEqual(settings['reload_templates'], True)
        self.assertEqual(settings['debug_authorization'], False)
        self.assertEqual(settings['mysetting'], True)

    def test_ctor_noreg_debug_logger_None_default(self):
        from pyramid.interfaces import IDebugLogger
        config = self._makeOne()
        logger = config.registry.getUtility(IDebugLogger)
        self.assertEqual(logger.name, 'pyramid.tests.test_config')

    def test_ctor_noreg_debug_logger_non_None(self):
        from pyramid.interfaces import IDebugLogger
        logger = object()
        config = self._makeOne(debug_logger=logger)
        result = config.registry.getUtility(IDebugLogger)
        self.assertEqual(logger, result)

    def test_ctor_authentication_policy(self):
        from pyramid.interfaces import IAuthenticationPolicy
        policy = object()
        config = self._makeOne(authentication_policy=policy)
        result = config.registry.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy, result)

    def test_ctor_authorization_policy_only(self):
        from zope.configuration.config import ConfigurationExecutionError
        policy = object()
        config = self._makeOne(authorization_policy=policy)
        self.assertRaises(ConfigurationExecutionError, config.commit)

    def test_ctor_no_root_factory(self):
        from pyramid.interfaces import IRootFactory
        config = self._makeOne()
        self.assertEqual(config.registry.queryUtility(IRootFactory), None)
        config.commit()
        self.assertTrue(config.registry.getUtility(IRootFactory))

    def test_ctor_alternate_renderers(self):
        from pyramid.interfaces import IRendererFactory
        renderer = object()
        config = self._makeOne(renderers=[('yeah', renderer)])
        self.assertEqual(config.registry.getUtility(IRendererFactory, 'yeah'),
                         renderer)

    def test_ctor_default_permission(self):
        from pyramid.interfaces import IDefaultPermission
        config = self._makeOne(default_permission='view')
        self.assertEqual(config.registry.getUtility(IDefaultPermission), 'view')

    def test_ctor_session_factory(self):
        from pyramid.interfaces import ISessionFactory
        config = self._makeOne(session_factory='factory')
        self.assertEqual(config.registry.queryUtility(ISessionFactory), None)
        config.commit()
        self.assertEqual(config.registry.getUtility(ISessionFactory), 'factory')

    def test_ctor_default_view_mapper(self):
        from pyramid.interfaces import IViewMapperFactory
        mapper = object()
        config = self._makeOne(default_view_mapper=mapper)
        self.assertEqual(config.registry.getUtility(IViewMapperFactory),
                         mapper)

    def test_ctor_httpexception_view_default(self):
        from pyramid.interfaces import IExceptionResponse
        from pyramid.httpexceptions import default_exceptionresponse_view
        from pyramid.interfaces import IRequest
        config = self._makeOne()
        view = self._getViewCallable(config,
                                     ctx_iface=IExceptionResponse,
                                     request_iface=IRequest)
        self.assertTrue(view.__wraps__ is default_exceptionresponse_view)

    def test_ctor_exceptionresponse_view_None(self):
        from pyramid.interfaces import IExceptionResponse
        from pyramid.interfaces import IRequest
        config = self._makeOne(exceptionresponse_view=None)
        view = self._getViewCallable(config,
                                     ctx_iface=IExceptionResponse,
                                     request_iface=IRequest)
        self.assertTrue(view is None)

    def test_ctor_exceptionresponse_view_custom(self):
        from pyramid.interfaces import IExceptionResponse
        from pyramid.interfaces import IRequest
        def exceptionresponse_view(context, request): pass
        config = self._makeOne(exceptionresponse_view=exceptionresponse_view)
        view = self._getViewCallable(config,
                                     ctx_iface=IExceptionResponse,
                                     request_iface=IRequest)
        self.assertTrue(view.__wraps__ is exceptionresponse_view)

    def test_with_package_module(self):
        from pyramid.tests import test_configuration
        import pyramid.tests
        config = self._makeOne()
        newconfig = config.with_package(test_configuration)
        self.assertEqual(newconfig.package, pyramid.tests)

    def test_with_package_package(self):
        import pyramid.tests
        config = self._makeOne()
        newconfig = config.with_package(pyramid.tests)
        self.assertEqual(newconfig.package, pyramid.tests)

    def test_with_package_context_is_not_None(self):
        import pyramid.tests
        config = self._makeOne()
        config._ctx = DummyContext()
        config._ctx.registry = None
        config._ctx.autocommit = True
        config._ctx.route_prefix = None
        newconfig = config.with_package(pyramid.tests)
        self.assertEqual(newconfig.package, pyramid.tests)

    def test_with_package_context_is_None(self):
        import pyramid.tests
        config = self._makeOne()
        config._ctx = None
        newconfig = config.with_package(pyramid.tests)
        self.assertEqual(newconfig.package, pyramid.tests)
        self.assertEqual(config._ctx.package, None)

    def test_maybe_dotted_string_success(self):
        import pyramid.tests
        config = self._makeOne()
        result = config.maybe_dotted('pyramid.tests')
        self.assertEqual(result, pyramid.tests)

    def test_maybe_dotted_string_fail(self):
        config = self._makeOne()
        self.assertRaises(ImportError,
                          config.maybe_dotted, 'cant.be.found')

    def test_maybe_dotted_notstring_success(self):
        import pyramid.tests
        config = self._makeOne()
        result = config.maybe_dotted(pyramid.tests)
        self.assertEqual(result, pyramid.tests)

    def test_absolute_asset_spec_already_absolute(self):
        import pyramid.tests
        config = self._makeOne(package=pyramid.tests)
        result = config.absolute_asset_spec('already:absolute')
        self.assertEqual(result, 'already:absolute')

    def test_absolute_asset_spec_notastring(self):
        import pyramid.tests
        config = self._makeOne(package=pyramid.tests)
        result = config.absolute_asset_spec(None)
        self.assertEqual(result, None)

    def test_absolute_asset_spec_relative(self):
        import pyramid.tests
        config = self._makeOne(package=pyramid.tests)
        result = config.absolute_asset_spec('templates')
        self.assertEqual(result, 'pyramid.tests:templates')

    def test__fix_registry_has_listeners(self):
        reg = DummyRegistry()
        config = self._makeOne(reg)
        config._fix_registry()
        self.assertEqual(reg.has_listeners, True)

    def test__fix_registry_notify(self):
        reg = DummyRegistry()
        config = self._makeOne(reg)
        config._fix_registry()
        self.assertEqual(reg.notify(1), None)
        self.assertEqual(reg.events, (1,))

    def test__fix_registry_queryAdapterOrSelf(self):
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        class Foo(object):
            implements(IFoo)
        class Bar(object):
            pass
        adaptation = ()
        foo = Foo()
        bar = Bar()
        reg = DummyRegistry(adaptation)
        config = self._makeOne(reg)
        config._fix_registry()
        self.assertTrue(reg.queryAdapterOrSelf(foo, IFoo) is foo)
        self.assertTrue(reg.queryAdapterOrSelf(bar, IFoo) is adaptation)

    def test__fix_registry_registerSelfAdapter(self):
        reg = DummyRegistry()
        config = self._makeOne(reg)
        config._fix_registry()
        reg.registerSelfAdapter('required', 'provided', name='abc')
        self.assertEqual(len(reg.adapters), 1)
        args, kw = reg.adapters[0]
        self.assertEqual(args[0]('abc'), 'abc')
        self.assertEqual(kw,
                         {'info': u'', 'provided': 'provided',
                          'required': 'required', 'name': 'abc', 'event': True})

    def test_setup_registry_calls_fix_registry(self):
        reg = DummyRegistry()
        config = self._makeOne(reg)
        config.add_view = lambda *arg, **kw: False
        config._add_tween = lambda *arg, **kw: False
        config.setup_registry()
        self.assertEqual(reg.has_listeners, True)

    def test_setup_registry_registers_default_exceptionresponse_view(self):
        from webob.exc import WSGIHTTPException
        from pyramid.interfaces import IExceptionResponse
        from pyramid.view import default_exceptionresponse_view
        reg = DummyRegistry()
        config = self._makeOne(reg)
        views = []
        config.add_view = lambda *arg, **kw: views.append((arg, kw))
        config._add_tween = lambda *arg, **kw: False
        config.setup_registry()
        self.assertEqual(views[0], ((default_exceptionresponse_view,),
                                    {'context':IExceptionResponse}))
        self.assertEqual(views[1], ((default_exceptionresponse_view,),
                                    {'context':WSGIHTTPException}))

    def test_setup_registry_registers_default_webob_iresponse_adapter(self):
        from webob import Response
        from pyramid.interfaces import IResponse
        config = self._makeOne()
        config.setup_registry()
        response = Response()
        self.assertTrue(
            config.registry.queryAdapter(response, IResponse) is response)

    def test_setup_registry_explicit_notfound_trumps_iexceptionresponse(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.httpexceptions import HTTPNotFound
        from pyramid.registry import Registry
        reg = Registry()
        config = self._makeOne(reg, autocommit=True)
        config.setup_registry() # registers IExceptionResponse default view
        def myview(context, request):
            return 'OK'
        config.add_view(myview, context=HTTPNotFound, renderer=null_renderer)
        request = self._makeRequest(config)
        view = self._getViewCallable(config,
                                     ctx_iface=implementedBy(HTTPNotFound),
                                     request_iface=IRequest)
        result = view(None, request)
        self.assertEqual(result, 'OK')

    def test_setup_registry_custom_settings(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import ISettings
        settings = {'reload_templates':True,
                    'mysetting':True}
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry(settings=settings)
        settings = reg.getUtility(ISettings)
        self.assertEqual(settings['reload_templates'], True)
        self.assertEqual(settings['debug_authorization'], False)
        self.assertEqual(settings['mysetting'], True)

    def test_setup_registry_debug_logger_None_default(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import IDebugLogger
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry()
        logger = reg.getUtility(IDebugLogger)
        self.assertEqual(logger.name, 'pyramid.tests.test_config')

    def test_setup_registry_debug_logger_non_None(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import IDebugLogger
        logger = object()
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry(debug_logger=logger)
        result = reg.getUtility(IDebugLogger)
        self.assertEqual(logger, result)

    def test_setup_registry_debug_logger_name(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import IDebugLogger
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry(debug_logger='foo')
        result = reg.getUtility(IDebugLogger)
        self.assertEqual(result.name, 'foo')

    def test_setup_registry_authentication_policy(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import IAuthenticationPolicy
        policy = object()
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry(authentication_policy=policy)
        result = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy, result)

    def test_setup_registry_authentication_policy_dottedname(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import IAuthenticationPolicy
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry(authentication_policy='pyramid.tests')
        result = reg.getUtility(IAuthenticationPolicy)
        import pyramid.tests
        self.assertEqual(result, pyramid.tests)

    def test_setup_registry_authorization_policy_dottedname(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import IAuthorizationPolicy
        reg = Registry()
        config = self._makeOne(reg)
        dummy = object()
        config.setup_registry(authentication_policy=dummy,
                              authorization_policy='pyramid.tests')
        result = reg.getUtility(IAuthorizationPolicy)
        import pyramid.tests
        self.assertEqual(result, pyramid.tests)

    def test_setup_registry_authorization_policy_only(self):
        from zope.configuration.config import ConfigurationExecutionError
        from pyramid.registry import Registry
        policy = object()
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry(authorization_policy=policy)
        config = self.assertRaises(ConfigurationExecutionError, config.commit)

    def test_setup_registry_default_root_factory(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import IRootFactory
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry()
        self.assertEqual(reg.queryUtility(IRootFactory), None)
        config.commit()
        self.assertTrue(reg.getUtility(IRootFactory))

    def test_setup_registry_dottedname_root_factory(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import IRootFactory
        reg = Registry()
        config = self._makeOne(reg)
        import pyramid.tests
        config.setup_registry(root_factory='pyramid.tests')
        self.assertEqual(reg.queryUtility(IRootFactory), None)
        config.commit()
        self.assertEqual(reg.getUtility(IRootFactory), pyramid.tests)

    def test_setup_registry_locale_negotiator_dottedname(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import ILocaleNegotiator
        reg = Registry()
        config = self._makeOne(reg)
        import pyramid.tests
        config.setup_registry(locale_negotiator='pyramid.tests')
        self.assertEqual(reg.queryUtility(ILocaleNegotiator), None)
        config.commit()
        utility = reg.getUtility(ILocaleNegotiator)
        self.assertEqual(utility, pyramid.tests)

    def test_setup_registry_locale_negotiator(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import ILocaleNegotiator
        reg = Registry()
        config = self._makeOne(reg)
        negotiator = object()
        config.setup_registry(locale_negotiator=negotiator)
        self.assertEqual(reg.queryUtility(ILocaleNegotiator), None)
        config.commit()
        utility = reg.getUtility(ILocaleNegotiator)
        self.assertEqual(utility, negotiator)

    def test_setup_registry_request_factory(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import IRequestFactory
        reg = Registry()
        config = self._makeOne(reg)
        factory = object()
        config.setup_registry(request_factory=factory)
        self.assertEqual(reg.queryUtility(IRequestFactory), None)
        config.commit()
        utility = reg.getUtility(IRequestFactory)
        self.assertEqual(utility, factory)

    def test_setup_registry_request_factory_dottedname(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import IRequestFactory
        reg = Registry()
        config = self._makeOne(reg)
        import pyramid.tests
        config.setup_registry(request_factory='pyramid.tests')
        self.assertEqual(reg.queryUtility(IRequestFactory), None)
        config.commit()
        utility = reg.getUtility(IRequestFactory)
        self.assertEqual(utility, pyramid.tests)

    def test_setup_registry_renderer_globals_factory(self):
        import warnings
        warnings.filterwarnings('ignore')
        try:
            from pyramid.registry import Registry
            from pyramid.interfaces import IRendererGlobalsFactory
            reg = Registry()
            config = self._makeOne(reg)
            factory = object()
            config.setup_registry(renderer_globals_factory=factory)
            self.assertEqual(reg.queryUtility(IRendererGlobalsFactory), None)
            config.commit()
            utility = reg.getUtility(IRendererGlobalsFactory)
            self.assertEqual(utility, factory)
        finally:
            warnings.resetwarnings()

    def test_setup_registry_renderer_globals_factory_dottedname(self):
        import warnings
        warnings.filterwarnings('ignore')
        try:
            from pyramid.registry import Registry
            from pyramid.interfaces import IRendererGlobalsFactory
            reg = Registry()
            config = self._makeOne(reg)
            import pyramid.tests
            config.setup_registry(renderer_globals_factory='pyramid.tests')
            self.assertEqual(reg.queryUtility(IRendererGlobalsFactory), None)
            config.commit()
            utility = reg.getUtility(IRendererGlobalsFactory)
            self.assertEqual(utility, pyramid.tests)
        finally:
            warnings.resetwarnings()

    def test_setup_registry_alternate_renderers(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import IRendererFactory
        renderer = object()
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry(renderers=[('yeah', renderer)])
        self.assertEqual(reg.getUtility(IRendererFactory, 'yeah'),
                         renderer)

    def test_setup_registry_default_permission(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import IDefaultPermission
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry(default_permission='view')
        self.assertEqual(reg.getUtility(IDefaultPermission), 'view')

    def test_setup_registry_includes(self):
        from pyramid.registry import Registry
        reg = Registry()
        config = self._makeOne(reg)
        settings = {
            'pyramid.includes':
"""pyramid.tests.test_config.dummy_include
pyramid.tests.test_config.dummy_include2""",
        }
        config.setup_registry(settings=settings)
        self.assert_(reg.included)
        self.assert_(reg.also_included)

    def test_setup_registry_includes_spaces(self):
        from pyramid.registry import Registry
        reg = Registry()
        config = self._makeOne(reg)
        settings = {
            'pyramid.includes':
"""pyramid.tests.test_config.dummy_include pyramid.tests.test_config.dummy_include2""",
        }
        config.setup_registry(settings=settings)
        self.assert_(reg.included)
        self.assert_(reg.also_included)

    def test_setup_registry_tweens(self):
        from pyramid.interfaces import ITweens
        from pyramid.registry import Registry
        reg = Registry()
        config = self._makeOne(reg)
        settings = {
            'pyramid.tweens':
                    'pyramid.tests.test_config.dummy_tween_factory'
        }
        config.setup_registry(settings=settings)
        config.commit()
        tweens = config.registry.getUtility(ITweens)
        self.assertEqual(
            tweens.explicit,
            [('pyramid.tests.test_config.dummy_tween_factory',
              dummy_tween_factory)])

    def test_get_settings_nosettings(self):
        from pyramid.registry import Registry
        reg = Registry()
        config = self._makeOne(reg)
        self.assertEqual(config.get_settings(), None)

    def test_get_settings_withsettings(self):
        settings = {'a':1}
        config = self._makeOne()
        config.registry.settings = settings
        self.assertEqual(config.get_settings(), settings)

    def test_add_settings_settings_already_registered(self):
        from pyramid.registry import Registry
        reg = Registry()
        config = self._makeOne(reg)
        config._set_settings({'a':1})
        config.add_settings({'b':2})
        settings = reg.settings
        self.assertEqual(settings['a'], 1)
        self.assertEqual(settings['b'], 2)

    def test_add_settings_settings_not_yet_registered(self):
        from pyramid.registry import Registry
        from pyramid.interfaces import ISettings
        reg = Registry()
        config = self._makeOne(reg)
        config.add_settings({'a':1})
        settings = reg.getUtility(ISettings)
        self.assertEqual(settings['a'], 1)

    def test_add_tweens_names_distinct(self):
        from pyramid.interfaces import ITweens
        from pyramid.tweens import excview_tween_factory
        def factory1(handler, registry): return handler
        def factory2(handler, registry): return handler
        config = self._makeOne()
        config.add_tween(
            'pyramid.tests.test_config.dummy_tween_factory')
        config.add_tween(
            'pyramid.tests.test_config.dummy_tween_factory2')
        config.commit()
        tweens = config.registry.queryUtility(ITweens)
        implicit = tweens.implicit()
        self.assertEqual(
            implicit,
            [
                ('pyramid.tests.test_config.dummy_tween_factory2',
                 dummy_tween_factory2),
                ('pyramid.tests.test_config.dummy_tween_factory',
                 dummy_tween_factory),
                ('pyramid.tweens.excview_tween_factory',
                 excview_tween_factory),
                ]
            )

    def test_add_tweens_names_with_underover(self):
        from pyramid.interfaces import ITweens
        from pyramid.tweens import excview_tween_factory
        from pyramid.tweens import MAIN
        config = self._makeOne()
        config.add_tween(
            'pyramid.tests.test_config.dummy_tween_factory',
            over=MAIN)
        config.add_tween(
            'pyramid.tests.test_config.dummy_tween_factory2',
            over=MAIN,
            under='pyramid.tests.test_config.dummy_tween_factory')
        config.commit()
        tweens = config.registry.queryUtility(ITweens)
        implicit = tweens.implicit()
        self.assertEqual(
            implicit,
            [
                ('pyramid.tweens.excview_tween_factory', excview_tween_factory),
                ('pyramid.tests.test_config.dummy_tween_factory',
                 dummy_tween_factory),
                ('pyramid.tests.test_config.dummy_tween_factory2',
                 dummy_tween_factory2),
             ])

    def test_add_tweens_names_with_under_nonstringoriter(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(
            ConfigurationError, config.add_tween,
            'pyramid.tests.test_config.dummy_tween_factory',
            under=False)

    def test_add_tweens_names_with_over_nonstringoriter(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(
            ConfigurationError, config.add_tween,
            'pyramid.tests.test_config.dummy_tween_factory',
            over=False)

    def test_add_tween_dottedname(self):
        from pyramid.interfaces import ITweens
        from pyramid.tweens import excview_tween_factory
        config = self._makeOne()
        config.add_tween('pyramid.tests.test_config.dummy_tween_factory')
        config.commit()
        tweens = config.registry.queryUtility(ITweens)
        self.assertEqual(
            tweens.implicit(),
            [
                ('pyramid.tests.test_config.dummy_tween_factory',
                 dummy_tween_factory),
                ('pyramid.tweens.excview_tween_factory',
                 excview_tween_factory),
                ])

    def test_add_tween_instance(self):
        from pyramid.exceptions import ConfigurationError
        class ATween(object): pass
        atween = ATween()
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.add_tween, atween)

    def test_add_tween_unsuitable(self):
        from pyramid.exceptions import ConfigurationError
        import pyramid.tests
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.add_tween, pyramid.tests)

    def test_add_tween_name_ingress(self):
        from pyramid.exceptions import ConfigurationError
        from pyramid.tweens import INGRESS
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.add_tween, INGRESS)

    def test_add_tween_name_main(self):
        from pyramid.exceptions import ConfigurationError
        from pyramid.tweens import MAIN
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.add_tween, MAIN)

    def test_add_tweens_conflict(self):
        from zope.configuration.config import ConfigurationConflictError
        config = self._makeOne()
        config.add_tween('pyramid.tests.test_config.dummy_tween_factory')
        config.add_tween('pyramid.tests.test_config.dummy_tween_factory')
        self.assertRaises(ConfigurationConflictError, config.commit)

    def test_add_tween_over_ingress(self):
        from pyramid.exceptions import ConfigurationError
        from pyramid.tweens import INGRESS
        config = self._makeOne()
        self.assertRaises(
            ConfigurationError,
            config.add_tween,
            'pyramid.tests.test_config.dummy_tween_factory',
            over=INGRESS)

    def test_add_tween_over_ingress_iterable(self):
        from pyramid.exceptions import ConfigurationError
        from pyramid.tweens import INGRESS
        config = self._makeOne()
        self.assertRaises(
            ConfigurationError,
            config.add_tween,
            'pyramid.tests.test_config.dummy_tween_factory',
            over=('a', INGRESS))

    def test_add_tween_under_main(self):
        from pyramid.exceptions import ConfigurationError
        from pyramid.tweens import MAIN
        config = self._makeOne()
        self.assertRaises(
            ConfigurationError,
            config.add_tween,
            'pyramid.tests.test_config.dummy_tween_factory',
            under=MAIN)

    def test_add_tween_under_main_iterable(self):
        from pyramid.exceptions import ConfigurationError
        from pyramid.tweens import MAIN
        config = self._makeOne()
        self.assertRaises(
            ConfigurationError,
            config.add_tween,
            'pyramid.tests.test_config.dummy_tween_factory',
            under=('a', MAIN))

    def test_add_subscriber_defaults(self):
        from zope.interface import implements
        from zope.interface import Interface
        class IEvent(Interface):
            pass
        class Event:
            implements(IEvent)
        L = []
        def subscriber(event):
            L.append(event)
        config = self._makeOne(autocommit=True)
        config.add_subscriber(subscriber)
        event = Event()
        config.registry.notify(event)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        config.registry.notify(object())
        self.assertEqual(len(L), 2)

    def test_add_subscriber_iface_specified(self):
        from zope.interface import implements
        from zope.interface import Interface
        class IEvent(Interface):
            pass
        class Event:
            implements(IEvent)
        L = []
        def subscriber(event):
            L.append(event)
        config = self._makeOne(autocommit=True)
        config.add_subscriber(subscriber, IEvent)
        event = Event()
        config.registry.notify(event)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        config.registry.notify(object())
        self.assertEqual(len(L), 1)

    def test_add_subscriber_dottednames(self):
        import pyramid.tests
        from pyramid.interfaces import INewRequest
        config = self._makeOne(autocommit=True)
        config.add_subscriber('pyramid.tests',
                              'pyramid.interfaces.INewRequest')
        handlers = list(config.registry.registeredHandlers())
        self.assertEqual(len(handlers), 1)
        handler = handlers[0]
        self.assertEqual(handler.handler, pyramid.tests)
        self.assertEqual(handler.required, (INewRequest,))

    def test_add_object_event_subscriber(self):
        from zope.interface import implements
        from zope.interface import Interface
        class IEvent(Interface):
            pass
        class Event:
            object = 'foo'
            implements(IEvent)
        event = Event()
        L = []
        def subscriber(object, event):
            L.append(event)
        config = self._makeOne(autocommit=True)
        config.add_subscriber(subscriber, (Interface, IEvent))
        config.registry.subscribers((event.object, event), None)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        config.registry.subscribers((event.object, IDummy), None)
        self.assertEqual(len(L), 1)

    def test_make_wsgi_app(self):
        import pyramid.config
        from pyramid.router import Router
        from pyramid.interfaces import IApplicationCreated
        manager = DummyThreadLocalManager()
        config = self._makeOne()
        subscriber = self._registerEventListener(config, IApplicationCreated)
        config.manager = manager
        app = config.make_wsgi_app()
        self.assertEqual(app.__class__, Router)
        self.assertEqual(manager.pushed['registry'], config.registry)
        self.assertEqual(manager.pushed['request'], None)
        self.assertTrue(manager.popped)
        self.assertEqual(pyramid.config.global_registries.last, app.registry)
        self.assertEqual(len(subscriber), 1)
        self.assertTrue(IApplicationCreated.providedBy(subscriber[0]))
        pyramid.config.global_registries.empty()

    def test_global_registries_empty(self):
        from pyramid.config import global_registries
        self.assertEqual(global_registries.last, None)

    def test_global_registries(self):
        from pyramid.config import global_registries
        global_registries.empty()
        config1 = self._makeOne()
        config1.make_wsgi_app()
        self.assertEqual(global_registries.last, config1.registry)
        config2 = self._makeOne()
        config2.make_wsgi_app()
        self.assertEqual(global_registries.last, config2.registry)
        self.assertEqual(list(global_registries),
                         [config1.registry, config2.registry])
        global_registries.remove(config2.registry)
        self.assertEqual(global_registries.last, config1.registry)
        global_registries.empty()

    def test_include_with_dotted_name(self):
        from pyramid.tests import test_config
        config = self._makeOne()
        context_before = config._make_context()
        config._ctx = context_before
        config.include('pyramid.tests.test_config.dummy_include')
        context_after = config._ctx
        actions = context_after.actions
        self.assertEqual(len(actions), 1)
        self.assertEqual(
            context_after.actions[0][:3],
            ('discrim', None, test_config),
            )
        self.assertEqual(context_after.basepath, None)
        self.assertEqual(context_after.includepath, ())
        self.assertTrue(context_after is context_before)

    def test_include_with_python_callable(self):
        from pyramid.tests import test_config
        config = self._makeOne()
        context_before = config._make_context()
        config._ctx = context_before
        config.include(dummy_include)
        context_after = config._ctx
        actions = context_after.actions
        self.assertEqual(len(actions), 1)
        self.assertEqual(
            actions[0][:3],
            ('discrim', None, test_config),
            )
        self.assertEqual(context_after.basepath, None)
        self.assertEqual(context_after.includepath, ())
        self.assertTrue(context_after is context_before)

    def test_include_with_module_defaults_to_includeme(self):
        from pyramid.tests import test_config
        config = self._makeOne()
        context_before = config._make_context()
        config._ctx = context_before
        config.include('pyramid.tests.test_config')
        context_after = config._ctx
        actions = context_after.actions
        self.assertEqual(len(actions), 1)
        self.assertEqual(
            actions[0][:3],
            ('discrim', None, test_config),
            )
        self.assertEqual(context_after.basepath, None)
        self.assertEqual(context_after.includepath, ())
        self.assertTrue(context_after is context_before)

    def test_include_with_route_prefix(self):
        root_config = self._makeOne(autocommit=True)
        def dummy_subapp(config):
            self.assertEqual(config.route_prefix, 'root')
        root_config.include(dummy_subapp, route_prefix='root')

    def test_include_with_nested_route_prefix(self):
        root_config = self._makeOne(autocommit=True, route_prefix='root')
        def dummy_subapp(config):
            self.assertEqual(config.route_prefix, 'root/nested')
        root_config.include(dummy_subapp, route_prefix='nested')

    def test_with_context(self):
        config = self._makeOne()
        ctx = config._make_context()
        newconfig = config.with_context(ctx)
        self.assertEqual(newconfig._ctx, ctx)

    def test_add_view_view_callable_None_no_renderer(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne(autocommit=True)
        self.assertRaises(ConfigurationError, config.add_view)

    def test_add_view_with_request_type_and_route_name(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne(autocommit=True)
        view = lambda *arg: 'OK'
        self.assertRaises(ConfigurationError, config.add_view, view, '', None,
                          None, True, True)

    def test_add_view_with_request_type(self):
        from pyramid.renderers import null_renderer
        from zope.interface import directlyProvides
        from pyramid.interfaces import IRequest
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view,
                        request_type='pyramid.interfaces.IRequest',
                        renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        self._assertNotFound(wrapper, None, request)
        directlyProvides(request, IRequest)
        result = wrapper(None, request)
        self.assertEqual(result, 'OK')

    def test_add_view_view_callable_None_with_renderer(self):
        config = self._makeOne(autocommit=True)
        self._registerRenderer(config, name='dummy')
        config.add_view(renderer='dummy')
        view = self._getViewCallable(config)
        self.assertTrue('Hello!' in view(None, None).body)

    def test_add_view_wrapped_view_is_decorated(self):
        def view(request): # request-only wrapper
            """ """
        config = self._makeOne(autocommit=True)
        config.add_view(view=view)
        wrapper = self._getViewCallable(config)
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)

    def test_add_view_view_callable_dottedname(self):
        from pyramid.renderers import null_renderer
        config = self._makeOne(autocommit=True)
        config.add_view(view='pyramid.tests.test_config.dummy_view',
                        renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        self.assertEqual(wrapper(None, None), 'OK')

    def test_add_view_with_function_callable(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_add_view_with_function_callable_requestonly(self):
        from pyramid.renderers import null_renderer
        def view(request):
            return 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_add_view_with_decorator(self):
        from pyramid.renderers import null_renderer
        def view(request):
            """ ABC """
            return 'OK'
        def view_wrapper(fn):
            def inner(context, request):
                return fn(context, request)
            return inner
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, decorator=view_wrapper,
                        renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        self.assertFalse(wrapper is view)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_add_view_with_http_cache(self):
        import datetime
        from pyramid.response import Response
        response = Response('OK')
        def view(request):
            """ ABC """
            return response
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, http_cache=(86400, {'public':True}))
        wrapper = self._getViewCallable(config)
        self.assertFalse(wrapper is view)
        self.assertEqual(wrapper.__doc__, view.__doc__)
        request = testing.DummyRequest()
        when = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        result = wrapper(None, request)
        self.assertEqual(result, response)
        headers = dict(response.headerlist)
        self.assertEqual(headers['Cache-Control'], 'max-age=86400, public')
        expires = parse_httpdate(headers['Expires'])
        assert_similar_datetime(expires, when)

    def test_add_view_as_instance(self):
        from pyramid.renderers import null_renderer
        class AView:
            def __call__(self, context, request):
                """ """
                return 'OK'
        view = AView()
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_add_view_as_instance_requestonly(self):
        from pyramid.renderers import null_renderer
        class AView:
            def __call__(self, request):
                """ """
                return 'OK'
        view = AView()
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_add_view_as_oldstyle_class(self):
        from pyramid.renderers import null_renderer
        class view:
            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self):
                return 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        result = wrapper(None, request)
        self.assertEqual(result, 'OK')
        self.assertEqual(request.__view__.__class__, view)

    def test_add_view_as_oldstyle_class_requestonly(self):
        from pyramid.renderers import null_renderer
        class view:
            def __init__(self, request):
                self.request = request

            def __call__(self):
                return 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, renderer=null_renderer)
        wrapper = self._getViewCallable(config)

        request = self._makeRequest(config)
        result = wrapper(None, request)
        self.assertEqual(result, 'OK')
        self.assertEqual(request.__view__.__class__, view)

    def test_add_view_context_as_class(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        view = lambda *arg: 'OK'
        class Foo:
            pass
        config = self._makeOne(autocommit=True)
        config.add_view(context=Foo, view=view, renderer=null_renderer)
        foo = implementedBy(Foo)
        wrapper = self._getViewCallable(config, foo)
        self.assertEqual(wrapper, view)

    def test_add_view_context_as_iface(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(context=IDummy, view=view, renderer=null_renderer)
        wrapper = self._getViewCallable(config, IDummy)
        self.assertEqual(wrapper, view)

    def test_add_view_context_as_dottedname(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(context='pyramid.tests.test_config.IDummy',
                        view=view,  renderer=null_renderer)
        wrapper = self._getViewCallable(config, IDummy)
        self.assertEqual(wrapper, view)

    def test_add_view_for__as_dottedname(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(for_='pyramid.tests.test_config.IDummy',
                        view=view, renderer=null_renderer)
        wrapper = self._getViewCallable(config, IDummy)
        self.assertEqual(wrapper, view)

    def test_add_view_for_as_class(self):
        # ``for_`` is older spelling for ``context``
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        view = lambda *arg: 'OK'
        class Foo:
            pass
        config = self._makeOne(autocommit=True)
        config.add_view(for_=Foo, view=view, renderer=null_renderer)
        foo = implementedBy(Foo)
        wrapper = self._getViewCallable(config, foo)
        self.assertEqual(wrapper, view)

    def test_add_view_for_as_iface(self):
        # ``for_`` is older spelling for ``context``
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(for_=IDummy, view=view, renderer=null_renderer)
        wrapper = self._getViewCallable(config, IDummy)
        self.assertEqual(wrapper, view)

    def test_add_view_context_trumps_for(self):
        # ``for_`` is older spelling for ``context``
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        class Foo:
            pass
        config.add_view(context=IDummy, for_=Foo, view=view,
                        renderer=null_renderer)
        wrapper = self._getViewCallable(config, IDummy)
        self.assertEqual(wrapper, view)

    def test_add_view_register_secured_view(self):
        from pyramid.renderers import null_renderer
        from zope.interface import Interface
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import ISecuredView
        from pyramid.interfaces import IViewClassifier
        view = lambda *arg: 'OK'
        view.__call_permissive__ = view
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, renderer=null_renderer)
        wrapper = config.registry.adapters.lookup(
            (IViewClassifier, IRequest, Interface),
            ISecuredView, name='', default=None)
        self.assertEqual(wrapper, view)

    def test_add_view_exception_register_secured_view(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IExceptionViewClassifier
        view = lambda *arg: 'OK'
        view.__call_permissive__ = view
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, context=RuntimeError, renderer=null_renderer)
        wrapper = config.registry.adapters.lookup(
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='', default=None)
        self.assertEqual(wrapper, view)

    def test_add_view_same_phash_overrides_existing_single_view(self):
        from pyramid.renderers import null_renderer
        from hashlib import md5
        from zope.interface import Interface
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IMultiView
        phash = md5()
        phash.update('xhr:True')
        view = lambda *arg: 'NOT OK'
        view.__phash__ = phash.hexdigest()
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface), IView, name='')
        def newview(context, request):
            return 'OK'
        config.add_view(view=newview, xhr=True, renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        self.assertFalse(IMultiView.providedBy(wrapper))
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_exc_same_phash_overrides_existing_single_view(self):
        from pyramid.renderers import null_renderer
        from hashlib import md5
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IExceptionViewClassifier
        from pyramid.interfaces import IMultiView
        phash = md5()
        phash.update('xhr:True')
        view = lambda *arg: 'NOT OK'
        view.__phash__ = phash.hexdigest()
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        def newview(context, request):
            return 'OK'
        config.add_view(view=newview, xhr=True, context=RuntimeError,
                        renderer=null_renderer)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.assertFalse(IMultiView.providedBy(wrapper))
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_default_phash_overrides_no_phash(self):
        from pyramid.renderers import null_renderer
        from zope.interface import Interface
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IMultiView
        view = lambda *arg: 'NOT OK'
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface), IView, name='')
        def newview(context, request):
            return 'OK'
        config.add_view(view=newview, renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        self.assertFalse(IMultiView.providedBy(wrapper))
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_exc_default_phash_overrides_no_phash(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IExceptionViewClassifier
        from pyramid.interfaces import IMultiView
        view = lambda *arg: 'NOT OK'
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        def newview(context, request):
            return 'OK'
        config.add_view(view=newview, context=RuntimeError,
                        renderer=null_renderer)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.assertFalse(IMultiView.providedBy(wrapper))
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_default_phash_overrides_default_phash(self):
        from pyramid.renderers import null_renderer
        from pyramid.config.util import DEFAULT_PHASH
        from zope.interface import Interface
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IMultiView
        view = lambda *arg: 'NOT OK'
        view.__phash__ = DEFAULT_PHASH
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface), IView, name='')
        def newview(context, request):
            return 'OK'
        config.add_view(view=newview, renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        self.assertFalse(IMultiView.providedBy(wrapper))
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_exc_default_phash_overrides_default_phash(self):
        from pyramid.renderers import null_renderer
        from pyramid.config.util import DEFAULT_PHASH
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IExceptionViewClassifier
        from pyramid.interfaces import IMultiView
        view = lambda *arg: 'NOT OK'
        view.__phash__ = DEFAULT_PHASH
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        def newview(context, request):
            return 'OK'
        config.add_view(view=newview, context=RuntimeError,
                        renderer=null_renderer)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.assertFalse(IMultiView.providedBy(wrapper))
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_multiview_replaces_existing_view(self):
        from pyramid.renderers import null_renderer
        from zope.interface import Interface
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IMultiView
        view = lambda *arg: 'OK'
        view.__phash__ = 'abc'
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface), IView, name='')
        config.add_view(view=view, renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        self.assertTrue(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper(None, None), 'OK')

    def test_add_view_exc_multiview_replaces_existing_view(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IExceptionViewClassifier
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IMultiView
        view = lambda *arg: 'OK'
        view.__phash__ = 'abc'
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view,
            (IViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        config.add_view(view=view, context=RuntimeError,
                        renderer=null_renderer)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.assertTrue(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper(None, None), 'OK')

    def test_add_view_multiview_replaces_existing_securedview(self):
        from pyramid.renderers import null_renderer
        from zope.interface import Interface
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import ISecuredView
        from pyramid.interfaces import IMultiView
        from pyramid.interfaces import IViewClassifier
        view = lambda *arg: 'OK'
        view.__phash__ = 'abc'
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface),
            ISecuredView, name='')
        config.add_view(view=view, renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        self.assertTrue(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper(None, None), 'OK')

    def test_add_view_exc_multiview_replaces_existing_securedview(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import ISecuredView
        from pyramid.interfaces import IMultiView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        view = lambda *arg: 'OK'
        view.__phash__ = 'abc'
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view,
            (IViewClassifier, IRequest, implementedBy(RuntimeError)),
            ISecuredView, name='')
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            ISecuredView, name='')
        config.add_view(view=view, context=RuntimeError, renderer=null_renderer)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.assertTrue(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper(None, None), 'OK')

    def test_add_view_with_accept_multiview_replaces_existing_view(self):
        from pyramid.renderers import null_renderer
        from zope.interface import Interface
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IMultiView
        from pyramid.interfaces import IViewClassifier
        def view(context, request):
            return 'OK'
        def view2(context, request):
            return 'OK2'
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface), IView, name='')
        config.add_view(view=view2, accept='text/html', renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        self.assertTrue(IMultiView.providedBy(wrapper))
        self.assertEqual(len(wrapper.views), 1)
        self.assertEqual(len(wrapper.media_views), 1)
        self.assertEqual(wrapper(None, None), 'OK')
        request = DummyRequest()
        request.accept = DummyAccept('text/html', 'text/html')
        self.assertEqual(wrapper(None, request), 'OK2')

    def test_add_view_exc_with_accept_multiview_replaces_existing_view(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IMultiView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        def view(context, request):
            return 'OK'
        def view2(context, request):
            return 'OK2'
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view,
            (IViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        config.add_view(view=view2, accept='text/html', context=RuntimeError,
                        renderer=null_renderer)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.assertTrue(IMultiView.providedBy(wrapper))
        self.assertEqual(len(wrapper.views), 1)
        self.assertEqual(len(wrapper.media_views), 1)
        self.assertEqual(wrapper(None, None), 'OK')
        request = DummyRequest()
        request.accept = DummyAccept('text/html', 'text/html')
        self.assertEqual(wrapper(None, request), 'OK2')

    def test_add_view_multiview_replaces_existing_view_with___accept__(self):
        from pyramid.renderers import null_renderer
        from zope.interface import Interface
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IMultiView
        from pyramid.interfaces import IViewClassifier
        def view(context, request):
            return 'OK'
        def view2(context, request):
            return 'OK2'
        view.__accept__ = 'text/html'
        view.__phash__ = 'abc'
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface), IView, name='')
        config.add_view(view=view2, renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        self.assertTrue(IMultiView.providedBy(wrapper))
        self.assertEqual(len(wrapper.views), 1)
        self.assertEqual(len(wrapper.media_views), 1)
        self.assertEqual(wrapper(None, None), 'OK2')
        request = DummyRequest()
        request.accept = DummyAccept('text/html')
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_exc_mulview_replaces_existing_view_with___accept__(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IMultiView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        def view(context, request):
            return 'OK'
        def view2(context, request):
            return 'OK2'
        view.__accept__ = 'text/html'
        view.__phash__ = 'abc'
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view,
            (IViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        config.add_view(view=view2, context=RuntimeError,
                        renderer=null_renderer)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.assertTrue(IMultiView.providedBy(wrapper))
        self.assertEqual(len(wrapper.views), 1)
        self.assertEqual(len(wrapper.media_views), 1)
        self.assertEqual(wrapper(None, None), 'OK2')
        request = DummyRequest()
        request.accept = DummyAccept('text/html')
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_multiview_replaces_multiview(self):
        from pyramid.renderers import null_renderer
        from zope.interface import Interface
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IMultiView
        from pyramid.interfaces import IViewClassifier
        view = DummyMultiView()
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface),
            IMultiView, name='')
        view2 = lambda *arg: 'OK2'
        config.add_view(view=view2, renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        self.assertTrue(IMultiView.providedBy(wrapper))
        self.assertEqual([x[:2] for x in wrapper.views], [(view2, None)])
        self.assertEqual(wrapper(None, None), 'OK1')

    def test_add_view_exc_multiview_replaces_multiview(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IMultiView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        view = DummyMultiView()
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view,
            (IViewClassifier, IRequest, implementedBy(RuntimeError)),
            IMultiView, name='')
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IMultiView, name='')
        view2 = lambda *arg: 'OK2'
        config.add_view(view=view2, context=RuntimeError,
                        renderer=null_renderer)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.assertTrue(IMultiView.providedBy(wrapper))
        self.assertEqual([x[:2] for x in wrapper.views], [(view2, None)])
        self.assertEqual(wrapper(None, None), 'OK1')

    def test_add_view_multiview_context_superclass_then_subclass(self):
        from pyramid.renderers import null_renderer
        from zope.interface import Interface
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IMultiView
        from pyramid.interfaces import IViewClassifier
        class ISuper(Interface):
            pass
        class ISub(ISuper):
            pass
        view = lambda *arg: 'OK'
        view2 = lambda *arg: 'OK2'
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, ISuper), IView, name='')
        config.add_view(view=view2, for_=ISub, renderer=null_renderer)
        wrapper = self._getViewCallable(config, ISuper, IRequest)
        self.assertFalse(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper(None, None), 'OK')
        wrapper = self._getViewCallable(config, ISub, IRequest)
        self.assertFalse(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper(None, None), 'OK2')

    def test_add_view_multiview_exception_superclass_then_subclass(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IMultiView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        class Super(Exception):
            pass
        class Sub(Super):
            pass
        view = lambda *arg: 'OK'
        view2 = lambda *arg: 'OK2'
        config = self._makeOne(autocommit=True)
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Super), IView, name='')
        config.registry.registerAdapter(
            view, (IExceptionViewClassifier, IRequest, Super), IView, name='')
        config.add_view(view=view2, for_=Sub, renderer=null_renderer)
        wrapper = self._getViewCallable(
            config, implementedBy(Super), IRequest)
        wrapper_exc_view = self._getViewCallable(
            config, implementedBy(Super), IRequest, exception_view=True)
        self.assertEqual(wrapper_exc_view, wrapper)
        self.assertFalse(IMultiView.providedBy(wrapper_exc_view))
        self.assertEqual(wrapper_exc_view(None, None), 'OK')
        wrapper = self._getViewCallable(
            config, implementedBy(Sub), IRequest)
        wrapper_exc_view = self._getViewCallable(
            config, implementedBy(Sub), IRequest, exception_view=True)
        self.assertEqual(wrapper_exc_view, wrapper)
        self.assertFalse(IMultiView.providedBy(wrapper_exc_view))
        self.assertEqual(wrapper_exc_view(None, None), 'OK2')

    def test_add_view_multiview_call_ordering(self):
        from pyramid.renderers import null_renderer as nr
        from zope.interface import directlyProvides
        def view1(context, request): return 'view1'
        def view2(context, request): return 'view2'
        def view3(context, request): return 'view3'
        def view4(context, request): return 'view4'
        def view5(context, request): return 'view5'
        def view6(context, request): return 'view6'
        def view7(context, request): return 'view7'
        def view8(context, request): return 'view8'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view1, renderer=nr)
        config.add_view(view=view2, request_method='POST', renderer=nr)
        config.add_view(view=view3,request_param='param', renderer=nr)
        config.add_view(view=view4, containment=IDummy, renderer=nr)
        config.add_view(view=view5, request_method='POST',
                        request_param='param',  renderer=nr)
        config.add_view(view=view6, request_method='POST', containment=IDummy,
                        renderer=nr)
        config.add_view(view=view7, request_param='param', containment=IDummy,
                        renderer=nr)
        config.add_view(view=view8, request_method='POST',request_param='param',
                        containment=IDummy, renderer=nr)


        wrapper = self._getViewCallable(config)

        ctx = DummyContext()
        request = self._makeRequest(config)
        request.method = 'GET'
        request.params = {}
        self.assertEqual(wrapper(ctx, request), 'view1')

        ctx = DummyContext()
        request = self._makeRequest(config)
        request.params = {}
        request.method = 'POST'
        self.assertEqual(wrapper(ctx, request), 'view2')

        ctx = DummyContext()
        request = self._makeRequest(config)
        request.params = {'param':'1'}
        request.method = 'GET'
        self.assertEqual(wrapper(ctx, request), 'view3')

        ctx = DummyContext()
        directlyProvides(ctx, IDummy)
        request = self._makeRequest(config)
        request.method = 'GET'
        request.params = {}
        self.assertEqual(wrapper(ctx, request), 'view4')

        ctx = DummyContext()
        request = self._makeRequest(config)
        request.method = 'POST'
        request.params = {'param':'1'}
        self.assertEqual(wrapper(ctx, request), 'view5')

        ctx = DummyContext()
        directlyProvides(ctx, IDummy)
        request = self._makeRequest(config)
        request.params = {}
        request.method = 'POST'
        self.assertEqual(wrapper(ctx, request), 'view6')

        ctx = DummyContext()
        directlyProvides(ctx, IDummy)
        request = self._makeRequest(config)
        request.method = 'GET'
        request.params = {'param':'1'}
        self.assertEqual(wrapper(ctx, request), 'view7')

        ctx = DummyContext()
        directlyProvides(ctx, IDummy)
        request = self._makeRequest(config)
        request.method = 'POST'
        request.params = {'param':'1'}
        self.assertEqual(wrapper(ctx, request), 'view8')

    def test_add_view_with_template_renderer(self):
        from pyramid.tests import test_config
        from pyramid.interfaces import ISettings
        class view(object):
            def __init__(self, context, request):
                self.request = request
                self.context = context

            def __call__(self):
                return {'a':'1'}
        config = self._makeOne(autocommit=True)
        renderer = self._registerRenderer(config)
        fixture = 'pyramid.tests:fixtures/minimal.txt'
        config.add_view(view=view, renderer=fixture)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        result = wrapper(None, request)
        self.assertEqual(result.body, 'Hello!')
        settings = config.registry.queryUtility(ISettings)
        result = renderer.info
        self.assertEqual(result.registry, config.registry)
        self.assertEqual(result.type, '.txt')
        self.assertEqual(result.package, test_config)
        self.assertEqual(result.name, fixture)
        self.assertEqual(result.settings, settings)

    def test_add_view_with_default_renderer(self):
        class view(object):
            def __init__(self, context, request):
                self.request = request
                self.context = context

            def __call__(self):
                return {'a':'1'}
        config = self._makeOne(autocommit=True)
        class moo(object):
            def __init__(self, *arg, **kw):
                pass
            def __call__(self, *arg, **kw):
                return 'moo'
        config.add_renderer(None, moo)
        config.add_view(view=view)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        result = wrapper(None, request)
        self.assertEqual(result.body, 'moo')

    def test_add_view_with_template_renderer_no_callable(self):
        from pyramid.tests import test_config
        from pyramid.interfaces import ISettings
        config = self._makeOne(autocommit=True)
        renderer = self._registerRenderer(config)
        fixture = 'pyramid.tests:fixtures/minimal.txt'
        config.add_view(view=None, renderer=fixture)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        result = wrapper(None, request)
        self.assertEqual(result.body, 'Hello!')
        settings = config.registry.queryUtility(ISettings)
        result = renderer.info
        self.assertEqual(result.registry, config.registry)
        self.assertEqual(result.type, '.txt')
        self.assertEqual(result.package, test_config)
        self.assertEqual(result.name, fixture)
        self.assertEqual(result.settings, settings)

    def test_add_view_with_request_type_as_iface(self):
        from pyramid.renderers import null_renderer
        from zope.interface import directlyProvides
        def view(context, request):
            return 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(request_type=IDummy, view=view, renderer=null_renderer)
        wrapper = self._getViewCallable(config, None)
        request = self._makeRequest(config)
        directlyProvides(request, IDummy)
        result = wrapper(None, request)
        self.assertEqual(result, 'OK')

    def test_add_view_with_request_type_as_noniface(self):
        from pyramid.exceptions import ConfigurationError
        view = lambda *arg: 'OK'
        config = self._makeOne()
        self.assertRaises(ConfigurationError,
                          config.add_view, view, '', None, None, object)

    def test_add_view_with_route_name(self):
        from pyramid.renderers import null_renderer
        from zope.component import ComponentLookupError
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, route_name='foo', renderer=null_renderer)
        self.assertEqual(len(config.registry.deferred_route_views), 1)
        infos = config.registry.deferred_route_views['foo']
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info['route_name'], 'foo')
        self.assertEqual(info['view'], view)
        self.assertRaises(ComponentLookupError,
                          self._getRouteRequestIface, config, 'foo')
        wrapper = self._getViewCallable(config, None)
        self.assertEqual(wrapper, None)
        config.add_route('foo', '/a/b')
        request_iface = self._getRouteRequestIface(config, 'foo')
        self.assertNotEqual(request_iface, None)
        wrapper = self._getViewCallable(config, request_iface=request_iface)
        self.assertNotEqual(wrapper, None)
        self.assertEqual(wrapper(None, None), 'OK')

    def test_add_view_with_route_name_deferred_views_already_exist(self):
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.registry.deferred_route_views = {'bar':[]}
        config.add_view(view=view, route_name='foo')
        self.assertEqual(len(config.registry.deferred_route_views), 2)
        self.assertEqual(config.registry.deferred_route_views['bar'], [])
        infos = config.registry.deferred_route_views['foo']
        self.assertEqual(len(infos), 1)

    def test_deferred_route_views_retains_custom_predicates(self):
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, route_name='foo', custom_predicates=('123',))
        self.assertEqual(len(config.registry.deferred_route_views), 1)
        infos = config.registry.deferred_route_views['foo']
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info['route_name'], 'foo')
        self.assertEqual(info['custom_predicates'], ('123',))

    def test_add_view_with_route_name_exception(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        from zope.component import ComponentLookupError
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, route_name='foo', context=RuntimeError,
                        renderer=null_renderer)
        self.assertEqual(len(config.registry.deferred_route_views), 1)
        infos = config.registry.deferred_route_views['foo']
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info['route_name'], 'foo')
        self.assertEqual(info['view'], view)
        self.assertRaises(ComponentLookupError,
                          self._getRouteRequestIface, config, 'foo')
        wrapper_exc_view = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError),
            exception_view=True)
        self.assertEqual(wrapper_exc_view, None)
        config.add_route('foo', '/a/b')
        request_iface = self._getRouteRequestIface(config, 'foo')
        self.assertNotEqual(request_iface, None)
        wrapper_exc_view = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError),
            request_iface=request_iface, exception_view=True)
        self.assertNotEqual(wrapper_exc_view, None)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError),
            request_iface=request_iface)
        self.assertEqual(wrapper_exc_view, wrapper)
        self.assertEqual(wrapper_exc_view(None, None), 'OK')

    def test_add_view_with_request_method_true(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, request_method='POST',
                        renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.method = 'POST'
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_request_method_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, request_method='POST')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.method = 'GET'
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_request_param_noval_true(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, request_param='abc', renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.params = {'abc':''}
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_request_param_noval_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, request_param='abc')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.params = {}
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_request_param_val_true(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, request_param='abc=123',
                        renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.params = {'abc':'123'}
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_request_param_val_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, request_param='abc=123')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.params = {'abc':''}
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_xhr_true(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, xhr=True, renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_xhr_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, xhr=True)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.is_xhr = False
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_header_badregex(self):
        from pyramid.exceptions import ConfigurationError
        view = lambda *arg: 'OK'
        config = self._makeOne()
        self.assertRaises(ConfigurationError,
                          config.add_view, view=view, header='Host:a\\')

    def test_add_view_with_header_noval_match(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, header='Host', renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.headers = {'Host':'whatever'}
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_header_noval_nomatch(self):
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, header='Host')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.headers = {'NotHost':'whatever'}
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_header_val_match(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, header=r'Host:\d', renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.headers = {'Host':'1'}
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_header_val_nomatch(self):
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, header=r'Host:\d')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.headers = {'Host':'abc'}
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_header_val_missing(self):
        from pyramid.httpexceptions import HTTPNotFound
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, header=r'Host:\d')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.headers = {'NoHost':'1'}
        self.assertRaises(HTTPNotFound, wrapper, None, request)

    def test_add_view_with_accept_match(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, accept='text/xml', renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.accept = ['text/xml']
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_accept_nomatch(self):
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, accept='text/xml')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.accept = ['text/html']
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_containment_true(self):
        from pyramid.renderers import null_renderer
        from zope.interface import directlyProvides
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, containment=IDummy, renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        context = DummyContext()
        directlyProvides(context, IDummy)
        self.assertEqual(wrapper(context, None), 'OK')

    def test_add_view_with_containment_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, containment=IDummy)
        wrapper = self._getViewCallable(config)
        context = DummyContext()
        self._assertNotFound(wrapper, context, None)

    def test_add_view_with_containment_dottedname(self):
        from pyramid.renderers import null_renderer
        from zope.interface import directlyProvides
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(
            view=view,
            containment='pyramid.tests.test_config.IDummy',
            renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        context = DummyContext()
        directlyProvides(context, IDummy)
        self.assertEqual(wrapper(context, None), 'OK')

    def test_add_view_with_path_info_badregex(self):
        from pyramid.exceptions import ConfigurationError
        view = lambda *arg: 'OK'
        config = self._makeOne()
        self.assertRaises(ConfigurationError,
                          config.add_view, view=view, path_info='\\')

    def test_add_view_with_path_info_match(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, path_info='/foo', renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.path_info = '/foo'
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_path_info_nomatch(self):
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, path_info='/foo')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.path_info = '/'
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_custom_predicates_match(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        def pred1(context, request):
            return True
        def pred2(context, request):
            return True
        predicates = (pred1, pred2)
        config.add_view(view=view, custom_predicates=predicates,
                        renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_custom_predicates_nomatch(self):
        view = lambda *arg: 'OK'
        config = self._makeOne(autocommit=True)
        def pred1(context, request):
            return True
        def pred2(context, request):
            return False
        predicates = (pred1, pred2)
        config.add_view(view=view, custom_predicates=predicates)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        self._assertNotFound(wrapper, None, request)

    def test_add_view_custom_predicate_bests_standard_predicate(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        view2 = lambda *arg: 'NOT OK'
        config = self._makeOne(autocommit=True)
        def pred1(context, request):
            return True
        config.add_view(view=view, custom_predicates=(pred1,),
                        renderer=null_renderer)
        config.add_view(view=view2, request_method='GET',
                        renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.method = 'GET'
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_custom_more_preds_first_bests_fewer_preds_last(self):
        from pyramid.renderers import null_renderer
        view = lambda *arg: 'OK'
        view2 = lambda *arg: 'NOT OK'
        config = self._makeOne(autocommit=True)
        config.add_view(view=view, request_method='GET', xhr=True,
                        renderer=null_renderer)
        config.add_view(view=view2, request_method='GET',
                        renderer=null_renderer)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.method = 'GET'
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_same_predicates(self):
        from zope.configuration.config import ConfigurationConflictError
        view2 = lambda *arg: 'second'
        view1 = lambda *arg: 'first'
        config = self._makeOne()
        config.add_view(view=view1)
        config.add_view(view=view2)
        self.assertRaises(ConfigurationConflictError, config.commit)

    def test_add_view_with_permission(self):
        from pyramid.renderers import null_renderer
        view1 = lambda *arg: 'OK'
        outerself = self
        class DummyPolicy(object):
            def effective_principals(self, r):
                outerself.assertEqual(r, request)
                return ['abc']
            def permits(self, context, principals, permission):
                outerself.assertEqual(context, None)
                outerself.assertEqual(principals, ['abc'])
                outerself.assertEqual(permission, 'view')
                return True
        policy = DummyPolicy()
        config = self._makeOne(authorization_policy=policy,
                               authentication_policy=policy,
                               autocommit=True)
        config.add_view(view=view1, permission='view', renderer=null_renderer)
        view = self._getViewCallable(config)
        request = self._makeRequest(config)
        self.assertEqual(view(None, request), 'OK')

    def test_add_view_with_default_permission_no_explicit_permission(self):
        from pyramid.renderers import null_renderer
        view1 = lambda *arg: 'OK'
        outerself = self
        class DummyPolicy(object):
            def effective_principals(self, r):
                outerself.assertEqual(r, request)
                return ['abc']
            def permits(self, context, principals, permission):
                outerself.assertEqual(context, None)
                outerself.assertEqual(principals, ['abc'])
                outerself.assertEqual(permission, 'view')
                return True
        policy = DummyPolicy()
        config = self._makeOne(authorization_policy=policy,
                               authentication_policy=policy,
                               default_permission='view',
                               autocommit=True)
        config.add_view(view=view1, renderer=null_renderer)
        view = self._getViewCallable(config)
        request = self._makeRequest(config)
        self.assertEqual(view(None, request), 'OK')

    def test_add_view_with_no_default_permission_no_explicit_permission(self):
        from pyramid.renderers import null_renderer
        view1 = lambda *arg: 'OK'
        class DummyPolicy(object): pass # wont be called
        policy = DummyPolicy()
        config = self._makeOne(authorization_policy=policy,
                               authentication_policy=policy,
                               autocommit=True)
        config.add_view(view=view1, renderer=null_renderer)
        view = self._getViewCallable(config)
        request = self._makeRequest(config)
        self.assertEqual(view(None, request), 'OK')

    def _assertRoute(self, config, name, path, num_predicates=0):
        from pyramid.interfaces import IRoutesMapper
        mapper = config.registry.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        route = routes[0]
        self.assertEqual(len(routes), 1)
        self.assertEqual(route.name, name)
        self.assertEqual(route.path, path)
        self.assertEqual(len(routes[0].predicates), num_predicates)
        return route

    def test_get_routes_mapper_not_yet_registered(self):
        config = self._makeOne()
        mapper = config.get_routes_mapper()
        self.assertEqual(mapper.routelist, [])

    def test_get_routes_mapper_already_registered(self):
        from pyramid.interfaces import IRoutesMapper
        config = self._makeOne()
        mapper = object()
        config.registry.registerUtility(mapper, IRoutesMapper)
        result = config.get_routes_mapper()
        self.assertEqual(result, mapper)

    def test_add_route_defaults(self):
        config = self._makeOne(autocommit=True)
        route = config.add_route('name', 'path')
        self._assertRoute(config, 'name', 'path')
        self.assertEqual(route.name, 'name')

    def test_add_route_with_route_prefix(self):
        config = self._makeOne(autocommit=True)
        config.route_prefix = 'root'
        route = config.add_route('name', 'path')
        self.assertEqual(route.name, 'name')
        self.assertEqual(route.pattern, 'root/path')

        self._assertRoute(config, 'name', 'root/path')

    def test_add_route_discriminator(self):
        config = self._makeOne()
        route = config.add_route('name', 'path')
        self._assertRoute(config, 'name', 'path')
        self.assertEqual(route.name, 'name')
        self.assertEqual(config._ctx.actions[-1][0], ('route', 'name'))

    def test_add_route_with_factory(self):
        config = self._makeOne(autocommit=True)
        factory = object()
        route = config.add_route('name', 'path', factory=factory)
        self.assertEqual(route.factory, factory)

    def test_add_route_with_static(self):
        config = self._makeOne(autocommit=True)
        route = config.add_route('name', 'path/{foo}', static=True)
        self.assertEqual(route.name, 'name')
        mapper = config.get_routes_mapper()
        self.assertEqual(len(mapper.get_routes()), 0)
        self.assertEqual(mapper.generate('name', {"foo":"a"}), '/path/a')

    def test_add_route_with_factory_dottedname(self):
        config = self._makeOne(autocommit=True)
        route = config.add_route(
            'name', 'path',
            factory='pyramid.tests.test_config.dummyfactory')
        self.assertEqual(route.factory, dummyfactory)

    def test_add_route_with_xhr(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path', xhr=True)
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.is_xhr = True
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.is_xhr = False
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_request_method(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path', request_method='GET')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.method = 'GET'
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.method = 'POST'
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_path_info(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path', path_info='/foo')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.path_info = '/foo'
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.path_info = '/'
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_request_param(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path', request_param='abc')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.params = {'abc':'123'}
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.params = {}
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_custom_predicates(self):
        config = self._makeOne(autocommit=True)
        def pred1(context, request): pass
        def pred2(context, request): pass
        config.add_route('name', 'path', custom_predicates=(pred1, pred2))
        route = self._assertRoute(config, 'name', 'path', 2)
        self.assertEqual(route.predicates, [pred1, pred2])

    def test_add_route_with_header(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path', header='Host')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.headers = {'Host':'example.com'}
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.headers = {}
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_accept(self):
        config = self._makeOne(autocommit=True)
        config.add_route('name', 'path', accept='text/xml')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.accept = ['text/xml']
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.accept = ['text/html']
        self.assertEqual(predicate(None, request), False)

    def test_add_route_no_pattern_with_path(self):
        config = self._makeOne(autocommit=True)
        route = config.add_route('name', path='path')
        self._assertRoute(config, 'name', 'path')
        self.assertEqual(route.name, 'name')

    def test_add_route_no_path_no_pattern(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.add_route, 'name')

    def test_add_route_with_pregenerator(self):
        config = self._makeOne(autocommit=True)
        route = config.add_route('name', 'pattern', pregenerator='123')
        self.assertEqual(route.pregenerator, '123')

    def test_add_route_no_view_with_view_attr(self):
        config = self._makeOne(autocommit=True)
        from pyramid.exceptions import ConfigurationError
        try:
            config.add_route('name', '/pattern', view_attr='abc')
        except ConfigurationError:
            pass
        else: # pragma: no cover
            raise AssertionError

    def test_add_route_no_view_with_view_context(self):
        config = self._makeOne(autocommit=True)
        from pyramid.exceptions import ConfigurationError
        try:
            config.add_route('name', '/pattern', view_context=DummyContext)
        except ConfigurationError:
            pass
        else: # pragma: no cover
            raise AssertionError

    def test_add_route_no_view_with_view_permission(self):
        config = self._makeOne(autocommit=True)
        from pyramid.exceptions import ConfigurationError
        try:
            config.add_route('name', '/pattern', view_permission='edit')
        except ConfigurationError:
            pass
        else: # pragma: no cover
            raise AssertionError

    def test_add_route_no_view_with_view_renderer(self):
        config = self._makeOne(autocommit=True)
        from pyramid.exceptions import ConfigurationError
        try:
            config.add_route('name', '/pattern', view_renderer='json')
        except ConfigurationError:
            pass
        else: # pragma: no cover
            raise AssertionError

    def test_derive_view_function(self):
        from pyramid.renderers import null_renderer
        def view(request):
            return 'OK'
        config = self._makeOne()
        result = config.derive_view(view, renderer=null_renderer)
        self.assertFalse(result is view)
        self.assertEqual(result(None, None), 'OK')

    def test_derive_view_dottedname(self):
        from pyramid.renderers import null_renderer
        config = self._makeOne()
        result = config.derive_view(
            'pyramid.tests.test_config.dummy_view',
            renderer=null_renderer)
        self.assertFalse(result is dummy_view)
        self.assertEqual(result(None, None), 'OK')

    def test_derive_view_with_default_renderer_no_explicit_renderer(self):
        config = self._makeOne()
        class moo(object):
            def __init__(self, view):
                pass
            def __call__(self, *arg, **kw):
                return 'moo'
        config.add_renderer(None, moo)
        def view(request):
            return 'OK'
        result = config.derive_view(view)
        self.assertFalse(result is view)
        self.assertEqual(result(None, None).body, 'moo')

    def test_derive_view_with_default_renderer_with_explicit_renderer(self):
        class moo(object): pass
        class foo(object):
            def __init__(self, view):
                pass
            def __call__(self, *arg, **kw):
                return 'foo'
        def view(request):
            return 'OK'
        config = self._makeOne()
        config.add_renderer(None, moo)
        config.add_renderer('foo', foo)
        result = config.derive_view(view, renderer='foo')
        self.assertFalse(result is view)
        request = self._makeRequest(config)
        self.assertEqual(result(None, request).body, 'foo')

    def test__override_not_yet_registered(self):
        from pyramid.interfaces import IPackageOverrides
        package = DummyPackage('package')
        opackage = DummyPackage('opackage')
        config = self._makeOne()
        config._override(package, 'path', opackage, 'oprefix',
                         PackageOverrides=DummyOverrides)
        overrides = config.registry.queryUtility(IPackageOverrides,
                                                 name='package')
        self.assertEqual(overrides.inserted, [('path', 'opackage', 'oprefix')])
        self.assertEqual(overrides.package, package)

    def test__override_already_registered(self):
        from pyramid.interfaces import IPackageOverrides
        package = DummyPackage('package')
        opackage = DummyPackage('opackage')
        overrides = DummyOverrides(package)
        config = self._makeOne()
        config.registry.registerUtility(overrides, IPackageOverrides,
                                        name='package')
        config._override(package, 'path', opackage, 'oprefix',
                         PackageOverrides=DummyOverrides)
        self.assertEqual(overrides.inserted, [('path', 'opackage', 'oprefix')])
        self.assertEqual(overrides.package, package)

    def test_action_branching_kw_is_None(self):
        config = self._makeOne(autocommit=True)
        self.assertEqual(config.action('discrim'), None)

    def test_action_branching_kw_is_not_None(self):
        config = self._makeOne(autocommit=True)
        self.assertEqual(config.action('discrim', kw={'a':1}), None)

    def test_action_branching_nonautocommit_without_context_info(self):
        config = self._makeOne(autocommit=False)
        config._ctx = DummyContext()
        config._ctx.info = None
        config._ctx.autocommit = False
        config._ctx.actions = []
        self.assertEqual(config.action('discrim', kw={'a':1}), None)
        self.assertEqual(config._ctx.actions, [('discrim', None, (), {'a': 1})])
        # info is not set on ctx, it's set on the groupingcontextdecorator,
        # and then lost

    def test_action_branching_nonautocommit_with_context_info(self):
        config = self._makeOne(autocommit=False)
        config._ctx = DummyContext()
        config._ctx.info = 'abc'
        config._ctx.autocommit = False
        config._ctx.actions = []
        config._ctx.action = lambda *arg, **kw: self.assertEqual(
            arg,
            ('discrim', None, (), {'a': 1}, 0))
        self.assertEqual(config.action('discrim', kw={'a':1}), None)
        self.assertEqual(config._ctx.actions, [])
        self.assertEqual(config._ctx.info, 'abc')

    def test_add_static_here_no_utility_registered(self):
        from pyramid.renderers import null_renderer
        from zope.interface import Interface
        from pyramid.static import PackageURLParser
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        config = self._makeOne(autocommit=True)
        config.add_static_view('static', 'fixtures/static',
                               renderer=null_renderer)
        request_type = self._getRouteRequestIface(config, 'static/')
        self._assertRoute(config, 'static/', 'static/*subpath')
        wrapped = config.registry.adapters.lookup(
            (IViewClassifier, request_type, Interface), IView, name='')
        request = self._makeRequest(config)
        result = wrapped(None, request)
        self.assertEqual(result.__class__, PackageURLParser)

    def test_add_static_view_package_relative(self):
        from pyramid.interfaces import IStaticURLInfo
        info = DummyStaticURLInfo()
        config = self._makeOne(autocommit=True)
        config.registry.registerUtility(info, IStaticURLInfo)
        config.add_static_view('static', 'pyramid.tests:fixtures/static')
        self.assertEqual(
            info.added,
            [('static', 'pyramid.tests:fixtures/static', {})])

    def test_add_static_view_package_here_relative(self):
        from pyramid.interfaces import IStaticURLInfo
        info = DummyStaticURLInfo()
        config = self._makeOne(autocommit=True)
        config.registry.registerUtility(info, IStaticURLInfo)
        config.add_static_view('static', 'fixtures/static')
        self.assertEqual(
            info.added,
            [('static', 'pyramid.tests.test_config:fixtures/static', {})])

    def test_add_static_view_absolute(self):
        import os
        from pyramid.interfaces import IStaticURLInfo
        info = DummyStaticURLInfo()
        config = self._makeOne(autocommit=True)
        config.registry.registerUtility(info, IStaticURLInfo)
        here = os.path.dirname(__file__)
        static_path = os.path.join(here, 'fixtures', 'static')
        config.add_static_view('static', static_path)
        self.assertEqual(info.added,
                         [('static', static_path, {})])

    def test_set_notfound_view(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.httpexceptions import HTTPNotFound
        config = self._makeOne(autocommit=True)
        view = lambda *arg: arg
        config.set_notfound_view(view, renderer=null_renderer)
        request = self._makeRequest(config)
        view = self._getViewCallable(config,
                                     ctx_iface=implementedBy(HTTPNotFound),
                                     request_iface=IRequest)
        result = view(None, request)
        self.assertEqual(result, (None, request))

    def test_set_notfound_view_request_has_context(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.httpexceptions import HTTPNotFound
        config = self._makeOne(autocommit=True)
        view = lambda *arg: arg
        config.set_notfound_view(view, renderer=null_renderer)
        request = self._makeRequest(config)
        request.context = 'abc'
        view = self._getViewCallable(config,
                                     ctx_iface=implementedBy(HTTPNotFound),
                                     request_iface=IRequest)
        result = view(None, request)
        self.assertEqual(result, ('abc', request))

    @testing.skip_on('java')
    def test_set_notfound_view_with_renderer(self):
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.httpexceptions import HTTPNotFound
        config = self._makeOne(autocommit=True)
        view = lambda *arg: {}
        config.set_notfound_view(
            view,
            renderer='pyramid.tests:fixtures/minimal.pt')
        config.begin()
        try: # chameleon depends on being able to find a threadlocal registry
            request = self._makeRequest(config)
            view = self._getViewCallable(config,
                                         ctx_iface=implementedBy(HTTPNotFound),
                                         request_iface=IRequest)
            result = view(None, request)
        finally:
            config.end()
        self.assertTrue('div' in result.body)

    def test_set_forbidden_view(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.httpexceptions import HTTPForbidden
        config = self._makeOne(autocommit=True)
        view = lambda *arg: 'OK'
        config.set_forbidden_view(view, renderer=null_renderer)
        request = self._makeRequest(config)
        view = self._getViewCallable(config,
                                     ctx_iface=implementedBy(HTTPForbidden),
                                     request_iface=IRequest)
        result = view(None, request)
        self.assertEqual(result, 'OK')

    def test_set_forbidden_view_request_has_context(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.httpexceptions import HTTPForbidden
        config = self._makeOne(autocommit=True)
        view = lambda *arg: arg
        config.set_forbidden_view(view, renderer=null_renderer)
        request = self._makeRequest(config)
        request.context = 'abc'
        view = self._getViewCallable(config,
                                     ctx_iface=implementedBy(HTTPForbidden),
                                     request_iface=IRequest)
        result = view(None, request)
        self.assertEqual(result, ('abc', request))

    @testing.skip_on('java')
    def test_set_forbidden_view_with_renderer(self):
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.httpexceptions import HTTPForbidden
        config = self._makeOne(autocommit=True)
        view = lambda *arg: {}
        config.set_forbidden_view(
            view,
            renderer='pyramid.tests:fixtures/minimal.pt')
        config.begin()
        try: # chameleon requires a threadlocal registry
            request = self._makeRequest(config)
            view = self._getViewCallable(config,
                                         ctx_iface=implementedBy(HTTPForbidden),
                                         request_iface=IRequest)
            result = view(None, request)
        finally:
            config.end()
        self.assertTrue('div' in result.body)

    def test_set_locale_negotiator(self):
        from pyramid.interfaces import ILocaleNegotiator
        config = self._makeOne(autocommit=True)
        def negotiator(request): pass
        config.set_locale_negotiator(negotiator)
        self.assertEqual(config.registry.getUtility(ILocaleNegotiator),
                         negotiator)

    def test_set_locale_negotiator_dottedname(self):
        from pyramid.interfaces import ILocaleNegotiator
        config = self._makeOne(autocommit=True)
        config.set_locale_negotiator(
            'pyramid.tests.test_config.dummyfactory')
        self.assertEqual(config.registry.getUtility(ILocaleNegotiator),
                         dummyfactory)

    def test_set_request_factory(self):
        from pyramid.interfaces import IRequestFactory
        config = self._makeOne(autocommit=True)
        factory = object()
        config.set_request_factory(factory)
        self.assertEqual(config.registry.getUtility(IRequestFactory), factory)

    def test_set_request_factory_dottedname(self):
        from pyramid.interfaces import IRequestFactory
        config = self._makeOne(autocommit=True)
        config.set_request_factory(
            'pyramid.tests.test_config.dummyfactory')
        self.assertEqual(config.registry.getUtility(IRequestFactory),
                         dummyfactory)

    def test_set_renderer_globals_factory(self):
        import warnings
        warnings.filterwarnings('ignore')
        try:
            from pyramid.interfaces import IRendererGlobalsFactory
            config = self._makeOne(autocommit=True)
            factory = object()
            config.set_renderer_globals_factory(factory)
            self.assertEqual(
                config.registry.getUtility(IRendererGlobalsFactory),
                factory)
        finally:
            warnings.resetwarnings()

    def test_set_renderer_globals_factory_dottedname(self):
        import warnings
        warnings.filterwarnings('ignore')
        try:
            from pyramid.interfaces import IRendererGlobalsFactory
            config = self._makeOne(autocommit=True)
            config.set_renderer_globals_factory(
                'pyramid.tests.test_config.dummyfactory')
            self.assertEqual(
                config.registry.getUtility(IRendererGlobalsFactory),
                dummyfactory)
        finally:
            warnings.resetwarnings()

    def test_set_default_permission(self):
        from pyramid.interfaces import IDefaultPermission
        config = self._makeOne(autocommit=True)
        config.set_default_permission('view')
        self.assertEqual(config.registry.getUtility(IDefaultPermission),
                         'view')

    def test_add_view_mapper(self):
        from pyramid.interfaces import IViewMapperFactory
        config = self._makeOne(autocommit=True)
        mapper = object()
        config.set_view_mapper(mapper)
        result = config.registry.getUtility(IViewMapperFactory)
        self.assertEqual(result, mapper)

    def test_add_view_mapper_dottedname(self):
        from pyramid.interfaces import IViewMapperFactory
        config = self._makeOne(autocommit=True)
        config.set_view_mapper('pyramid.tests.test_config')
        result = config.registry.getUtility(IViewMapperFactory)
        from pyramid.tests import test_config
        self.assertEqual(result, test_config)

    def test_set_session_factory(self):
        from pyramid.interfaces import ISessionFactory
        config = self._makeOne(autocommit=True)
        config.set_session_factory('factory')
        self.assertEqual(config.registry.getUtility(ISessionFactory),
                         'factory')

    def test_add_translation_dirs_missing_dir(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError,
                          config.add_translation_dirs,
                          '/wont/exist/on/my/system')

    def test_add_translation_dirs_no_specs(self):
        from pyramid.interfaces import ITranslationDirectories
        from pyramid.interfaces import IChameleonTranslate
        config = self._makeOne()
        config.add_translation_dirs()
        self.assertEqual(config.registry.queryUtility(ITranslationDirectories),
                         None)
        self.assertEqual(config.registry.queryUtility(IChameleonTranslate),
                         None)

    def test_add_translation_dirs_asset_spec(self):
        from pyramid.interfaces import ITranslationDirectories
        config = self._makeOne(autocommit=True)
        config.add_translation_dirs('pyramid.tests.localeapp:locale')
        self.assertEqual(config.registry.getUtility(ITranslationDirectories),
                         [locale])

    def test_add_translation_dirs_asset_spec_existing_translation_dirs(self):
        from pyramid.interfaces import ITranslationDirectories
        config = self._makeOne(autocommit=True)
        directories = ['abc']
        config.registry.registerUtility(directories, ITranslationDirectories)
        config.add_translation_dirs('pyramid.tests.localeapp:locale')
        result = config.registry.getUtility(ITranslationDirectories)
        self.assertEqual(result, [locale, 'abc'])

    def test_add_translation_dirs_multiple_specs(self):
        from pyramid.interfaces import ITranslationDirectories
        config = self._makeOne(autocommit=True)
        config.add_translation_dirs('pyramid.tests.localeapp:locale',
                                    'pyramid.tests.localeapp:locale2')
        self.assertEqual(config.registry.getUtility(ITranslationDirectories),
                         [locale, locale2])

    def test_add_translation_dirs_multiple_specs_multiple_calls(self):
        from pyramid.interfaces import ITranslationDirectories
        config = self._makeOne(autocommit=True)
        config.add_translation_dirs('pyramid.tests.localeapp:locale',
                                    'pyramid.tests.localeapp:locale2')
        config.add_translation_dirs('pyramid.tests.localeapp:locale3')
        self.assertEqual(config.registry.getUtility(ITranslationDirectories),
                         [locale3, locale, locale2])

    def test_add_translation_dirs_registers_chameleon_translate(self):
        from pyramid.interfaces import IChameleonTranslate
        from pyramid.threadlocal import manager
        request = DummyRequest()
        config = self._makeOne(autocommit=True)
        manager.push({'request':request, 'registry':config.registry})
        try:
            config.add_translation_dirs('pyramid.tests.localeapp:locale')
            translate = config.registry.getUtility(IChameleonTranslate)
            self.assertEqual(translate('Approve'), u'Approve')
        finally:
            manager.pop()

    def test_add_translation_dirs_abspath(self):
        from pyramid.interfaces import ITranslationDirectories
        config = self._makeOne(autocommit=True)
        config.add_translation_dirs(locale)
        self.assertEqual(config.registry.getUtility(ITranslationDirectories),
                         [locale])

    def test_override_asset_samename(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.override_asset,'a', 'a')

    def test_override_asset_directory_with_file(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.override_asset,
                          'a:foo/', 'a:foo.pt')

    def test_override_asset_file_with_directory(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.override_asset,
                          'a:foo.pt', 'a:foo/')

    def test_override_asset_file_with_package(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.override_asset,
                          'a:foo.pt', 'a')

    def test_override_asset_file_with_file(self):
        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'pyramid.tests.fixtureapp:templates/foo.pt',
            'pyramid.tests.fixtureapp.subpackage:templates/bar.pt',
            _override=override)
        from pyramid.tests import fixtureapp
        from pyramid.tests.fixtureapp import subpackage
        self.assertEqual(override.package, fixtureapp)
        self.assertEqual(override.path, 'templates/foo.pt')
        self.assertEqual(override.override_package, subpackage)
        self.assertEqual(override.override_prefix, 'templates/bar.pt')

    def test_override_asset_package_with_package(self):
        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'pyramid.tests.fixtureapp',
            'pyramid.tests.fixtureapp.subpackage',
            _override=override)
        from pyramid.tests import fixtureapp
        from pyramid.tests.fixtureapp import subpackage
        self.assertEqual(override.package, fixtureapp)
        self.assertEqual(override.path, '')
        self.assertEqual(override.override_package, subpackage)
        self.assertEqual(override.override_prefix, '')

    def test_override_asset_directory_with_directory(self):
        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'pyramid.tests.fixtureapp:templates/',
            'pyramid.tests.fixtureapp.subpackage:templates/',
            _override=override)
        from pyramid.tests import fixtureapp
        from pyramid.tests.fixtureapp import subpackage
        self.assertEqual(override.package, fixtureapp)
        self.assertEqual(override.path, 'templates/')
        self.assertEqual(override.override_package, subpackage)
        self.assertEqual(override.override_prefix, 'templates/')

    def test_override_asset_directory_with_package(self):
        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'pyramid.tests.fixtureapp:templates/',
            'pyramid.tests.fixtureapp.subpackage',
            _override=override)
        from pyramid.tests import fixtureapp
        from pyramid.tests.fixtureapp import subpackage
        self.assertEqual(override.package, fixtureapp)
        self.assertEqual(override.path, 'templates/')
        self.assertEqual(override.override_package, subpackage)
        self.assertEqual(override.override_prefix, '')

    def test_override_asset_package_with_directory(self):
        config = self._makeOne(autocommit=True)
        override = DummyUnderOverride()
        config.override_asset(
            'pyramid.tests.fixtureapp',
            'pyramid.tests.fixtureapp.subpackage:templates/',
            _override=override)
        from pyramid.tests import fixtureapp
        from pyramid.tests.fixtureapp import subpackage
        self.assertEqual(override.package, fixtureapp)
        self.assertEqual(override.path, '')
        self.assertEqual(override.override_package, subpackage)
        self.assertEqual(override.override_prefix, 'templates/')

    def test_add_renderer(self):
        from pyramid.interfaces import IRendererFactory
        config = self._makeOne(autocommit=True)
        renderer = object()
        config.add_renderer('name', renderer)
        self.assertEqual(config.registry.getUtility(IRendererFactory, 'name'),
                         renderer)

    def test_add_renderer_dottedname_factory(self):
        from pyramid.interfaces import IRendererFactory
        config = self._makeOne(autocommit=True)
        import pyramid.tests
        config.add_renderer('name', 'pyramid.tests')
        self.assertEqual(config.registry.getUtility(IRendererFactory, 'name'),
                         pyramid.tests)

    def test_add_response_adapter(self):
        from pyramid.interfaces import IResponse
        config = self._makeOne(autocommit=True)
        class Adapter(object):
            def __init__(self, other):
                self.other = other
        config.add_response_adapter(Adapter, str)
        result = config.registry.queryAdapter('foo', IResponse)
        self.assertTrue(result.other, 'foo')

    def test_add_response_adapter_self(self):
        from pyramid.interfaces import IResponse
        config = self._makeOne(autocommit=True)
        class Adapter(object):
            pass
        config.add_response_adapter(None, Adapter)
        adapter = Adapter()
        result = config.registry.queryAdapter(adapter, IResponse)
        self.assertTrue(result is adapter)

    def test_add_response_adapter_dottednames(self):
        from pyramid.interfaces import IResponse
        config = self._makeOne(autocommit=True)
        config.add_response_adapter('pyramid.response.Response',
                                    'types.StringType')
        result = config.registry.queryAdapter('foo', IResponse)
        self.assertTrue(result.body, 'foo')

    def test_scan_integration(self):
        import os
        from zope.interface import alsoProvides
        from pyramid.interfaces import IRequest
        from pyramid.view import render_view_to_response
        import pyramid.tests.grokkedapp as package
        config = self._makeOne(autocommit=True)
        config.scan(package)

        ctx = DummyContext()
        req = DummyRequest()
        alsoProvides(req, IRequest)
        req.registry = config.registry

        req.method = 'GET'
        result = render_view_to_response(ctx, req, '')
        self.assertEqual(result, 'grokked')

        req.method = 'POST'
        result = render_view_to_response(ctx, req, '')
        self.assertEqual(result, 'grokked_post')

        result= render_view_to_response(ctx, req, 'grokked_class')
        self.assertEqual(result, 'grokked_class')

        result= render_view_to_response(ctx, req, 'grokked_instance')
        self.assertEqual(result, 'grokked_instance')

        result= render_view_to_response(ctx, req, 'oldstyle_grokked_class')
        self.assertEqual(result, 'oldstyle_grokked_class')

        req.method = 'GET'
        result = render_view_to_response(ctx, req, 'another')
        self.assertEqual(result, 'another_grokked')

        req.method = 'POST'
        result = render_view_to_response(ctx, req, 'another')
        self.assertEqual(result, 'another_grokked_post')

        result= render_view_to_response(ctx, req, 'another_grokked_class')
        self.assertEqual(result, 'another_grokked_class')

        result= render_view_to_response(ctx, req, 'another_grokked_instance')
        self.assertEqual(result, 'another_grokked_instance')

        result= render_view_to_response(ctx, req,
                                        'another_oldstyle_grokked_class')
        self.assertEqual(result, 'another_oldstyle_grokked_class')

        result = render_view_to_response(ctx, req, 'stacked1')
        self.assertEqual(result, 'stacked')

        result = render_view_to_response(ctx, req, 'stacked2')
        self.assertEqual(result, 'stacked')

        result = render_view_to_response(ctx, req, 'another_stacked1')
        self.assertEqual(result, 'another_stacked')

        result = render_view_to_response(ctx, req, 'another_stacked2')
        self.assertEqual(result, 'another_stacked')

        result = render_view_to_response(ctx, req, 'stacked_class1')
        self.assertEqual(result, 'stacked_class')

        result = render_view_to_response(ctx, req, 'stacked_class2')
        self.assertEqual(result, 'stacked_class')

        result = render_view_to_response(ctx, req, 'another_stacked_class1')
        self.assertEqual(result, 'another_stacked_class')

        result = render_view_to_response(ctx, req, 'another_stacked_class2')
        self.assertEqual(result, 'another_stacked_class')

        if not os.name.startswith('java'):
            # on Jython, a class without an __init__ apparently accepts
            # any number of arguments without raising a TypeError.

            self.assertRaises(TypeError,
                              render_view_to_response, ctx, req, 'basemethod')

        result = render_view_to_response(ctx, req, 'method1')
        self.assertEqual(result, 'method1')

        result = render_view_to_response(ctx, req, 'method2')
        self.assertEqual(result, 'method2')

        result = render_view_to_response(ctx, req, 'stacked_method1')
        self.assertEqual(result, 'stacked_method')

        result = render_view_to_response(ctx, req, 'stacked_method2')
        self.assertEqual(result, 'stacked_method')

        result = render_view_to_response(ctx, req, 'subpackage_init')
        self.assertEqual(result, 'subpackage_init')

        result = render_view_to_response(ctx, req, 'subpackage_notinit')
        self.assertEqual(result, 'subpackage_notinit')

        result = render_view_to_response(ctx, req, 'subsubpackage_init')
        self.assertEqual(result, 'subsubpackage_init')

        result = render_view_to_response(ctx, req, 'pod_notinit')
        self.assertEqual(result, None)

    def test_scan_integration_dottedname_package(self):
        from zope.interface import alsoProvides
        from pyramid.interfaces import IRequest
        from pyramid.view import render_view_to_response
        config = self._makeOne(autocommit=True)
        config.scan('pyramid.tests.grokkedapp')

        ctx = DummyContext()
        req = DummyRequest()
        alsoProvides(req, IRequest)
        req.registry = config.registry

        req.method = 'GET'
        result = render_view_to_response(ctx, req, '')
        self.assertEqual(result, 'grokked')

    def test_scan_integration_with_extra_kw(self):
        config = self._makeOne(autocommit=True)
        config.scan('pyramid.tests.venusianapp', a=1)
        self.assertEqual(config.a, 1)

    def test_testing_securitypolicy(self):
        from pyramid.testing import DummySecurityPolicy
        config = self._makeOne(autocommit=True)
        config.testing_securitypolicy('user', ('group1', 'group2'),
                                      permissive=False)
        from pyramid.interfaces import IAuthenticationPolicy
        from pyramid.interfaces import IAuthorizationPolicy
        ut = config.registry.getUtility(IAuthenticationPolicy)
        self.assertTrue(isinstance(ut, DummySecurityPolicy))
        ut = config.registry.getUtility(IAuthorizationPolicy)
        self.assertEqual(ut.userid, 'user')
        self.assertEqual(ut.groupids, ('group1', 'group2'))
        self.assertEqual(ut.permissive, False)

    def test_testing_resources(self):
        from pyramid.traversal import find_resource
        from pyramid.interfaces import ITraverser
        ob1 = object()
        ob2 = object()
        resources = {'/ob1':ob1, '/ob2':ob2}
        config = self._makeOne(autocommit=True)
        config.testing_resources(resources)
        adapter = config.registry.getAdapter(None, ITraverser)
        result = adapter(DummyRequest({'PATH_INFO':'/ob1'}))
        self.assertEqual(result['context'], ob1)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'ob1',))
        self.assertEqual(result['virtual_root'], ob1)
        self.assertEqual(result['virtual_root_path'], ())
        result = adapter(DummyRequest({'PATH_INFO':'/ob2'}))
        self.assertEqual(result['context'], ob2)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'ob2',))
        self.assertEqual(result['virtual_root'], ob2)
        self.assertEqual(result['virtual_root_path'], ())
        self.assertRaises(KeyError, adapter, DummyRequest({'PATH_INFO':'/ob3'}))
        try:
            config.begin()
            self.assertEqual(find_resource(None, '/ob1'), ob1)
        finally:
            config.end()

    def test_testing_add_subscriber_single(self):
        config = self._makeOne(autocommit=True)
        L = config.testing_add_subscriber(IDummy)
        event = DummyEvent()
        config.registry.notify(event)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        config.registry.notify(object())
        self.assertEqual(len(L), 1)

    def test_testing_add_subscriber_dottedname(self):
        config = self._makeOne(autocommit=True)
        L = config.testing_add_subscriber(
            'pyramid.tests.test_config.test_init.IDummy')
        event = DummyEvent()
        config.registry.notify(event)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        config.registry.notify(object())
        self.assertEqual(len(L), 1)

    def test_testing_add_subscriber_multiple(self):
        config = self._makeOne(autocommit=True)
        L = config.testing_add_subscriber((Interface, IDummy))
        event = DummyEvent()
        event.object = 'foo'
        # the below is the equivalent of z.c.event.objectEventNotify(event)
        config.registry.subscribers((event.object, event), None)
        self.assertEqual(len(L), 2)
        self.assertEqual(L[0], 'foo')
        self.assertEqual(L[1], event)

    def test_testing_add_subscriber_defaults(self):
        config = self._makeOne(autocommit=True)
        L = config.testing_add_subscriber()
        event = object()
        config.registry.notify(event)
        self.assertEqual(L[-1], event)
        event2 = object()
        config.registry.notify(event2)
        self.assertEqual(L[-1], event2)

    def test_hook_zca(self):
        from zope.component import getSiteManager
        def foo():
            '123'
        try:
            config = self._makeOne()
            config.hook_zca()
            config.begin()
            sm = getSiteManager()
            self.assertEqual(sm, config.registry)
        finally:
            getSiteManager.reset()

    def test_unhook_zca(self):
        from zope.component import getSiteManager
        def foo():
            '123'
        try:
            getSiteManager.sethook(foo)
            config = self._makeOne()
            config.unhook_zca()
            sm = getSiteManager()
            self.assertNotEqual(sm, '123')
        finally:
            getSiteManager.reset()
        
    def test_testing_add_renderer(self):
        config = self._makeOne(autocommit=True)
        renderer = config.testing_add_renderer('templates/foo.pt')
        from pyramid.testing import DummyTemplateRenderer
        self.assertTrue(isinstance(renderer, DummyTemplateRenderer))
        from pyramid.renderers import render_to_response
        # must provide request to pass in registry (this is a functest)
        request = DummyRequest()
        request.registry = config.registry
        render_to_response(
            'templates/foo.pt', {'foo':1, 'bar':2}, request=request)
        renderer.assert_(foo=1)
        renderer.assert_(bar=2)
        renderer.assert_(request=request)

    def test_testing_add_renderer_twice(self):
        config = self._makeOne(autocommit=True)
        renderer1 = config.testing_add_renderer('templates/foo.pt')
        renderer2 = config.testing_add_renderer('templates/bar.pt')
        from pyramid.testing import DummyTemplateRenderer
        self.assertTrue(isinstance(renderer1, DummyTemplateRenderer))
        self.assertTrue(isinstance(renderer2, DummyTemplateRenderer))
        from pyramid.renderers import render_to_response
        # must provide request to pass in registry (this is a functest)
        request = DummyRequest()
        request.registry = config.registry
        render_to_response(
            'templates/foo.pt', {'foo':1, 'bar':2}, request=request)
        renderer1.assert_(foo=1)
        renderer1.assert_(bar=2)
        renderer1.assert_(request=request)
        render_to_response(
            'templates/bar.pt', {'foo':1, 'bar':2}, request=request)
        renderer2.assert_(foo=1)
        renderer2.assert_(bar=2)
        renderer2.assert_(request=request)

    def test_testing_add_renderer_explicitrenderer(self):
        config = self._makeOne(autocommit=True)
        class E(Exception): pass
        def renderer(kw, system):
            self.assertEqual(kw, {'foo':1, 'bar':2})
            raise E
        renderer = config.testing_add_renderer('templates/foo.pt', renderer)
        from pyramid.renderers import render_to_response
        # must provide request to pass in registry (this is a functest)
        request = DummyRequest()
        request.registry = config.registry
        try:
            render_to_response(
                'templates/foo.pt', {'foo':1, 'bar':2}, request=request)
        except E:
            pass
        else: # pragma: no cover
            raise AssertionError

    def test_testing_add_template(self):
        config = self._makeOne(autocommit=True)
        renderer = config.testing_add_template('templates/foo.pt')
        from pyramid.testing import DummyTemplateRenderer
        self.assertTrue(isinstance(renderer, DummyTemplateRenderer))
        from pyramid.renderers import render_to_response
        # must provide request to pass in registry (this is a functest)
        request = DummyRequest()
        request.registry = config.registry
        render_to_response('templates/foo.pt', dict(foo=1, bar=2),
                           request=request)
        renderer.assert_(foo=1)
        renderer.assert_(bar=2)
        renderer.assert_(request=request)

    def test_commit_conflict_simple(self):
        from zope.configuration.config import ConfigurationConflictError
        config = self._makeOne()
        def view1(request): pass
        def view2(request): pass
        config.add_view(view1)
        config.add_view(view2)
        self.assertRaises(ConfigurationConflictError, config.commit)

    def test_commit_conflict_resolved_with_include(self):
        config = self._makeOne()
        def view1(request): pass
        def view2(request): pass
        def includeme(config):
            config.add_view(view2)
        config.add_view(view1)
        config.include(includeme)
        config.commit()
        registeredview = self._getViewCallable(config)
        self.assertEqual(registeredview.__name__, 'view1')

    def test_commit_conflict_with_two_includes(self):
        from zope.configuration.config import ConfigurationConflictError
        config = self._makeOne()
        def view1(request): pass
        def view2(request): pass
        def includeme1(config):
            config.add_view(view1)
        def includeme2(config):
            config.add_view(view2)
        config.include(includeme1)
        config.include(includeme2)
        try:
            config.commit()
        except ConfigurationConflictError, why:
            c1, c2 = self._conflictFunctions(why)
            self.assertEqual(c1, 'includeme1')
            self.assertEqual(c2, 'includeme2')
        else: #pragma: no cover
            raise AssertionError

    def test_commit_conflict_resolved_with_two_includes_and_local(self):
        config = self._makeOne()
        def view1(request): pass
        def view2(request): pass
        def view3(request): pass
        def includeme1(config):
            config.add_view(view1)
        def includeme2(config):
            config.add_view(view2)
        config.include(includeme1)
        config.include(includeme2)
        config.add_view(view3)
        config.commit()
        registeredview = self._getViewCallable(config)
        self.assertEqual(registeredview.__name__, 'view3')

    def test_autocommit_no_conflicts(self):
        from pyramid.renderers import null_renderer
        config = self._makeOne(autocommit=True)
        def view1(request): pass
        def view2(request): pass
        def view3(request): pass
        config.add_view(view1, renderer=null_renderer)
        config.add_view(view2, renderer=null_renderer)
        config.add_view(view3, renderer=null_renderer)
        config.commit()
        registeredview = self._getViewCallable(config)
        self.assertEqual(registeredview.__name__, 'view3')

    def test_conflict_set_notfound_view(self):
        from zope.configuration.config import ConfigurationConflictError
        config = self._makeOne()
        def view1(request): pass
        def view2(request): pass
        config.set_notfound_view(view1)
        config.set_notfound_view(view2)
        try:
            config.commit()
        except ConfigurationConflictError, why:
            c1, c2 = self._conflictFunctions(why)
            self.assertEqual(c1, 'test_conflict_set_notfound_view')
            self.assertEqual(c2, 'test_conflict_set_notfound_view')
        else: # pragma: no cover
            raise AssertionError

    def test_conflict_set_forbidden_view(self):
        from zope.configuration.config import ConfigurationConflictError
        config = self._makeOne()
        def view1(request): pass
        def view2(request): pass
        config.set_forbidden_view(view1)
        config.set_forbidden_view(view2)
        try:
            config.commit()
        except ConfigurationConflictError, why:
            c1, c2 = self._conflictFunctions(why)
            self.assertEqual(c1, 'test_conflict_set_forbidden_view')
            self.assertEqual(c2, 'test_conflict_set_forbidden_view')
        else: # pragma: no cover
            raise AssertionError

    def test_scan_conflict(self):
        from zope.configuration.config import ConfigurationConflictError
        from pyramid.tests import selfscanapp
        from pyramid.config import Configurator
        c = Configurator()
        c.scan(selfscanapp)
        c.scan(selfscanapp)
        try:
            c.commit()
        except ConfigurationConflictError, why:
            def scanconflicts(e):
                conflicts = e._conflicts.values()
                for conflict in conflicts:
                    for confinst in conflict:
                        yield confinst[3]
            which = list(scanconflicts(why))
            self.assertEqual(len(which), 4)
            self.assertTrue("@view_config(renderer='string')" in which)
            self.assertTrue("@view_config(name='two', renderer='string')" in
                            which)

    def test___getattr__missing_when_directives_exist(self):
        config = self._makeOne()
        directives = {}
        config.registry._directives = directives
        self.assertRaises(AttributeError, config.__getattr__, 'wontexist')

    def test___getattr__missing_when_directives_dont_exist(self):
        config = self._makeOne()
        self.assertRaises(AttributeError, config.__getattr__, 'wontexist')

    def test___getattr__matches(self):
        config = self._makeOne()
        def foo(config): pass
        directives = {'foo':(foo, True)}
        config.registry._directives = directives
        foo_meth = config.foo
        self.assertTrue(foo_meth.im_func.__docobj__ is foo)

    def test___getattr__matches_no_action_wrap(self):
        config = self._makeOne()
        def foo(config): pass
        directives = {'foo':(foo, False)}
        config.registry._directives = directives
        foo_meth = config.foo
        self.assertTrue(foo_meth.im_func is foo)

class TestConfiguratorDeprecatedFeatures(unittest.TestCase):
    def setUp(self):
        import warnings
        warnings.filterwarnings('ignore')

    def tearDown(self):
        import warnings
        warnings.resetwarnings()

    def _makeOne(self, *arg, **kw):
        from pyramid.config import Configurator
        config = Configurator(*arg, **kw)
        config.registry._dont_resolve_responses = True
        return config
    
    def _getRouteRequestIface(self, config, name):
        from pyramid.interfaces import IRouteRequest
        iface = config.registry.getUtility(IRouteRequest, name)
        return iface

    def _getViewCallable(self, config, ctx_iface=None, request_iface=None,
                         name='', exception_view=False):
        from zope.interface import Interface
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IExceptionViewClassifier
        if exception_view:
            classifier = IExceptionViewClassifier
        else:
            classifier = IViewClassifier
        if ctx_iface is None:
            ctx_iface = Interface
        return config.registry.adapters.lookup(
            (classifier, request_iface, ctx_iface), IView, name=name,
            default=None)

    def _registerRenderer(self, config, name='.txt'):
        from pyramid.interfaces import IRendererFactory
        from pyramid.interfaces import ITemplateRenderer
        from zope.interface import implements
        class Renderer:
            implements(ITemplateRenderer)
            def __init__(self, info):
                self.__class__.info = info
            def __call__(self, *arg):
                return 'Hello!'
        config.registry.registerUtility(Renderer, IRendererFactory, name=name)
        return Renderer

    def _assertRoute(self, config, name, path, num_predicates=0):
        from pyramid.interfaces import IRoutesMapper
        mapper = config.registry.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        route = routes[0]
        self.assertEqual(len(routes), 1)
        self.assertEqual(route.name, name)
        self.assertEqual(route.path, path)
        self.assertEqual(len(routes[0].predicates), num_predicates)
        return route

    def _makeRequest(self, config):
        request = DummyRequest()
        request.registry = config.registry
        return request

    def _conflictFunctions(self, e):
        conflicts = e._conflicts.values()
        for conflict in conflicts:
            for confinst in conflict:
                yield confinst[2]

    def test_add_route_with_view(self):
        from pyramid.renderers import null_renderer
        config = self._makeOne(autocommit=True)
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view, view_renderer=null_renderer)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        self.assertEqual(wrapper(None, None), 'OK')
        self._assertRoute(config, 'name', 'path')

    def test_add_route_with_view_context(self):
        from pyramid.renderers import null_renderer
        config = self._makeOne(autocommit=True)
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view, view_context=IDummy,
                         view_renderer=null_renderer)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, IDummy, request_type)
        self.assertEqual(wrapper(None, None), 'OK')
        self._assertRoute(config, 'name', 'path')
        wrapper = self._getViewCallable(config, IOther, request_type)
        self.assertEqual(wrapper, None)

    def test_add_route_with_view_exception(self):
        from pyramid.renderers import null_renderer
        from zope.interface import implementedBy
        config = self._makeOne(autocommit=True)
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view, view_context=RuntimeError,
                         view_renderer=null_renderer)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError),
            request_iface=request_type, exception_view=True)
        self.assertEqual(wrapper(None, None), 'OK')
        self._assertRoute(config, 'name', 'path')
        wrapper = self._getViewCallable(
            config, ctx_iface=IOther,
            request_iface=request_type, exception_view=True)
        self.assertEqual(wrapper, None)

    def test_add_route_with_view_for(self):
        from pyramid.renderers import null_renderer
        config = self._makeOne(autocommit=True)
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view, view_for=IDummy,
                         view_renderer=null_renderer)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, IDummy, request_type)
        self.assertEqual(wrapper(None, None), 'OK')
        self._assertRoute(config, 'name', 'path')
        wrapper = self._getViewCallable(config, IOther, request_type)
        self.assertEqual(wrapper, None)

    def test_add_route_with_for_(self):
        from pyramid.renderers import null_renderer
        config = self._makeOne(autocommit=True)
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view, for_=IDummy,
                         view_renderer=null_renderer)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, IDummy, request_type)
        self.assertEqual(wrapper(None, None), 'OK')
        self._assertRoute(config, 'name', 'path')
        wrapper = self._getViewCallable(config, IOther, request_type)
        self.assertEqual(wrapper, None)

    def test_add_route_with_view_renderer(self):
        config = self._makeOne(autocommit=True)
        self._registerRenderer(config)
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view,
                         view_renderer='fixtures/minimal.txt')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        self._assertRoute(config, 'name', 'path')
        self.assertEqual(wrapper(None, None).body, 'Hello!')

    def test_add_route_with_view_attr(self):
        from pyramid.renderers import null_renderer
        config = self._makeOne(autocommit=True)
        self._registerRenderer(config)
        class View(object):
            def __init__(self, context, request):
                pass
            def alt(self):
                return 'OK'
        config.add_route('name', 'path', view=View, view_attr='alt',
                         view_renderer=null_renderer)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        self._assertRoute(config, 'name', 'path')
        request = self._makeRequest(config)
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_route_with_view_renderer_alias(self):
        config = self._makeOne(autocommit=True)
        self._registerRenderer(config)
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view,
                         renderer='fixtures/minimal.txt')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        self._assertRoute(config, 'name', 'path')
        self.assertEqual(wrapper(None, None).body, 'Hello!')

    def test_add_route_with_view_permission(self):
        from pyramid.interfaces import IAuthenticationPolicy
        from pyramid.interfaces import IAuthorizationPolicy
        config = self._makeOne(autocommit=True)
        policy = lambda *arg: None
        config.registry.registerUtility(policy, IAuthenticationPolicy)
        config.registry.registerUtility(policy, IAuthorizationPolicy)
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view, view_permission='edit')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        self._assertRoute(config, 'name', 'path')
        self.assertTrue(hasattr(wrapper, '__call_permissive__'))

    def test_add_route_with_view_permission_alias(self):
        from pyramid.interfaces import IAuthenticationPolicy
        from pyramid.interfaces import IAuthorizationPolicy
        config = self._makeOne(autocommit=True)
        policy = lambda *arg: None
        config.registry.registerUtility(policy, IAuthenticationPolicy)
        config.registry.registerUtility(policy, IAuthorizationPolicy)
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view, permission='edit')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        self._assertRoute(config, 'name', 'path')
        self.assertTrue(hasattr(wrapper, '__call_permissive__'))

    def test_conflict_route_with_view(self):
        from zope.configuration.config import ConfigurationConflictError
        config = self._makeOne()
        def view1(request): pass
        def view2(request): pass
        config.add_route('a', '/a', view=view1)
        config.add_route('a', '/a', view=view2)
        try:
            config.commit()
        except ConfigurationConflictError, why:
            c1, c2, c3, c4 = self._conflictFunctions(why)
            self.assertEqual(c1, 'test_conflict_route_with_view')
            self.assertEqual(c2, 'test_conflict_route_with_view')
            self.assertEqual(c3, 'test_conflict_route_with_view')
            self.assertEqual(c4, 'test_conflict_route_with_view')
        else: # pragma: no cover
            raise AssertionError
        

class TestConfigurator_add_directive(unittest.TestCase):

    def setUp(self):
        from pyramid.config import Configurator
        self.config = Configurator()

    def test_extend_with_dotted_name(self):
        from pyramid.tests import test_config
        config = self.config
        config.add_directive(
            'dummy_extend', 'pyramid.tests.test_config.dummy_extend')
        self.assert_(hasattr(config, 'dummy_extend'))
        config.dummy_extend('discrim')
        context_after = config._ctx
        self.assertEqual(
            context_after.actions[-1][:3],
            ('discrim', None, test_config),
            )

    def test_extend_with_python_callable(self):
        from pyramid.tests import test_config
        config = self.config
        config.add_directive(
            'dummy_extend', dummy_extend)
        self.assert_(hasattr(config, 'dummy_extend'))
        config.dummy_extend('discrim')
        context_after = config._ctx
        self.assertEqual(
            context_after.actions[-1][:3],
            ('discrim', None, test_config),
            )

    def test_extend_same_name_doesnt_conflict(self):
        config = self.config
        config.add_directive(
            'dummy_extend', dummy_extend)
        config.add_directive(
            'dummy_extend', dummy_extend2)
        self.assert_(hasattr(config, 'dummy_extend'))
        config.dummy_extend('discrim')
        context_after = config._ctx
        self.assertEqual(
            context_after.actions[-1][:3],
            ('discrim', None, config.registry),
            )

    def test_extend_action_method_successful(self):
        from zope.configuration.config import ConfigurationConflictError
        config = self.config
        config.add_directive(
            'dummy_extend', dummy_extend)
        config.dummy_extend('discrim')
        config.dummy_extend('discrim')
        self.assertRaises(ConfigurationConflictError, config.commit)

    def test_directive_persists_across_configurator_creations(self):
        from zope.configuration.config import GroupingContextDecorator
        config = self.config
        config.add_directive('dummy_extend', dummy_extend)
        context = config._make_context(autocommit=False)
        context = GroupingContextDecorator(context)
        config2 = config.with_context(context)
        config2.dummy_extend('discrim')
        context_after = config2._ctx
        actions = context_after.actions
        self.assertEqual(len(actions), 1)
        self.assertEqual(
            context_after.actions[0][:3],
            ('discrim', None, config2.package),
            )

class TestPyramidConfigurationMachine(unittest.TestCase):
    def test_it(self):
        from pyramid.config import PyramidConfigurationMachine
        m = PyramidConfigurationMachine()
        self.assertEqual(m.autocommit, False)
        self.assertEqual(m.route_prefix, None)

class DummyRequest:
    subpath = ()
    matchdict = None
    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ
        self.params = {}
        self.cookies = {}
    def copy(self):
        return self
    def get_response(self, app):
        return app

class DummyContext:
    pass

class DummyPackage:
    def __init__(self, name):
        self.__name__ = name

class DummyOverrides:
    def __init__(self, package):
        self.package = package
        self.inserted = []

    def insert(self, path, package, prefix):
        self.inserted.append((path, package, prefix))

class DummyUnderOverride:
    def __call__(self, package, path, override_package, override_prefix,
                 _info=u''):
        self.package = package
        self.path = path
        self.override_package = override_package
        self.override_prefix = override_prefix

class DummyResponse:
    status = '200 OK'
    headerlist = ()
    app_iter = ()
    body = ''

from zope.interface import implements
from pyramid.interfaces import IMultiView
class DummyMultiView:
    implements(IMultiView)
    def __init__(self):
        self.views = []
        self.name = 'name'
    def add(self, view, order, accept=None, phash=None):
        self.views.append((view, accept, phash))
    def __call__(self, context, request):
        return 'OK1'
    def __permitted__(self, context, request):
        """ """

class DummyThreadLocalManager(object):
    pushed = None
    popped = False
    def push(self, d):
        self.pushed = d
    def pop(self):
        self.popped = True

class DummyEvent:
    implements(IDummy)

class DummyStaticURLInfo:
    def __init__(self):
        self.added = []

    def add(self, name, spec, **kw):
        self.added.append((name, spec, kw))

class DummyRegistry(object):
    def __init__(self, adaptation=None):
        self.utilities = []
        self.adapters = []
        self.adaptation = adaptation
    def subscribers(self, events, name):
        self.events = events
        return events
    def registerUtility(self, *arg, **kw):
        self.utilities.append((arg, kw))
    def registerAdapter(self, *arg, **kw):
        self.adapters.append((arg, kw))
    def queryAdapter(self, *arg, **kw):
        return self.adaptation

from pyramid.interfaces import IResponse
class DummyResponse(object):
    implements(IResponse)
    
class DummyAccept(object):
    def __init__(self, *matches):
        self.matches = list(matches)

    def best_match(self, offered):
        if self.matches:
            for match in self.matches:
                if match in offered:
                    self.matches.remove(match)
                    return match
    def __contains__(self, val):
        return val in self.matches

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

from zope.interface import Interface
class IOther(Interface):
    pass

