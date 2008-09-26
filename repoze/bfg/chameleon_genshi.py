import os

from webob import Response

from zope.component import queryUtility
from zope.component.interfaces import ComponentLookupError
from zope.component import getSiteManager

from zope.interface import classProvides
from zope.interface import implements

from repoze.bfg.path import caller_path
from repoze.bfg.interfaces import ITemplateFactory
from repoze.bfg.interfaces import ITemplate
from repoze.bfg.interfaces import ISettings

from chameleon.genshi.template import GenshiTemplateFile

class GenshiTemplateFactory(object):
    classProvides(ITemplateFactory)
    implements(ITemplate)

    def __init__(self, path, auto_reload=False):
        try:
            self.template = GenshiTemplateFile(path, auto_reload=auto_reload)
        except ImportError, why:
            why = str(why)
            if 'z3c.pt' in why:
                # unpickling error due to move from z3c.pt -> chameleon
                cachefile = '%s.cache' % path
                if os.path.isfile(cachefile):
                    os.remove(cachefile)
                self.template = GenshiTemplateFile(path,
                                                   auto_reload=auto_reload)
            else:
                raise

    def __call__(self, **kw):
        result = self.template.render(**kw)
        return result

def _get_template(path, **kw):
    # XXX use pkg_resources
    template = queryUtility(ITemplate, path)

    if template is None:
        if not os.path.exists(path):
            raise ValueError('Missing template file: %s' % path)
        settings = queryUtility(ISettings)
        auto_reload = settings and settings.reload_templates
        template = GenshiTemplateFactory(path, auto_reload)
        try:
            sm = getSiteManager()
        except ComponentLookupError:
            pass
        else:
            sm.registerUtility(template, ITemplate, name=path)
        
    return template

def get_template(path):
    """ Return a ``chameleon.genshi`` template object at the
    package-relative path (may also be absolute)"""
    path = caller_path(path)
    return _get_template(path).template

def render_template(path, **kw):
    """ Render a ``chameleon.genshi`` template at the package-relative
    path (may also be absolute) using the kwargs in ``*kw`` as
    top-level names and return a string."""
    path = caller_path(path)
    template = get_template(path)
    return template(**kw)

def render_template_to_response(path, **kw):
    """ Render a ``chameleon.genshi`` template at the package-relative
    path (may also be absolute) using the kwargs in ``*kw`` as
    top-level names and return a Response object."""
    path = caller_path(path)
    result = render_template(path, **kw)
    return Response(result)

