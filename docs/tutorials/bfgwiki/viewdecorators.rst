==========================================================
Using View Decorators Rather than ZCML ``view`` directives
==========================================================

So far we've been using :term:`ZCML` to map model types to views.
It's often easier to use the ``bfg_view`` view decorator to do this
mapping.  Using view decorators provides better locality of reference
for the mapping, because you can see which model types and view names
the view will serve right next to the view function itself.  In this
mode, however, you lose the ability for some views to be overridden
"from the outside" (by someone using your application as a framework,
as explained in the :ref:`extending_chapter`).  Since this application
is not meant to be a framework, it makes sense for us to switch over
to using view decorators.

Adding View Decorators
======================

We're going to import the :class:`repoze.bfg.view.bfg_view` callable.
This callable can be used as a function, class, or method decorator.
We'll use it to decorate our ``view_wiki``, ``view_page``,
``add_page`` and ``edit_page`` view functions.

The :class:`repoze.bfg.view.bfg_view` callable accepts a number of
arguments:

``context``

  The model type which the :term:`context` of our view will be, in our
  case a class.

``name``

  The name of the view.

``renderer``

  The renderer (usually a *template name*) that will be used when the
  view returns a non-:term:`response` object.

There are other arguments which this callable accepts, but these are
the ones we're going to use.

The ``view_wiki`` view function
-------------------------------

The decorator above the ``view_wiki`` function will be:

.. ignore-next-block
.. code-block:: python
   :linenos:

   @bfg_view(context=Wiki)

This indicates that the view is for the Wiki class and has the *empty*
view_name (indicating the :term:`default view` for the Wiki class).
After injecting this decorator, we can now *remove* the following from
our ``configure.zcml`` file:

.. code-block:: xml
   :linenos:

   <view
      context=".models.Wiki"
      view=".views.view_wiki"
      />

Our new decorator takes its place.

The ``view_page`` view function
-------------------------------

The decorator above the ``view_page`` function will be:

.. ignore-next-block
.. code-block:: python
   :linenos:

   @bfg_view(context=Page, renderer='templates/view.pt')

This indicates that the view is for the Page class and has the *empty*
view_name (indicating the :term:`default view` for the Page class).
After injecting this decorator, we can now *remove* the following from
our ``configure.zcml`` file:

.. code-block:: xml
   :linenos:

   <view
      context=".models.Page"
      view=".views.view_page"
      renderer="templates/view.pt"
      />

Our new decorator takes its place.

The ``add_page`` view function
------------------------------

The decorator above the ``add_page`` function will be:

.. ignore-next-block
.. code-block:: python
   :linenos:

   @bfg_view(context=Wiki, name='add_page', renderer='templates/edit.pt')

This indicates that the view is for the Wiki class and has the
``add_page`` view_name.  After injecting this decorator, we can now
*remove* the following from our ``configure.zcml`` file:

.. code-block:: xml
   :linenos:

   <view
      context=".models.Wiki"
      name="add_page"
      view=".views.add_page"
      renderer="templates/edit.pt"
      />

Our new decorator takes its place.

The ``edit_page`` view function
-------------------------------

The decorator above the ``edit_page`` function will be:

.. ignore-next-block
.. code-block:: python
   :linenos:

   @bfg_view(context=Page, name='edit_page', renderer='templates/edit.pt')

This indicates that the view is for the Page class and has the
``edit_page`` view_name.  After injecting this decorator, we can now
*remove* the following from our ``configure.zcml`` file:

.. code-block:: xml
   :linenos:

   <view
      context=".models.Page"
      name="edit_page"
      view=".views.edit_page"
      renderer="templates/edit.pt"
      />

Our new decorator takes its place.

Adding a Scan Directive
=======================

In order for our decorators to be recognized, we must add a bit of
boilerplate to our ``configure.zcml`` file which tells
:mod:`repoze.bfg` to kick off a :term:`scan` at startup time.  Add the
following tag anywhere beneath the ``<include
package="repoze.bfg.includes">`` tag but before the ending
``</configure>`` tag within ``configure.zcml``:

.. code-block:: xml
   :linenos:

   <scan package="."/>

Viewing the Result of Our Edits to ``views.py``
===============================================

The result of all of our edits to ``views.py`` will leave it looking
like this:

.. literalinclude:: src/viewdecorators/tutorial/views.py
   :linenos:
   :language: python

Viewing the Results of Our Edits to ``configure.zcml``
======================================================

The result of all of our edits to ``configure.zcml`` will leave it
looking like this:

.. literalinclude:: src/viewdecorators/tutorial/configure.zcml
   :linenos:
   :language: xml

Running the Tests
=================

We can run these tests by using ``setup.py test`` in the same way we
did in :ref:`running_tests`.  Assuming our shell's current working
directory is the "tutorial" distribution directory:

On UNIX:

.. code-block:: text

   $ ../bin/python setup.py test -q

On Windows:

.. code-block:: text

   c:\bigfntut\tutorial> ..\Scripts\python setup.py test -q

Hopefully nothing will have changed.  The expected result looks
something like:

.. code-block:: text

   .........
   ----------------------------------------------------------------------
   Ran 9 tests in 0.203s
   
   OK

Viewing the Application in a Browser
====================================

Once we've set up the WSGI pipeline properly, we can finally examine
our application in a browser.  We'll make sure that we didn't break
any views by trying each of them.

- Visiting ``http://localhost:6543/`` in a
  browser invokes the ``view_wiki`` view.  This always redirects to
  the ``view_page`` view of the FrontPage page object.

- Visiting ``http://localhost:6543/FrontPage/`` in a browser invokes
  the ``view_page`` view of the front page page object.  This is
  because it's the *default view* (a view without a ``name``) for Page
  objects.

- Visiting ``http://localhost:6543/FrontPage/edit_page`` in a browser
  invokes the edit view for the front page object.

- Visiting ``http://localhost:6543/add_page/SomePageName`` in a
  browser invokes the add view for a page.



