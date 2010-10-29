import os
from pyramid.view import view_config

@view_config(renderer='templates/foo.pt', name='first')
def first(request):
    return {'result':'OK1'}

@view_config(renderer='pyramid.tests.viewdecoratorapp.views:templates/foo.pt',
             name='second')
def second(request):
    return {'result':'OK2'}

here = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
foo = os.path.join(here, 'templates', 'foo.pt')
@view_config(renderer=foo, name='third')
def third(request):
    return {'result':'OK3'}
