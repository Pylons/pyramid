import mimetypes
from os.path import getmtime, getsize

import venusian

from webob import Response as _Response
from zope.interface import implementer
from pyramid.interfaces import IResponse, IResponseFactory

_BLOCK_SIZE = 4096 * 64  # 256K


@implementer(IResponse)
class Response(_Response):
    pass


class FileResponse(Response):
    """
    A Response object that can be used to serve a static file from disk
    simply.

    ``path`` is a file path on disk.

    ``request`` must be a Pyramid :term:`request` object.  Note
    that a request *must* be passed if the response is meant to attempt to
    use the ``wsgi.file_wrapper`` feature of the web server that you're using
    to serve your Pyramid application.

    ``cache_max_age`` is the number of seconds that should be used
    to HTTP cache this response.

    ``content_type`` is the content_type of the response.

    ``content_encoding`` is the content_encoding of the response.
    It's generally safe to leave this set to ``None`` if you're serving a
    binary file.  This argument will be ignored if you also leave
    ``content-type`` as ``None``.
    """

    def __init__(
        self,
        path,
        request=None,
        cache_max_age=None,
        content_type=None,
        content_encoding=None,
    ):
        if content_type is None:
            content_type, content_encoding = _guess_type(path)
        super(FileResponse, self).__init__(
            conditional_response=True,
            content_type=content_type,
            content_encoding=content_encoding,
        )
        self.last_modified = getmtime(path)
        content_length = getsize(path)
        f = open(path, 'rb')
        app_iter = None
        if request is not None:
            environ = request.environ
            if 'wsgi.file_wrapper' in environ:
                app_iter = environ['wsgi.file_wrapper'](f, _BLOCK_SIZE)
        if app_iter is None:
            app_iter = FileIter(f, _BLOCK_SIZE)
        self.app_iter = app_iter
        # assignment of content_length must come after assignment of app_iter
        self.content_length = content_length
        if cache_max_age is not None:
            self.cache_expires = cache_max_age


class FileIter(object):
    """ A fixed-block-size iterator for use as a WSGI app_iter.

    ``file`` is a Python file pointer (or at least an object with a ``read``
    method that takes a size hint).

    ``block_size`` is an optional block size for iteration.
    """

    def __init__(self, file, block_size=_BLOCK_SIZE):
        self.file = file
        self.block_size = block_size

    def __iter__(self):
        return self

    def __next__(self):
        val = self.file.read(self.block_size)
        if not val:
            raise StopIteration
        return val

    def close(self):
        self.file.close()


class response_adapter(object):
    """ Decorator activated via a :term:`scan` which treats the function
    being decorated as a :term:`response adapter` for the set of types or
    interfaces passed as ``*types_or_ifaces`` to the decorator constructor.

    For example, if you scan the following response adapter:

    .. code-block:: python

        from pyramid.response import Response
        from pyramid.response import response_adapter

        @response_adapter(int)
        def myadapter(i):
            return Response(status=i)

    You can then return an integer from your view callables, and it will be
    converted into a response with the integer as the status code.

    More than one type or interface can be passed as a constructor argument.
    The decorated response adapter will be called for each type or interface.

    .. code-block:: python

        import json

        from pyramid.response import Response
        from pyramid.response import response_adapter

        @response_adapter(dict, list)
        def myadapter(ob):
            return Response(json.dumps(ob))

    This method will have no effect until a :term:`scan` is performed
    agains the package or module which contains it, ala:

    .. code-block:: python

        from pyramid.config import Configurator
        config = Configurator()
        config.scan('somepackage_containing_adapters')

    Two additional keyword arguments which will be passed to the
    :term:`venusian` ``attach`` function are ``_depth`` and ``_category``.

    ``_depth`` is provided for people who wish to reuse this class from another
    decorator. The default value is ``0`` and should be specified relative to
    the ``response_adapter`` invocation. It will be passed in to the
    :term:`venusian` ``attach`` function as the depth of the callstack when
    Venusian checks if the decorator is being used in a class or module
    context. It's not often used, but it can be useful in this circumstance.

    ``_category`` sets the decorator category name. It can be useful in
    combination with the ``category`` argument of ``scan`` to control which
    views should be processed.

    See the :py:func:`venusian.attach` function in Venusian for more
    information about the ``_depth`` and ``_category`` arguments.

    .. versionchanged:: 1.9.1
       Added the ``_depth`` and ``_category`` arguments.

    """

    venusian = venusian  # for unit testing

    def __init__(self, *types_or_ifaces, **kwargs):
        self.types_or_ifaces = types_or_ifaces
        self.depth = kwargs.pop('_depth', 0)
        self.category = kwargs.pop('_category', 'pyramid')
        self.kwargs = kwargs

    def register(self, scanner, name, wrapped):
        config = scanner.config
        for type_or_iface in self.types_or_ifaces:
            config.add_response_adapter(wrapped, type_or_iface, **self.kwargs)

    def __call__(self, wrapped):
        self.venusian.attach(
            wrapped,
            self.register,
            category=self.category,
            depth=self.depth + 1,
        )
        return wrapped


def _get_response_factory(registry):
    """ Obtain a :class: `pyramid.response.Response` using the
    `pyramid.interfaces.IResponseFactory`.
    """
    response_factory = registry.queryUtility(
        IResponseFactory, default=lambda r: Response()
    )

    return response_factory


def _guess_type(path):
    content_type, content_encoding = mimetypes.guess_type(path, strict=False)
    if content_type is None:
        content_type = 'application/octet-stream'
    return content_type, content_encoding
