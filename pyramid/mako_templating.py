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
        lookup = TemplateLookup(directories=directories,
                                module_directory=module_directory,
                                input_encoding=input_encoding,
                                filesystem_checks=reload_templates)
        registry.registerUtility(lookup, IMakoLookup)
    _, path = resolve_resource_spec(path)
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

