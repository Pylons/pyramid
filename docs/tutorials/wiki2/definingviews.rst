.. _wiki2_defining_views:

==============
Defining Views
==============

A :term:`view callable` in a :app:`Pyramid` application is typically a simple
Python function that accepts a single parameter named :term:`request`. A view
callable is assumed to return a :term:`response` object.

The request object has a dictionary as an attribute named ``matchdict``. A
``matchdict`` maps the placeholders in the matching URL ``pattern`` to the
substrings of the path in the :term:`request` URL. For instance, if a call to
:meth:`pyramid.config.Configurator.add_route` has the pattern ``/{one}/{two}``,
and a user visits ``http://example.com/foo/bar``, our pattern would be matched
against ``/foo/bar`` and the ``matchdict`` would look like ``{'one':'foo',
'two':'bar'}``.


Adding the ``docutils`` dependency
==================================

Remember in the previous chapter we added a new dependency of the ``bcrypt``
package. Again, the view code in our application will depend on a package which
is not a dependency of the original "tutorial" application.

We need to add a dependency on the ``docutils`` package to our ``tutorial``
package's ``setup.py`` file by assigning this dependency to the ``requires``
parameter in the ``setup()`` function.

Open ``tutorial/setup.py`` and edit it to look like the following:

.. literalinclude:: src/views/setup.py
   :linenos:
   :emphasize-lines: 13
   :language: python

Only the highlighted line needs to be added.

Again, as we did in the previous chapter, the dependency now needs to be
installed, so re-run the ``$VENV/bin/pip install -e .`` command.


Static assets
=============

Our templates name static assets, including CSS and images.  We don't need
to create these files within our package's ``static`` directory because they
were provided at the time we created the project.

As an example, the CSS file will be accessed via
``http://localhost:6543/static/theme.css`` by virtue of the call to the
``add_static_view`` directive we've made in the ``routes.py`` file. Any number
and type of static assets can be placed in this directory (or subdirectories)
and are just referred to by URL or by using the convenience method
``static_url``, e.g., ``request.static_url('<package>:static/foo.css')`` within
templates.


Adding routes to ``routes.py``
==============================

This is the `URL Dispatch` tutorial, so let's start by adding some URL patterns
to our app. Later we'll attach views to handle the URLs.

The ``routes.py`` file contains :meth:`pyramid.config.Configurator.add_route`
calls which serve to add routes to our application. First we'll get rid of the
existing route created by the template using the name ``'home'``. It's only an
example and isn't relevant to our application.

We then need to add four calls to ``add_route``. Note that the *ordering* of
these declarations is very important. Route declarations are matched in the
order they're registered.

#. Add a declaration which maps the pattern ``/`` (signifying the root URL) to
   the route named ``view_wiki``. In the next step, we will map it to our
   ``view_wiki`` view callable by virtue of the ``@view_config`` decorator
   attached to the ``view_wiki`` view function, which in turn will be indicated
   by ``route_name='view_wiki'``.

#. Add a declaration which maps the pattern ``/{pagename}`` to the route named
   ``view_page``. This is the regular view for a page. Again, in the next step,
   we will map it to our ``view_page`` view callable by virtue of the
   ``@view_config`` decorator attached to the ``view_page`` view function,
   whin in turn will be indicated by ``route_name='view_page'``.

#. Add a declaration which maps the pattern ``/add_page/{pagename}`` to the
   route named ``add_page``. This is the add view for a new page. We will map
   it to our ``add_page`` view callable by virtue of the ``@view_config``
   decorator attached to the ``add_page`` view function, which in turn will be
   indicated by ``route_name='add_page'``.

#. Add a declaration which maps the pattern ``/{pagename}/edit_page`` to the
   route named ``edit_page``. This is the edit view for a page. We will map it
   to our ``edit_page`` view callable by virtue of the ``@view_config``
   decorator attached to the ``edit_page`` view function, which in turn will be
   indicated by ``route_name='edit_page'``.

As a result of our edits, the ``routes.py`` file should look like the
following:

.. literalinclude:: src/views/tutorial/routes.py
   :linenos:
   :emphasize-lines: 3-6
   :language: python

The highlighted lines are the ones that need to be added or edited.

.. warning::

   The order of the routes is important! If you placed
   ``/{pagename}/edit_page`` *before* ``/add_page/{pagename}``, then we would
   never be able to add pages. This is because the first route would always
   match a request to ``/add_page/edit_page`` whereas we want ``/add_page/..``
   to have priority. This isn't a huge problem in this particular app because
   wiki pages are always camel case, but it's important to be aware of this
   behavior in your own apps.


