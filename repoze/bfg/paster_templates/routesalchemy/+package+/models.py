import transaction

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Unicode

from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import mapper

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

metadata = MetaData()

def get_root_model(**kw):
    session = DBSession()
    root = session.query(Model).filter(Model.name==u'root').first()
    return root

class Model(object):
    def __init__(self, name=''):
        self.name = name

models_table = Table(
    'models',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Unicode(255), unique=True),
    )

models_mapper = mapper(Model, models_table)

def populate():
    session = DBSession()
    model = Model(name=u'root')
    session.add(model)
    session.flush()
    transaction.commit()
    
def initialize_sql(db_string, echo=False):
    engine = create_engine(db_string, echo=echo)
    DBSession.configure(bind=engine)
    metadata.bind = engine
    metadata.create_all(engine)
    try:
        populate()
    except IntegrityError:
        pass
