from pyramid.view import view_config


@view_config(route_name='home', renderer='hello_world:templates/mytemplate.jinja2')
def my_view(request):
    return {'project': 'hello_world'}