Adding view functions in ``views/default.py``
=============================================

It's time for a major change.  Open ``tutorial/views/default.py`` and
edit it to look like the following:

.. literalinclude:: src/views/tutorial/views/default.py
   :linenos:
   :language: python
   :emphasize-lines: 1-9,12-

The highlighted lines need to be added or edited.

We added some imports, and created a regular expression to find "WikiWords".

We got rid of the ``my_view`` view function and its decorator that was added
when we originally rendered the ``alchemy`` cookiecutter.  It was only an example
and isn't relevant to our application.  We also deleted the ``db_err_msg``
string.

Then we added four :term:`view callable` functions to our ``views/default.py``
module, as mentioned in the previous step:

* ``view_wiki()`` - Displays the wiki itself. It will answer on the root URL.
* ``view_page()`` - Displays an individual page.
* ``edit_page()`` - Allows the user to edit a page.
* ``add_page()`` - Allows the user to add a page.

We'll describe each one briefly in the following sections.

.. note::

  There is nothing special about the filename ``default.py`` exept that it is a
  Python module. A project may have many view callables throughout its codebase
  in arbitrarily named modules. Modules implementing view callables often have
  ``view`` in their name (or may live in a Python subpackage of your
  application package named ``views``, as in our case), but this is only by
  convention, not a requirement.


The ``view_wiki`` view function
-------------------------------

Following is the code for the ``view_wiki`` view function and its decorator:

.. literalinclude:: src/views/tutorial/views/default.py
   :lines: 17-20
   :lineno-match:
   :linenos:
   :language: python

``view_wiki()`` is the :term:`default view` that gets called when a request is
made to the root URL of our wiki.  It always redirects to a URL which
represents the path to our "FrontPage".

