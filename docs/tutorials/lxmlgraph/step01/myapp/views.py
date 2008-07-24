from webob import Response

def my_hello_view(context, request):
    response = Response('Hello from %s @ %s' % (
            context.__name__, 
            request.environ['PATH_INFO']))
    return response
