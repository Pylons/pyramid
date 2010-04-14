from zope.interface import Interface
from webob import Response
from repoze.bfg.exceptions import Forbidden

def fixture_view(context, request):
    """ """
    return Response('fixture')

def erroneous_view(context, request):
    """ """
    raise RuntimeError()

def exception_view(context, request):
    """ """
    return Response('supressed')

def protected_view(context, request):
    """ """
    raise Forbidden()

class IDummy(Interface):
    pass
