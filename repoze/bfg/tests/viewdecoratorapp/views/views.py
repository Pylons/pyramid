import os
from repoze.bfg.view import bfg_view

@bfg_view(renderer='templates/foo.pt', name='first')
def first(request):
    return {'result':'OK1'}

@bfg_view(renderer='repoze.bfg.tests.viewdecoratorapp.views:templates/foo.pt',
          name='second')
def second(request):
    return {'result':'OK2'}

here = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
foo = os.path.join(here, 'templates', 'foo.pt')
@bfg_view(renderer=foo, name='third')
def third(request):
    return {'result':'OK3'}
