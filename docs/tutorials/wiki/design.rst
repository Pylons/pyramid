.. _wiki_design:

======
Design
======

Following is a quick overview of the design of our wiki application, to help
us understand the changes that we will be making as we work through the
tutorial.

Overall
-------

We choose to use :term:`reStructuredText` markup in the wiki text. Translation
from reStructuredText to HTML is provided by the widely used ``docutils``
Python module.  We will add this module in the dependency list on the project
``setup.py`` file.

Models
------

The root resource named ``Wiki`` will be a mapping of wiki page
names to page resources.  The page resources will be instances
of a *Page* class and they store the text content.

URLs like ``/PageName`` will be traversed using  Wiki[
*PageName* ] => page, and the context that results is the page
resource of an existing page.

To add a page to the wiki, a new instance of the page resource
is created and its name and reference are added to the Wiki
mapping.

A page named ``FrontPage`` containing the text *This is the front page*, will
be created when the storage is initialized, and will be used as the wiki home
page.

Views
-----

There will be three views to handle the normal operations of adding,
editing, and viewing wiki pages, plus one view for the wiki front page.
Two templates will be used, one for viewing, and one for both adding
and editing wiki pages.

As of version 1.5 :app:`Pyramid` no longer ships with templating systems.  In this tutorial, we will use :term:`Chameleon`.  Chameleon is a variant of :term:`ZPT`, which is an XML-based templating language.


Security
--------

We'll eventually be adding security to our application.  The components we'll
use to do this are below.

- USERS, a dictionary mapping :term:`userids <userid>` to their
  corresponding passwords.

- GROUPS, a dictionary mapping :term:`userids <userid>` to a
  list of groups to which they belong.

- ``groupfinder``, an *authorization callback* that looks up USERS and
  GROUPS.  It will be provided in a new ``security.py`` file.

- An :term:`ACL` is attached to the root :term:`resource`.  Each row below
  details an :term:`ACE`:

  +----------+----------------+----------------+
  | Action   | Principal      | Permission     |
  +==========+================+================+
  | Allow    | Everyone       | View           |
  +----------+----------------+----------------+
  | Allow    | group:editors  | Edit           |
  +----------+----------------+----------------+

- Permission declarations are added to the views to assert the security
  policies as each request is handled.

Two additional views and one template will handle the login and
logout tasks.

Summary
-------

The URL, context, actions, template and permission associated to each view are
listed in the following table:

+----------------------+-------------+-----------------+-----------------------+------------+------------+
| URL                  |  View       |  Context        |  Action               |  Template  | Permission |
|                      |             |                 |                       |            |            |
+======================+=============+=================+=======================+============+============+
| /                    |  view_wiki  |  Wiki           |  Redirect to          |            |            |
|                      |             |                 |  /FrontPage           |            |            |
+----------------------+-------------+-----------------+-----------------------+------------+------------+
| /PageName            |  view_page  |  Page           |  Display existing     |  view.pt   |  view      |
|                      |  [1]_       |                 |  page [2]_            |            |            |
|                      |             |                 |                       |            |            |
|                      |             |                 |                       |            |            |
|                      |             |                 |                       |            |            |
+----------------------+-------------+-----------------+-----------------------+------------+------------+
| /PageName/edit_page  |  edit_page  |  Page           |  Display edit form    |  edit.pt   |  edit      |
|                      |             |                 |  with existing        |            |            |
|                      |             |                 |  content.             |            |            |
|                      |             |                 |                       |            |            |
|                      |             |                 |  If the form was      |            |            |
|                      |             |                 |  submitted, redirect  |            |            |
|                      |             |                 |  to /PageName         |            |            |
+----------------------+-------------+-----------------+-----------------------+------------+------------+
| /add_page/PageName   |  add_page   |  Wiki           |  Create the page      |  edit.pt   |  edit      |
|                      |             |                 |  *PageName* in        |            |            |
|                      |             |                 |  storage,  display    |            |            |
|                      |             |                 |  the edit form        |            |            |
|                      |             |                 |  without content.     |            |            |
|                      |             |                 |                       |            |            |
|                      |             |                 |  If the form was      |            |            |
|                      |             |                 |  submitted,           |            |            |
|                      |             |                 |  redirect to          |            |            |
|                      |             |                 |  /PageName            |            |            |
+----------------------+-------------+-----------------+-----------------------+------------+------------+
| /login               |  login      |  Wiki,          |  Display login form.  |  login.pt  |            |
|                      |             |  Forbidden [3]_ |                       |            |            |
|                      |             |                 |  If the form was      |            |            |
|                      |             |                 |  submitted,           |            |            |
|                      |             |                 |  authenticate.        |            |            |
|                      |             |                 |                       |            |            |
|                      |             |                 |  - If authentication  |            |            |
|                      |             |                 |    succeeds,          |            |            |
|                      |             |                 |    redirect to the    |            |            |
|                      |             |                 |    page that we       |            |            |
|                      |             |                 |    came from.         |            |            |
|                      |             |                 |                       |            |            |
|                      |             |                 |  - If authentication  |            |            |
|                      |             |                 |    fails, display     |            |            |
|                      |             |                 |    login form with    |            |            |
|                      |             |                 |    "login failed"     |            |            |
|                      |             |                 |    message.           |            |            |
|                      |             |                 |                       |            |            |
+----------------------+-------------+-----------------+-----------------------+------------+------------+
| /logout              |  logout     |  Wiki           |  Redirect to          |            |            |
|                      |             |                 |  /FrontPage           |            |            |
+----------------------+-------------+-----------------+-----------------------+------------+------------+

.. [1] This is the default view for a Page context
       when there is no view name.
.. [2] Pyramid will return a default 404 Not Found page
       if the page *PageName* does not exist yet.
.. [3] ``pyramid.exceptions.Forbidden`` is reached when a
       user tries to invoke a view that is
       not authorized by the authorization policy.
