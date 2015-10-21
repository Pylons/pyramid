=========================
Defining the Domain Model
=========================

The first change we'll make to our stock ``pcreate``-generated application will
be to define a :term:`domain model` constructor representing a wiki page.
We'll do this inside our ``models.py`` file.


Edit ``models.py``
------------------

.. note::

  There is nothing special about the filename ``models.py``.  A
  project may have many models throughout its codebase in arbitrarily named
  files.  Files implementing models often have ``model`` in their filenames
  or they may live in a Python subpackage of your application package named
  ``models``, but this is only by convention.

Open ``tutorial/tutorial/models.py`` file and edit it to look like the
following:

.. literalinclude:: src/models/tutorial/models.py
   :linenos:
   :language: py
   :emphasize-lines: 20-22,24,25

The highlighted lines are the ones that need to be changed, as well as
removing lines that reference ``Index``.

The first thing we've done is remove the stock ``MyModel`` class
from the generated ``models.py`` file.  The ``MyModel`` class is only a
sample and we're not going to use it.

Then, we added a ``Page`` class.  Because this is a SQLAlchemy application,
this class inherits from an instance of
:func:`sqlalchemy.ext.declarative.declarative_base`.

.. literalinclude:: src/models/tutorial/models.py
   :pyobject: Page
   :linenos:
   :language: python

As you can see, our ``Page`` class has a class level attribute
``__tablename__`` which equals the string ``'pages'``.  This means that
SQLAlchemy will store our wiki data in a SQL table named ``pages``.  Our
``Page`` class will also have class-level attributes named ``id``, ``name``
and ``data`` (all instances of :class:`sqlalchemy.schema.Column`). These will
map to columns in the ``pages`` table. The ``id`` attribute will be the
primary key in the table. The ``name`` attribute will be a text attribute,
each value of which needs to be unique within the column.  The ``data``
attribute is a text attribute that will hold the body of each page.

Changing ``scripts/initializedb.py``
------------------------------------

We haven't looked at the details of this file yet, but within the ``scripts``
directory of your ``tutorial`` package is a file named ``initializedb.py``.
Code in this file is executed whenever we run the ``initialize_tutorial_db``
command, as we did in the installation step of this tutorial.

Since we've changed our model, we need to make changes to our
``initializedb.py`` script.  In particular, we'll replace our import of
``MyModel`` with one of ``Page`` and we'll change the very end of the script
to create a ``Page`` rather than a ``MyModel`` and add it to our
``DBSession``.

Open ``tutorial/tutorial/scripts/initializedb.py`` and edit it to look like
the following:

.. literalinclude:: src/models/tutorial/scripts/initializedb.py
   :linenos:
   :language: python
   :emphasize-lines: 14,31,36

Only the highlighted lines need to be changed, as well as removing the lines
referencing ``pyramid.scripts.common`` and ``options`` under the ``main``
function.

Installing the project and re-initializing the database
-------------------------------------------------------

Because our model has changed, in order to reinitialize the database, we need
to rerun the ``initialize_tutorial_db`` command to pick up the changes you've
made to both the models.py file and to the initializedb.py file. See
:ref:`initialize_db_wiki2` for instructions.

Success will look something like this::

    2015-05-24 15:34:14,542 INFO  [sqlalchemy.engine.base.Engine:1192][MainThread] SELECT CAST('test plain returns' AS VARCHAR(60)) AS anon_1
    2015-05-24 15:34:14,542 INFO  [sqlalchemy.engine.base.Engine:1193][MainThread] ()
    2015-05-24 15:34:14,543 INFO  [sqlalchemy.engine.base.Engine:1192][MainThread] SELECT CAST('test unicode returns' AS VARCHAR(60)) AS anon_1
    2015-05-24 15:34:14,543 INFO  [sqlalchemy.engine.base.Engine:1193][MainThread] ()
    2015-05-24 15:34:14,543 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] PRAGMA table_info("pages")
    2015-05-24 15:34:14,544 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ()
    2015-05-24 15:34:14,544 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] 
    CREATE TABLE pages (
            id INTEGER NOT NULL, 
            name TEXT, 
            data TEXT, 
            PRIMARY KEY (id), 
            UNIQUE (name)
    )


    2015-05-24 15:34:14,545 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ()
    2015-05-24 15:34:14,546 INFO  [sqlalchemy.engine.base.Engine:686][MainThread] COMMIT
    2015-05-24 15:34:14,548 INFO  [sqlalchemy.engine.base.Engine:646][MainThread] BEGIN (implicit)
    2015-05-24 15:34:14,549 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] INSERT INTO pages (name, data) VALUES (?, ?)
    2015-05-24 15:34:14,549 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ('FrontPage', 'This is the front page')
    2015-05-24 15:34:14,550 INFO  [sqlalchemy.engine.base.Engine:686][MainThread] COMMIT

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
