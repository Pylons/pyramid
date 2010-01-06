import os
import pkg_resources

from repoze.bfg.interfaces import ITemplateRenderer

from repoze.bfg.compat import json
from repoze.bfg.path import caller_package
from repoze.bfg.settings import get_settings
from repoze.bfg.threadlocal import get_current_registry

# concrete renderer factory implementations

def json_renderer_factory(name):
    def _render(value, system):
        request = system.get('request')
        if request is not None:
            if not hasattr(request, 'response_content_type'):
                request.response_content_type = 'application/json'
        return json.dumps(value)
    return _render

def string_renderer_factory(name):
    def _render(value, system):
        if not isinstance(value, basestring):
            value = str(value)
        request = system.get('request')
        if request is not None:
            if not hasattr(request, 'response_content_type'):
                request.response_content_type = 'text/plain'
        return value
    return _render

# utility functions

def template_renderer_factory(spec, impl):
    reg = get_current_registry()
    if os.path.isabs(spec):
        # 'spec' is an absolute filename
        if not os.path.exists(spec):
            raise ValueError('Missing template file: %s' % spec)
        renderer = reg.queryUtility(ITemplateRenderer, name=spec)
        if renderer is None:
            renderer = impl(spec)
            reg.registerUtility(renderer, ITemplateRenderer, name=spec)
    else:
        # spec is a package:relpath resource spec
        renderer = reg.queryUtility(ITemplateRenderer, name=spec)
        if renderer is None:
            try:
                package_name, filename = spec.split(':', 1)
            except ValueError: # pragma: no cover
                # unit test or somehow we were passed a relative pathname;
                # this should die
                package_name = caller_package(4).__name__
                filename = spec
            abspath = pkg_resources.resource_filename(package_name, filename)
            if not pkg_resources.resource_exists(package_name, filename):
                raise ValueError(
                    'Missing template resource: %s (%s)' % (spec, abspath))
            renderer = impl(abspath)
            if not _reload_resources():
                # cache the template
                reg.registerUtility(renderer, ITemplateRenderer, name=spec)
        
    return renderer

def renderer_from_name(path):
    from repoze.bfg.configuration import Configurator
    reg = get_current_registry()
    config = Configurator(reg)
    return config._renderer_from_name(path)

def _reload_resources():
    settings = get_settings()
    return settings and settings.get('reload_resources')
