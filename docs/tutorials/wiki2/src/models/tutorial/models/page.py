import bcrypt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .meta import Base


class Page(Base):
    """ The SQLAlchemy declarative model class for a Page object. """
    __tablename__ = 'pages'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    data: Mapped[str]

    creator_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    creator: Mapped['User'] = relationship('User', back_populates='created_pages')
