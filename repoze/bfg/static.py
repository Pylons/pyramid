import os
import pkg_resources
from urlparse import urljoin
from urlparse import urlparse

from paste import httpexceptions
from paste import request
from paste.httpheaders import ETAG
from paste.urlparser import StaticURLParser

from zope.interface import implements

from repoze.bfg.interfaces import IStaticURLInfo
from repoze.bfg.path import caller_package
from repoze.bfg.resource import resolve_resource_spec
from repoze.bfg.url import route_url

class PackageURLParser(StaticURLParser):
    """ This probably won't work with zipimported resources """
    def __init__(self, package_name, resource_name, root_resource=None,
                 cache_max_age=None):
        self.package_name = package_name
        self.resource_name = os.path.normpath(resource_name)
        if root_resource is None:
            root_resource = self.resource_name
        self.root_resource = root_resource
        self.cache_max_age = cache_max_age

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if not path_info:
            return self.add_slash(environ, start_response)
        if path_info == '/':
            # @@: This should obviously be configurable
            filename = 'index.html'
        else:
            filename = request.path_info_pop(environ)
        resource = os.path.normcase(os.path.normpath(
                    self.resource_name + '/' + filename))
        if ( (self.root_resource is not None) and
            (not resource.startswith(self.root_resource)) ):
            # Out of bounds
            return self.not_found(environ, start_response)
        if not pkg_resources.resource_exists(self.package_name, resource):
            return self.not_found(environ, start_response)
        if pkg_resources.resource_isdir(self.package_name, resource):
            # @@: Cache?
            child_root = (self.root_resource is not None and
                          self.root_resource or self.resource_name)
            return self.__class__(
                self.package_name, resource, root_resource=child_root,
                cache_max_age=self.cache_max_age)(environ, start_response)
        if (environ.get('PATH_INFO')
            and environ.get('PATH_INFO') != '/'): # pragma: no cover
            return self.error_extra_path(environ, start_response) 
        full = pkg_resources.resource_filename(self.package_name, resource)
        if_none_match = environ.get('HTTP_IF_NONE_MATCH')
        if if_none_match:
            mytime = os.stat(full).st_mtime
            if str(mytime) == if_none_match:
                headers = []
                ETAG.update(headers, mytime)
                start_response('304 Not Modified', headers)
                return [''] # empty body

        fa = self.make_app(full)
        if self.cache_max_age:
            fa.cache_control(max_age=self.cache_max_age)
        return fa(environ, start_response)

    def not_found(self, environ, start_response, debug_message=None):
        comment=('SCRIPT_NAME=%r; PATH_INFO=%r; looking in package %s; '
                 'subdir %s ;debug: %s' % (environ.get('SCRIPT_NAME'),
                                           environ.get('PATH_INFO'),
                                           self.package_name,
                                           self.resource_name,
                                           debug_message or '(none)'))
        exc = httpexceptions.HTTPNotFound(
            'The resource at %s could not be found'
            % request.construct_url(environ),
            comment=comment)
        return exc.wsgi_application(environ, start_response)

    def __repr__(self):
        return '<%s %s:%s at %s>' % (self.__class__.__name__, self.package_name,
                                     self.root_resource, id(self))

class StaticURLInfo(object):
    implements(IStaticURLInfo)

    route_url = staticmethod(route_url) # for testing only

    def __init__(self, config):
        self.config = config
        self.registrations = []

    def generate(self, path, request, **kw):
        for (name, spec, is_url) in self.registrations:
            if path.startswith(spec):
                subpath = path[len(spec):]
                if is_url:
                    return urljoin(name, subpath[1:])
                else:
                    kw['subpath'] = subpath
                    return self.route_url(name, request, **kw)

        raise ValueError('No static URL definition matching %s' % path)

    def add(self, name, spec, **extra):
        names = [ t[0] for t in self.registrations ]
        if name in names:
            idx = names.index(name)
            self.registrations.pop(idx)

        if urlparse(name)[0]:
            # it's a URL
            if not name.endswith('/'):
                # make sure it ends with a slash
                name = name + '/'
            self.registrations.append((name, spec, True))
        else:
            # it's a view name
            _info = extra.pop('_info', None)
            cache_max_age = extra.pop('cache_max_age', None)
            view = static_view(spec, cache_max_age=cache_max_age)
            # register a route using this view
            self.config.add_route(
                name,
                "%s*subpath" % name,
                view=view,
                view_for=self.__class__,
                factory=lambda *x: self,
                _info=_info
                )
            self.registrations.append((name, spec, False))

class static_view(object):
    """ An instance of this class is a callable which can act as a
    :mod:`repoze.bfg` :term:`view callable`; this view will serve
    static files from a directory on disk based on the ``root_dir``
    you provide to its constructor.

    The directory may contain subdirectories (recursively); the static
    view implementation will descend into these directories as
    necessary based on the components of the URL in order to resolve a
    path into a response.

    You may pass an absolute or relative filesystem path or a
    :term:`resource specification` representing the directory
    containing static files as the ``root_dir`` argument to this
    class' constructor.

    If the ``root_dir`` path is relative, and the ``package_name``
    argument is ``None``, ``root_dir`` will be considered relative to
    the directory in which the Python file which *calls* ``static``
    resides.  If the ``package_name`` name argument is provided, and a
    relative ``root_dir`` is provided, the ``root_dir`` will be
    considered relative to the Python :term:`package` specified by
    ``package_name`` (a dotted path to a Python package).

    ``cache_max_age`` influences the ``Expires`` and ``Max-Age``
    response headers returned by the view (default is 3600 seconds or
    five minutes).

    .. note:: If the ``root_dir`` is relative to a :term:`package`, or
         is a :term:`resource specification` the :mod:`repoze.bfg`
         ``resource`` ZCML directive or
         :class:`repoze.bfg.configuration.Configurator` method can be
         used to override resources within the named ``root_dir``
         package-relative directory.  However, if the ``root_dir`` is
         absolute, the ``resource`` directive will not be able to
         override the resources it contains.  """
    
    def __init__(self, root_dir, cache_max_age=3600, package_name=None):
        # package_name is for bw compat; it is preferred to pass in a
        # package-relative path as root_dir
        # (e.g. ``anotherpackage:foo/static``).
        caller_package_name = caller_package().__name__
        package_name = package_name or caller_package_name
        package_name, root_dir = resolve_resource_spec(root_dir, package_name)
        if package_name is None:
            app = StaticURLParser(root_dir, cache_max_age=cache_max_age)
        else:
            app = PackageURLParser(
                package_name, root_dir, cache_max_age=cache_max_age)
        self.app = app

    def __call__(self, context, request):
        subpath = '/'.join(request.subpath)
        request_copy = request.copy()
        # Fix up PATH_INFO to get rid of everything but the "subpath"
        # (the actual path to the file relative to the root dir).
        request_copy.environ['PATH_INFO'] = '/' + subpath
        # Zero out SCRIPT_NAME for good measure.
        request_copy.environ['SCRIPT_NAME'] = ''
        return request_copy.get_response(self.app)

