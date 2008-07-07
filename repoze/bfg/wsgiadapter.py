from zope.interface import implements
from zope.interface import classProvides

from repoze.bfg.interfaces import IWSGIApplicationFactory
from repoze.bfg.interfaces import IWSGIApplication
from repoze.bfg.mapply import mapply

class NaiveWSGIViewAdapter:
    classProvides(IWSGIApplicationFactory)
    implements(IWSGIApplication)

    def __init__(self, view, request):
        self.view = view
        self.request = request

    def __call__(self, environ, start_response):
        catch_response = []
        def replace_start_response(status, headers):
            catch_response[:] = (status, headers)
        kwdict = {
            'request':self.request,
            'environ':environ,
            'start_response':start_response,
            }
        response =  mapply(self.view, positional = (), keyword = kwdict)
        if not catch_response:
            catch_response = (response.status, response.headerlist)
        start_response(*catch_response)
        return response.app_iter
