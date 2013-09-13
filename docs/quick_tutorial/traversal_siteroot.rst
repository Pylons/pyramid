===================================
22: Basic Traversal With Site Roots
===================================

Model websites as a hierarchy of objects with operations.

Background
==========

Web applications have URLs which locate data and make operations on that
data. Pyramid supports two ways of mapping URLs into Python operations:

- The more-traditional approach of *URL dispatch* aka *routes*

- The more object-oriented approach of
  :ref:`traversal <pyramid:traversal_chapter>` popularized by Zope

In this section we will introduce traversal bit-by-bit. Along the way,
we will try to show how easy and Pythonic it is to think in terms of
traversal.

Remember...traversal is easy, powerful, and useful.

With traversal, you think of your website as a tree of Python objects,
just like a dictionary of dictionaries. For example::

  http://example.com/company1/aFolder/subFolder/search?term=hello

...is nothing more than::

  >>> root['aFolder']['subFolder'].search(x=1)

To remove some mystery about traversal, we start with the smallest
possible step: an object at the top of our URL space. This object acts
as the "root" and has a view which shows some data on that object.

Objectives
==========

- Make a factory for the root object

- Pass it to the configurator

- Have a view which displays an attribute on that object

Steps
=====

#. We are going to use the view classes step as our starting point:

   .. code-block:: bash

    (env27)$ cd ..; cp -r view_classes traversal_siteroot; cd traversal_siteroot
    (env27)$ python setup.py develop

#. In ``traversal_siteroot/tutorial/__init__.py`` make a root factory
   and remove the ``add_route`` statements from the
   :term:`configurator`:

   .. literalinclude:: traversal_siteroot/tutorial/__init__.py
      :linenos:

#. We have ``traversal_siteroot/tutorial/resources.py`` with a class for
   the root of our site and a factory that returns it:

   .. literalinclude:: traversal_siteroot/tutorial/resources.py
      :linenos:

#. Our views in ``traversal_siteroot/tutorial/views.py`` are now
   quite different...no ``route_name``:

   .. literalinclude:: traversal_siteroot/tutorial/views.py
      :linenos:

#. A template in ``traversal_siteroot/tutorial/home.pt``:

   .. literalinclude:: traversal_siteroot/tutorial/home.pt
    :language: html
    :linenos:


#. Simplified tests in ``traversal_siteroot/tutorial/tests.py``:

   .. literalinclude:: traversal_siteroot/tutorial/tests.py
      :linenos:

#. Now run the tests:

   .. code-block:: bash


    (env27)$ nosetests tutorial
    .
    ----------------------------------------------------------------------
    Ran 4 tests in 0.141s

    OK

#. Run your Pyramid application with:

   .. code-block:: bash

    (env27)$ pserve development.ini --reload

#. Open ``http://localhost:6543/`` in your browser.

Analysis
========

Our ``__init__.py`` has a small but important change: we create the
configuration with a *root factory*. Our root factory is a simple
function that performs some work and returns the root object in the
:ref:`resource tree <pyramid:the_resource_tree>`.

In the resource tree, Pyramid can match URLs to objects and subobjects,
finishing in a view as the operation to perform. Traversing through
containers is done using Python's normal ``__getitem__`` dictionary
protocol.

Pyramid provides services beyond simple Python dictionaries. These
:ref:`location <pyramid:location_aware>`
services need a little bit more protocol than just ``__getitem__``.
Namely, objects need to provide an attribute/callable for
``__name__`` and ``__parent__``.

In this step, our tree has one object: the root. It is an instance of
``SiteFolder``. Since it is the root, it doesn't need a ``__name__``
(aka ``id``) nor a ``__parent__`` (reference to the container an object
is in.)

Our ``home`` view is passed, by Pyramid, the instance of this folder as
``context``. The view can then grab attributes and other data from the
object that is the focus of the URL.

Now, on to the most visible part: no more routes! Previously we wrote
URL "replacement patterns" which mapped to a route. The route extracted
data from the patterns and made this data available to views that were
mapped to that route.

Instead, segments in URLs become object identifiers in Python.

Extra Credit
============

#. Is the root factory called once on startup, or on every request? Do
   a small change that answers this. What is the impact of the answer
   on this?

.. seealso::
   :ref:`pyramid:traversal_chapter`,
   :ref:`pyramid:location_aware`,
   :ref:`pyramid:the_resource_tree`,
   :ref:`much_ado_about_traversal_chapter`
