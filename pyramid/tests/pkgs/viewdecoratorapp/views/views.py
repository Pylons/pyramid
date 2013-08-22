from pyramid.view import view_config

@view_config(renderer='templates/foo.pt', name='first')
def first(request):
    return {'result':'OK1'}

@view_config(
    renderer='pyramid.tests.pkgs.viewdecoratorapp.views:templates/foo.pt',
             name='second')
def second(request):
    return {'result':'OK2'}

