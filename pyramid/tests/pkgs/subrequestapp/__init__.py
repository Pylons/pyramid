from pyramid.config import Configurator
from pyramid.request import Request

def view_one(request):
    subreq = Request.blank('/view_two')
    response = request.subrequest(subreq)
    return response

def view_two(request):
    request.response.body = 'This came from view_two'
    return request.response

def main():
    config = Configurator()
    config.add_route('one', '/view_one')
    config.add_route('two', '/view_two')
    config.add_view(view_one, route_name='one')
    config.add_view(view_two, route_name='two')
    return config

