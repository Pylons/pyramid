from pyramid.config import Configurator
from myproject.resources import Root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.add_view('myproject.views.my_view',
                    context='myproject.resources.Root',
                    renderer='myproject:templates/mytemplate.pt')
    config.add_static_view('static', 'myproject:static')
    return config.make_wsgi_app()
