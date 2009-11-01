import os
import pkg_resources

from zope.component import getSiteManager
from zope.component import queryUtility

from repoze.bfg.interfaces import IRendererFactory
from repoze.bfg.interfaces import ITemplateRenderer

from repoze.bfg.compat import json
from repoze.bfg.path import caller_package
from repoze.bfg.resource import resource_spec
from repoze.bfg.settings import get_settings

# concrete renderer factory implementations

def json_renderer_factory(name):
    def _render(value, system):
        return json.dumps(value)
    return _render

def string_renderer_factory(name):
    def _render(value, system):
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
        spec = resource_spec(path, caller_package(level=level).__name__)
        renderer = queryUtility(ITemplateRenderer, name=spec)
        if renderer is None:
            # service unit tests by trying the relative path string as
            # the utility name directly
            renderer = queryUtility(ITemplateRenderer, name=path)
        if renderer is None:
            pkg, path = spec.split(':', 1)
            if not pkg_resources.resource_exists(pkg, path):
                raise ValueError('Missing template resource: %s' % spec)
            abspath = pkg_resources.resource_filename(pkg, path)
            renderer = impl(abspath)
            if not _reload_resources():
                # cache the template
                sm = getSiteManager()
                sm.registerUtility(renderer, ITemplateRenderer,
                                   name=spec)
        
    return renderer

def renderer_from_name(path):
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



