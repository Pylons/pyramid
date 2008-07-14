from zope.component import queryMultiAdapter
from zope.interface import classProvides
from zope.interface import implements
from zope.interface import Interface

from repoze.bfg.interfaces import IWSGIApplicationFactory
from repoze.bfg.interfaces import IWSGIApplication
from repoze.bfg.mapply import mapply

class IViewSecurityPolicy(Interface):
    """ Marker interface for a view security policy; a view security
    policy. """
    def __call__():
        """ Return None if the security check succeeded,
        otherwise it should return a WSGI application representing an
        unauthorized view"""

def isResponse(ob):
    if ( hasattr(ob, 'app_iter') and hasattr(ob, 'headerlist') and
         hasattr(ob, 'status') ):
        if ( hasattr(ob.app_iter, '__iter__') and
             hasattr(ob.headerlist, '__iter__') ):
            return True

class NaiveWSGIViewAdapter:
    classProvides(IWSGIApplicationFactory)
    implements(IWSGIApplication)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def __call__(self, environ, start_response):
        context = self.context
        request = self.request
        view = self.view
        security_policy = queryMultiAdapter((context, request),
                                            IViewSecurityPolicy)
        if security_policy:
            failed_view = security_policy()
            if failed_view:
                view = failed_view

        catch_response = []
        def replace_start_response(status, headers):
            catch_response[:] = (status, headers)
        kwdict = {
            'request':self.request,
            'environ':environ,
            'start_response':start_response,
            }

        if isResponse(view):
            response = view
        else:
            response =  mapply(view, positional = (), keyword = kwdict)
        if not catch_response:
            catch_response = (response.status, response.headerlist)
        start_response(*catch_response)
        return response.app_iter
