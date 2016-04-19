.. _qtut_databases:

==============================
19: Databases Using SQLAlchemy
==============================

Store and retrieve data using the SQLAlchemy ORM atop the SQLite database.


Background
==========

Our Pyramid-based wiki application now needs database-backed storage of pages.
This frequently means an SQL database. The Pyramid community strongly supports
the :ref:`SQLAlchemy <sqla:index_toplevel>` project and its
:ref:`object-relational mapper (ORM) <sqla:ormtutorial_toplevel>` as a
convenient, Pythonic way to interface to databases.

In this step we hook up SQLAlchemy to a SQLite database table, providing
storage and retrieval for the wiki pages in the previous step.

.. note::

    The ``alchemy`` scaffold is really helpful for getting an SQLAlchemy
    project going, including generation of the console script. Since we want to
    see all the decisions, we will forgo convenience in this tutorial, and wire
    it up ourselves.


Objectives
==========

- Store pages in SQLite by using SQLAlchemy models.

- Use SQLAlchemy queries to list/add/view/edit pages.

- Provide a database-initialize command by writing a Pyramid *console script*
  which can be run from the command line.


Steps
=====

#. We are going to use the forms step as our starting point:

   .. code-block:: bash

    $ cd ..; cp -r forms databases; cd databases

#. We need to add some dependencies in ``databases/setup.py`` as well as an
   "entry point" for the command-line script:

   .. literalinclude:: databases/setup.py
    :linenos:

   .. note::

     We aren't yet doing ``$VENV/bin/pip install -e .`` as we will change it
     later.

#. Our configuration file at ``databases/development.ini`` wires together some
   new pieces:

   .. literalinclude:: databases/development.ini
    :language: ini

#. This engine configuration now needs to be read into the application through
   changes in ``databases/tutorial/__init__.py``:

   .. literalinclude:: databases/tutorial/__init__.py
    :linenos:

#. Make a command-line script at ``databases/tutorial/initialize_db.py`` to
   initialize the database:

   .. literalinclude:: databases/tutorial/initialize_db.py
    :linenos:

#. Since ``setup.py`` changed, we now run it:

   .. code-block:: bash

    $ $VENV/bin/pip install -e .

#. The script references some models in ``databases/tutorial/models.py``:

   .. literalinclude:: databases/tutorial/models.py
    :linenos:

#. Let's run this console script, thus producing our database and table:

   .. code-block:: bash

    $ $VENV/bin/initialize_tutorial_db development.ini

    2016-04-16 13:01:33,055 INFO  [sqlalchemy.engine.base.Engine][MainThread] SELECT CAST('test plain returns' AS VARCHAR(60)) AS anon_1
    2016-04-16 13:01:33,055 INFO  [sqlalchemy.engine.base.Engine][MainThread] ()
    2016-04-16 13:01:33,056 INFO  [sqlalchemy.engine.base.Engine][MainThread] SELECT CAST('test unicode returns' AS VARCHAR(60)) AS anon_1
    2016-04-16 13:01:33,056 INFO  [sqlalchemy.engine.base.Engine][MainThread] ()
    2016-04-16 13:01:33,057 INFO  [sqlalchemy.engine.base.Engine][MainThread] PRAGMA table_info("wikipages")
    2016-04-16 13:01:33,057 INFO  [sqlalchemy.engine.base.Engine][MainThread] ()
    2016-04-16 13:01:33,058 INFO  [sqlalchemy.engine.base.Engine][MainThread]
    CREATE TABLE wikipages (
            uid INTEGER NOT NULL,
            title TEXT,
            body TEXT,
            PRIMARY KEY (uid),
            UNIQUE (title)
    )


    2016-04-16 13:01:33,058 INFO  [sqlalchemy.engine.base.Engine][MainThread] ()
    2016-04-16 13:01:33,059 INFO  [sqlalchemy.engine.base.Engine][MainThread] COMMIT
    2016-04-16 13:01:33,062 INFO  [sqlalchemy.engine.base.Engine][MainThread] BEGIN (implicit)
    2016-04-16 13:01:33,062 INFO  [sqlalchemy.engine.base.Engine][MainThread] INSERT INTO wikipages (title, body) VALUES (?, ?)
    2016-04-16 13:01:33,063 INFO  [sqlalchemy.engine.base.Engine][MainThread] ('Root', '<p>Root</p>')
    2016-04-16 13:01:33,063 INFO  [sqlalchemy.engine.base.Engine][MainThread] COMMIT

#. With our data now driven by SQLAlchemy queries, we need to update our
   ``databases/tutorial/views.py``:

   .. literalinclude:: databases/tutorial/views.py
    :linenos:

#. Our tests in ``databases/tutorial/tests.py`` changed to include SQLAlchemy
   bootstrapping:

   .. literalinclude:: databases/tutorial/tests.py
    :linenos:

#. Run the tests in your package using ``py.test``:

   .. code-block:: bash

    $ $VENV/bin/py.test tutorial/tests.py -q
    ..
    2 passed in 1.41 seconds

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ in a browser.


Analysis
========

Let's start with the dependencies. We made the decision to use ``SQLAlchemy``
to talk to our database. We also, though, installed ``pyramid_tm`` and
``zope.sqlalchemy``. Why?

Pyramid has a strong orientation towards support for ``transactions``.
Specifically, you can install a transaction manager into your application
either as middleware or a Pyramid "tween". Then, just before you return the
response, all transaction-aware parts of your application are executed.

This means Pyramid view code usually doesn't manage transactions. If your view
code or a template generates an error, the transaction manager aborts the
transaction. This is a very liberating way to write code.

The ``pyramid_tm`` package provides a "tween" that is configured in the
``development.ini`` configuration file. That installs it. We then need a
package that makes SQLAlchemy, and thus the RDBMS transaction manager,
integrate with the Pyramid transaction manager. That's what ``zope.sqlalchemy``
does.

Where do we point at the location on disk for the SQLite file? In the
configuration file. This lets consumers of our package change the location in a
safe (non-code) way. That is, in configuration. This configuration-oriented
approach isn't required in Pyramid; you can still make such statements in your
``__init__.py`` or some companion module.

The ``initialize_tutorial_db`` is a nice example of framework support. You
point your setup at the location of some ``[console_scripts]``, and these get
generated into your virtual environment's ``bin`` directory. Our console script
follows the pattern of being fed a configuration file with all the
bootstrapping. It then opens SQLAlchemy and creates the root of the wiki, which
also makes the SQLite file. Note the ``with transaction.manager`` part that
puts the work in the scope of a transaction, as we aren't inside a web request
where this is done automatically.

The ``models.py`` does a little bit of extra work to hook up SQLAlchemy into
the Pyramid transaction manager. It then declares the model for a ``Page``.

Our views have changes primarily around replacing our dummy
dictionary-of-dictionaries data with proper database support: list the rows,
add a row, edit a row, and delete a row.


Extra credit
============

#. Why all this code? Why can't I just type two lines and have magic ensue?

#. Give a try at a button that deletes a wiki page.
