import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models.meta import (
    Base,
    get_session,
    get_engine,
    get_dbmaker,
    )
from ..models.mymodel import Page


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    engine = get_engine(settings)
    dbmaker = get_dbmaker(engine)

    dbsession = get_session(transaction.manager, dbmaker)

    Base.metadata.create_all(engine)

    with transaction.manager:
        model = Page(name='FrontPage', data='This is the front page')
        dbsession.add(model)
