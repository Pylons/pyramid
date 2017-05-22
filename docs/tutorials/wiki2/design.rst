.. _wiki2_design:

======
Design
======

Following is a quick overview of the design of our wiki application to help us
understand the changes that we will be making as we work through the tutorial.

Overall
=======

We choose to use :term:`reStructuredText` markup in the wiki text. Translation
from reStructuredText to HTML is provided by the widely used ``docutils``
Python module.  We will add this module to the dependency list in the project's
``setup.py`` file.

Models
======

We'll be using an SQLite database to hold our wiki data, and we'll be using
:term:`SQLAlchemy` to access the data in this database.

Within the database, we will define two tables:

- The ``users`` table which will store the ``id``, ``name``, ``password_hash`` and
  ``role`` of each wiki user.
- The ``pages`` table, whose elements will store the wiki pages.
  There are four columns: ``id``, ``name``, ``data`` and ``creator_id``.

There is a one-to-many relationship between ``users`` and ``pages`` tracking
the user who created each wiki page defined by the ``creator_id`` column on the
``pages`` table.

URLs like ``/PageName`` will try to find an element in the ``pages`` table that
has a corresponding name.

To add a page to the wiki, a new row is created and the text is stored in
``data``.

A page named ``FrontPage`` containing the text "This is the front page" will
be created when the storage is initialized, and will be used as the wiki home
page.

Wiki Views
==========

There will be three views to handle the normal operations of adding, editing,
and viewing wiki pages, plus one view for the wiki front page. Two templates
will be used, one for viewing, and one for both adding and editing wiki pages.

As of version 1.5 :app:`Pyramid` no longer ships with templating systems.  In
this tutorial, we will use :term:`Jinja2`.  Jinja2 is a modern and
designer-friendly templating language for Python, modeled after Django's
templates.

Security
========

We'll eventually be adding security to our application.  To do this, we'll
be using a very simple role-based security model. We'll assign a single
role category to each user in our system.

``basic``
  An authenticated user who can view content and create new pages. A ``basic``
  user may also edit the pages they have created but not pages created by
  other users.

``editor``
  An authenticated user who can create and edit any content in the system.

In order to accomplish this we'll need to define an authentication policy
which can identify users by their :term:`userid` and role. Then we'll
need to define a page :term:`resource` which contains the appropriate
:term:`ACL`:

+----------+--------------------+----------------+
| Action   | Principal          | Permission     |
+==========+====================+================+
| Allow    | Everyone           | view           |
+----------+--------------------+----------------+
| Allow    | group:basic        | create         |
+----------+--------------------+----------------+
| Allow    | group:editors      | edit           |
+----------+--------------------+----------------+
| Allow    | <creator of page>  | edit           |
+----------+--------------------+----------------+

Permission declarations will be added to the views to assert the security
policies as each request is handled.

On the security side of the application there are two additional views for
handling login and logout as well as two exception views for handling
invalid access attempts and unhandled URLs.

Summary
=======

The URL, actions, template, and permission associated to each view are listed
in the following table:

+----------------------+-----------------------+-------------+----------------+------------+
| URL                  |  Action               |  View       |  Template      | Permission |
+======================+=======================+=============+================+============+
| /                    |  Redirect to          |  view_wiki  |                |            |
|                      |  /FrontPage           |             |                |            |
+----------------------+-----------------------+-------------+----------------+------------+
| /PageName            |  Display existing     |  view_page  |  view.jinja2   |  view      |
|                      |  page [2]_            |  [1]_       |                |            |
+----------------------+-----------------------+-------------+----------------+------------+
| /PageName/edit_page  |  Display edit form    |  edit_page  |  edit.jinja2   |  edit      |
|                      |  with existing        |             |                |            |
|                      |  content.             |             |                |            |
|                      |                       |             |                |            |
|                      |  If the form was      |             |                |            |
|                      |  submitted, redirect  |             |                |            |
|                      |  to /PageName         |             |                |            |
+----------------------+-----------------------+-------------+----------------+------------+
| /add_page/PageName   |  Create the page      |  add_page   |  edit.jinja2   |  create    |
|                      |  *PageName* in        |             |                |            |
|                      |  storage,  display    |             |                |            |
|                      |  the edit form        |             |                |            |
|                      |  without content.     |             |                |            |
|                      |                       |             |                |            |
|                      |  If the form was      |             |                |            |
|                      |  submitted,           |             |                |            |
|                      |  redirect to          |             |                |            |
|                      |  /PageName            |             |                |            |
+----------------------+-----------------------+-------------+----------------+------------+
| /login               |  Display login form,  |  login      |  login.jinja2  |            |
|                      |  Forbidden [3]_       |             |                |            |
|                      |                       |             |                |            |
|                      |  If the form was      |             |                |            |
|                      |  submitted,           |             |                |            |
|                      |  authenticate.        |             |                |            |
|                      |                       |             |                |            |
|                      |  - If authentication  |             |                |            |
|                      |    succeeds,          |             |                |            |
|                      |    redirect to the    |             |                |            |
|                      |    page from which    |             |                |            |
|                      |    we came.           |             |                |            |
|                      |                       |             |                |            |
|                      |  - If authentication  |             |                |            |
|                      |    fails, display     |             |                |            |
|                      |    login form with    |             |                |            |
|                      |    "login failed"     |             |                |            |
|                      |    message.           |             |                |            |
+----------------------+-----------------------+-------------+----------------+------------+
| /logout              |  Redirect to          |  logout     |                |            |
|                      |  /FrontPage           |             |                |            |
+----------------------+-----------------------+-------------+----------------+------------+

.. [1] This is the default view for a Page context when there is no view name.
.. [2] Pyramid will return a default 404 Not Found page if the page ``PageName``
       does not exist yet.
.. [3] ``pyramid.exceptions.Forbidden`` is reached when a user tries to invoke
       a view that is not authorized by the authorization policy.
