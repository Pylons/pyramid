# -*- coding: utf-8 -*-
import hashlib
import os

from os.path import (
    normcase,
    normpath,
    join,
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

from pyramid.path import AssetResolver, caller_package
from pyramid.response import FileResponse
from pyramid.traversal import traversal_path_info

slash = text_('/')

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
    one hour).

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
                 use_subpath=False, index='index.html', cachebust_match=None):
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
        self.cachebust_match = cachebust_match

    def __call__(self, context, request):
        if self.use_subpath:
            path_tuple = request.subpath
        else:
            path_tuple = traversal_path_info(request.environ['PATH_INFO'])
        if self.cachebust_match:
            path_tuple = self.cachebust_match(path_tuple)
        path = _secure_path(path_tuple)

        if path is None:
            raise HTTPNotFound('Out of bounds: %s' % request.url)

        if self.package_name: # package resource

            resource_path ='%s/%s' % (self.docroot.rstrip('/'), path)
            if resource_isdir(self.package_name, resource_path):
                if not request.path_url.endswith('/'):
                    self.add_slash_redirect(request)
                resource_path = '%s/%s' % (resource_path.rstrip('/'),self.index)
            if not resource_exists(self.package_name, resource_path):
                raise HTTPNotFound(request.url)
            filepath = resource_filename(self.package_name, resource_path)

        else: # filesystem file

            # os.path.normpath converts / to \ on windows
            filepath = normcase(normpath(join(self.norm_docroot, path)))
            if isdir(filepath):
                if not request.path_url.endswith('/'):
                    self.add_slash_redirect(request)
                filepath = join(filepath, self.index)
            if not exists(filepath):
                raise HTTPNotFound(request.url)

        return FileResponse(filepath, request, self.cache_max_age)

    def add_slash_redirect(self, request):
        url = request.path_url + '/'
        qs = request.query_string
        if qs:
            url = url + '?' + qs
        raise HTTPMovedPermanently(url)

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

def _generate_md5(spec):
    asset = AssetResolver(None).resolve(spec)
    md5 = hashlib.md5()
    with asset.stream() as stream:
        for block in iter(lambda: stream.read(4096), b''):
            md5.update(block)
    return md5.hexdigest()

class Md5AssetTokenGenerator(object):
    """
    A mixin class which provides an implementation of
    :meth:`~pyramid.interfaces.ICacheBuster.target` which generates an md5
    checksum token for an asset, caching it for subsequent calls.
    """
    def __init__(self):
        self.token_cache = {}

    def tokenize(self, pathspec):
        # An astute observer will notice that this use of token_cache doesn't
        # look particularly thread safe.  Basic read/write operations on Python
        # dicts, however, are atomic, so simply accessing and writing values
        # to the dict shouldn't cause a segfault or other catastrophic failure.
        # (See: http://effbot.org/pyfaq/what-kinds-of-global-value-mutation-are-thread-safe.htm)
        #
        # We do have a race condition that could result in the same md5
        # checksum getting computed twice or more times in parallel.  Since
        # the program would still function just fine if this were to occur,
        # the extra overhead of using locks to serialize access to the dict
        # seems an unnecessary burden.
        #
        token = self.token_cache.get(pathspec)
        if not token:
            self.token_cache[pathspec] = token = _generate_md5(pathspec)
        return token

class PathSegmentCacheBuster(object):
    """
    An implementation of :class:`~pyramid.interfaces.ICacheBuster` which
    inserts a token for cache busting in the path portion of an asset URL.

    To use this class, subclass it and provide a ``tokenize`` method which
    accepts a ``pathspec`` and returns a token.

    .. versionadded:: 1.6
    """
    def pregenerate(self, pathspec, subpath, kw):
        token = self.tokenize(pathspec)
        return (token,) + subpath, kw

    def match(self, subpath):
        return subpath[1:]

class PathSegmentMd5CacheBuster(PathSegmentCacheBuster,
                                Md5AssetTokenGenerator):
    """
    An implementation of :class:`~pyramid.interfaces.ICacheBuster` which
    inserts an md5 checksum token for cache busting in the path portion of an
    asset URL.  Generated md5 checksums are cached in order to speed up
    subsequent calls.

    .. versionadded:: 1.6
    """
    def __init__(self):
        super(PathSegmentMd5CacheBuster, self).__init__()

class QueryStringCacheBuster(object):
    """
    An implementation of :class:`~pyramid.interfaces.ICacheBuster` which adds
    a token for cache busting in the query string of an asset URL.

    The optional ``param`` argument determines the name of the parameter added
    to the query string and defaults to ``'x'``.

    To use this class, subclass it and provide a ``tokenize`` method which
    accepts a ``pathspec`` and returns a token.

    .. versionadded:: 1.6
    """
    def __init__(self, param='x'):
        self.param = param

    def pregenerate(self, pathspec, subpath, kw):
        token = self.tokenize(pathspec)
        query = kw.setdefault('_query', {})
        if isinstance(query, dict):
            query[self.param] = token
        else:
            kw['_query'] = tuple(query) + ((self.param, token),)
        return subpath, kw

class QueryStringMd5CacheBuster(QueryStringCacheBuster,
                                Md5AssetTokenGenerator):
    """
    An implementation of :class:`~pyramid.interfaces.ICacheBuster` which adds
    an md5 checksum token for cache busting in the query string of an asset
    URL.  Generated md5 checksums are cached in order to speed up subsequent
    calls.

    The optional ``param`` argument determines the name of the parameter added
    to the query string and defaults to ``'x'``.

    .. versionadded:: 1.6
    """
    def __init__(self, param='x'):
        super(QueryStringMd5CacheBuster, self).__init__(param=param)

class QueryStringConstantCacheBuster(QueryStringCacheBuster):
    """
    An implementation of :class:`~pyramid.interfaces.ICacheBuster` which adds
    an arbitrary token for cache busting in the query string of an asset URL.

    The ``token`` parameter is the token string to use for cache busting and
    will be the same for every request.

    The optional ``param`` argument determines the name of the parameter added
    to the query string and defaults to ``'x'``.

    .. versionadded:: 1.6
    """
    def __init__(self, token, param='x'):
        super(QueryStringConstantCacheBuster, self).__init__(param=param)
        self._token = token

    def tokenize(self, pathspec):
        return self._token
