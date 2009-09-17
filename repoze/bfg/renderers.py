import os
import pkg_resources

from zope.component import queryUtility
from zope.component import getSiteManager

from repoze.bfg.path import caller_package
from repoze.bfg.settings import get_settings

from repoze.bfg.interfaces import IRendererFactory
from repoze.bfg.interfaces import ITemplateRenderer

try:
    import json
except ImportError:
    import simplejson as json

# concrete renderer factory implementations

def json_renderer_factory(name):
    def _render(value):
        return json.dumps(value)
    return _render

def string_renderer_factory(name):
    def _render(value):
        if not isinstance(value, basestring):
            value = str(value)
        return value
    return _render

# utility functions

def template_renderer_factory(path, impl, level=3):
    if os.path.isabs(path):
        # 'path' is an absolute filename (not common and largely only
        # for backwards compatibility)
        if not os.path.exists(path):
            raise ValueError('Missing template file: %s' % path)
        renderer = queryUtility(ITemplateRenderer, name=path)
        if renderer is None:
            renderer = impl(path)
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
            renderer = impl(abspath)
            if not _reload_resources():
                # cache the template
                sm = getSiteManager()
                sm.registerUtility(renderer, ITemplateRenderer,
                                   name=utility_name)
        
    return renderer

def renderer_from_name(path, level=4):
    name = os.path.splitext(path)[1]
    if not name:
        name = path
    factory = queryUtility(IRendererFactory, name=name)
    if factory is None:
        raise ValueError('No renderer for renderer name %r' % name)
    return factory(path)

def _reload_resources():
    settings = get_settings()
    return settings and settings.get('reload_resources')



