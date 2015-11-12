from .meta import Base
from sqlalchemy import (
    Column,
    Integer,
    Text,
)


class Page(Base):
    """ The SQLAlchemy declarative model class for a Page object. """
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    data = Column(Integer)
