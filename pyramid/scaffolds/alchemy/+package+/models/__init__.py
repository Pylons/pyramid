def _build_facade():
    """
    Build a facade by scanning the entire package.

    - Scan the entire package to pick up all of the models ensuring that
      they are attached to the metadata.
    - Expose the models conveniently at the top level as a single view of
      the database schema.
    """
    from sqlalchemy.orm import configure_mappers
    from .meta import Base
    from .utils import scan, get_all_subclasses

    # execute all of the modules in the package
    registry = scan(__package__)

    # add all the model classes to the facade
    all_models = get_all_subclasses(Base)
    for m in all_models:
        registry[m.__name__] = m

    # expose the public api for the package
    globals().update(registry)

    # run configure mappers to ensure we avoid any race conditions
    configure_mappers()

_build_facade()
del _build_facade
