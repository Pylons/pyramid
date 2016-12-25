from pyramid.view import view_config

import logging
log = logging.getLogger(__name__)

@view_config(route_name='home', renderer='templates/mytemplate.jinja2')
def my_view(request):
    log.debug('Some Message')
    session = request.session
    if 'counter' in session:
        session['counter'] += 1
    else:
        session['counter'] = 0
    return {'project': 'hello_world'}
