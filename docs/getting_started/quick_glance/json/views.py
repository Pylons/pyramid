from pyramid.view import view_config


@view_config(route_name='hello', renderer='hello_world.pt')
def hello_world(request):
    return dict(name=request.matchdict['name'])


# Start View 1
@view_config(route_name='hello_json', renderer='json')
def hello_json(request):
    return [1, 2, 3]
    # End View 1