.. _wiki_defining_the_domain_model:

=========================
Defining the Domain Model
=========================

Let's make changes to our stock cookiecutter-generated application.
We will define two :term:`resource` constructors, one representing a wiki page, and another representing the wiki as a mapping of wiki page names to page objects.
We will do this inside our ``models.py`` file.

Because we are using :term:`ZODB` to represent our :term:`resource tree`, each of these resource constructors represents a :term:`domain model` object.
We will call these constructors "model constructors".
Both our ``Page`` and ``Wiki`` constructors will be class objects.
A single instance of the "Wiki" class will serve as a container for "Page" objects, which will be instances of the "Page" class.

.. seealso::

    We will introduce a lot of concepts throughout the remainder of this tutorial.
    See also the chapter :ref:`resources_chapter` for a complete description of resources and the chapter :ref:`traversal_chapter` for the technical details of how traversal works in Pyramid.


Delete the database
-------------------

In the next step, we will remove the ``MyModel`` Python model class from our ``models`` package.
Since this class is referred to within our persistent storage (represented on disk as a file named ``Data.fs``), we will have strange things happen the next time we want to visit the application in a browser.

Remove the ``Data.fs`` from the ``tutorial`` directory before proceeding any further.
It is always fine to do this as long as you don't care about the content of the database.
The database itself will be recreated as necessary.


Edit ``models`` package
-----------------------

.. note::

    There is nothing special about the package name ``models``.
    A project may have many models throughout its codebase in arbitrarily named files and directories.
    Files that implement models often have ``model`` in their names, or they may live in a Python subpackage of your application package named ``models``, but this is only by convention.

Open ``tutorial/models/__init__.py`` file and edit it to look like the following:

.. literalinclude:: src/models/tutorial/models/__init__.py
    :linenos:
    :emphasize-lines: 1,5-11,15-19
    :language: python

The emphasized lines indicate changes, described as follows.

Remove the ``MyModel`` class from the generated ``models/__init__.py`` file.
The ``MyModel`` class is only a sample and we're not going to use it.

Next we add an import at the top for the :class:`persistent.Persistent` class.
We will use this for a new ``Page`` class in a moment.

.. literalinclude:: src/models/tutorial/models/__init__.py
    :lines: 1-2
    :lineno-match:
    :emphasize-lines: 1
    :language: py

Then we add a ``Wiki`` class.

.. literalinclude:: src/models/tutorial/models/__init__.py
    :pyobject: Wiki
    :lineno-match:
    :emphasize-lines: 1-3
    :language: py

We want it to inherit from the :class:`persistent.mapping.PersistentMapping` class because it provides mapping behavior.
It also makes sure that our ``Wiki`` page is stored as a "first-class" persistent object in our ZODB database.

Our ``Wiki`` class should have two attributes set to ``None`` at class scope: ``__parent__`` and ``__name__``.
If a model has a ``__parent__`` attribute of ``None`` in a traversal-based :app:`Pyramid` application, it means that it is the :term:`root` model.
The ``__name__`` of the root model is also always ``None``.

Now we add a ``Page`` class.

.. literalinclude:: src/models/tutorial/models/__init__.py
    :pyobject: Page
    :lineno-match:
    :emphasize-lines: 1-3
    :language: py

This class should inherit from the :class:`persistent.Persistent` class.
We will give it an ``__init__`` method that accepts a single parameter named ``data``.
This parameter will contain the :term:`reStructuredText` body representing the wiki page content.

Note that ``Page`` objects don't have an initial ``__name__`` or ``__parent__`` attribute.
All objects in a traversal graph must have a ``__name__`` and a ``__parent__`` attribute.
We do not specify these here.
Instead both ``__name__`` and ``__parent__`` will be set by a :term:`view` function when a ``Page`` is added to our ``Wiki`` mapping.
We will create this function in the next chapter.

As a last step, edit the ``appmaker`` function.

.. literalinclude:: src/models/tutorial/models/__init__.py
    :pyobject: appmaker
    :lineno-match:
    :emphasize-lines: 3-7
    :language: py

The :term:`root` :term:`resource` of our application is a Wiki instance.

We will also slot a single page object (the front page) into the Wiki within the ``appmaker``.
This will provide :term:`traversal` a :term:`resource tree` to work against when it attempts to resolve URLs to resources.


View the application in a browser
---------------------------------

We cannot.
At this point, our system is in a "non-runnable" state
We will need to change view-related files in the next chapter to be able to start the application successfully.
If you try to start the application (See :ref:`wiki-start-the-application`), you will wind up with a Python traceback on your console that ends with this exception:

.. code-block:: text

    ImportError: cannot import name MyModel

This will also happen if you attempt to run the tests.
