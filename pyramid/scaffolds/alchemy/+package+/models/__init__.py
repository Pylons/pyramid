from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import configure_mappers
import zope.sqlalchemy

# import or define all models here to ensure they are attached to the
# Base.metadata prior to any initialization routines
from .mymodel import MyModel # flake8: noqa

# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()


def get_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)


def get_sessionmaker(engine):
    dbmaker = sessionmaker()
    dbmaker.configure(bind=engine)
    return dbmaker


def get_tm_session(dbmaker, transaction_manager):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example::

          import transaction

          engine = get_engine(settings)
          dbmaker = get_sessionmaker(engine)
          with transaction.manager:
              dbsession = get_tm_session(dbmaker, transaction.manager)

    """
    dbsession = dbmaker()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction_manager)
    return dbsession


def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('{{package}}.models')``.

    """
    settings = config.get_settings()

    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include('pyramid_tm')

    dbmaker = get_sessionmaker(get_engine(settings))

    # make request.dbsession available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(dbmaker, r.tm),
        'dbsession',
        reify=True
    )
