.. _catalog_tutorial:

Using :mod:`repoze.catalog` Within :mod:`repoze.bfg`
====================================================

:mod:`repoze.catalog` is a ZODB-based system that can be used to index
Python objects.  It also offers a query interface for retrieving
previously indexed data.  Those whom are used to Zope's "ZCatalog"
implementation will feel at home using :mod:`repoze.catalog`.

This tutorial assumes that you want a Zope-like setup.  For example,
it assumes you want to use a persistent ZODB object as your
:term:`root` object, and that the :mod:`repoze.catalog` catalog will
be an attribute of this root object.  It is further assumed that you
want the application to be based on :term:`traversal`.

#. Follow the :ref:`zodb_with_zeo` tutorial to get a system set up
   with ZODB and ZEO.  When you are finished, come back here.

#. Install the :mod:`repoze.catalog` software within your application's
   environment:

   .. code-block:: text
   
      $ easy_install repoze.catalog

#. Change your ZODB application's ``models.py`` file to look like the
   below:

   .. code-block:: python
      :linenos:

       from repoze.folder import Folder
       from repoze.catalog.catalog import Catalog
       from repoze.catalog.document import DocumentMap
       from repoze.catalog.indexes.field import CatalogFieldIndex

       def get_title(object, default):
           title = getattr(object, 'title', '')
           if isinstance(title, basestring):
               # lowercase for alphabetic sorting
               title = title.lower()
           return title

       class Document(Folder):
           def __init__(self, title):
               self.title = title
               Folder.__init__(self)

       class Site(Folder):
           def __init__(self):
               self.catalog = Catalog()
               self.catalog.document_map = DocumentMap()
               self.update_indexes()
               Folder.__init__(self)

           def update_indexes(self):
               indexes = {
                   'title': CatalogFieldIndex(get_title),
               }

               catalog = self.catalog

               # add indexes
               for name, index in indexes.iteritems():
                   if name not in catalog:
                       catalog[name] = index

               # remove indexes
               for name in catalog.keys():
                   if name not in indexes:
                       del catalog[name]

       def appmaker(root):
           if not 'site' in root:
               root['site'] = Site()
               transaction.commit()
           return root['site']

#.  We'll demonstrate how you might interact with a catalog from code
    by manipulating the database directly using the ``bfgshell``
    command in a terminal window:

    .. code-block:: text

       [chrism@snowpro sess]$ ../bin/paster --plugin=repoze.bfg bfgshell \
              myapp.ini myapp
       Python 2.5.4 (r254:67916, Sep  4 2009, 02:12:16) 
       [GCC 4.2.1 (Apple Inc. build 5646)] on darwin
       Type "help" for more information. "root" is the BFG app root object.
       >>> from repoze.bfg.traversal import model_path
       >>> from myapp.models import Document
       >>> root['name'] = Document('title')
       >>> doc = root['name']
       >>> docid = root.catalog.document_map.add(model_path(doc))
       >>> root.catalog.index_doc(docid, doc)
       >>> import transaction
       >>> transaction.commit()
       >>> root.catalog.search(title='title')
       (1, IFSet([-787959756]))

As you need them, add other indexes required by your application to
the catalog by modifying the ``update_indexes`` method of the ``Site``
object.  Whenever an index is added or removed, invoke the
``update_indexes`` method of the site (the root object) from a script
or from within a ``bfgshell`` session to update the set of indexes
used by your application.

In :term:`view` code, you should be able to get a hold of the root
object via the :func:`repoze.bfg.traversal.find_root` API.  The
``catalog`` attribute of that root object will represent the catalog
previously added.

Read the :mod:`repoze.catalog` `documentation
<http://docs.repoze.org/catalog>`_ for further information about other
types of indexes to add, using the document map, and how to issue
queries using the catalog query API.

.. note::

   The :mod:`repoze.folder` implementation sends events that can be
   intercepted by a :term:`subscriber` when objects are added and
   removed from a folder.  It is often useful to hook these events for
   the purpose of mutating the catalog when a new documentlike object
   is added or removed.  See the `repoze.folder documentation
   <http://docs.repoze.org/folder>`_ for more information about the
   events it sends.