The ``view_wiki`` view callable always redirects to the URL of a Page resource
named "FrontPage".  To do so, it returns an instance of the
:class:`pyramid.httpexceptions.HTTPFound` class (instances of which implement
the :class:`pyramid.interfaces.IResponse` interface, like
:class:`pyramid.response.Response`). It uses the
:meth:`pyramid.request.Request.route_url` API to construct a URL to the
``FrontPage`` page (i.e., ``http://localhost:6543/FrontPage``), and uses it as
the "location" of the ``HTTPFound`` response, forming an HTTP redirect.


The ``view_page`` view function
-------------------------------

Here is the code for the ``view_page`` view function and its decorator:

.. literalinclude:: src/views/tutorial/views/default.py
   :lines: 22-42
   :lineno-match:
   :linenos:
   :language: python

``view_page()`` is used to display a single page of our wiki.  It renders the
:term:`reStructuredText` body of a page (stored as the ``data`` attribute of a
``Page`` model object) as HTML.  Then it substitutes an HTML anchor for each
*WikiWord* reference in the rendered HTML using a compiled regular expression.

The curried function named ``add_link`` is used as the first argument to
``wikiwords.sub``, indicating that it should be called to provide a value for
each WikiWord match found in the content.  If the wiki already contains a
page with the matched WikiWord name, ``add_link()`` generates a view
link to be used as the substitution value and returns it.  If the wiki does
not already contain a page with the matched WikiWord name, ``add_link()``
generates an "add" link as the substitution value and returns it.

As a result, the ``content`` variable is now a fully formed bit of HTML
containing various view and add links for WikiWords based on the content of
our current page object.

We then generate an edit URL, because it's easier to do here than in the
template, and we return a dictionary with a number of arguments.  The fact that
``view_page()`` returns a dictionary (as opposed to a :term:`response` object)
is a cue to :app:`Pyramid` that it should try to use a :term:`renderer`
associated with the view configuration to render a response.  In our case, the
renderer used will be the ``view.jinja2`` template, as indicated in
the ``@view_config`` decorator that is applied to ``view_page()``.

If the page does not exist, then we need to handle that by raising a
:class:`pyramid.httpexceptions.HTTPNotFound` to trigger our 404 handling,
defined in ``tutorial/views/notfound.py``.

.. note::

   Using ``raise`` versus ``return`` with the HTTP exceptions is an important
   distinction that can commonly mess people up. In
   ``tutorial/views/notfound.py`` there is an :term:`exception view`
   registered for handling the ``HTTPNotFound`` exception. Exception views are
   only triggered for raised exceptions. If the ``HTTPNotFound`` is returned,
   then it has an internal "stock" template that it will use to render itself
   as a response. If you aren't seeing your exception view being executed, this
   is most likely the problem! See :ref:`special_exceptions_in_callables` for
   more information about exception views.


The ``edit_page`` view function
-------------------------------

Here is the code for the ``edit_page`` view function and its decorator:

.. literalinclude:: src/views/tutorial/views/default.py
   :lines: 44-56
   :lineno-match:
   :linenos:
   :language: python

``edit_page()`` is invoked when a user clicks the "Edit this Page" button on
the view form. It renders an edit form, but it also acts as the handler for the
form which it renders. The ``matchdict`` attribute of the request passed to the
``edit_page`` view will have a ``'pagename'`` key matching the name of the page
that the user wants to edit.

If the view execution *is* a result of a form submission (i.e., the expression
``'form.submitted' in request.params`` is ``True``), the view grabs the
``body`` element of the request parameters and sets it as the ``data``
attribute of the page object.  It then redirects to the ``view_page`` view
of the wiki page.

If the view execution is *not* a result of a form submission (i.e., the
expression ``'form.submitted' in request.params`` is ``False``), the view
simply renders the edit form, passing the page object and a ``save_url``
which will be used as the action of the generated form.

.. note::

   Since our ``request.dbsession`` defined in the previous chapter is
   registered with the ``pyramid_tm`` transaction manager, any changes we make
   to objects managed by the that session will be committed automatically. In
   the event that there was an error (even later, in our template code), the
   changes would be aborted. This means the view itself does not need to
   concern itself with commit/rollback logic.


The ``add_page`` view function
------------------------------

Here is the code for the ``add_page`` view function and its decorator:

.. literalinclude:: src/views/tutorial/views/default.py
   :lines: 58-
   :lineno-match:
   :linenos:
   :language: python

``add_page()`` is invoked when a user clicks on a *WikiWord* which isn't yet
represented as a page in the system. The ``add_link`` function within the
``view_page`` view generates URLs to this view. ``add_page()`` also acts as a
handler for the form that is generated when we want to add a page object. The
``matchdict`` attribute of the request passed to the ``add_page()`` view will
have the values we need to construct URLs and find model objects.

The ``matchdict`` will have a ``'pagename'`` key that matches the name of the
page we'd like to add. If our add view is invoked via, for example,
``http://localhost:6543/add_page/SomeName``, the value for ``'pagename'`` in
the ``matchdict`` will be ``'SomeName'``.

Next a check is performed to determine whether the ``Page`` already exists in
the database. If it already exists, then the client is redirected to the
``edit_page`` view, else we continue to the next check.

If the view execution *is* a result of a form submission (i.e., the expression
``'form.submitted' in request.params`` is ``True``), we grab the page body from
the form data, create a Page object with this page body and the name taken from
``matchdict['pagename']``, and save it into the database using
``request.dbession.add``. Since we have not yet covered authentication, we
don't have a logged-in user to add as the page's ``creator``. Until we get to
that point in the tutorial, we'll just assume that all pages are created by the
``editor`` user. Thus we query for that object, and set it on ``page.creator``.
Finally, we redirect the client back to the ``view_page`` view for the newly
created page.

If the view execution is *not* a result of a form submission (i.e., the
expression ``'form.submitted' in request.params`` is ``False``), the view
callable renders a template.  To do so, it generates a ``save_url`` which the
template uses as the form post URL during rendering.  We're lazy here, so
we're going to use the same template (``templates/edit.jinja2``) for the add
view as well as the page edit view. To do so we create a dummy ``Page`` object
in order to satisfy the edit form's desire to have *some* page object
exposed as ``page``. :app:`Pyramid` will render the template associated
with this view to a response.


Adding templates
================

The ``view_page``, ``add_page`` and ``edit_page`` views that we've added
reference a :term:`template`.  Each template is a :term:`Jinja2` template.
These templates will live in the ``templates`` directory of our tutorial
package.  Jinja2 templates must have a ``.jinja2`` extension to be recognized
as such.


The ``layout.jinja2`` template
------------------------------

Update ``tutorial/templates/layout.jinja2`` with the following content, as
indicated by the emphasized lines:

.. literalinclude:: src/views/tutorial/templates/layout.jinja2
   :linenos:
   :emphasize-lines: 11,35-37
   :language: html

Since we're using a templating engine, we can factor common boilerplate out of
our page templates into reusable components. One method for doing this is
template inheritance via blocks.

- We have defined two placeholders in the layout template where a child
  template can override the content. These blocks are named ``subtitle`` (line
  11) and ``content`` (line 36).
- Please refer to the `Jinja2 documentation <http://jinja.pocoo.org/>`_ for more information about template
  inheritance.


The ``view.jinja2`` template
----------------------------

Create ``tutorial/templates/view.jinja2`` and add the following content:

.. literalinclude:: src/views/tutorial/templates/view.jinja2
   :linenos:
   :language: html

This template is used by ``view_page()`` for displaying a single wiki page.

- We begin by extending the ``layout.jinja2`` template defined above, which
  provides the skeleton of the page (line 1).
- We override the ``subtitle`` block from the base layout, inserting the page
  name into the page's title (line 3).
- We override the ``content`` block from the base layout to insert our markup
  into the body (lines 5-18).
- We use a variable that is replaced with the ``content`` value provided by the
  view (line 6). ``content`` contains HTML, so the ``|safe`` filter is used to
  prevent escaping it (e.g., changing ">" to "&gt;").
- We create a link that points at the "edit" URL, which when clicked invokes
  the ``edit_page`` view for the requested page (lines 8-10).


The ``edit.jinja2`` template
----------------------------

Create ``tutorial/templates/edit.jinja2`` and add the following content:

.. literalinclude:: src/views/tutorial/templates/edit.jinja2
   :linenos:
   :emphasize-lines: 1,3,12,14,17
   :language: html

This template serves two use cases. It is used by ``add_page()`` and
``edit_page()`` for adding and editing a wiki page.  It displays a page
containing a form and which provides the following:

- Again, we extend the ``layout.jinja2`` template, which provides the skeleton
  of the page (line 1).
- Override the ``subtitle`` block to affect the ``<title>`` tag in the
  ``head`` of the page (line 3).
- A 10-row by 60-column ``textarea`` field named ``body`` that is filled with
  any existing page data when it is rendered (line 14).
- A submit button that has the name ``form.submitted`` (line 17).
- The form POSTs back to the ``save_url`` argument supplied by the view (line
  12). The view will use the ``body`` and ``form.submitted`` values.


The ``404.jinja2`` template
---------------------------

Replace ``tutorial/templates/404.jinja2`` with the following content:

.. literalinclude:: src/views/tutorial/templates/404.jinja2
   :linenos:
   :language: html

This template is linked from the ``notfound_view`` defined in
``tutorial/views/notfound.py`` as shown here:

.. literalinclude:: src/views/tutorial/views/notfound.py
   :linenos:
   :emphasize-lines: 6
   :language: python

There are several important things to note about this configuration:

- The ``notfound_view`` in the above snippet is called an
  :term:`exception view`. For more information see
  :ref:`special_exceptions_in_callables`.
- The ``notfound_view`` sets the response status to 404. It's possible
  to affect the response object used by the renderer via
  :ref:`request_response_attr`.
- The ``notfound_view`` is registered as an exception view and will be invoked
  **only** if ``pyramid.httpexceptions.HTTPNotFound`` is raised as an
  exception. This means it will not be invoked for any responses returned
  from a view normally. For example, on line 27 of
  ``tutorial/views/default.py`` the exception is raised which will trigger
  the view.

Finally, we may delete the ``tutorial/templates/mytemplate.jinja2`` template
that was provided by the ``alchemy`` cookiecutter, as we have created our own
templates for the wiki.

.. note::

   Our templates use a ``request`` object that none of our tutorial
   views return in their dictionary. ``request`` is one of several names that
   are available "by default" in a template when a template renderer is used.
   See :ref:`renderer_system_values` for information about other names that
   are available by default when a template is used as a renderer.


Viewing the application in a browser
====================================

We can finally examine our application in a browser (See
:ref:`wiki2-start-the-application`).  Launch a browser and visit
each of the following URLs, checking that the result is as expected:

- http://localhost:6543/ invokes the ``view_wiki`` view.  This always
  redirects to the ``view_page`` view of the ``FrontPage`` page object.

- http://localhost:6543/FrontPage invokes the ``view_page`` view of the
  ``FrontPage`` page object.

- http://localhost:6543/FrontPage/edit_page invokes the ``edit_page`` view for
  the ``FrontPage`` page object.

- http://localhost:6543/add_page/SomePageName invokes the ``add_page`` view for
  a page. If the page already exists, then it redirects the user to the
  ``edit_page`` view for the page object.

- http://localhost:6543/SomePageName/edit_page invokes the ``edit_page`` view
  for an existing page, or generates an error if the page does not exist.

- To generate an error, visit http://localhost:6543/foobars/edit_page which
  will generate a ``NoResultFound: No row was found for one()`` error. You'll
  see an interactive traceback facility provided by
  :term:`pyramid_debugtoolbar`.
