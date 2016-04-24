from pyramid import testing
from pyramid.config import Configurator


def total(request, *args):
    return sum(args)


def prop(request):
    print("getting the property")
    return "the property"


config = Configurator()
config.add_request_method(total)
config.add_request_method(prop, reify=True)

request = testing.DummyRequest()
