import json

from zope.deprecation import deprecate
from zope.deprecation.deprecation import deprecated
from zope.interface import implementer
from zope.interface.interface import InterfaceClass

from webob import BaseRequest

from pyramid.interfaces import (
    IRequest,
    IResponse,
    ISessionFactory,
    IResponseFactory,
    )

from pyramid.compat import (
    iterkeys_,
    itervalues_,
    iteritems_,
    text_,
    bytes_,
    native_,
    )

from pyramid.decorator import reify
from pyramid.response import Response
from pyramid.url import URLMethodsMixin
from pyramid.util import InstancePropertyMixin

class TemplateContext(object):
    pass

class DeprecatedRequestMethodsMixin(object):

    # b/c dict interface for "root factory" code that expects a bare
    # environ.  Explicitly omitted dict methods: clear (unnecessary),
    # copy (implemented by WebOb), fromkeys (unnecessary); deprecated
    # as of Pyramid 1.1.

    dictlike = ('Use of the request as a dict-like object is deprecated as '
                'of Pyramid 1.1.  Use dict-like methods of "request.environ" '
                'instead.')

    @deprecate(dictlike)
    def __contains__(self, k):
        return self.environ.__contains__(k)

    @deprecate(dictlike)
    def __delitem__(self, k):
        return self.environ.__delitem__(k)

    @deprecate(dictlike)
    def __getitem__(self, k):
        return self.environ.__getitem__(k)

    @deprecate(dictlike)
    def __iter__(self):
        return iter(self.environ)

    @deprecate(dictlike)
    def __setitem__(self, k, v):
        self.environ[k] = v

    @deprecate(dictlike)
    def get(self, k, default=None):
        return self.environ.get(k, default)

    @deprecate(dictlike)
    def has_key(self, k):
        return k in self.environ

    @deprecate(dictlike)
    def items(self):
        return self.environ.items()

    @deprecate(dictlike)
    def iteritems(self):
        return iteritems_(self.environ)

    @deprecate(dictlike)
    def iterkeys(self):
        return iterkeys_(self.environ)

    @deprecate(dictlike)
    def itervalues(self):
        return itervalues_(self.environ)

    @deprecate(dictlike)
    def keys(self):
        return self.environ.keys()

    @deprecate(dictlike)
    def pop(self, k):
        return self.environ.pop(k)

    @deprecate(dictlike)
    def popitem(self):
        return self.environ.popitem()

    @deprecate(dictlike)
    def setdefault(self, v, default):
        return self.environ.setdefault(v, default)

    @deprecate(dictlike)
    def update(self, v, **kw):
        return self.environ.update(v, **kw)

    @deprecate(dictlike)
    def values(self):
        return self.environ.values()

    # 1.0 deprecated bw compat code for using response_* values

    rr_dep = ('Accessing and setting "request.response_%s" is '
              'deprecated as of Pyramid 1.1; access or set '
              '"request.response.%s" instead.')

    # response_content_type
    def _response_content_type_get(self):
        return self._response_content_type
    def _response_content_type_set(self, value):
        self._response_content_type = value
    def _response_content_type_del(self):
        del self._response_content_type
    response_content_type = property(_response_content_type_get,
                                     _response_content_type_set,
                                     _response_content_type_del)
    response_content_type = deprecated(
        response_content_type,
        rr_dep % ('content_type', 'content_type'))

    # response_headerlist
    def _response_headerlist_get(self):
        return self._response_headerlist
    def _response_headerlist_set(self, value):
        self._response_headerlist = value
    def _response_headerlist_del(self):
        del self._response_headerlist
    response_headerlist = property(_response_headerlist_get,
                                   _response_headerlist_set,
                                   _response_headerlist_del)

    hl_dep = ('Accessing and setting "request.response_headerlist" is '
              'deprecated as of Pyramid 1.1; access the headerlist via '
              '"request.response.headerlist" and extend headers via '
              '"request.response.headerlist.extend(alist)" instead of '
              '"request.response_headerlist = alist"')

    response_headerlist = deprecated(response_headerlist, hl_dep)

    # response_status
    def _response_status_get(self):
        return self._response_status
    def _response_status_set(self, value):
        self._response_status = value
    def _response_status_del(self):
        del self._response_status
    response_status = property(_response_status_get,
                               _response_status_set,
                               _response_status_del)

    response_status = deprecated(
        response_status,
        rr_dep % ('status', 'status'))

    # response_charset
    def _response_charset_get(self):
        return self._response_charset
    def _response_charset_set(self, value):
        self._response_charset = value
    def _response_charset_del(self):
        del self._response_charset
    response_charset = property(_response_charset_get,
                                _response_charset_set,
                                _response_charset_del)
    response_charset = deprecated(
        response_charset,
        rr_dep % ('charset', 'charset'))

    # response_cache_for
    def _response_cache_for_get(self):
        return self._response_cache_for
    def _response_cache_for_set(self, value):
        self._response_cache_for = value
    def _response_cache_for_del(self):
        del self._response_cache_for
    response_cache_for = property(_response_cache_for_get,
                                  _response_cache_for_set,
                                  _response_cache_for_del)
    response_cache_for = deprecated(
        response_cache_for,
        rr_dep % ('cache_for', 'cache_expires'))

