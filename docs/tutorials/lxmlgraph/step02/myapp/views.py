from webob import Response

def my_view(context, request):
    response = Response('Hello to %s from %s @ %s' % (
            context.tag, 
            context.__name__, 
            request.environ['PATH_INFO']))
    return response
