# Start Logging 1
import logging
log = logging.getLogger(__name__)
# End Logging 1

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('hello_world')


def my_view(request):
    # Start Logging 2
    log.debug('Some Message')
    # End Logging 2
    # Start Sphinx Include 1
    session = request.session
    if 'counter' in session:
        session['counter'] += 1
    else:
        session['counter'] = 0
    # End Sphinx Include 1
    return {'project': 'hello_world'}
