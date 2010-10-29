from pyramid.view import view_config

@view_config()
def grokked(context, request):
    return 'grokked'

@view_config(request_method='POST')
def grokked_post(context, request):
    return 'grokked_post'

@view_config(name='stacked2')
@view_config(name='stacked1')
def stacked(context, request):
    return 'stacked'

class stacked_class(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return 'stacked_class'

stacked_class = view_config(name='stacked_class1')(stacked_class)
stacked_class = view_config(name='stacked_class2')(stacked_class)
    
class oldstyle_grokked_class:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return 'oldstyle_grokked_class'
    
oldstyle_grokked_class = view_config(name='oldstyle_grokked_class')(
    oldstyle_grokked_class)

class grokked_class(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return 'grokked_class'
        
grokked_class = view_config(name='grokked_class')(grokked_class)

class Foo(object):
    def __call__(self, context, request):
        return 'grokked_instance'

grokked_instance = Foo()
grokked_instance = view_config(name='grokked_instance')(grokked_instance)

class Base(object):
    @view_config(name='basemethod')
    def basemethod(self):
        """ """
    
class MethodViews(Base):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(name='method1')
    def method1(self):
        return 'method1'

    @view_config(name='method2')
    def method2(self):
        return 'method2'

    @view_config(name='stacked_method2')
    @view_config(name='stacked_method1')
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
