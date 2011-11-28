# -*- coding: utf-8 -*-
import mimetypes
import os

from os.path import (
    normcase,
    normpath,
    join,
    getmtime,
    getsize,
    isdir,
    exists,
    )

from pkg_resources import (
    resource_exists,
    resource_filename,
    resource_isdir,
    )

from repoze.lru import lru_cache

from pyramid.asset import resolve_asset_spec

from pyramid.compat import text_

from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPMovedPermanently,
    )

from pyramid.path import caller_package
from pyramid.response import Response
from pyramid.traversal import traversal_path_info

slash = text_('/')

def init_mimetypes(mimetypes):
    # this is a function so it can be unittested
    if hasattr(mimetypes, 'init'):
        mimetypes.init()
        return True
    return False

# See http://bugs.python.org/issue5853 which is a recursion bug
# that seems to effect Python 2.6, Python 2.6.1, and 2.6.2 (a fix
# has been applied on the Python 2 trunk).
init_mimetypes(mimetypes)

class _FileResponse(Response):
    """
    Serves a static filelike object.
    """
    def __init__(self, path, cache_max_age):
        super(_FileResponse, self).__init__(conditional_response=True)
        self.last_modified = getmtime(path)
        content_type, content_encoding = mimetypes.guess_type(path,
                                                              strict=False)
        if content_type is None:
            content_type = 'application/octet-stream'
        self.content_type = content_type
        self.content_encoding = content_encoding
        content_length = getsize(path)
        self.app_iter = _FileIter(open(path, 'rb'), content_length)
        # assignment of content_length must come after assignment of app_iter
        self.content_length = content_length
        if cache_max_age is not None:
            self.cache_expires = cache_max_age

class _FileIter(object):
    block_size = 4096 * 64 # (256K)

    def __init__(self, file, size=None):
        self.file = file
        self.size = size

    def __iter__(self):
        return self

    def next(self):
        chunk_size = self.block_size
        if self.size is not None:
            if chunk_size > self.size:
                chunk_size = self.size
            self.size -= chunk_size
        data = self.file.read(chunk_size)
        if not data:
            raise StopIteration
        return data

    __next__ = next # py3

    def close(self):
        self.file.close()

class static_view(object):
    """ An instance of this class is a callable which can act as a
    :app:`Pyramid` :term:`view callable`; this view will serve
    static files from a directory on disk based on the ``root_dir``
    you provide to its constructor.

    The directory may contain subdirectories (recursively); the static
    view implementation will descend into these directories as
    necessary based on the components of the URL in order to resolve a
    path into a response.

    You may pass an absolute or relative filesystem path or a
    :term:`asset specification` representing the directory
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

    ``use_subpath`` influences whether ``request.subpath`` will be used as
    ``PATH_INFO`` when calling the underlying WSGI application which actually
    serves the static files.  If it is ``True``, the static application will
    consider ``request.subpath`` as ``PATH_INFO`` input.  If it is ``False``,
    the static application will consider request.environ[``PATH_INFO``] as
    ``PATH_INFO`` input. By default, this is ``False``.

    .. note::

       If the ``root_dir`` is relative to a :term:`package`, or is a
       :term:`asset specification` the :app:`Pyramid`
       :class:`pyramid.config.Configurator` method can be used to override
       assets within the named ``root_dir`` package-relative directory.
       However, if the ``root_dir`` is absolute, configuration will not be able
       to override the assets it contains.
    """

    def __init__(self, root_dir, cache_max_age=3600, package_name=None,
                 use_subpath=False, index='index.html'):
        # package_name is for bw compat; it is preferred to pass in a
        # package-relative path as root_dir
        # (e.g. ``anotherpackage:foo/static``).
        self.cache_max_age = cache_max_age
        if package_name is None:
            package_name = caller_package().__name__
        package_name, docroot = resolve_asset_spec(root_dir, package_name)
        self.use_subpath = use_subpath
        self.package_name = package_name
        self.docroot = docroot
        self.norm_docroot = normcase(normpath(docroot))
        self.index = index

    def __call__(self, context, request):
        if self.use_subpath:
            path_tuple = request.subpath
        else:
            path_tuple = traversal_path_info(request.environ['PATH_INFO'])

        path = _secure_path(path_tuple)

        if path is None:
            return HTTPNotFound('Out of bounds: %s' % request.url)

        if self.package_name: # package resource

            resource_path ='%s/%s' % (self.docroot.rstrip('/'), path)
            if resource_isdir(self.package_name, resource_path):
                if not request.path_url.endswith('/'):
                    return self.add_slash_redirect(request)
                resource_path = '%s/%s' % (resource_path.rstrip('/'),self.index)
            if not resource_exists(self.package_name, resource_path):
                return HTTPNotFound(request.url)
            filepath = resource_filename(self.package_name, resource_path)

        else: # filesystem file

            # os.path.normpath converts / to \ on windows
            filepath = normcase(normpath(join(self.norm_docroot, path)))
            if isdir(filepath):
                if not request.path_url.endswith('/'):
                    return self.add_slash_redirect(request)
                filepath = join(filepath, self.index)
            if not exists(filepath):
                return HTTPNotFound(request.url)

        return _FileResponse(filepath ,self.cache_max_age)

    def add_slash_redirect(self, request):
        url = request.path_url + '/'
        qs = request.query_string
        if qs:
            url = url + '?' + qs
        return HTTPMovedPermanently(url)

_seps = set(['/', os.sep])
def _contains_slash(item):
    for sep in _seps:
        if sep in item:
            return True

_has_insecure_pathelement = set(['..', '.', '']).intersection

@lru_cache(1000)
def _secure_path(path_tuple):
    if _has_insecure_pathelement(path_tuple):
        # belt-and-suspenders security; this should never be true
        # unless someone screws up the traversal_path code
        # (request.subpath is computed via traversal_path too)
        return None
    if any([_contains_slash(item) for item in path_tuple]):
        return None
    encoded = slash.join(path_tuple) # will be unicode
    return encoded

