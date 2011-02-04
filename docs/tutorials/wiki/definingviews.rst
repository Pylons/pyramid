==============
Defining Views
==============

Conventionally, :term:`view callable` objects are defined within a
``views.py`` module in an :app:`Pyramid` application.  There is nothing
automagically special about the filename ``views.py``.  Files implementing
views often have ``view`` in their filenames (or may live in a Python
subpackage of your application package named ``views``), but this is only by
convention.  A project may have many views throughout its codebase in
arbitrarily-named files.  In this application, however, we'll be continuing
to use the ``views.py`` module, because there's no reason to break
convention.

A :term:`view callable` in a :app:`Pyramid` application is typically a simple
Python function that accepts a single parameter: :term:`request`.  A view
callable is assumed to return a :term:`response` object.

However, a :app:`Pyramid` view can also be defined as callable which accepts
*two* arguments: a :term:`context` and a :term:`request`.  In :term:`url
dispatch` based applications, the context resource is rarely used in the view
body itself, so within code that uses URL-dispatch-only, it's common to
define views as callables that accept only a ``request`` to avoid the visual
"noise" of a ``context`` argument.  This application, however, uses
:term:`traversal` to map URLs to a context :term:`resource`, and since our
:term:`resource tree` also represents our application's "domain model", we're
often interested in the context, because it represents the persistent storage
of our application.  For this reason, having ``context`` in the callable
argument list is not "noise" to us; instead it's actually rather important
within the view code we'll define in this application.

The single-arg (``request`` -only) or two-arg (``context`` and ``request``)
calling conventions will work in any :app:`Pyramid` application for any view;
they can be used interchangeably as necessary.  We'll be using the
two-argument ``(context, request)`` view callable argument list syntax in
this application.

We're going to define several :term:`view callable` functions then wire them
into :app:`Pyramid` using some :term:`view configuration`.

The source code for this tutorial stage can be browsed via
`http://github.com/Pylons/pyramid/tree/master/docs/tutorials/wiki/src/views/
<http://github.com/Pylons/pyramid/tree/master/docs/tutorials/wiki/src/views/>`_.

Adding View Functions
=====================

We're going to add four :term:`view callable` functions to our ``views.py``
module.  One view named ``view_wiki`` will display the wiki itself (it will
answer on the root URL), another named ``view_page`` will display an
individual page, another named ``add_page`` will allow a page to be added,
and a final view named ``edit_page`` will allow a page to be edited.

The ``view_wiki`` view function
-------------------------------

The ``view_wiki`` function will be configured to respond as the default view
callable for a Wiki resource.  We'll provide it with a ``@view_config``
decorator which names the class ``tutorial.models.Wiki`` as its context.
This means that when a Wiki resource is the context, and no :term:`view name`
exists in the request, this view will be used.  The view configuration
associated with ``view_wiki`` does not use a ``renderer`` because the view
callable always returns a :term:`response` object rather than a dictionary.
No renderer is necessary when a view returns a response object.

