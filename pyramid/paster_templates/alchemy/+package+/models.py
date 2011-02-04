import transaction

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import Column

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value

class MyApp(object):
    __name__ = None
    __parent__ = None

    def __getitem__(self, key):
        session= DBSession()
        try:
            id = int(key)
        except (ValueError, TypeError):
            raise KeyError(key)

        query = session.query(MyModel).filter_by(id=id)

        try:
            item = query.one()
            item.__parent__ = self
            item.__name__ = key
            return item
        except NoResultFound:
            raise KeyError(key)

    def get(self, key, default=None):
        try:
            item = self.__getitem__(key)
        except KeyError:
            item = default
        return item

    def __iter__(self):
        session= DBSession()
        query = session.query(MyModel)
        return iter(query)

root = MyApp()

def default_get_root(request):
    return root

def populate():
    session = DBSession()
    model = MyModel(name=u'test name', value=55)
    session.add(model)
    session.flush()
    transaction.commit()

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    try:
        populate()
    except IntegrityError:
        DBSession.rollback()

def appmaker(engine):
    initialize_sql(engine)
    return default_get_root
