.. _wiki2_adding_authorization:

====================
Adding authorization
====================

:app:`Pyramid` provides facilities for :term:`authentication` and
:term:`authorization`.  We'll make use of both features to provide security
to our application.  Our application currently allows anyone with access to
the server to view, edit, and add pages to our wiki.  We'll change that to
allow only people who are members of a *group* named ``group:editors`` to add
and edit wiki pages but we'll continue allowing anyone with access to the
server to view pages.

We will also add a login page and a logout link on all the pages.  The login
page will be shown when a user is denied access to any of the views that
require permission, instead of a default "403 Forbidden" page.

We will implement the access control with the following steps:

* Add users and groups (``security/default.py``, a new subpackage).
* Add an :term:`ACL` (``models/mymodel.py`` and ``__init__.py``).
* Add an :term:`authentication policy` and an :term:`authorization policy`
  (``__init__.py``).
* Add :term:`permission` declarations to the ``edit_page`` and ``add_page``
  views (``views/default.py``).

Then we will add the login and logout feature:

* Add routes for /login and /logout (``__init__.py``).
* Add ``login`` and ``logout`` views (``views/default.py``).
* Add a login template (``login.jinja2``).
* Make the existing views return a ``logged_in`` flag to the renderer
  (``views/default.py``).
* Add a "Logout" link to be shown when logged in and viewing or editing a page
  (``view.jinja2``, ``edit.jinja2``).


Access control
--------------

Add users and groups
~~~~~~~~~~~~~~~~~~~~

Create a new ``tutorial/security/default.py`` subpackage with the
following content:

.. literalinclude:: src/authorization/tutorial/security/default.py
   :linenos:
   :language: python

The ``groupfinder`` function accepts a userid and a request and
returns one of these values:

