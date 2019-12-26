from webob import Response

from pyramid.httpexceptions import HTTPBadRequest

from .models import AnException


def no(request):
    return Response('no')


def yes(request):
    return Response('yes')


def maybe(request):
    return Response('maybe')


def whoa(request):
    return Response('whoa')


def raise_exception(request):
    raise AnException()


def raise_httpexception(request):
    raise HTTPBadRequest


def catch_httpexception(request):
    return Response('caught')
