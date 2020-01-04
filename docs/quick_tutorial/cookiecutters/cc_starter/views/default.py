from pyramid.view import view_config


@view_config(route_name='home', renderer='cc_starter:templates/mytemplate.jinja2')
def my_view(request):
    return {'project': 'cc_starter'}
