import os
import pkg_resources

from zope.component import queryUtility
from zope.component import getSiteManager

from zope.interface import classProvides
from zope.interface import implements

from chameleon.core.template import TemplateFile
from chameleon.zpt.language import Parser

from repoze.bfg.interfaces import ISettings
from repoze.bfg.interfaces import ITemplateRenderer
from repoze.bfg.interfaces import ITemplateRendererFactory
from repoze.bfg.path import caller_package
from repoze.bfg.settings import get_settings

class TextTemplateFile(TemplateFile):
    default_parser = Parser()
    
    def __init__(self, filename, parser=None, format=None, doctype=None,
                 **kwargs):
        if parser is None:
            parser = self.default_parser
        super(TextTemplateFile, self).__init__(filename, parser, format,
                                               doctype, **kwargs)

class TextTemplateRenderer(object):
    classProvides(ITemplateRendererFactory)
    implements(ITemplateRenderer)

    def __init__(self, path, auto_reload=False):
        self.template = TextTemplateFile(path, format='text',
                                         auto_reload=auto_reload)

    def implementation(self):
        return self.template
    
    def __call__(self, **kw):
        return self.template(**kw)

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
        # 'path' is a relative filename or a package:relpath spec
        if ':' in path:
            # it's a package:relpath spec
            spec = path.split(':', 1)
            utility_name = path
        else:
            # it's a relpath only
            package = caller_package(level=level)
            spec = (package.__name__, path) 
            utility_name = '%s:%s' % spec # utility name must be a string
        renderer = queryUtility(ITemplateRenderer, name=utility_name)
        if renderer is None:
            # service unit tests here by trying the relative path
            # string as the utility name directly
            renderer = queryUtility(ITemplateRenderer, name=path)
        if renderer is None:
            if not pkg_resources.resource_exists(*spec):
                raise ValueError('Missing template resource: %s' % utility_name)
            abspath = pkg_resources.resource_filename(*spec)
            renderer = factory(abspath, **kw)
            settings = get_settings()
            if (not settings) or (not settings.get('reload_resources')):
                # cache the template
                sm = getSiteManager()
                sm.registerUtility(renderer, ITemplateRenderer,
                                   name=utility_name)
        
    return renderer

def renderer_from_path(path, level=4, **kw):
    extension = os.path.splitext(path)[1]
    factory = queryUtility(ITemplateRendererFactory, name=extension,
                           default=TextTemplateRenderer)
    return renderer_from_cache(path, factory, level, **kw)

def _auto_reload():
    settings = queryUtility(ISettings)
    auto_reload = settings and settings['reload_templates']
    return auto_reload

