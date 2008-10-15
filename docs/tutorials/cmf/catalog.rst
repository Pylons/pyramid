.. _catalog_chapter:

=======
Catalog
=======

The main feature of the CMF catalog is that it filters search results
from the Zope 2 "catalog" based on the requesting user's ability to
view a particular cataloged object.

:mod:`repoze.bfg` itself has no cataloging facility, but an addon
package named :term:`repoze.catalog` offers similar functionality.

Creating an Allowed Index
-------------------------

In CMF, a catalog index named ``getAllowedRolesAndUsers`` along with
application indexing code allows for filtered search results.  It's
reasonably easy to reproduce this pattern using some custom code.

Creating The ``allowed`` Index
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's some code which creates an ``allowed`` index for use in a
``repoze.catalog`` catalog::

    from repoze.bfg.security import principals_allowed_by_permission
    from repoze.catalog.indexes.keyword import CatalogKeywordIndex
    from repoze.catalog.catalog import Catalog

    class Allowed:
        def __init__(self, permission):
            self.permission = permission

        def __call__(self, context, default):
            principals = principals_allowed_by_permission(context, 
                                                          self.permission)
            return principals

    def make_allowed_index(permission='View'):
        index = CatalogKeywordIndex(Allowed(permission))
        return index

    index = make_allowed_index()
    catalog = Catalog()
    catalog['allowed'] = index

When you index an item, the allowed index will be populated with all
the principal ids which have the 'View' permission.

Using the ``allowed`` Index
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's how you might use the ``allowed`` index within a query::

  from repoze.bfg.security import effective_principals
  principals = effective_principals(request)
  catalog.searchResults(allowed={'operator':'or', 'query':principals})

The above query will return all document ids that the current user has
the 'View' permission against.  Add other indexes to the query to get
a useful result.

See the `repoze.catalog package
<http://svn.repoze.org/repoze.catalog/trunk>`_ for more information.








