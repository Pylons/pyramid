from pyramid.view import view_config


# First view, available at http://localhost:6543/
@view_config(route_name='home', renderer='tutorial:home.pt')
def home(request):
    return {'name': 'Home View'}


# /howdy
@view_config(route_name='hello', renderer='tutorial:home.pt')
def hello(request):
    return {'name': 'Hello View'}
