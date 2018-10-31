from webob import Response


def bview(request):  # pragma: no cover
    return Response('b view')


def includeme(config):
    config.add_view(bview)
