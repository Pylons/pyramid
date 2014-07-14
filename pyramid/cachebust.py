import hashlib
import pkg_resources

from zope.interface import implementer

from .interfaces import ICacheBuster

from pyramid.asset import resolve_asset_spec


def generate_md5(spec):
    package, filename = resolve_asset_spec(spec)
    md5 = hashlib.md5()
    with pkg_resources.resource_stream(package, filename) as stream:
        for block in iter(lambda: stream.read(4096), ''):
            md5.update(block)
    return md5.hexdigest()


@implementer(ICacheBuster)
class DefaultCacheBuster(object):

    def generate_token(self, request, pathspec):
        token_cache = request.registry.setdefault('md5-token-cache', {})
        token = token_cache.get(pathspec)
        if not token:
            token_cache[pathspec] = token = generate_md5(pathspec)
        return token

    def pregenerate_url(self, request, token, subpath, kw):
        return token + '/' + subpath, kw

    def match_url(self, request, path_elements):
        return path_elements[1:]
