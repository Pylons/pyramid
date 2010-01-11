==============
Defining Views
==============

A :term:`view callable` in a traversal-based :mod:`repoze.bfg`
applications is typically a simple Python function that accepts two
parameters: :term:`context`, and :term:`request`.  A view callable is
assumed to return a :term:`response` object.

.. note:: A :mod:`repoze.bfg` view can also be defined as callable
   which accepts *one* arguments: a :term:`request`.  You'll see this
   one-argument pattern used in other :mod:`repoze.bfg` tutorials and
   applications.  Either calling convention will work in any
   :mod:`repoze.bfg` application; the calling conventions can be used
   interchangeably as necessary.  In :term:`traversal` based
   applications, such as this tutorial, the context is used frequently
   within the body of a view method, so it makes sense to use the
   two-argument syntax in this application.  However, in :term:`url
   dispatch` based applications, however, the context object is rarely
   used in the view body itself, so within code that uses
   URL-dispatch-only, it's common to define views as callables that
   accept only a request to avoid the visual "noise".

We're going to define several :term:`view callable` functions then
wire them into :mod:`repoze.bfg` using some :term:`view
configuration` via :term:`ZCML`.

The source code for this tutorial stage can be browsed at
`docs.repoze.org <http://docs.repoze.org/bfgwiki-1.2/views>`_.

Adding View Functions
=====================

We're going to add four :term:`view callable` functions to our
``views.py`` module.  One view (named ``view_wiki``) will display the
wiki itself (it will answer on the root URL), another named
``view_page`` will display an individual page, another named
``add_page`` will allow a page to be added, and a final view named
``edit_page`` will allow a page to be edited.

.. note::

  There is nothing automagically special about the filename
  ``views.py``.  A project may have many views throughout its codebase
  in arbitrarily-named files.  Files implementing views often have
  ``view`` in their filenames (or may live in a Python subpackage of
  your application package named ``views``), but this is only by
  convention.

The ``view_wiki`` view function
-------------------------------

