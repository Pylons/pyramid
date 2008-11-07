from zope.component import queryUtility
from repoze.bfg.interfaces import ITemplateRenderer
from repoze.bfg.interfaces import ITestingTemplateRenderer
from zope.component.interfaces import ComponentLookupError
from zope.component import getSiteManager
from repoze.bfg.path import caller_path
import os

def renderer_from_cache(path, factory, level=3, **kw):
    # XXX use pkg_resources
    abspath = caller_path(path, level=level)
    renderer = queryUtility(ITemplateRenderer, abspath)

    if renderer is None:
        # service unit tests by trying the relative path
        renderer = queryUtility(ITestingTemplateRenderer, path)

    if renderer is None:
        if not os.path.exists(abspath):
            raise ValueError('Missing template file: %s' % abspath)
        renderer = factory(abspath, **kw)
        try:
            sm = getSiteManager()
        except ComponentLookupError:
            pass
        else:
            sm.registerUtility(renderer, ITemplateRenderer, name=abspath)
        
    return renderer

