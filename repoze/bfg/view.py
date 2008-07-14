from zope.interface import implements
from zope.interface import classProvides

from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IViewFactory

class View(object):
    """ Convenience base class for user-defined views """
    implements(IView)
    classProvides(IViewFactory)
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, **kw):
        raise NotImplementedError


    
