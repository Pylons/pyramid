from zope.interface import classProvides
from zope.interface import implements

from repoze.bfg.interfaces import IWSGIApplicationFactory
from repoze.bfg.interfaces import IWSGIApplication
from repoze.bfg.mapply import mapply

def isResponse(ob):
    if ( hasattr(ob, 'app_iter') and hasattr(ob, 'headerlist') and
         hasattr(ob, 'status') ):
        if ( hasattr(ob.app_iter, '__iter__') and
             hasattr(ob.headerlist, '__iter__') and
             isinstance(ob.status, basestring) ) :
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
        if not isResponse(response):
            raise ValueError('response was not IResponse: %s' % response)
        if not catch_response:
            catch_response = (response.status, response.headerlist)
        start_response(*catch_response)
        return response.app_iter
