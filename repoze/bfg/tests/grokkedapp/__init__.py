from repoze.bfg.view import bfg_view

@bfg_view()
def grokked(context, request):
    return 'grokked'

@bfg_view(request_method='POST')
def grokked_post(context, request):
    return 'grokked_post'

@bfg_view(name='stacked2')
@bfg_view(name='stacked1')
def stacked(context, request):
    return 'stacked'

class stacked_class(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return 'stacked_class'

stacked_class = bfg_view(name='stacked_class1')(stacked_class)
stacked_class = bfg_view(name='stacked_class2')(stacked_class)
    
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

class Base(object):
    @bfg_view(name='basemethod')
    def basemethod(self):
        """ """
    
class MethodViews(Base):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @bfg_view(name='method1')
    def method1(self):
        return 'method1'

    @bfg_view(name='method2')
    def method2(self):
        return 'method2'

    @bfg_view(name='stacked_method2')
    @bfg_view(name='stacked_method1')
    def stacked(self):
        return 'stacked_method'

# ungrokkable

A = 1
B = {}

def stuff():
    """ """

class Whatever(object):
    pass

class Whatever2:
    pass
