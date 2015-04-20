from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    )

from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import zope.sqlalchemy


Base = declarative_base()


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
    zope.sqlalchemy.register(dbsession, transaction_manager=transaction_manager)
    return dbsession


def get_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)


def get_dbmaker(engine):
    dbmaker = sessionmaker()
    dbmaker.configure(bind=engine)
    return dbmaker


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)


Index('my_index', MyModel.name, unique=True, mysql_length=255)
