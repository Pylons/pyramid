from pyramid.i18n import TranslationStringFactory

import logging
log = logging.getLogger(__name__)

_ = TranslationStringFactory('hello_world')


def my_view(request):
    log.debug('Some Message')
    session = request.session
    if 'counter' in session:
        session['counter'] += 1
    else:
        session['counter'] = 0
    return {'project': 'hello_world'}
