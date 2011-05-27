import os
import threading

from zope.interface import implements
from zope.interface import Interface

from pyramid.asset import resolve_asset_spec
from pyramid.asset import abspath_from_asset_spec
from pyramid.exceptions import ConfigurationError
from pyramid.interfaces import ITemplateRenderer
from pyramid.settings import asbool
from pyramid.util import DottedNameResolver

from mako.lookup import TemplateLookup
from mako import exceptions

class IMakoLookup(Interface):
    pass

class PkgResourceTemplateLookup(TemplateLookup):
    """TemplateLookup subclass that handles asset specification URIs"""
    def adjust_uri(self, uri, relativeto):
        """Called from within a Mako template, avoids adjusting the
        uri if it looks like an asset specification"""
        # Don't adjust asset spec names
        if ':' in uri:
            return uri
        return TemplateLookup.adjust_uri(self, uri, relativeto)

    def get_template(self, uri):
        """Fetch a template from the cache, or check the filesystem
        for it
        
        In addition to the basic filesystem lookup, this subclass will
        use pkg_resource to load a file using the asset
        specification syntax.
        
        """
        isabs = os.path.isabs(uri)
        if (not isabs) and (':' in uri):
            try:
                if self.filesystem_checks:
                    return self._check(uri, self._collection[uri])
                else:
                    return self._collection[uri]
            except KeyError:
                pname, path = resolve_asset_spec(uri)
                srcfile = abspath_from_asset_spec(path, pname)
                if os.path.isfile(srcfile):
                    return self._load(srcfile, uri)
                raise exceptions.TopLevelLookupException(
                    "Cant locate template for uri %r" % uri)
        return TemplateLookup.get_template(self, uri)


registry_lock = threading.Lock() 

def renderer_factory(info):
    path = info.name
    registry = info.registry
    settings = info.settings
    lookup = registry.queryUtility(IMakoLookup)
    if lookup is None:
        reload_templates = settings.get('reload_templates', False)
        directories = settings.get('mako.directories', None)
        module_directory = settings.get('mako.module_directory', None)
        input_encoding = settings.get('mako.input_encoding', 'utf-8')
        error_handler = settings.get('mako.error_handler', None)
        default_filters = settings.get('mako.default_filters', 'h')
        imports = settings.get('mako.imports', None)
        strict_undefined = settings.get('mako.strict_undefined', 'false')
        if directories is None:
            raise ConfigurationError(
                'Mako template used without a ``mako.directories`` setting')
        if not hasattr(directories, '__iter__'):
            directories = filter(None, directories.splitlines())
        directories = [ abspath_from_asset_spec(d) for d in directories ]
        if module_directory is not None:
            module_directory = abspath_from_asset_spec(module_directory)
        if error_handler is not None:
            dotted = DottedNameResolver(info.package)
            error_handler = dotted.maybe_resolve(error_handler)
        if default_filters is not None:
            if not hasattr(default_filters, '__iter__'):
                default_filters = filter(None, default_filters.splitlines())
        if imports is not None:
            if not hasattr(imports, '__iter__'):
                imports = filter(None, imports.splitlines())
        strict_undefined = asbool(strict_undefined)
        
        lookup = PkgResourceTemplateLookup(directories=directories,
                                           module_directory=module_directory,
                                           input_encoding=input_encoding,
                                           error_handler=error_handler,
                                           default_filters=default_filters,
                                           imports=imports,
                                           filesystem_checks=reload_templates,
                                           strict_undefined=strict_undefined)
        registry_lock.acquire()
        try:
            registry.registerUtility(lookup, IMakoLookup)
        finally:
            registry_lock.release()
            
    return MakoLookupTemplateRenderer(path, lookup)


class MakoLookupTemplateRenderer(object):
    implements(ITemplateRenderer)
    def __init__(self, path, lookup):
        self.path = path
        self.lookup = lookup
 
    def implementation(self):
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
        template = self.implementation()
        if def_name is not None:
            template = template.get_def(def_name)
        result = template.render_unicode(**system)
        return result