The ``view_wiki`` function will be configured to respond as the
default view of a ``Wiki`` model object.  It always redirects to the
``Page`` object named "FrontPage".  It returns an instance of the
:class:`webob.exc.HTTPFound` class (instances of which implement the
WebOb :term:`response` interface), and the
:func:`repoze.bfg.url.model_url` API.
:func:`repoze.bfg.url.model_url` constructs a URL to the ``FrontPage``
page (e.g. ``http://localhost:6543/FrontPage``), and uses it as the
"location" of the HTTPFound response, forming an HTTP redirect.

The ``view_page`` view function
-------------------------------

The ``view_page`` function will be configured to respond as the
default view of a ``Page`` object.  The ``view_page`` function renders
the :term:`ReStructuredText` body of a page (stored as the ``data``
attribute of the context passed to the view; the context will be a
Page object) as HTML.  Then it substitutes an HTML anchor for each
*WikiWord* reference in the rendered HTML using a compiled regular
expression.

The curried function named ``check`` is used as the first argument to
``wikiwords.sub``, indicating that it should be called to provide a
value for each WikiWord match found in the content.  If the wiki (our
page's ``__parent__``) already contains a page with the matched
WikiWord name, the ``check`` function generates a view link to be used
as the substitution value and returns it.  If the wiki does not
already contain a page with with the matched WikiWord name, the
function generates an "add" link as the substitution value and returns
it.

As a result, the ``content`` variable is now a fully formed bit of
HTML containing various view and add links for WikiWords based on the
content of our current page object.

We then generate an edit URL (because it's easier to do here than in
the template), and we wrap up a number of arguments in a dictionary
and return it.

The arguments we wrap into a dictionary include ``page``, ``content``,
and ``edit_url``.  As a result, the *template* associated with this
view callable will be able to use these names to perform various
rendering tasks.  The template associated with this view callable will
be a template which lives in ``templates/view.pt``, which we'll
associate with this view via the :term:`view configuration` which
lives in the ``configure.zcml`` file.

Note the contrast between this view callable and the ``view_wiki``
view callable.  In the ``view_wiki`` view callable, we return a
:term:`response` object.  In the ``view_page`` view callable, we
return a *dictionary*.  It is *always* fine to return a
:term:`response` object from a :mod:`repoze.bfg` view.  Returning a
dictionary is allowed only when there is a :term:`renderer` associated
with the view callable in the view configuration.

The ``add_page`` view function
------------------------------

The ``add_page`` function will be invoked when a user clicks on a
WikiWord which isn't yet represented as a page in the system.  The
``check`` function within the ``view_page`` view generates URLs to
this view.  It also acts as a handler for the form that is generated
when we want to add a page object.  The ``context`` of the
``add_page`` view is always a Wiki object (*not* a Page object).

The request :term:`subpath` in :mod:`repoze.bfg` is the sequence of
names that are found *after* the view name in the URL segments given
in the ``PATH_INFO`` of the WSGI request as the result of
:term:`traversal`.  If our add view is invoked via,
e.g. ``http://localhost:6543/add_page/SomeName``, the :term:`subpath`
will be a tuple: ``('SomeName',)``.

The add view takes the zeroth element of the subpath (the wiki page
name), and aliases it to the name attribute in order to know the name
of the page we're trying to add.

If the view rendering is *not* a result of a form submission (if the
expression ``'form.submitted' in request.params`` is ``False``), the
view renders a template.  To do so, it generates a "save url" which
the template use as the form post URL during rendering.  We're lazy
here, so we're trying to use the same template (``templates/edit.pt``)
for the add view as well as the page edit view.  To do so, we create a
dummy Page object in order to satisfy the edit form's desire to have
*some* page object exposed as ``page``, and we'll render the template
to a response.

If the view rendering *is* a result of a form submission (if the
expression ``'form.submitted' in request.params`` is ``True``), we
scrape the page body from the form data, create a Page object using
the name in the subpath and the page body, and save it into "our
context" (the wiki) using the ``__setitem__`` method of the
context. We then redirect back to the ``view_page`` view (the default
view for a page) for the newly created page.

The ``edit_page`` view function
-------------------------------

The ``edit_page`` function will be invoked when a user clicks the
"Edit this Page" button on the view form.  It renders an edit form but
it also acts as the handler for the form it renders.  The ``context``
of the ``edit_page`` view will *always* be a Page object (never a Wiki
object).

If the view execution is *not* a result of a form submission (if the
expression ``'form.submitted' in request.params`` is ``False``), the
view simply renders the edit form, passing the request, the page
object, and a save_url which will be used as the action of the
generated form.

If the view execution *is* a result of a form submission (if the
expression ``'form.submitted' in request.params`` is ``True``), the
view grabs the ``body`` element of the request parameter and sets it
as the ``data`` attribute of the page context.  It then redirects to
the default view of the context (the page), which will always be the
``view_page`` view.

Viewing the Result of Our Edits to ``views.py``
===============================================

The result of all of our edits to ``views.py`` will leave it looking
like this:

.. literalinclude:: src/views/tutorial/views.py
   :linenos:
   :language: python

Adding Templates
================

Most view callables we've added expected to be rendered via a
:term:`template`.  Each template is a :term:`Chameleon` template.  The
default templating system in :mod:`repoze.bfg` is a variant of
:term:`ZPT` provided by Chameleon.  These templates will live in the
``templates`` directory of our tutorial package.

The ``view.pt`` Template
------------------------

The ``view.pt`` template is used for viewing a single wiki page.  It
is used by the ``view_page`` view function.  It should have a div that
is "structure replaced" with the ``content`` value provided by the
view.  It should also have a link on the rendered page that points at
the "edit" URL (the URL which invokes the ``edit_page`` view for the
page being viewed).

Once we're done with the ``view.pt`` template, it will look a lot like
the below:

.. literalinclude:: src/views/tutorial/templates/view.pt
   :linenos:
   :language: xml

.. note:: The names available for our use in a template are always
   those that are present in the dictionary returned by the view
   callable.  But our templates make use of a ``request`` object that
   none of our tutorial views return in their dictionary.  This value
   appears as if "by magic".  However, ``request`` is one of several
   names that are available "by default" in a template when a template
   renderer is used.  See :ref:`chameleon_template_renderers` for more
   information about other names that are available by default in a
   template when a Chameleon template is used as a renderer.

The ``edit.pt`` Template
------------------------

The ``edit.pt`` template is used for adding and editing a wiki page.
It is used by the ``add_page`` and ``edit_page`` view functions.  It
should display a page containing a form that POSTs back to the
"save_url" argument supplied by the view.  The form should have a
"body" textarea field (the page data), and a submit button that has
the name "form.submitted".  The textarea in the form should be filled
with any existing page data when it is rendered.

Once we're done with the ``edit.pt`` template, it will look a lot like
the below:

.. literalinclude:: src/views/tutorial/templates/edit.pt
   :linenos:
   :language: xml

Static Resources
----------------

Our templates name a single static resource named ``style.css``.  We
need to create this and place it in a file named ``style.css`` within
our package's ``templates/static`` directory.  This file is a little
too long to replicate within the body of this guide, however it is
available `online
<http://docs.repoze.org/bfgwiki-1.2/views/tutorial/templates/static/style.css>`_.

This CSS file will be accessed via
e.g. ``http://localhost:6543/static/style.css`` by virtue of the
``static`` directive we've defined in the ``configure.zcml`` file.
Any number and type of static resources can be placed in this
directory (or subdirectories) and are just referred to by URL within
templates.

Testing the Views
=================

We'll modify our ``tests.py`` file, adding tests for each view
function we added above.  As a result, we'll *delete* the
``ViewTests`` test in the file, and add four other test classes:
``ViewWikiTests``, ``ViewPageTests``, ``AddPageTests``, and
``EditPageTests``.  These test the ``view_wiki``, ``view_page``,
``add_page``, and ``edit_page`` views respectively.  

Once we're done with the ``tests.py`` module, it will look a lot like
the below:

.. literalinclude:: src/views/tutorial/tests.py
   :linenos:
   :language: python

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

The expected result looks something like:

.. code-block:: text

   .........
   ----------------------------------------------------------------------
   Ran 9 tests in 0.203s
   
   OK

Mapping Views to URLs in ``configure.zcml``
===========================================

The ``configure.zcml`` file contains ``view`` declarations which serve
to map URLs (via :term:`traversal`) to view functions.  This is also
known as :term:`view configuration`.  You'll need to add four ``view``
declarations to ``configure.zcml``.

#. Add a declaration which maps the "Wiki" class in our ``models.py``
   file to the view named ``view_wiki`` in our ``views.py`` file with
   no view name.  This is the default view for a Wiki.  It does not
   use a ``renderer`` because the ``view_wiki`` view callable always
   returns a *response* object rather than a dictionary.

#. Add a declaration which maps the "Wiki" class in our ``models.py``
   file to the view named ``add_page`` in our ``views.py`` file with
   the view name ``add_page``.  Associate this view with the
   ``templates/edit.pt`` template file via the ``renderer`` attribute.
   This view will use the :term:`Chameleon` ZPT renderer configured
   with the ``templates/edit.pt`` template to render non-*response*
   return values from the ``add_page`` view.  This is the add view for
   a new Page.

#. Add a declaration which maps the "Page" class in our ``models.py``
   file to the view named ``view_page`` in our ``views.py`` file with
   no view name.  Associate this view with the ``templates/view.pt``
   template file via the ``renderer`` attribute.  This view will use
   the :term:`Chameleon` ZPT renderer configured with the
   ``templates/view.pt`` template to render non-*response* return
   values from the ``view_page`` view.  This is the default view for a
   Page.

#. Add a declaration which maps the "Page" class in our ``models.py``
   file to the view named ``edit_page`` in our ``views.py`` file with
   the view name ``edit_page``.  Associate this view with the
   ``templates/edit.pt`` template file via the ``renderer`` attribute.
   This view will use the :term:`Chameleon` ZPT renderer configured
   with the ``templates/edit.pt`` template to render non-*response*
   return values from the ``edit_page`` view.  This is the edit view
   for a page.

As a result of our edits, the ``configure.zcml`` file should look
something like so:

.. literalinclude:: src/views/tutorial/configure.zcml
   :linenos:
   :language: xml

Examining ``tutorial.ini``
==========================

Let's take a look at our ``tutorial.ini`` file.  The contents of the
file are as follows:

.. literalinclude:: src/models/tutorial.ini
   :linenos:
   :language: ini

The WSGI Pipeline
-----------------

Within ``tutorial.ini``, note the existence of a ``[pipeline:main]``
section which specifies our WSGI pipeline.  This "pipeline" will be
served up as our WSGI application.  As far as the WSGI server is
concerned the pipeline *is* our application.  Simpler configurations
don't use a pipeline: instead they expose a single WSGI application as
"main".  Our setup is more complicated, so we use a pipeline.

``egg:repoze.zodbconn#closer`` is at the "top" of the pipeline.  This
is a piece of middleware which closes the ZODB connection opened by
the PersistentApplicationFinder at the end of the request.

``egg:repoze.tm#tm`` is the second piece of middleware in the
pipeline.  This commits a transaction near the end of the request
unless there's an exception raised.

Adding an Element to the Pipeline
---------------------------------

Let's add a piece of middleware to the WSGI pipeline:
``egg:Paste#evalerror`` middleware which displays debuggable errors in
the browser while you're developing (not recommended for deployment).
Let's insert evalerror into the pipeline right below
"egg:repoze.zodbconn#closer", making our resulting ``tutorial.ini``
file look like so:

.. literalinclude:: src/views/tutorial.ini
   :linenos:
   :language: ini

Viewing the Application in a Browser
====================================

Once we've set up the WSGI pipeline properly, we can finally examine
our application in a browser.  The views we'll try are as follows:

- Visiting ``http://localhost:6543/`` in a browser invokes the
  ``view_wiki`` view.  This always redirects to the ``view_page`` view
  of the FrontPage page object.

- Visiting ``http://localhost:6543/FrontPage/`` in a browser invokes
  the ``view_page`` view of the front page page object.  This is
  because it's the *default view* (a view without a ``name``) for Page
  objects.

- Visiting ``http://localhost:6543/FrontPage/edit_page`` in a browser
  invokes the edit view for the front page object.

- Visiting ``http://localhost:6543/add_page/SomePageName`` in a
  browser invokes the add view for a page.

- To generate an error, visit ``http://localhost:6543/add_page`` which
  will generate an ``IndexError`` for the expression
  ``request.subpath[0]``.  You'll see an interactive traceback
  facility provided by evalerror.





