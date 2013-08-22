from pyramid.view import view_config


# Start View 1
@view_config(route_name='hello', renderer='hello_world.jinja2')
# End View 1
def hello_world(request):
    return dict(name=request.matchdict['name'])
