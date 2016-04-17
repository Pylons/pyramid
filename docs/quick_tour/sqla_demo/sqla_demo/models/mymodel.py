from .meta import Base
from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
)


# Start Sphinx Include
class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)
    # End Sphinx Include


Index('my_index', MyModel.name, unique=True, mysql_length=255)
