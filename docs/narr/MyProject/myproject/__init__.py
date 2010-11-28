from pyramid.configuration import Configurator
from myproject.models import get_root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=get_root, settings=settings)
    config.add_view('myproject.views.my_view',
                    context='myproject.models.MyModel',
                    renderer='myproject:templates/mytemplate.pt')
    config.add_static_view('static', 'myproject:static')
    return config.make_wsgi_app()

