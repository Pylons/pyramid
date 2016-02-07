from pyramid.view import view_config


@view_config(route_name='hello', renderer='hello_world.jinja2')
def hello_world(request):
    return dict(name=request.matchdict['name'])
