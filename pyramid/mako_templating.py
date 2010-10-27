import os
import posixpath
import re

from zope.interface import implements
from zope.interface import Interface

from pyramid.interfaces import ITemplateRenderer
from pyramid.exceptions import ConfigurationError
from pyramid.threadlocal import get_current_registry
from pyramid.settings import get_settings
from pyramid.resource import resolve_resource_spec
from pyramid.resource import abspath_from_resource_spec

class IMakoLookup(Interface):
    pass

def renderer_factory(path):
    from mako.lookup import TemplateLookup
    from mako import exceptions, util
    class PkgResourceTemplateLookup(TemplateLookup):
        def adjust_uri(self, uri, relativeto):
            # Don't adjust pkg resource spec names
            if ':' in uri:
                return uri
            return TemplateLookup.adjust_uri(self, uri, relativeto)
        
        def get_template(self, uri):
            if ':' not in uri:
                return TemplateLookup.get_template(self, uri)
            try:
                if self.filesystem_checks:
                    return self._check(uri, self._collection[uri])
                else:
                    return self._collection[uri]
            except KeyError:
                pname, path = resolve_resource_spec(uri)
                srcfile = abspath_from_resource_spec(path, pname)
                if os.path.isfile(srcfile):
                    return self._load(srcfile, uri)
                
                u = re.sub(r'^\/+', '', path)
                for dir in self.directories:
                    srcfile = posixpath.normpath(posixpath.join(dir, u))
                    if os.path.isfile(srcfile):
                        return self._load(srcfile, uri)
                else:
                    raise exceptions.TopLevelLookupException(
                                        "Cant locate template for uri %r" % uri)
    
    registry = get_current_registry()
    lookup = registry.queryUtility(IMakoLookup)
    if lookup is None:
        settings = get_settings() or {}
        reload_templates = settings.get('reload_templates', False)
        directories = settings.get('mako.directories')
        module_directory = settings.get('mako.module_directory')
        input_encoding = settings.get('mako.input_encoding', 'utf-8')
        if directories is None:
            raise ConfigurationError(
                'Mako template used without a lookup path')
        directories = directories.splitlines()
        directories = [ abspath_from_resource_spec(d) for d in directories ]
        lookup = PkgResourceTemplateLookup(directories=directories,
                                           module_directory=module_directory,
                                           input_encoding=input_encoding,
                                           filesystem_checks=reload_templates)
        registry.registerUtility(lookup, IMakoLookup)
    return MakoLookupTemplateRenderer(path, lookup)

class MakoLookupTemplateRenderer(object):
    implements(ITemplateRenderer)
    def __init__(self, path, lookup):
        self.path = path
        self.lookup = lookup
 
    def implementation(self):
        return self.template

    @property
    def template(self):
        return self.lookup.get_template(self.path)
   
    def __call__(self, value, system):
        context = system.pop('context', None)
        if context is not None:
            system['_context'] = context
        def_name = None
        if isinstance(value, tuple):
            def_name, value = value
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        template = self.template
        if def_name is not None:
            template = template.get_def(def_name)
        result = template.render_unicode(**system)
        return result

