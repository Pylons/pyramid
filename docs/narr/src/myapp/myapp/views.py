from pyramid.view import view_config

@view_config(route_name='my_view', renderer='string')
def my_view(request):
    return 'Welcome to this application'

@view_config(route_name='home', renderer='mytemplate.pt')
def home_view(request):
    return {'framework': 'Pyramid', 'project': 'myapp'}
