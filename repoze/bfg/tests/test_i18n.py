import unittest

class Test_get_translator(unittest.TestCase):
    def _callFUT(self, request):
        from repoze.bfg.i18n import get_translator
        return get_translator(request)

    def test_no_ITranslatorFactory(self):
        request = DummyRequest()
        request.registry = DummyRegistry()
        translator = self._callFUT(request)
        self.assertEqual(translator, None)

    def test_no_registry_on_request(self):
        request = DummyRequest()
        translator = self._callFUT(request)
        self.assertEqual(translator, None)

    def test_with_ITranslatorFactory_from_registry(self):
        request = DummyRequest()
        tfactory = DummyTranslatorFactory()
        request.registry = DummyRegistry(tfactory)
        translator = self._callFUT(request)
        self.assertEqual(translator.request, request)

    def test_with_ITranslatorFactory_from_request_cache(self):
        request = DummyRequest()
        request.registry = DummyRegistry()
        request._bfg_translator = 'abc'
        translator = self._callFUT(request)
        self.assertEqual(translator, 'abc')

    def test_with_ITranslatorFactory_from_request_neg_cache(self):
        request = DummyRequest()
        request.registry = DummyRegistry()
        request._bfg_translator = False
        translator = self._callFUT(request)
        self.assertEqual(translator, None)

class TestInterpolationOnlyTranslator(unittest.TestCase):
    def _makeOne(self, request):
        from repoze.bfg.i18n import InterpolationOnlyTranslator
        return InterpolationOnlyTranslator(request)

    def test_it(self):
        message = DummyMessage('text ${a}', mapping={'a':'1'})
        translator = self._makeOne(None)
        result = translator(message)
        self.assertEqual(result, u'text 1')

class TestChameleonTranslate(unittest.TestCase):
    def setUp(self):
        request = DummyRequest()
        from repoze.bfg.configuration import Configurator
        self.config = Configurator()
        self.config.begin(request=request)
        self.request = request

    def tearDown(self):
        self.config.end()
        
    def _makeOne(self, factory):
        from repoze.bfg.i18n import ChameleonTranslate
        return ChameleonTranslate(factory)

    def test_text_None(self):
        trans = self._makeOne(None)
        result = trans(None)
        self.assertEqual(result, None)

    def test_no_current_request(self):
        self.config.manager.pop()
        trans = self._makeOne(None)
        result = trans('text')
        self.assertEqual(result, 'text')

    def test_with_current_request_no_translator(self):
        trans = self._makeOne(None)
        result = trans('text')
        self.assertEqual(result, 'text')
        self.assertEqual(self.request.chameleon_target_language, None)

    def test_with_current_request_and_translator(self):
        from repoze.bfg.interfaces import ITranslatorFactory
        translator = DummyTranslator()
        factory = DummyTranslatorFactory(translator)
        self.config.registry.registerUtility(factory, ITranslatorFactory)
        trans = self._makeOne(None)
        result = trans('text')
        self.assertEqual(result, 'text')
        self.assertEqual(self.request.chameleon_target_language, None)
        self.assertEqual(result.domain, None)
        self.assertEqual(result.default, 'text')
        self.assertEqual(result.mapping, {})

    def test_with_allargs(self):
        from repoze.bfg.interfaces import ITranslatorFactory
        translator = DummyTranslator()
        factory = DummyTranslatorFactory(translator)
        self.config.registry.registerUtility(factory, ITranslatorFactory)
        trans = self._makeOne(None)
        result = trans('text', domain='domain', mapping={'a':'1'},
                       context=None, target_language='lang',
                       default='default')
        self.assertEqual(self.request.chameleon_target_language, 'lang')
        self.assertEqual(result, 'text')
        self.assertEqual(result.domain, 'domain')
        self.assertEqual(result.default, 'default')
        self.assertEqual(result.mapping, {'a':'1'})

class Test_interpolate(unittest.TestCase):
    def _callFUT(self, text, mapping=None):
        from repoze.bfg.i18n import interpolate
        return interpolate(text, mapping)

    def test_substitution(self):
        mapping = {"name": "Zope", "version": 3}
        result = self._callFUT(u"This is $name version ${version}.", mapping)
        self.assertEqual(result, u'This is Zope version 3.')

    def test_subsitution_more_than_once(self):
        mapping = {"name": "Zope", "version": 3}
        result = self._callFUT(
            u"This is $name version ${version}. ${name} $version!",
            mapping)
        self.assertEqual(result, u'This is Zope version 3. Zope 3!')

    def test_double_dollar_escape(self):
        mapping = {"name": "Zope", "version": 3}
        result = self._callFUT('$$name', mapping)
        self.assertEqual(result, u'$$name')

    def test_missing_not_interpolated(self):
        mapping = {"name": "Zope", "version": 3}
        result = self._callFUT(
            u"This is $name $version. $unknown $$name $${version}.",
            mapping)
        self.assertEqual(result,
                         u'This is Zope 3. $unknown $$name $${version}.')

    def test_missing_mapping(self):
        result = self._callFUT(u"This is ${name}")
        self.assertEqual(result, u'This is ${name}')

class DummyMessage(unicode):
    def __new__(cls, text, msgid=None, domain=None, mapping=None):
        self = unicode.__new__(cls, text)
        if msgid is None:
            msgid = unicode(text)
        self.msgid = msgid
        self.domain = domain
        self.mapping = mapping or {}
        return self
    
class DummyRequest(object):
    pass

class DummyRegistry(object):
    def __init__(self, tfactory=None):
        self.tfactory = tfactory

    def queryUtility(self, iface):
        return self.tfactory

class DummyTranslator(object):
    def __call__(self, message):
        return message
                    
class DummyTranslatorFactory(object):
    def __init__(self, translator=None):
        self.translator = translator

    def __call__(self, request):
        self.request = request
        if self.translator is None:
            return self
        return self.translator
    
        
