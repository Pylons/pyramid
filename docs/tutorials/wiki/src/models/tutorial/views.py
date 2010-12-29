from pyramid.view import view_config

@view_config(renderer='tutorial:templates/mytemplate.pt')
def my_view(request):
    return {'project':'tutorial'}
