==================================
26: Storing Resources In Databases
==================================

Store and retrieve resource tree containers and items in a database.

Background
==========

We now have a resource tree that can go infinitely deep,
adding items and subcontainers along the way. We obviously need a
database, one that can support hierarchies. ZODB is a transaction-based
Python database that supports transparent persistence. We will modify
our application to work with the ZODB.

Along the way we will add the use of ``pyramid_tm``,
a system for adding transaction awareness to our code. With this we
don't need to manually manage our transaction begin/commit cycles in
our application code. Instead, transactions are setup transparently on
request/response boundaries, outside our application code.

Objectives
==========

- Create a CRUD app that adds records to persistent storage.

- Setup ``pyramid_tm`` and ``pyramid_zodbconn``.

- Make our "content" classes inherit from ``Persistent``.

- Set up a database connection string in our application.

- Set up a root factory that serves the root from ZODB rather than from
  memory.

Steps
=====

#. We are going to use the previous step as our starting point:

   .. code-block:: bash

    (env27)$ cd ..; cp -r traversal_addcontent traversal_zodb; cd traversal_zodb

#. Introduce some new dependencies in  ``traversal_zodb/setup.py``:

   .. literalinclude:: traversal_zodb/setup.py
      :linenos:

#. We can now install our project:

   .. code-block:: bash

    (env27)$ python setup.py develop

#. Modify our ``traversal_zodb/development.ini`` to include some
   configuration and give database connection parameters:

   .. literalinclude:: traversal_zodb/development.ini
      :language: ini
      :linenos:

#. Our startup code in ``traversal_zodb/tutorial/__init__.py`` gets
   some bootstrapping changes:

   .. literalinclude:: traversal_zodb/tutorial/__init__.py
      :linenos:

#. Our views in ``traversal_zodb/tutorial/views.py`` change to create
   persistent objects:

   .. literalinclude:: traversal_zodb/tutorial/views.py
      :linenos:

#. As do our resources in ``traversal_zodb/tutorial/resources.py``:

   .. literalinclude:: traversal_zodb/tutorial/resources.py
      :linenos:

#. Run your Pyramid application with:

   .. code-block:: bash

    (env27)$ pserve development.ini --reload

#. Open ``http://localhost:6543/`` in your browser.

Analysis
========

We install ``pyramid_zodbconn`` to handle database connections to ZODB. This
pulls the ZODB3 package as well.

To enable ``pyramid_zodbconn``:

- We activate the package configuration using ``pyramid.includes``.

- We define a ``zodbconn.uri`` setting with the path to the Data.fs file.

In the root factory, instead of using our old root object, we now get a
connection to the ZODB and create the object using that.

Our resources need a couple of small changes. Folders now inherit from
persistent.PersistentMapping and document from persistent.Persistent. Note
that Folder now needs to call super() on the __init__ method, or the
mapping will not initialize properly.

On the bootstrap, note the use of transaction.commit() to commit the
change. This is because, on first startup, we want a root resource in
place before continuing.

Extra Credit
============

#. Create a view that deletes a document.

#. Remove the configuration line that includes ``pyramid_tm``.  What
   happens when you restart the application?  Are your changes
   persisted across restarts?

#. What happens if you delete the files named ``Data.fs*``?
