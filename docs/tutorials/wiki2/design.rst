==========
Design
==========

Following is a quick overview of the design of our wiki application, to help
us understand the changes that we will be making as we work through the
tutorial.

Overall
-------

We choose to use ``reStructuredText`` markup in the wiki text.  Translation
from reStructuredText to HTML is provided by the widely used ``docutils``
Python module.  We will add this module in the dependency list on the project
``setup.py`` file.

Models
------

We'll be using a SQLite database to hold our wiki data, and we'll be using
:term:`SQLAlchemy` to access the data in this database.

Within the database, we define a single table named `pages`, whose elements
will store the wiki pages.  There are two columns: `name` and `data`.

URLs like ``/PageName`` will try to find an element in 
the table that has a corresponding name.

To add a page to the wiki, a new row is created and the text
is stored in `data`.

A page named ``FrontPage`` containing the text *This is the front page*, will
be created when the storage is initialized, and will be used as the wiki home
page.

Views
-----

There will be three views to handle the normal operations of adding,
editing and viewing wiki pages, plus one view for the wiki front page.
Two templates will be used, one for viewing, and one for both for adding
and editing wiki pages.

The default templating systems in :app:`Pyramid` are
:term:`Chameleon` and :term:`Mako`.  Chameleon is a variant of
:term:`ZPT`, which is an XML-based templating language.  Mako is a
non-XML-based templating language.  Because we had to pick one,
we chose Chameleon for this tutorial.

Security
--------

We'll eventually be adding security to our application.  The components we'll
use to do this are below.

- USERS, a dictionary mapping users names to their corresponding passwords.

- GROUPS, a dictionary mapping user names to a list of groups they belong to.

- ``groupfinder``, an *authorization callback* that looks up USERS and
  GROUPS.  It will be provided in a new *security.py* file.

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

The URL, actions, template and permission associated to each view are
listed in the following table:

+----------------------+-----------------------+-------------+------------+------------+
| URL                  |  Action               |  View       |  Template  | Permission |
|                      |                       |             |            |            |
+======================+=======================+=============+============+============+
| /                    |  Redirect to          |  view_wiki  |            |            |
|                      |  /FrontPage           |             |            |            |
+----------------------+-----------------------+-------------+------------+------------+
| /PageName            |  Display existing     |  view_page  |  view.pt   |  view      |
|                      |  page [2]_            |  [1]_       |            |            |
|                      |                       |             |            |            |
|                      |                       |             |            |            |
|                      |                       |             |            |            |
+----------------------+-----------------------+-------------+------------+------------+
| /PageName/edit_page  |  Display edit form    |  edit_page  |  edit.pt   |  edit      |
|                      |  with existing        |             |            |            |
|                      |  content.             |             |            |            |
|                      |                       |             |            |            |
|                      |  If the form was      |             |            |            |
|                      |  submitted, redirect  |             |            |            |
|                      |  to /PageName         |             |            |            |
+----------------------+-----------------------+-------------+------------+------------+
| /add_page/PageName   |  Create the page      |  add_page   |  edit.pt   |  edit      |
|                      |  *PageName* in        |             |            |            |
|                      |  storage,  display    |             |            |            |
|                      |  the edit form        |             |            |            |
|                      |  without content.     |             |            |            |
|                      |                       |             |            |            |
|                      |  If the form was      |             |            |            |
|                      |  submitted,           |             |            |            |
|                      |  redirect to          |             |            |            |
|                      |  /PageName            |             |            |            |
+----------------------+-----------------------+-------------+------------+------------+
| /login               |  Display login form,  |  login      |  login.pt  |            |
|                      |   Forbidden [3]_      |             |            |            |
|                      |                       |             |            |            |
|                      |  If the form was      |             |            |            |
|                      |  submitted,           |             |            |            |
|                      |  authenticate.        |             |            |            |
|                      |                       |             |            |            |
|                      |  - If authentication  |             |            |            |
|                      |    successful,        |             |            |            |
|                      |    redirect to the    |             |            |            |
|                      |    page that we       |             |            |            |
|                      |    came from.         |             |            |            |
|                      |                       |             |            |            |
|                      |  - If authentication  |             |            |            |
|                      |    fails, display     |             |            |            |
|                      |    login form with    |             |            |            |
|                      |    "login failed"     |             |            |            |
|                      |    message.           |             |            |            |
|                      |                       |             |            |            |
+----------------------+-----------------------+-------------+------------+------------+
| /logout              |  Redirect to          |  logout     |            |            |
|                      |  /FrontPage           |             |            |            |
+----------------------+-----------------------+-------------+------------+------------+

.. [1] This is the default view for a Page context
       when there is no view name.
.. [2] Pyramid will return a default 404 Not Found page
       if the page *PageName* does not exist yet.
.. [3] pyramid.exceptions.Forbidden is reached when a
       user tries to invoke a view that is
       not authorized by the authorization policy.
