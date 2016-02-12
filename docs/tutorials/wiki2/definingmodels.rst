=========================
Defining the Domain Model
=========================

The first change we'll make to our stock ``pcreate``-generated application will
be to define a wiki page :term:`domain model`.
We'll do this inside our ``mymodel.py`` file.


Edit ``mymodel.py``
-------------------

.. note::

  There is nothing special about the filename ``mymodel.py`` except that it
  is a Python module.  A project may have many models throughout its codebase
  in arbitrarily named modules.  Modules implementing models often have
  ``model`` in their names or they may live in a Python subpackage of your
  application package named ``models`` (as we've done in this tutorial), but
  this is only a convention and not a requirement.

Open the ``tutorial/models/mymodel.py`` file and edit it to look like
the following:

.. literalinclude:: src/models/tutorial/models/mymodel.py
   :linenos:
   :language: py
   :emphasize-lines: 10-12,14-15

The highlighted lines are the ones that need to be changed, as well as
removing lines that reference ``Index``.

The first thing we've done is remove the stock ``MyModel`` class
from the generated ``models.py`` file.  The ``MyModel`` class is only a
sample and we're not going to use it.

Then we added a ``Page`` class.  Because this is a SQLAlchemy application,
this class inherits from an instance of
:func:`sqlalchemy.ext.declarative.declarative_base`.

.. literalinclude:: src/models/tutorial/models/mymodel.py
   :pyobject: Page
   :linenos:
   :language: python

As you can see, our ``Page`` class has a class-level attribute
``__tablename__`` which equals the string ``'pages'``.  This means that
SQLAlchemy will store our wiki data in a SQL table named ``pages``.  Our
``Page`` class will also have class-level attributes named ``id``, ``name``,
and ``data`` (all instances of :class:`sqlalchemy.schema.Column`). These will
map to columns in the ``pages`` table. The ``id`` attribute will be the
primary key in the table. The ``name`` attribute will be a text attribute,
each value of which needs to be unique within the column.  The ``data``
attribute is a text attribute that will hold the body of each page.


Edit ``models/__init__.py``
---------------------------

Since we are using a package for our models, we also need to update our
``__init__.py`` file to ensure that the model is attached to the metadata.

Open the ``tutorial/models/__init__.py`` file and edit it to look like
the following:

.. literalinclude:: src/models/tutorial/models/__init__.py
   :linenos:
   :language: py
   :emphasize-lines: 8

Here we need to align our import with the name of the model ``Page``.


Edit ``scripts/initializedb.py``
--------------------------------

We haven't looked at the details of this file yet, but within the ``scripts``
directory of your ``tutorial`` package is a file named ``initializedb.py``.
Code in this file is executed whenever we run the ``initialize_tutorial_db``
command, as we did in the installation step of this tutorial.

Since we've changed our model, we need to make changes to our
``initializedb.py`` script.  In particular, we'll replace our import of
``MyModel`` with one of ``Page`` and we'll change the very end of the script
to create a ``Page`` rather than a ``MyModel`` and add it to our
``dbsession``.

Open ``tutorial/scripts/initializedb.py`` and edit it to look like
the following:

.. literalinclude:: src/models/tutorial/scripts/initializedb.py
   :linenos:
   :language: python
   :emphasize-lines: 18,44-45

Only the highlighted lines need to be changed.


Installing the project and re-initializing the database
-------------------------------------------------------

Because our model has changed, in order to reinitialize the database, we need
to rerun the ``initialize_tutorial_db`` command to pick up the changes you've
made to both the models.py file and to the initializedb.py file. See
:ref:`initialize_db_wiki2` for instructions.

Success will look something like this::

  2016-02-12 01:06:35,855 INFO  [sqlalchemy.engine.base.Engine:1192][MainThread] SELECT CAST('test plain returns' AS VARCHAR(60)) AS anon_1
  2016-02-12 01:06:35,855 INFO  [sqlalchemy.engine.base.Engine:1193][MainThread] ()
  2016-02-12 01:06:35,855 INFO  [sqlalchemy.engine.base.Engine:1192][MainThread] SELECT CAST('test unicode returns' AS VARCHAR(60)) AS anon_1
  2016-02-12 01:06:35,855 INFO  [sqlalchemy.engine.base.Engine:1193][MainThread] ()
  2016-02-12 01:06:35,856 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] PRAGMA table_info("pages")
  2016-02-12 01:06:35,856 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ()
  2016-02-12 01:06:35,856 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] PRAGMA table_info("users")
  2016-02-12 01:06:35,856 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ()
  2016-02-12 01:06:35,857 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread]
  CREATE TABLE users (
    id INTEGER NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    password_hash TEXT,
    CONSTRAINT pk_users PRIMARY KEY (id),
    CONSTRAINT uq_users_name UNIQUE (name)
  )


  2016-02-12 01:06:35,857 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ()
  2016-02-12 01:06:35,858 INFO  [sqlalchemy.engine.base.Engine:686][MainThread] COMMIT
  2016-02-12 01:06:35,858 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread]
  CREATE TABLE pages (
    id INTEGER NOT NULL,
    name TEXT NOT NULL,
    data INTEGER NOT NULL,
    creator_id INTEGER NOT NULL,
    CONSTRAINT pk_pages PRIMARY KEY (id),
    CONSTRAINT uq_pages_name UNIQUE (name),
    CONSTRAINT fk_pages_creator_id_users FOREIGN KEY(creator_id) REFERENCES users (id)
  )


  2016-02-12 01:06:35,859 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ()
  2016-02-12 01:06:35,859 INFO  [sqlalchemy.engine.base.Engine:686][MainThread] COMMIT
  2016-02-12 01:06:36,383 INFO  [sqlalchemy.engine.base.Engine:646][MainThread] BEGIN (implicit)
  2016-02-12 01:06:36,384 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] INSERT INTO users (name, role, password_hash) VALUES (?, ?, ?)
  2016-02-12 01:06:36,384 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ('editor', 'editor', '$2b$12$bSr5QR3wFs1LAnld7R94e.TXPj7DVoTxu2hA1kY6rm.Q3cAhD.AQO')
  2016-02-12 01:06:36,384 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] INSERT INTO users (name, role, password_hash) VALUES (?, ?, ?)
  2016-02-12 01:06:36,384 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ('basic', 'basic', '$2b$12$.v0BQK2xWEQOnywbX2BFs.qzXo5Qf9oZohGWux/MOSj6Z.pVaY2Z6')
  2016-02-12 01:06:36,385 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] INSERT INTO pages (name, data, creator_id) VALUES (?, ?, ?)
  2016-02-12 01:06:36,385 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ('FrontPage', 'This is the front page', 1)
  2016-02-12 01:06:36,385 INFO  [sqlalchemy.engine.base.Engine:686][MainThread] COMMIT

View the application in a browser
---------------------------------

We can't.  At this point, our system is in a "non-runnable" state; we'll need
to change view-related files in the next chapter to be able to start the
application successfully.  If you try to start the application (See
:ref:`wiki2-start-the-application`), you'll wind
up with a Python traceback on your console that ends with this exception:

.. code-block:: text

   ImportError: cannot import name MyModel

This will also happen if you attempt to run the tests.
