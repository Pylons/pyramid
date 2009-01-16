from repoze.bfg.view import bfg_view
from zope.interface import Interface

class INothing(Interface):
    pass
    
@bfg_view(for_=INothing)
def grokked(context, request):
    """ """
    

