=========================
Defining the Domain Model
=========================

The first change we'll make to our stock paster-generated application will be
to define two :term:`resource` constructors, one representing a wiki page,
and another representing the wiki as a mapping of wiki page names to page
objects.  We'll do this inside our ``models.py`` file.

Because we're using :term:`ZODB` to represent our
:term:`resource tree`, each of these resource constructors represents a
:term:`domain model` object, so we'll call these constructors "model
constructors". Both our Page and Wiki constructors will be class objects.  A
single instance of the "Wiki" class will serve as a container for "Page"
objects, which will be instances of the "Page" class.

The source code for this tutorial stage can be browsed via
`http://github.com/Pylons/pyramid/tree/1.2-branch/docs/tutorials/wiki/src/models/
<http://github.com/Pylons/pyramid/tree/1.2-branch/docs/tutorials/wiki/src/models/>`_.

Deleting the Database
---------------------

In the next step, we're going to remove the ``MyModel`` Python model
class from our ``models.py`` file.  Since this class is referred to within
our persistent storage (represented on disk as a file named ``Data.fs``),
we'll have strange things happen the next time we want to visit the
application in a browser.  Remove the ``Data.fs`` from the ``tutorial``
directory before proceeding any further.  It's always fine to do this as long
as you don't care about the content of the database; the database itself will
be recreated as necessary.

Making Edits to ``models.py``
-----------------------------

.. note::

  There is nothing automagically special about the filename ``models.py``.  A
  project may have many models throughout its codebase in arbitrarily-named
  files.  Files implementing models often have ``model`` in their filenames,
  or they may live in a Python subpackage of your application package named
  ``models``, but this is only by convention.

The first thing we want to do is remove the ``MyModel`` class from the
generated ``models.py`` file.  The ``MyModel`` class is only a sample and
we're not going to use it.

Then, we'll add a ``Wiki`` class.  We want it to inherit from the
:class:`persistent.mapping.PersistentMapping` class because it provides
mapping behavior, and it makes sure that our Wiki page is stored as a
"first-class" persistent object in our ZODB database.

Our ``Wiki`` class should have two attributes set to ``None`` at
class scope: ``__parent__`` and ``__name__``.  If a model has a
``__parent__`` attribute of ``None`` in a traversal-based :app:`Pyramid`
application, it means that it's the :term:`root` model.  The ``__name__``
of the root model is also always ``None``.

Then we'll add a ``Page`` class.  This class should inherit from the
:class:`persistent.Persistent` class.  We'll also give it an ``__init__``
method that accepts a single parameter named ``data``.  This parameter will
contain the :term:`ReStructuredText` body representing the wiki page content.
Note that ``Page`` objects don't have an initial ``__name__`` or
``__parent__`` attribute.  All objects in a traversal graph must have a
``__name__`` and a ``__parent__`` attribute.  We don't specify these here
because both ``__name__`` and ``__parent__`` will be set by by a :term:`view`
function when a Page is added to our Wiki mapping.

As a last step, we want to change the ``appmaker`` function in our
``models.py`` file so that the :term:`root` :term:`resource` of our
application is a Wiki instance.  We'll also slot a single page object (the
front page) into the Wiki within the ``appmaker``.  This will provide
:term:`traversal` a :term:`resource tree` to work against when it attempts to
resolve URLs to resources.

Looking at the Result of Our Edits to ``models.py``
---------------------------------------------------

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
