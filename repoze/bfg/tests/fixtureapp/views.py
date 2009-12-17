from zope.interface import Interface
from webob import Response

def fixture_view(context, request):
    """ """
    return Response('fixture')

class IDummy(Interface):
    pass

