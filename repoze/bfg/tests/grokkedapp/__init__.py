from repoze.bfg.view import bfg_view

@bfg_view()
def grokked(context, request):
    """ """

@bfg_view(request_type='POST')
def grokked_post(context, request):
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
grokked_klass = bfg_view(name='grokked_klass')(grokked_klass)
