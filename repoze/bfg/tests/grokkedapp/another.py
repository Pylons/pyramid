from repoze.bfg.view import bfg_view

@bfg_view(name='another')
def grokked(context, request):
    return 'another_grokked'

@bfg_view(request_method='POST', name='another')
def grokked_post(context, request):
    return 'another_grokked_post'

@bfg_view(name='another_stacked2')
@bfg_view(name='another_stacked1')
def stacked(context, request):
    return 'another_stacked'

class stacked_class(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return 'another_stacked_class'

stacked_class = bfg_view(name='another_stacked_class1')(stacked_class)
stacked_class = bfg_view(name='another_stacked_class2')(stacked_class)

class oldstyle_grokked_class:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return 'another_oldstyle_grokked_class'
    
oldstyle_grokked_class = bfg_view(name='another_oldstyle_grokked_class')(
    oldstyle_grokked_class)

class grokked_class(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return 'another_grokked_class'
        
grokked_class = bfg_view(name='another_grokked_class')(grokked_class)

class Foo(object):
    def __call__(self, context, request):
        return 'another_grokked_instance'

grokked_instance = Foo()
grokked_instance = bfg_view(name='another_grokked_instance')(grokked_instance)

# ungrokkable

A = 1
B = {}

def stuff():
    """ """
    