The ``view_wiki`` view callable always redirects to the URL of a Page
resource named "FrontPage".  To do so, it returns an instance of the
:class:`pyramid.httpexceptions.HTTPFound` class (instances of which implement
the WebOb :term:`response` interface).  The :func:`pyramid.url.resource_url`
API.  :func:`pyramid.url.resource_url` constructs a URL to the ``FrontPage``
page resource (e.g. ``http://localhost:6543/FrontPage``), and uses it as the
"location" of the HTTPFound response, forming an HTTP redirect.

The ``view_page`` view function
-------------------------------

The ``view_page`` function will be configured to respond as the default view
of a Page resource.  We'll provide it with a ``@view_config`` decorator which
names the class ``tutorial.models.Page`` as its context.  This means that
when a Page resource is the context, and no :term:`view name` exists in the
request, this view will be used.  We inform :app:`Pyramid` this view will use
the ``templates/view.pt`` template file as a ``renderer``.

The ``view_page`` function generates the :term:`ReStructuredText` body of a
page (stored as the ``data`` attribute of the context passed to the view; the
context will be a Page resource) as HTML.  Then it substitutes an HTML anchor
for each *WikiWord* reference in the rendered HTML using a compiled regular
expression.

The curried function named ``check`` is used as the first argument to
``wikiwords.sub``, indicating that it should be called to provide a value for
each WikiWord match found in the content.  If the wiki (our page's
``__parent__``) already contains a page with the matched WikiWord name, the
``check`` function generates a view link to be used as the substitution value
and returns it.  If the wiki does not already contain a page with with the
matched WikiWord name, the function generates an "add" link as the
substitution value and returns it.

As a result, the ``content`` variable is now a fully formed bit of HTML
containing various view and add links for WikiWords based on the content of
our current page resource.

We then generate an edit URL (because it's easier to do here than in the
template), and we wrap up a number of arguments in a dictionary and return
it.

The arguments we wrap into a dictionary include ``page``, ``content``, and
``edit_url``.  As a result, the *template* associated with this view callable
(via ``renderer=`` in its configuration) will be able to use these names to
perform various rendering tasks.  The template associated with this view
callable will be a template which lives in ``templates/view.pt``.

Note the contrast between this view callable and the ``view_wiki`` view
callable.  In the ``view_wiki`` view callable, we unconditionally return a
:term:`response` object.  In the ``view_page`` view callable, we return a
*dictionary*.  It is *always* fine to return a :term:`response` object from a
:app:`Pyramid` view.  Returning a dictionary is allowed only when there is a
:term:`renderer` associated with the view callable in the view configuration.

The ``add_page`` view function
------------------------------

The ``add_page`` function will be configured to respond when the context
resource is a Wiki and the :term:`view name` is ``add_page``.  We'll provide
it with a ``@view_config`` decorator which names the string ``add_page`` as
its :term:`view name` (via name=), the class ``tutorial.models.Wiki`` as its
context, and the renderer named ``templates/edit.pt``.  This means that when
a Wiki resource is the context, and a :term:`view name` named ``add_page``
exists as the result of traversal, this view will be used.  We inform
:app:`Pyramid` this view will use the ``templates/edit.pt`` template file as
a ``renderer``.  We share the same template between add and edit views, thus
``edit.pt`` instead of ``add.pt``.

The ``add_page`` function will be invoked when a user clicks on a WikiWord
which isn't yet represented as a page in the system.  The ``check`` function
within the ``view_page`` view generates URLs to this view.  It also acts as a
handler for the form that is generated when we want to add a page resource.
The ``context`` of the ``add_page`` view is always a Wiki resource (*not* a
Page resource).

The request :term:`subpath` in :app:`Pyramid` is the sequence of names that
are found *after* the :term:`view name` in the URL segments given in the
``PATH_INFO`` of the WSGI request as the result of :term:`traversal`.  If our
add view is invoked via, e.g. ``http://localhost:6543/add_page/SomeName``,
the :term:`subpath` will be a tuple: ``('SomeName',)``.

The add view takes the zeroth element of the subpath (the wiki page name),
and aliases it to the name attribute in order to know the name of the page
we're trying to add.

If the view rendering is *not* a result of a form submission (if the
expression ``'form.submitted' in request.params`` is ``False``), the view
renders a template.  To do so, it generates a "save url" which the template
use as the form post URL during rendering.  We're lazy here, so we're trying
to use the same template (``templates/edit.pt``) for the add view as well as
the page edit view.  To do so, we create a dummy Page resource object in
order to satisfy the edit form's desire to have *some* page object exposed as
``page``, and we'll render the template to a response.

If the view rendering *is* a result of a form submission (if the expression
``'form.submitted' in request.params`` is ``True``), we scrape the page body
from the form data, create a Page object using the name in the subpath and
the page body, and save it into "our context" (the Wiki) using the
``__setitem__`` method of the context. We then redirect back to the
``view_page`` view (the default view for a page) for the newly created page.

The ``edit_page`` view function
-------------------------------

The ``edit_page`` function will be configured to respond when the context is
a Page resource and the :term:`view name` is ``edit_page``.  We'll provide it
with a ``@view_config`` decorator which names the string ``edit_page`` as its
:term:`view name` (via ``name=``), the class ``tutorial.models.Page`` as its
context, and the renderer named ``templates/edit.pt``.  This means that when
a Page resource is the context, and a :term:`view name` exists as the result
of traverasal named ``edit_page``, this view will be used.  We inform
:app:`Pyramid` this view will use the ``templates/edit.pt`` template file as
a ``renderer``.

The ``edit_page`` function will be invoked when a user clicks the "Edit this
Page" button on the view form.  It renders an edit form but it also acts as
the form post view callable for the form it renders.  The ``context`` of the
``edit_page`` view will *always* be a Page resource (never a Wiki resource).

If the view execution is *not* a result of a form submission (if the
expression ``'form.submitted' in request.params`` is ``False``), the view
simply renders the edit form, passing the request, the page resource, and a
save_url which will be used as the action of the generated form.

If the view execution *is* a result of a form submission (if the expression
``'form.submitted' in request.params`` is ``True``), the view grabs the
``body`` element of the request parameter and sets it as the ``data``
attribute of the page context.  It then redirects to the default view of the
context (the page), which will always be the ``view_page`` view.

Viewing the Result of Our Edits to ``views.py``
===============================================

The result of all of our edits to ``views.py`` will leave it looking like
this:

.. literalinclude:: src/views/tutorial/views.py
   :linenos:
   :language: python

Adding Templates
================

Most view callables we've added expected to be rendered via a
:term:`template`.  The default templating systems in :app:`Pyramid` are
:term:`Chameleon` and :term:`Mako`.  Chameleon is a variant of :term:`ZPT`,
which is an XML-based templating language.  Mako is a non-XML-based
templating language.  Because we had to pick one, we chose Chameleon for this
tutorial.

The templates we create will live in the ``templates`` directory of our
tutorial package.  Chameleon templates must have a ``.pt`` extension to be
recognized as such.

The ``view.pt`` Template
------------------------

The ``view.pt`` template is used for viewing a single Page.  It is used by
the ``view_page`` view function.  It should have a div that is "structure
replaced" with the ``content`` value provided by the view.  It should also
have a link on the rendered page that points at the "edit" URL (the URL which
invokes the ``edit_page`` view for the page being viewed).

Once we're done with the ``view.pt`` template, it will look a lot like
the below:

.. literalinclude:: src/views/tutorial/templates/view.pt
   :language: xml

.. note:: The names available for our use in a template are always those that
   are present in the dictionary returned by the view callable.  But our
   templates make use of a ``request`` object that none of our tutorial views
   return in their dictionary.  This value appears as if "by magic".
   However, ``request`` is one of several names that are available "by
   default" in a template when a template renderer is used.  See
   :ref:`chameleon_template_renderers` for more information about other names
   that are available by default in a template when a template is used as a
   renderer.

The ``edit.pt`` Template
------------------------

The ``edit.pt`` template is used for adding and editing a Page.  It is used
by the ``add_page`` and ``edit_page`` view functions.  It should display a
page containing a form that POSTs back to the "save_url" argument supplied by
the view.  The form should have a "body" textarea field (the page data), and
a submit button that has the name "form.submitted".  The textarea in the form
should be filled with any existing page data when it is rendered.

Once we're done with the ``edit.pt`` template, it will look a lot like the
below:

.. literalinclude:: src/views/tutorial/templates/edit.pt
   :language: xml

Static Assets
-------------

Our templates name a single static asset named ``pylons.css``.  We don't need
to create this file within our package's ``static`` directory because it was
provided at the time we created the project. This file is a little too long to
replicate within the body of this guide, however it is available `online
<http://github.com/Pylons/pyramid/blob/master/docs/tutorials/wiki/src/views/tutorial/static/pylons.css>`_.

This CSS file will be accessed via
e.g. ``http://localhost:6543/static/pylons.css`` by virtue of the call to
``add_static_view`` directive we've made in the ``__init__`` file.  Any
number and type of static assets can be placed in this directory (or
subdirectories) and are just referred to by URL or by using the convenience
method ``static_url`` e.g. ``request.static_url('{{package}}:static/foo.css')``
within templates.

Testing the Views
=================

We'll modify our ``tests.py`` file, adding tests for each view function we
added above.  As a result, we'll *delete* the ``ViewTests`` test in the file,
and add four other test classes: ``ViewWikiTests``, ``ViewPageTests``,
``AddPageTests``, and ``EditPageTests``.  These test the ``view_wiki``,
``view_page``, ``add_page``, and ``edit_page`` views respectively.

Once we're done with the ``tests.py`` module, it will look a lot like the
below:

.. literalinclude:: src/views/tutorial/tests.py
   :linenos:
   :language: python

Running the Tests
=================

We can run these tests by using ``setup.py test`` in the same way we did in
:ref:`running_tests`.  Assuming our shell's current working directory is the
"tutorial" distribution directory:

On UNIX:

.. code-block:: text

   $ ../bin/python setup.py test -q

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> ..\Scripts\python setup.py test -q

The expected result looks something like:

.. code-block:: text

   .........
   ----------------------------------------------------------------------
   Ran 9 tests in 0.203s
   
   OK

Viewing the Application in a Browser
====================================

Once we've completed our edits, we can finally examine our application in a
browser.  The views we'll try are as follows:

- Visiting ``http://localhost:6543/`` in a browser invokes the ``view_wiki``
  view.  This always redirects to the ``view_page`` view of the ``FrontPage``
  Page resource.

- Visiting ``http://localhost:6543/FrontPage/`` in a browser invokes
  the ``view_page`` view of the front page resource.  This is
  because it's the *default view* (a view without a ``name``) for Page
  resources.

- Visiting ``http://localhost:6543/FrontPage/edit_page`` in a browser
  invokes the edit view for the ``FrontPage`` Page resource.

- Visiting ``http://localhost:6543/add_page/SomePageName`` in a
  browser invokes the add view for a Page.

- To generate an error, visit ``http://localhost:6543/add_page`` which
  will generate an ``IndexError`` for the expression
  ``request.subpath[0]``.  You'll see an interactive traceback
  facility provided by :term:`WebError`.
