from pyramid.view import view_config

@view_config(name='another')
def grokked(context, request):
    return 'another_grokked'

@view_config(request_method='POST', name='another')
def grokked_post(context, request):
    return 'another_grokked_post'

@view_config(name='another_stacked2')
@view_config(name='another_stacked1')
def stacked(context, request):
    return 'another_stacked'

class stacked_class(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return 'another_stacked_class'

stacked_class = view_config(name='another_stacked_class1')(stacked_class)
stacked_class = view_config(name='another_stacked_class2')(stacked_class)

class oldstyle_grokked_class:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return 'another_oldstyle_grokked_class'
    
oldstyle_grokked_class = view_config(name='another_oldstyle_grokked_class')(
    oldstyle_grokked_class)

class grokked_class(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return 'another_grokked_class'
        
grokked_class = view_config(name='another_grokked_class')(grokked_class)

class Foo(object):
    def __call__(self, context, request):
        return 'another_grokked_instance'

grokked_instance = Foo()
grokked_instance = view_config(name='another_grokked_instance')(
    grokked_instance)

# ungrokkable

A = 1
B = {}

def stuff():
    """ """
    
