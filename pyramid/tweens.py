import sys

from pyramid.compat import reraise
from pyramid.httpexceptions import HTTPNotFound

def _error_handler(request, exc):
    # NOTE: we do not need to delete exc_info because this function
    # should never be in the call stack of the exception
    exc_info = sys.exc_info()

    try:
        response = request.invoke_exception_view(exc_info)
    except HTTPNotFound:
        # re-raise the original exception as no exception views were
        # able to handle the error
        reraise(*exc_info)

    return response

def excview_tween_factory(handler, registry):
    """ A :term:`tween` factory which produces a tween that catches an
    exception raised by downstream tweens (or the main Pyramid request
    handler) and, if possible, converts it into a Response using an
    :term:`exception view`.

    .. versionchanged:: 1.9
       The ``request.response`` will be remain unchanged even if the tween
       handles an exception. Previously it was deleted after handling an
       exception.

       Also, ``request.exception`` and ``request.exc_info`` are only set if
       the tween handles an exception and returns a response otherwise they
       are left at their original values.

    """

    def excview_tween(request):
        try:
            response = handler(request)
        except Exception as exc:
            response = _error_handler(request, exc)
        return response

    return excview_tween

MAIN = 'MAIN'
INGRESS = 'INGRESS'
EXCVIEW = 'pyramid.tweens.excview_tween_factory'
