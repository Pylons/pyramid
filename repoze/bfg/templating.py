import pkg_resources
from zope.component import queryUtility
from repoze.bfg.interfaces import ITemplateRenderer
from zope.component import getSiteManager
from repoze.bfg.path import caller_package
import os

def renderer_from_cache(path, factory, level=3, **kw):
    if os.path.isabs(path):
        # 'path' is an absolute filename (not common and largely only
        # for backwards compatibility)
        if not os.path.exists(path):
            raise ValueError('Missing template file: %s' % path)
        renderer = queryUtility(ITemplateRenderer, name=path)
        if renderer is None:
            renderer = factory(path, **kw)
            sm = getSiteManager()
            sm.registerUtility(renderer, ITemplateRenderer, name=path)

    else:
        # 'path' is a relative filename
        package = caller_package(level=level)
        spec = (package.__name__, path) 
        utility_name = '%s\t%s' % spec # utility name must be a string :-(
        renderer = queryUtility(ITemplateRenderer, name=utility_name)
        if renderer is None:
            # service unit tests here by trying the relative path
            # string as the utility name directly
            renderer = queryUtility(ITemplateRenderer, name=path)
        if renderer is None:
            if not pkg_resources.resource_exists(*spec):
                raise ValueError('Missing template resource: %s:%s' % spec)
            abspath = pkg_resources.resource_filename(*spec)
            renderer = factory(abspath, **kw)
            sm = getSiteManager()
            sm.registerUtility(renderer, ITemplateRenderer, name=utility_name)
        
    return renderer

