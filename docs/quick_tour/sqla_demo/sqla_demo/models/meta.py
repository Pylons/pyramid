from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData
import zope.sqlalchemy

# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.zzzcomputing.com/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)


def includeme(config):
    settings = config.get_settings()
    dbmaker = get_dbmaker(get_engine(settings))

    config.add_request_method(
        lambda r: get_session(r.tm, dbmaker),
        'dbsession',
        reify=True
    )

    config.include('pyramid_tm')


def get_session(transaction_manager, dbmaker):
    dbsession = dbmaker()
    zope.sqlalchemy.register(dbsession,
                             transaction_manager=transaction_manager)
    return dbsession


def get_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)


def get_dbmaker(engine):
    dbmaker = sessionmaker()
    dbmaker.configure(bind=engine)
    return dbmaker
