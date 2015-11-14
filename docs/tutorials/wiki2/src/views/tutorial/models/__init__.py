from sqlalchemy.orm import configure_mappers
# import all models classes here for sqlalchemy mappers
# to pick up
from .mymodel import Page # flake8: noqa

# run configure mappers to ensure we avoid any race conditions
configure_mappers()
