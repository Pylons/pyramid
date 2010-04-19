from zope.interface import implements
from zope.interface import classProvides

from repoze.bfg.interfaces import ITranslator
from repoze.bfg.interfaces import ITranslatorFactory
from repoze.bfg.threadlocal import get_current_registry
from repoze.bfg.threadlocal import get_current_request

def get_translator(request):
    try:
        reg = request.registry
    except AttributeError:
        reg = get_current_registry()

    if reg is None: # pragma: no cover
        return None # only in insane circumstances

    translator = getattr(request, '_bfg_translator', None)

    if translator is False:
        return None

    if translator is None:
        translator_factory = reg.queryUtility(ITranslatorFactory)
        if translator_factory is None:
            request_value = False
        else:
            translator = translator_factory(request)
            request_value = translator
        try:
            request._bfg_translator = request_value
        except AttributeError: # pragma: no cover
            pass # it's only a cache

    return translator

class InterpolationOnlyTranslator(object):
    classProvides(ITranslatorFactory)
    implements(ITranslator)
    def __init__(self, request):
        self.request = request

    def __call__(self, message):
        mapping = getattr(message, 'mapping', {}) #should be a TranslationString
        return message % mapping

class TranslationString(unicode):
    __slots__ = ('msgid', 'domain', 'mapping')
    def __new__(cls, text, msgid=None, domain=None, mapping=None):
        self = unicode.__new__(cls, text)
        if msgid is None:
            msgid = unicode(text)
        self.msgid = msgid
        self.domain = domain
        self.mapping = mapping or {}
        return self

    def __reduce__(self):
        return self.__class__, self.__getstate__()

    def __getstate__(self):
        return unicode(self), self.msgid, self.domain, self.mapping

def chameleon_translate(text, domain=None, mapping=None, context=None,
                        target_language=None, default=None):
    if text is None:
        return None
    translator = None
    request = get_current_request()
    if request is not None:
        request.chameleon_target_language = target_language
        translator = get_translator(request)
    if default is None:
        default = text
    if mapping is None:
        mapping = {}
    if translator is None:
        return unicode(default) % mapping
    if not isinstance(text, TranslationString):
        text = TranslationString(default, msgid=text, domain=domain,
                                 mapping=mapping)
    return translator(text)
        
    
    
    
    
