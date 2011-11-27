=========================
Defining the Domain Model
=========================

The first change we'll make to our stock paster-generated application will be
to define a :term:`domain model` constructor representing a wiki page.  We'll
do this inside our ``models.py`` file.

The source code for this tutorial stage can be browsed at
`http://github.com/Pylons/pyramid/tree/1.2-branch/docs/tutorials/wiki2/src/models/
<http://github.com/Pylons/pyramid/tree/1.2-branch/docs/tutorials/wiki2/src/models/>`_.

Making Edits to ``models.py``
-----------------------------

.. note::

  There is nothing automagically special about the filename
  ``models.py``.  A project may have many models throughout its
  codebase in arbitrarily-named files.  Files implementing models
  often have ``model`` in their filenames (or they may live in a
  Python subpackage of your application package named ``models``) ,
  but this is only by convention.

The first thing we want to do is remove the stock ``MyModel`` class from the
generated ``models.py`` file.  The ``MyModel`` class is only a sample and
we're not going to use it.

Next, we'll remove the :class:`sqlalchemy.Unicode` import and replace it
with :class:`sqlalchemy.Text`.

.. literalinclude:: src/models/tutorial/models.py
   :lines: 5
   :linenos:
   :language: py

Then, we'll add a ``Page`` class.  Because this is a SQLAlchemy
application, this class should inherit from an instance of
:class:`sqlalchemy.ext.declarative.declarative_base`.  Declarative
SQLAlchemy models are easier to use than directly-mapped ones.

.. literalinclude:: src/models/tutorial/models.py
   :pyobject: Page
   :linenos:
   :language: python

As you can see, our ``Page`` class has a class level attribute
``__tablename__`` which equals the string ``'pages'``.  This means that
SQLAlchemy will store our wiki data in a SQL table named ``pages``.  Our Page
class will also have class-level attributes named ``id``, ``name`` and
``data`` (all instances of :class:`sqlalchemy.Column`).  These will map to
columns in the ``pages`` table.  The ``id`` attribute will be the primary key
in the table.  The ``name`` attribute will be a text attribute, each value of
which needs to be unique within the column.  The ``data`` attribute is a text
attribute that will hold the body of each page.

We'll also remove our ``populate`` function.  We'll inline the populate step
into ``initialize_sql``, changing our ``initialize_sql`` function to add a
FrontPage object to our database at startup time.

.. literalinclude:: src/models/tutorial/models.py
   :pyobject: initialize_sql
   :linenos:
   :language: python

Here, we're using a slightly different binding syntax.  It is otherwise
largely the same as the ``initialize_sql`` in the paster-generated
``models.py``.

Our ``DBSession`` assignment stays the same as the original generated
``models.py``.

Looking at the Result of all Our Edits to ``models.py``
-------------------------------------------------------

The result of all of our edits to ``models.py`` will end up looking
something like this:

.. literalinclude:: src/models/tutorial/models.py
   :linenos:
   :language: python

Viewing the Application in a Browser
------------------------------------

We can't.  At this point, our system is in a "non-runnable" state; we'll need
to change view-related files in the next chapter to be able to start the
application successfully.  If you try to start the application, you'll wind
up with a Python traceback on your console that ends with this exception:

.. code-block:: text

   ImportError: cannot import name MyModel

This will also happen if you attempt to run the tests.
