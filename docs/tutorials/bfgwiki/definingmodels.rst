===============
Defining Models
===============

The first change we'll make to our bone-stock ``paster`` -generated
application will be to define a number of :term:`model` constructors.
For this application, which will be a Wiki, we will need two kinds of
model constructors: a "Wiki" model constructor, and a "Page" model
constructor.  Both our Page and Wiki constructors will be class
objects.  A single instance of the "Wiki" class will serve as a
container for "Page" objects, which will be instances of the "Page"
class.

The source code for this tutorial stage can be browsed at
`docs.repoze.org <http://docs.repoze.org/bfgwiki-1.2/models>`_.

Deleting the Database
---------------------

We're going to remove the ``MyModel`` Python model class from our
``models.py`` file.  Since this class is referred to within our
persistent storage (represented on disk as a file named ``Data.fs``),
we'll have strange things happen the next time we want to visit the
application in a browser.  Remove the ``Data.fs`` from the
``tutorial`` directory before proceeding any further.  It's always
fine to do this as long as you don't care about the content of the
database; the database itself will be recreated as necessary.

Adding Model Classes
--------------------

The next thing we want to do is remove the ``MyModel`` class from the
generated ``models.py`` file.  The ``MyModel`` class is only a sample
and we're not going to use it.

.. note::

  There is nothing automagically special about the filename
  ``models.py``.  A project may have many models throughout its
  codebase in arbitrarily-named files.  Files implementing models
  often have ``model`` in their filenames (or they may live in a
  Python subpackage of your application package named ``models``) ,
  but this is only by convention.

Then, we'll add a ``Wiki`` class.  Because this is a ZODB application,
this class should inherit from
:class:`persistent.mapping.PersistentMapping`.  We want it to inherit
from the :class:`persistent.mapping.PersistentMapping` class because
our Wiki class will be a mapping of wiki page names to ``Page``
objects.  The :class:`persistent.mapping.PersistentMapping` class
provides our class with mapping behavior, and makes sure that our Wiki
page is stored as a "first-class" persistent object in our ZODB
database.

Our ``Wiki`` class should also have a ``__name__`` attribute set to
``None`` at class scope, and should have a ``__parent__`` attribute
set to ``None`` at class scope as well.  If a model has a
``__parent__`` attribute of ``None`` in a traversal-based
:mod:`repoze.bfg` application, it means that it's the :term:`root`
model.  The ``__name__`` of the root model is also always ``None``.

Then we'll add a ``Page`` class.  This class should inherit from the
:class:`persistent.Persistent` class.  We'll also give it an
``__init__`` method that accepts a single parameter named ``data``.
This parameter will contain the :term:`ReStructuredText` body
representing the wiki page content.  Note that ``Page`` objects don't
have an initial ``__name__`` or ``__parent__`` attribute.  All objects
in a traversal graph must have a ``__name__`` and a ``__parent__``
attribute.  We don't specify these here because both ``__name__`` and
``__parent__`` will be set by by a :term:`view` function when a Page
is added to our Wiki mapping.

Add an Appmaker
---------------

We're using a mini-framework callable named
``PersistentApplicationFinder`` in our application (see ``run.py``).
A ``PersistentApplicationFinder`` accepts a ZODB URL as well as an
"appmaker" callback.  This callback typically lives in the
``models.py`` file.

We want to change the appmaker function in our ``models.py`` file so
that our application root is a Wiki instance, and we'll also slot a
single page object (the front page) into the wiki.

Looking at the Result of Our Edits to ``models.py``
---------------------------------------------------

The result of all of our edits to ``models.py`` will end up looking
something like this:

.. literalinclude:: src/models/tutorial/models.py
   :linenos:
   :language: python

Testing the Models
------------------

To make sure the code we just wrote works, we write tests for the
model classes and the appmaker.  Changing ``tests.py``, we'll write a
separate test class for each model class, and we'll write a test class
for the ``appmaker``.

To do so, we'll retain the ``tutorial.tests.ViewTests`` class provided
as a result of the ``bfg_zodb`` project generator.  We'll add three
test classes: one for the ``Page`` model named ``PageModelTests``, one
for the ``Wiki`` model named ``WikiModelTests``, and one for the
appmaker named ``AppmakerTests``.

When we're done changing ``tests.py``, it will look something like so:

.. literalinclude:: src/models/tutorial/tests.py
   :linenos:
   :language: python

Running the Tests
-----------------

We can run these tests by using ``setup.py test`` in the same way we
did in :ref:`running_tests`.  Assuming our shell's current working
directory is the "tutorial" distribution directory:

On UNIX:

.. code-block:: text

  $ ../bin/python setup.py test -q

On Windows:

.. code-block::  text

   c:\bigfntut\tutorial> ..\Scripts\python setup.py test -q

The expected output is something like this:

.. code-block:: text

  .....
  ----------------------------------------------------------------------
  Ran 5 tests in 0.008s

  OK

Declaring Dependencies in Our ``setup.py`` File
-----------------------------------------------

Our application depends on packages which are not dependencies of the
original "tutorial" application as it was generated by the ``paster
create`` command.  We'll add these dependencies to our ``tutorial``
package's ``setup.py`` file by assigning these dependencies to both
the ``install_requires`` and the ``tests_require`` parameters to the
``setup`` function.  In particular, we require the ``docutils``
package.

Our resulting ``setup.py`` should look like so:

.. literalinclude:: src/models/setup.py
   :linenos:
   :language: python

