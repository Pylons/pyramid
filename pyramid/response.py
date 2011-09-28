import venusian

from webob import Response as _Response
from zope.interface import implementer
from pyramid.interfaces import IResponse

@implementer(IResponse)
class Response(_Response):
    pass

class response_adapter(object):
    """ Decorator activated via a :term:`scan` which treats the function
    being decorated as a :term:`response adapter` for the set of types or
    interfaces passed as ``*types_or_ifaces`` to the decorator constructor.

    For example, if you scan the following response adapter:

    .. code-block:: python

        from pyramid.response import Response
        from pyramid.response import response_adapter

        @response_adapter(int)
        def myadapter(i):
            return Response(status=i)

    You can then return an integer from your view callables, and it will be
    converted into a response with the integer as the status code.

    More than one type or interface can be passed as a constructor argument.
    The decorated response adapter will be called for each type or interface.

    .. code-block:: python

        import json

        from pyramid.response import Response
        from pyramid.response import response_adapter

        @response_adapter(dict, list)
        def myadapter(ob):
            return Response(json.dumps(ob))
        
    This method will have no effect until a :term:`scan` is performed
    agains the package or module which contains it, ala:

    .. code-block:: python

        from pyramid.config import Configurator
        config = Configurator()
        config.scan('somepackage_containing_adapters')

    """
    venusian = venusian # for unit testing

    def __init__(self, *types_or_ifaces):
        self.types_or_ifaces = types_or_ifaces

    def register(self, scanner, name, wrapped):
        config = scanner.config
        for type_or_iface in self.types_or_ifaces:
            config.add_response_adapter(wrapped, type_or_iface)

    def __call__(self, wrapped):
        self.venusian.attach(wrapped, self.register, category='pyramid')
        return wrapped
