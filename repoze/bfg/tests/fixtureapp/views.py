from zope.interface import Interface
from webob import Response

def fixture_view(context, request):
    """ """
    return Response('fixture')

def renderer_view(request):
    return {'a':1}

class IDummy(Interface):
    pass

