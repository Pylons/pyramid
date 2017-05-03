import sys

from pyramid.compat import reraise
from pyramid.exceptions import PredicateMismatch
from pyramid.interfaces import (
    IExceptionViewClassifier,
    IRequest,
    )

from zope.interface import providedBy
from pyramid.view import _call_view

def _error_handler(request, exc):
    # NOTE: we do not need to delete exc_info because this function
    # should never be in the call stack of the exception
    exc_info = sys.exc_info()

    attrs = request.__dict__
    attrs['exc_info'] = exc_info
    attrs['exception'] = exc
    # clear old generated request.response, if any; it may
    # have been mutated by the view, and its state is not
    # sane (e.g. caching headers)
    if 'response' in attrs:
        del attrs['response']
    # we use .get instead of .__getitem__ below due to
    # https://github.com/Pylons/pyramid/issues/700
    request_iface = attrs.get('request_iface', IRequest)
    provides = providedBy(exc)
    try:
        response = _call_view(
            request.registry,
            request,
            exc,
            provides,
            '',
            view_classifier=IExceptionViewClassifier,
            request_iface=request_iface.combined
            )

    # if views matched but did not pass predicates then treat the
    # same as not finding any matching views
    except PredicateMismatch:
        response = None

    # re-raise the original exception as no exception views were
    # able to handle the error
    if response is None:
        if 'exception' in attrs:
            del attrs['exception']
        if 'exc_info' in attrs:
            del attrs['exc_info']
        reraise(*exc_info)

    return response

def excview_tween_factory(handler, registry):
    """ A :term:`tween` factory which produces a tween that catches an
    exception raised by downstream tweens (or the main Pyramid request
    handler) and, if possible, converts it into a Response using an
    :term:`exception view`."""

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