class CallbackMethodsMixin(object):
    response_callbacks = ()
    finished_callbacks = ()
    def add_response_callback(self, callback):
        """
        Add a callback to the set of callbacks to be called by the
        :term:`router` at a point after a :term:`response` object is
        successfully created.  :app:`Pyramid` does not have a
        global response object: this functionality allows an
        application to register an action to be performed against the
        response once one is created.

        A 'callback' is a callable which accepts two positional
        parameters: ``request`` and ``response``.  For example:

        .. code-block:: python
           :linenos:

           def cache_callback(request, response):
               'Set the cache_control max_age for the response'
               response.cache_control.max_age = 360
           request.add_response_callback(cache_callback)

        Response callbacks are called in the order they're added
        (first-to-most-recently-added).  No response callback is
        called if an exception happens in application code, or if the
        response object returned by :term:`view` code is invalid.

        All response callbacks are called *after* the
        :class:`pyramid.events.NewResponse` event is sent.

        Errors raised by callbacks are not handled specially.  They
        will be propagated to the caller of the :app:`Pyramid`
        router application.

        See also: :ref:`using_response_callbacks`.
        """

        callbacks = self.response_callbacks
        if not callbacks:
            callbacks = []
        callbacks.append(callback)
        self.response_callbacks = callbacks

    def _process_response_callbacks(self, response):
        callbacks = self.response_callbacks
        while callbacks:
            callback = callbacks.pop(0)
            callback(self, response)

    def add_finished_callback(self, callback):
        """
        Add a callback to the set of callbacks to be called
        unconditionally by the :term:`router` at the very end of
        request processing.

        ``callback`` is a callable which accepts a single positional
        parameter: ``request``.  For example:

        .. code-block:: python
           :linenos:

           import transaction

           def commit_callback(request):
               '''commit or abort the transaction associated with request'''
               if request.exception is not None:
                   transaction.abort()
               else:
                   transaction.commit()
           request.add_finished_callback(commit_callback)

        Finished callbacks are called in the order they're added (
        first- to most-recently- added).  Finished callbacks (unlike
        response callbacks) are *always* called, even if an exception
        happens in application code that prevents a response from
        being generated.

        The set of finished callbacks associated with a request are
        called *very late* in the processing of that request; they are
        essentially the last thing called by the :term:`router`. They
        are called after response processing has already occurred in a
        top-level ``finally:`` block within the router request
        processing code.  As a result, mutations performed to the
        ``request`` provided to a finished callback will have no
        meaningful effect, because response processing will have
        already occurred, and the request's scope will expire almost
        immediately after all finished callbacks have been processed.

        Errors raised by finished callbacks are not handled specially.
        They will be propagated to the caller of the :app:`Pyramid`
        router application.

        See also: :ref:`using_finished_callbacks`.
        """

        callbacks = self.finished_callbacks
        if not callbacks:
            callbacks = []
        callbacks.append(callback)
        self.finished_callbacks = callbacks

    def _process_finished_callbacks(self):
        callbacks = self.finished_callbacks
        while callbacks:
            callback = callbacks.pop(0)
            callback(self)