- If the userid exists in the system, it will return a sequence of group
  identifiers (or an empty sequence if the user isn't a member of any groups).
- If the userid *does not* exist in the system, it will return ``None``.

For example, ``groupfinder('editor', request )`` returns ``['group:editor']``,
``groupfinder('viewer', request)`` returns ``[]``, and ``groupfinder('admin',
request)`` returns ``None``.  We will use ``groupfinder()`` as an
:term:`authentication policy` "callback" that will provide the
:term:`principal` or principals for a user.

In a production system, user and group data will most often come from a
database, but here we use "dummy" data to represent user and groups sources.

Add an ACL
~~~~~~~~~~

Open ``tutorial/models/mymodel.py`` and add the following import
statement at the top:

.. literalinclude:: src/authorization/tutorial/models/mymodel.py
   :lines: 1-4
   :language: python

Add the following class definition at the end:

.. literalinclude:: src/authorization/tutorial/models/mymodel.py
   :lines: 22-29
   :language: python

We import :data:`~pyramid.security.Allow`, an action that means that
permission is allowed, and :data:`~pyramid.security.Everyone`, a special
:term:`principal` that is associated to all requests.  Both are used in the
:term:`ACE` entries that make up the ACL.

The ACL is a list that needs to be named `__acl__` and be an attribute of a
class.  We define an :term:`ACL` with two :term:`ACE` entries.  The first entry
allows any user (``Everyone``) the `view` permission.  The second entry allows
the ``group:editors`` principal the `edit` permission.

The ``RootFactory`` class that contains the ACL is a :term:`root factory`. We
need to associate it to our :app:`Pyramid` application, so the ACL is provided
to each view in the :term:`context` of the request as the ``context``
attribute.

Open ``tutorial/__init__.py`` and define a new root factory using
:meth:`pyramid.config.Configurator.set_root_factory` using the class that we
created above:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :lines: 14-17
   :emphasize-lines: 17
   :language: python

Only the highlighted line needs to be added.

We are now providing the ACL to the application.  See :ref:`assigning_acls`
for more information about what an :term:`ACL` represents.

.. note:: Although we don't use the functionality here, the ``factory`` used
   to create route contexts may differ per-route as opposed to globally.  See
   the ``factory`` argument to :meth:`pyramid.config.Configurator.add_route`
   for more info.

Add authentication and authorization policies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``tutorial/__init__.py`` and add the highlighted import
statements:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :lines: 1-5
   :emphasize-lines: 2-5
   :language: python

Now add those policies to the configuration:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :lines: 11-19
   :emphasize-lines: 1-3,8-9
   :language: python

Only the highlighted lines need to be added.

We are enabling an ``AuthTktAuthenticationPolicy``, which is based in an auth
ticket that may be included in the request. We are also enabling an
``ACLAuthorizationPolicy``, which uses an ACL to determine the *allow* or
*deny* outcome for a view.

Note that the :class:`pyramid.authentication.AuthTktAuthenticationPolicy`
constructor accepts two arguments: ``secret`` and ``callback``.  ``secret`` is
a string representing an encryption key used by the "authentication ticket"
machinery represented by this policy; it is required.  The ``callback`` is the
``groupfinder()`` function that we created before.


Add permission declarations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``tutorial/views/default.py`` and add a ``permission='view'``
parameter to the ``@view_config`` decorator for ``view_wiki()`` and
``view_page()`` as follows:

.. literalinclude:: src/authorization/tutorial/views/default.py
   :lines: 24-25
   :emphasize-lines: 1
   :language: python

.. literalinclude:: src/authorization/tutorial/views/default.py
   :lines: 29-31
   :emphasize-lines: 1-2
   :language: python

Only the highlighted lines, along with their preceding commas, need to be
edited and added.

This allows anyone to invoke these two views.

Add a ``permission='edit'`` parameter to the ``@view_config`` decorators for
``add_page()`` and ``edit_page()``:

.. literalinclude:: src/authorization/tutorial/views/default.py
   :lines: 52-54
   :emphasize-lines: 1-2
   :language: python

.. literalinclude:: src/authorization/tutorial/views/default.py
   :lines: 66-68
   :emphasize-lines: 1-2
   :language: python

Only the highlighted lines, along with their preceding commas, need to be
edited and added.

The result is that only users who possess the ``edit`` permission at the time
of the request may invoke those two views.

We are done with the changes needed to control access.  The changes that
follow will add the login and logout feature.

Login, logout
-------------

Add routes for /login and /logout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Go back to ``tutorial/__init__.py`` and add these two routes as
highlighted:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :lines: 21-24
   :emphasize-lines: 2-3
   :language: python

.. note:: The preceding lines must be added *before* the following
   ``view_page`` route definition:

   .. literalinclude:: src/authorization/tutorial/__init__.py
      :lines: 24
      :language: python

   This is because ``view_page``'s route definition uses a catch-all
   "replacement marker" ``/{pagename}`` (see :ref:`route_pattern_syntax`)
   which will catch any route that was not already caught by any route listed
   above it in ``__init__.py``. Hence, for ``login`` and ``logout`` views to
   have the opportunity of being matched (or "caught"), they must be above
   ``/{pagename}``.

Add login and logout views
~~~~~~~~~~~~~~~~~~~~~~~~~~

We'll add a ``login`` view which renders a login form and processes the post
from the login form, checking credentials.

We'll also add a ``logout`` view callable to our application and provide a
link to it.  This view will clear the credentials of the logged in user and
redirect back to the front page.

Add the following import statements to ``tutorial/views/default.py``
after the import from ``pyramid.httpexceptions``:

.. literalinclude:: src/authorization/tutorial/views/default.py
   :lines: 9-19
   :emphasize-lines: 1-8,11
   :language: python

All the highlighted lines need to be added or edited.

:meth:`~pyramid.view.forbidden_view_config` will be used to customize the
default 403 Forbidden page. :meth:`~pyramid.security.remember` and
:meth:`~pyramid.security.forget` help to create and expire an auth ticket
cookie.

Now add the ``login`` and ``logout`` views at the end of the file:

.. literalinclude:: src/authorization/tutorial/views/default.py
   :lines: 81-112
   :language: python

``login()`` has two decorators:

- a ``@view_config`` decorator which associates it with the ``login`` route
  and makes it visible when we visit ``/login``, and
- a ``@forbidden_view_config`` decorator which turns it into a
  :term:`forbidden view`. ``login()`` will be invoked when a user tries to
  execute a view callable for which they lack authorization.  For example, if
  a user has not logged in and tries to add or edit a wiki page, they will be
  shown the login form before being allowed to continue.

The order of these two :term:`view configuration` decorators is unimportant.

``logout()`` is decorated with a ``@view_config`` decorator which associates
it with the ``logout`` route.  It will be invoked when we visit ``/logout``.

Add the ``login.jinja2`` template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create ``tutorial/templates/login.jinja2`` with the following content:

.. literalinclude:: src/authorization/tutorial/templates/login.jinja2
   :language: html

The above template is referenced in the login view that we just added in
``views/default.py``.

Add a "Logout" link when logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``tutorial/templates/edit.jinja2`` and
``tutorial/templates/view.jinja2`` and add the following code as
indicated by the highlighted lines.

.. literalinclude:: src/authorization/tutorial/templates/edit.jinja2
   :lines: 34-40
   :emphasize-lines: 3-7
   :language: html

The :meth:`pyramid.request.Request.authenticated_userid` will be ``None`` if
the user is not authenticated, or a userid if the user is authenticated. This
check will make the logout link active only when the user is logged in.

Reviewing our changes
---------------------

Our ``tutorial/__init__.py`` will look like this when we're done:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :linenos:
   :emphasize-lines: 2-3,5,11-13,17-19,22-23
   :language: python

Only the highlighted lines need to be added or edited.

Our ``tutorial/models/mymodel.py`` will look like this when we're done:

.. literalinclude:: src/authorization/tutorial/models/mymodel.py
   :linenos:
   :emphasize-lines: 1-4,22-29
   :language: python

Only the highlighted lines need to be added or edited.

Our ``tutorial/views/default.py`` will look like this when we're done:

.. literalinclude:: src/authorization/tutorial/views/default.py
   :linenos:
   :emphasize-lines: 9-16,19,24,29-30,52-53,66-67,81-112
   :language: python

Only the highlighted lines need to be added or edited.

Our ``tutorial/templates/edit.jinja2`` template will look like this when
we're done:

.. literalinclude:: src/authorization/tutorial/templates/edit.jinja2
   :linenos:
   :emphasize-lines: 36-40
   :language: html

Only the highlighted lines need to be added or edited.

Our ``tutorial/templates/view.jinja2`` template will look like this when
we're done:

.. literalinclude:: src/authorization/tutorial/templates/view.jinja2
   :linenos:
   :emphasize-lines: 36-40
   :language: html

Only the highlighted lines need to be added or edited.

Viewing the application in a browser
------------------------------------

We can finally examine our application in a browser (See
:ref:`wiki2-start-the-application`).  Launch a browser and visit each of the
following URLs, checking that the result is as expected:

- http://localhost:6543/ invokes the ``view_wiki`` view.  This always
  redirects to the ``view_page`` view of the ``FrontPage`` page object.  It
  is executable by any user.

- http://localhost:6543/FrontPage invokes the ``view_page`` view of the
  ``FrontPage`` page object.

- http://localhost:6543/FrontPage/edit_page invokes the edit view for the
  FrontPage object.  It is executable by only the ``editor`` user.  If a
  different user (or the anonymous user) invokes it, a login form will be
  displayed.  Supplying the credentials with the username ``editor``, password
  ``editor`` will display the edit page form.

- http://localhost:6543/add_page/SomePageName invokes the add view for a page.
  It is executable by only the ``editor`` user.  If a different user (or the
  anonymous user) invokes it, a login form will be displayed. Supplying the
  credentials with the username ``editor``, password ``editor`` will display
  the edit page form.

- After logging in (as a result of hitting an edit or add page and submitting
  the login form with the ``editor`` credentials), we'll see a Logout link in
  the upper right hand corner.  When we click it, we're logged out, and
  redirected back to the front page.
