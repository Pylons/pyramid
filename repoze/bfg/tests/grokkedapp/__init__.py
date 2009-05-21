from repoze.bfg.view import bfg_view
from zope.interface import Interface

class INothing(Interface):
    pass
    
@bfg_view(for_=INothing)
def grokked(context, request):
    """ """
    
class grokked_klass(object):
    """ """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ """
        
# in 2.6+ the below can be spelled as a class decorator:
#
# @bfg_view(for_=INothing, name='grokked_klass')
# class grokked_class(object):
#     ....
#
grokked_klass = bfg_view(for_=INothing, name='grokked_klass')(grokked_klass)
