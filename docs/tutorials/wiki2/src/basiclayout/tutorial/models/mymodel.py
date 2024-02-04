from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from .meta import Base


class MyModel(Base):
    __tablename__ = 'models'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]]
    value: Mapped[Optional[int]]


Index('my_index', MyModel.name, unique=True, mysql_length=255)
