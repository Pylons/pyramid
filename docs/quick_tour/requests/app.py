from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response


def hello_world(request):
    # Some parameters from a request such as /?name=lisa
    url = request.url
    name = request.params.get('name', 'No Name Provided')

    body = 'URL %s with name: %s' % (url, name)
    return Response(
        content_type="text/plain",
        body=body
    )


if __name__ == '__main__':
    config = Configurator()
    config.add_route('hello', '/')
    config.add_view(hello_world, route_name='hello')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()
