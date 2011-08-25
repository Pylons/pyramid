from paste.httpserver import serve
from pyramid.configuration import Configurator

def hello_world(request):
   return 'Hello %(name)s!' % request.matchdict

if __name__ == '__main__':
   config = Configurator()
   config.add_route('hello', '/hello/{name}')
   config.add_view(hello_world, route_name='hello')
   app = config.make_wsgi_app()
   serve(app, host='0.0.0.0')