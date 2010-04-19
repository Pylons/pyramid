##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import re

from zope.interface import implements
from zope.interface import classProvides

from zope.i18nmessageid.message import Message

from repoze.bfg.interfaces import ITranslator
from repoze.bfg.interfaces import ITranslatorFactory
from repoze.bfg.interfaces import IChameleonTranslate

from repoze.bfg.threadlocal import get_current_registry
from repoze.bfg.threadlocal import get_current_request

TranslationString = Message

def get_translator(request, translator_factory=None):
    """ Return a :term:`translator` for the given request based on the
    :term:`translator factory` registered for the current application
    and the :term:`request` passed in as the request object.  If no
    translator factory was sent to the
    :class:`repoze.bfg.configuration.Configurator` constructor at
    application startup, this function will return ``None``.

    Note that the translation factory will only be called once per
    request instance.
    """
    
    translator = getattr(request, '_bfg_translator', None)

    if translator is False:
        return None

    if translator is None:
        if translator_factory is None:
            try:
                reg = request.registry
            except AttributeError:
                reg = get_current_registry()
            if reg is not None: # pragma: no cover
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
        mapping = getattr(message, 'mapping', None)
        return interpolate(message, mapping)

class ChameleonTranslate(object):
    implements(IChameleonTranslate)
    def __init__(self, translator_factory):
        self.translator_factory = translator_factory

    def __call__(self, text, domain=None, mapping=None, context=None,
                 target_language=None, default=None):
        if text is None:
            return None
        translator = None
        request = get_current_request()
        if request is not None:
            request.chameleon_target_language = target_language
            translator = get_translator(request, self.translator_factory)
        if default is None:
            default = text
        if mapping is None:
            mapping = {}
        if translator is None:
            return interpolate(unicode(default), mapping)
        if not hasattr(text, 'mapping'):
            text = TranslationString(text, domain=domain, default=default,
                                     mapping=mapping)
        return translator(text)
        
NAME_RE = r"[a-zA-Z][-a-zA-Z0-9_]*"

_interp_regex = re.compile(r'(?<!\$)(\$(?:(%(n)s)|{(%(n)s)}))'
    % ({'n': NAME_RE}))
    
def interpolate(text, mapping=None):
    def replace(match):
        whole, param1, param2 = match.groups()
        return unicode(mapping.get(param1 or param2, whole))

    if not text or not mapping:
        return text

    return _interp_regex.sub(replace, text)