@implementer(IRequest)
class Request(BaseRequest, DeprecatedRequestMethodsMixin, URLMethodsMixin,
              CallbackMethodsMixin, InstancePropertyMixin):
    """
    A subclass of the :term:`WebOb` Request class.  An instance of
    this class is created by the :term:`router` and is provided to a
    view callable (and to other subsystems) as the ``request``
    argument.

    The documentation below (save for the ``add_response_callback`` and
    ``add_finished_callback`` methods, which are defined in this subclass
    itself, and the attributes ``context``, ``registry``, ``root``,
    ``subpath``, ``traversed``, ``view_name``, ``virtual_root`` , and
    ``virtual_root_path``, each of which is added to the request by the
    :term:`router` at request ingress time) are autogenerated from the WebOb
    source code used when this documentation was generated.

    Due to technical constraints, we can't yet display the WebOb
    version number from which this documentation is autogenerated, but
    it will be the 'prevailing WebOb version' at the time of the
    release of this :app:`Pyramid` version.  See
    http://pythonpaste.org/webob/ for further information.
    """
    exception = None
    exc_info = None
    matchdict = None
    matched_route = None

    @reify
    def tmpl_context(self):
        """ Template context (for Pylons apps) """
        return TemplateContext()

    @reify
    def session(self):
        """ Obtain the :term:`session` object associated with this
        request.  If a :term:`session factory` has not been registered
        during application configuration, a
        :class:`pyramid.exceptions.ConfigurationError` will be raised"""
        factory = self.registry.queryUtility(ISessionFactory)
        if factory is None:
            raise AttributeError(
                'No session factory registered '
                '(see the Sessions chapter of the Pyramid documentation)')
        return factory(self)

    @reify
    def response(self):
        """This attribute is actually a "reified" property which returns an
        instance of the :class:`pyramid.response.Response`. class.  The
        response object returned does not exist until this attribute is
        accessed.  Once it is accessed, subsequent accesses will return the
        same Response object.

        The ``request.response`` API is used by renderers.  A render obtains
        the response object it will return from a view that uses that renderer
        by accessing ``request.response``.  Therefore, it's possible to use the
        ``request.response`` API to set up a response object with "the
        right" attributes (e.g. by calling ``request.response.set_cookie()``)
        within a view that uses a renderer.  Mutations to this response object
        will be preserved in the response sent to the client."""
        registry = self.registry
        response_factory = registry.queryUtility(IResponseFactory,
                                                 default=Response)
        return response_factory()

    def is_response(self, ob):
        """ Return ``True`` if the object passed as ``ob`` is a valid
        response object, ``False`` otherwise."""
        registry = self.registry
        adapted = registry.queryAdapterOrSelf(ob, IResponse)
        if adapted is None:
            return False
        return adapted is ob

    @property
    def json_body(self):
        return json.loads(text_(self.body, self.charset))

def route_request_iface(name, bases=()):
    # zope.interface treats the __name__ as the __doc__ and changes __name__
    # to None for interfaces that contain spaces if you do not pass a
    # nonempty __doc__ (insane); see
    # zope.interface.interface.Element.__init__ and
    # https://github.com/Pylons/pyramid/issues/232; as a result, always pass
    # __doc__ to the InterfaceClass constructor.
    iface = InterfaceClass('%s_IRequest' % name, bases=bases,
                           __doc__="route_request_iface-generated interface")
    # for exception view lookups
    iface.combined = InterfaceClass(
        '%s_combined_IRequest' % name,
        bases=(iface, IRequest),
        __doc__ = 'route_request_iface-generated combined interface')
    return iface

def add_global_response_headers(request, headerlist):
    def add_headers(request, response):
        for k, v in headerlist:
            response.headerlist.append((k, v))
    request.add_response_callback(add_headers)

def call_app_with_subpath_as_path_info(request, app):
    # Copy the request.  Use the source request's subpath (if it exists) as
    # the new request's PATH_INFO.  Set the request copy's SCRIPT_NAME to the
    # prefix before the subpath.  Call the application with the new request
    # and return a response.
    #
    # Postconditions:
    # - SCRIPT_NAME and PATH_INFO are empty or start with /
    # - At least one of SCRIPT_NAME or PATH_INFO are set.
    # - SCRIPT_NAME is not '/' (it should be '', and PATH_INFO should
    #   be '/').

    environ = request.environ
    script_name = environ.get('SCRIPT_NAME', '')
    path_info = environ.get('PATH_INFO', '/')
    subpath = list(getattr(request, 'subpath', ()))

    new_script_name = ''

    # compute new_path_info
    new_path_info = '/' + '/'.join([native_(x.encode('utf-8'), 'latin-1')
                                    for x in subpath])

    if new_path_info != '/': # don't want a sole double-slash
        if path_info != '/': # if orig path_info is '/', we're already done
            if path_info.endswith('/'):
                # readd trailing slash stripped by subpath (traversal)
                # conversion
                new_path_info += '/'

    # compute new_script_name
    workback = (script_name + path_info).split('/')

    tmp = []
    while workback:
        if tmp == subpath:
            break
        el = workback.pop()
        if el:
            tmp.insert(0, text_(bytes_(el, 'latin-1'), 'utf-8'))

    # strip all trailing slashes from workback to avoid appending undue slashes
    # to end of script_name
    while workback and (workback[-1] == ''):
        workback = workback[:-1]

    new_script_name = '/'.join(workback)

    new_request = request.copy()
    new_request.environ['SCRIPT_NAME'] = new_script_name
    new_request.environ['PATH_INFO'] = new_path_info
    return new_request.get_response(app)
