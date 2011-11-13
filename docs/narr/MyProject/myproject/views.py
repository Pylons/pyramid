from pyramid.view import view_config
from .resources import Root

@view_config(context=Root, renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project':'MyProject'}
