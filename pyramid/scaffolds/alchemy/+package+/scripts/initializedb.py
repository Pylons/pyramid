import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models.meta import (
    Base,
    get_session,
    get_engine,
    get_dbmaker,
    )
from ..models.mymodel import MyModel


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    dbmaker = get_dbmaker(engine)

    dbsession = get_session(transaction.manager, dbmaker)

    Base.metadata.create_all(engine)

    with transaction.manager:
        model = MyModel(name='one', value=1)
        dbsession.add(model)
