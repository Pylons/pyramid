=========================
Defining the Domain Model
=========================

The first change we'll make to our stock ``pcreate``-generated application will
be to define a :term:`domain model` constructor representing a wiki page.
We'll do this inside our ``models.py`` file.


Making Edits to ``models.py``
-----------------------------

.. note::

  There is nothing special about the filename ``models.py``.  A
  project may have many models throughout its codebase in arbitrarily-named
  files.  Files implementing models often have ``model`` in their filenames
  (or they may live in a Python subpackage of your application package named
  ``models``) , but this is only by convention.

Open ``tutorial/tutorial/models.py`` file and edit it to look like the 
following:

.. literalinclude:: src/models/tutorial/models.py
   :linenos:
   :language: py
   :emphasize-lines: 20-22,25

(The highlighted lines are the ones that need to be changed.)

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
``Page`` class will also have class-level attributes named ``id``, ``name`` and
``data`` (all instances of :class:`sqlalchemy.schema.Column`).
These will map to columns in the ``pages`` table.
The ``id`` attribute will be the primary key in the table.
The ``name`` attribute will be a text attribute, each value of
which needs to be unique within the column.  The ``data`` attribute is a text
attribute that will hold the body of each page.

Changing ``scripts/initializedb.py``
------------------------------------

We haven't looked at the details of this file yet, but within the ``scripts``
directory of your ``tutorial`` package is a file named ``initializedb.py``.  Code
in this file is executed whenever we run the ``initialize_tutorial_db`` command
(as we did in the installation step of this tutorial).

Since we've changed our model, we need to make changes to our ``initializedb.py``
script.  In particular, we'll replace our import of ``MyModel`` with one of
``Page`` and we'll change the very end of the script to create a ``Page``
rather than a ``MyModel`` and add it to our ``DBSession``.

Open ``tutorial/tutorial/scripts/initializedb.py`` and edit it to look like the 
following:

.. literalinclude:: src/models/tutorial/scripts/initializedb.py
   :linenos:
   :language: python
   :emphasize-lines: 14,36

(Only the highlighted lines need to be changed.)

Installing the Project and re-initializing the Database
-------------------------------------------------------

Because our model has changed, in order to reinitialize the database, we need
to rerun the ``initialize_tutorial_db`` command to pick up the changes you've made
to both the models.py file and to the initializedb.py file.
See :ref:`initialize_db_wiki2` for instructions.

Success will look something like this::

  2011-11-27 01:22:45,277 INFO  [sqlalchemy.engine.base.Engine][MainThread] 
                                PRAGMA table_info("pages")
  2011-11-27 01:22:45,277 INFO  [sqlalchemy.engine.base.Engine][MainThread] ()
  2011-11-27 01:22:45,277 INFO  [sqlalchemy.engine.base.Engine][MainThread] 
  CREATE TABLE pages (
  	id INTEGER NOT NULL, 
  	name TEXT, 
  	data TEXT, 
  	PRIMARY KEY (id), 
  	UNIQUE (name)
  )


  2011-11-27 01:22:45,278 INFO  [sqlalchemy.engine.base.Engine][MainThread] ()
  2011-11-27 01:22:45,397 INFO  [sqlalchemy.engine.base.Engine][MainThread] 
                                COMMIT
  2011-11-27 01:22:45,400 INFO  [sqlalchemy.engine.base.Engine][MainThread] 
                                BEGIN (implicit)
  2011-11-27 01:22:45,401 INFO  [sqlalchemy.engine.base.Engine][MainThread] 
                                INSERT INTO pages (name, data) VALUES (?, ?)
  2011-11-27 01:22:45,401 INFO  [sqlalchemy.engine.base.Engine][MainThread] 
                                ('FrontPage', 'This is the front page')
  2011-11-27 01:22:45,402 INFO  [sqlalchemy.engine.base.Engine][MainThread] 
                                COMMIT

Viewing the Application in a Browser
------------------------------------

We can't.  At this point, our system is in a "non-runnable" state; we'll need
to change view-related files in the next chapter to be able to start the
application successfully.  If you try to start the application (See
:ref:`wiki2-start-the-application`), you'll wind
up with a Python traceback on your console that ends with this exception:

.. code-block:: text

   ImportError: cannot import name MyModel

This will also happen if you attempt to run the tests.
