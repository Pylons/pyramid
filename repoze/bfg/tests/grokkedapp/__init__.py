from repoze.bfg.view import bfg_view

@bfg_view()
def grokked(context, request):
    return 'grokked'

@bfg_view(request_method='POST')
def grokked_post(context, request):
    return 'grokked_post'
    
class oldstyle_grokked_class:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return 'oldstyle_grokked_class'
    
oldstyle_grokked_class = bfg_view(name='oldstyle_grokked_class')(
    oldstyle_grokked_class)

class grokked_class(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return 'grokked_class'
        
grokked_class = bfg_view(name='grokked_class')(grokked_class)

class Foo(object):
    def __call__(self, context, request):
        return 'grokked_instance'

grokked_instance = Foo()
grokked_instance = bfg_view(name='grokked_instance')(grokked_instance)

# ungrokkable

A = 1
B = {}

def stuff():
    """ """
    
