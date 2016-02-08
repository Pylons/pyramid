from pyramid.security import (
    Allow,
    Everyone,
)
from sqlalchemy import (
    Column,
    Integer,
    Text,
)

from .meta import Base


class Page(Base):
    """ The SQLAlchemy declarative model class for a Page object. """
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    data = Column(Integer)


class RootFactory(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, 'group:editors', 'edit'),
    ]

    def __init__(self, request):
        pass
