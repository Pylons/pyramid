=======================
24: Type-Specific Views
=======================

Type-specific views by registering a view against a class.

Background
==========

In :doc:`../traversal_hierarchy` we had 3 "content types" (SiteFolder,
Folder, and Document.) All, however, used the same view and template.

Pyramid traversal though lets you bind a view to a particular content
type. This ability to make your URLs "object oriented" is one of the
distinguishing features of traversal and makes crafting a URL space
more natural. Once Pyramid finds the :term:`context` object in the URL
path, developers have a lot of flexibility in view predicates.

Objectives
==========

- ``@view_config`` which uses the ``context`` attribute to associate a
  particular view with ``context`` instances of a particular class

- Views and templates which are unique to a particular class (aka type)

- Patterns in test writing to handle multiple kinds of contexts

Steps
=====

#. We are going to use the previous step as our starting point and add a
   ``tutorial/templates`` subdirectory:

   .. code-block:: bash

    (env27)$ cd ..; cp -r traversal_hierarchy traversal_typeviews; cd traversal_typeviews
    (env27)$ python setup.py develop
    (env27)$ mkdir traversal_typeviews/tutorial/templates

#. Our views in ``traversal_typeviews/tutorial/views.py`` need
   type-specific registrations:

   .. literalinclude:: traversal_typeviews/tutorial/views.py
      :linenos:

#. Copy the following into
   ``traversal_typeviews/tutorial/templates/document.pt``:

   .. literalinclude:: traversal_typeviews/tutorial/templates/document.pt
      :language: html
      :linenos:

#. Copy the following into
   ``traversal_typeviews/tutorial/templates/folder.pt``:

   .. literalinclude:: traversal_typeviews/tutorial/templates/folder.pt
      :language: html
      :linenos:

#. Copy the following into
   ``traversal_typeviews/tutorial/templates/site.pt``:

   .. literalinclude:: traversal_typeviews/tutorial/templates/site.pt
      :language: html
      :linenos:

#. More tests needed in ``traversal_typeviews/tutorial/tests.py``:

   .. literalinclude:: traversal_typeviews/tutorial/tests.py
      :linenos:

#. ``$ nosetests`` should report running 4 tests.

#. Run your Pyramid application with:

   .. code-block:: bash

    (env27)$ pserve development.ini --reload

#. Open ``http://localhost:6543/`` in your browser.

Analysis
========

We made a ``templates`` subdirectory, just for the purposes of
organization and to match a common project layout style.

For the most significant change, our ``@view_config`` now matches on a
``context`` view predicate. We can say "use this view for when looking
at *this* kind of thing." The concept of a route as an intermediary
step between URLs and views has been eliminated.

Extra Credit
============

#. Should you calculate the list of children on the Python side,
   or access it on the template side by operating on the context?

#. What if you need different traversal policies?

#. In Zope, *interfaces* were used to register a view. How do you do
   register a Pyramid view against instances that support a particular
   interface? When should you?

#. Let's say you need a more-specific view to be used on a particular
   instance of a class, letting a more-general view cover all other
   instances. What are some of your options?

.. seealso::
   :ref:`Traversal Details <pyramid:traversal_chapter>`
   :ref:`Hybrid Traversal and URL Dispatch <pyramid:hybrid_chapter>`