from pyramid.view import view_config

from ..models import MyModel


@view_config(context=MyModel, renderer='tutorial:templates/mytemplate.pt')
def my_view(request):
    return {'project': 'tutorial'}
