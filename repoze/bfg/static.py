import os
import pkg_resources

from paste import httpexceptions
from paste import request
from paste.httpheaders import ETAG
from paste.urlparser import StaticURLParser

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

class StaticRootFactory:
    def __init__(self, spec):
        self.spec = spec

    def __call__(self, environ):
        return self

