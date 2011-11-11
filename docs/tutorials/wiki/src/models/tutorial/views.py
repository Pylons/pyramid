from pyramid.view import view_config

@view_config(renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project':'tutorial'}
