import os
import posixpath
import sys
import threading
import warnings

from zope.interface import (
    implementer,
    Interface,
    )

from pyramid.asset import (
    resolve_asset_spec,
    abspath_from_asset_spec,
    )

from pyramid.compat import (
    is_nonstr_iter,
    reraise,
    )

from pyramid.interfaces import ITemplateRenderer
from pyramid.settings import asbool
from pyramid.util import DottedNameResolver

def _no_mako(*arg, **kw): # pragma: no cover
    raise NotImplementedError(
        "'mako' package is not importable (maybe downgrade MarkupSafe to "
        "0.16 or below if you're using Python 3.2)"
        )

try:
    from mako.lookup import TemplateLookup
except (ImportError, SyntaxError, AttributeError): #pragma NO COVER
    class TemplateLookup(object):
        def __init__(self, **kw):
            for name in ('adjust_uri', 'get_template', 'filename_to_uri',
                         'put_string', 'put_template'):
                setattr(self, name, _no_mako)
            self.filesystem_checks = False

try:
    from mako.exceptions import TopLevelLookupException
except (ImportError, SyntaxError, AttributeError): #pragma NO COVER
    class TopLevelLookupException(Exception):
        pass

try:
    from mako.exceptions import text_error_template
except (ImportError, SyntaxError, AttributeError): #pragma NO COVER
    def text_error_template(lookup=None):
        _no_mako()


class IMakoLookup(Interface):
    pass

class PkgResourceTemplateLookup(TemplateLookup):
    """TemplateLookup subclass that handles asset specification URIs"""
    def adjust_uri(self, uri, relativeto):
        """Called from within a Mako template, avoids adjusting the
        uri if it looks like an asset specification"""
        # Don't adjust asset spec names
        isabs = os.path.isabs(uri)
        if (not isabs) and (':' in uri):
            return uri
        if not(isabs) and ('$' in uri):
            return uri.replace('$', ':')
        if relativeto is not None:
            relativeto = relativeto.replace('$', ':')
            if not(':' in uri) and (':' in relativeto):
                if uri.startswith('/'):
                    return uri
                pkg, relto = relativeto.split(':')
                _uri = posixpath.join(posixpath.dirname(relto), uri)
                return '{0}:{1}'.format(pkg, _uri)
            if not(':' in uri) and not(':' in relativeto):
                return posixpath.join(posixpath.dirname(relativeto), uri)
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
            # Windows can't cope with colons in filenames, so we replace the
            # colon with a dollar sign in the filename mako uses to actually
            # store the generated python code in the mako module_directory or
            # in the temporary location of mako's modules
            adjusted = uri.replace(':', '$')
            try:
                if self.filesystem_checks:
                    return self._check(adjusted, self._collection[adjusted])
                else:
                    return self._collection[adjusted]
            except KeyError:
                pname, path = resolve_asset_spec(uri)
                srcfile = abspath_from_asset_spec(path, pname)
                if os.path.isfile(srcfile):
                    return self._load(srcfile, adjusted)
                raise TopLevelLookupException(
                    "Can not locate template for uri %r" % uri)
        return TemplateLookup.get_template(self, uri)

registry_lock = threading.Lock()

class MakoRendererFactoryHelper(object):
    def __init__(self, settings_prefix=None):
        self.settings_prefix = settings_prefix

    def __call__(self, info):
        defname = None
        asset, ext = info.name.rsplit('.', 1)
        if '#' in asset:
            asset, defname = asset.rsplit('#', 1)

        path = '%s.%s' % (asset, ext)
        registry = info.registry
        settings = info.settings
        settings_prefix = self.settings_prefix

        if settings_prefix is None:
            settings_prefix = info.type +'.'

        lookup = registry.queryUtility(IMakoLookup, name=settings_prefix)

        def sget(name, default=None):
            return settings.get(settings_prefix + name, default)

        if lookup is None:
            reload_templates = settings.get('pyramid.reload_templates', None)
            if reload_templates is None:
                reload_templates = settings.get('reload_templates', False)
            reload_templates = asbool(reload_templates)
            directories = sget('directories', [])
            module_directory = sget('module_directory', None)
            input_encoding = sget('input_encoding', 'utf-8')
            error_handler = sget('error_handler', None)
            default_filters = sget('default_filters', 'h')
            imports = sget('imports', None)
            strict_undefined = asbool(sget('strict_undefined', False))
            preprocessor = sget('preprocessor', None)
            if not is_nonstr_iter(directories):
                directories = list(filter(None, directories.splitlines()))
            directories = [ abspath_from_asset_spec(d) for d in directories ]
            if module_directory is not None:
                module_directory = abspath_from_asset_spec(module_directory)
            if error_handler is not None:
                dotted = DottedNameResolver(info.package)
                error_handler = dotted.maybe_resolve(error_handler)
            if default_filters is not None:
                if not is_nonstr_iter(default_filters):
                    default_filters = list(filter(
                        None, default_filters.splitlines()))
            if imports is not None:
                if not is_nonstr_iter(imports):
                    imports = list(filter(None, imports.splitlines()))
            if preprocessor is not None:
                dotted = DottedNameResolver(info.package)
                preprocessor = dotted.maybe_resolve(preprocessor)


            lookup = PkgResourceTemplateLookup(
                directories=directories,
                module_directory=module_directory,
                input_encoding=input_encoding,
                error_handler=error_handler,
                default_filters=default_filters,
                imports=imports,
                filesystem_checks=reload_templates,
                strict_undefined=strict_undefined,
                preprocessor=preprocessor
                )

            with registry_lock:
                registry.registerUtility(lookup, IMakoLookup,
                                         name=settings_prefix)

        return MakoLookupTemplateRenderer(path, defname, lookup)

renderer_factory = MakoRendererFactoryHelper('mako.')

class MakoRenderingException(Exception):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text

    __str__ = __repr__

@implementer(ITemplateRenderer)
class MakoLookupTemplateRenderer(object):
    """ Render a :term:`Mako` template using the template
    implied by the ``path`` argument.The ``path`` argument may be a
    package-relative path, an absolute path, or a :term:`asset
    specification`. If a defname is defined, in the form of
    package:path/to/template#defname.mako, a function named ``defname``
    inside the template will then be rendered.
    """
    def __init__(self, path, defname, lookup):
        self.path = path
        self.defname = defname
        self.lookup = lookup

    def implementation(self):
        return self.lookup.get_template(self.path)

    def __call__(self, value, system):
        context = system.pop('context', None)
        if context is not None:
            system['_context'] = context
        # tuple returned to be deprecated
        if isinstance(value, tuple):
            warnings.warn(
                'Using a tuple in the form (\'defname\', {}) to render a '
                'Mako partial will be deprecated in the future. Use a '
                'Mako template renderer as documented in the "Using A '
                'Mako def name Within a Renderer Name" chapter of the '
                'Pyramid narrative documentation instead',
                DeprecationWarning,
                3)
            self.defname, value = value
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        template = self.implementation()
        if self.defname is not None:
            template = template.get_def(self.defname)
        try:
            result = template.render_unicode(**system)
        except:
            try:
                exc_info = sys.exc_info()
                errtext = text_error_template().render(
                    error=exc_info[1],
                    traceback=exc_info[2]
                    )
                reraise(MakoRenderingException(errtext), None, exc_info[2])
            finally:
                del exc_info

        return result
