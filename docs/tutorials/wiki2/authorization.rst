.. _wiki2_adding_authorization:

====================
Adding Authorization
====================

:app:`Pyramid` provides facilities for :term:`authentication` and
:term:`authorization`.  We'll make use of both features to provide security
to our application.  Our application currently allows anyone with access to
the server to view, edit, and add pages to our wiki.  We'll change that
to allow only people who are members of a *group* named ``group:editors``
to add and edit wiki pages but we'll continue allowing
anyone with access to the server to view pages.

We will also add a login page and a logout link on all the
pages.  The login page will be shown when a user is denied
access to any of the views that require a permission, instead of
a default "403 Forbidden" page.

We will implement the access control with the following steps:

* Add users and groups (``security.py``, a new module).
* Add an :term:`ACL` (``models.py`` and
  ``__init__.py``).
* Add an :term:`authentication policy` and an :term:`authorization policy`
  (``__init__.py``).
* Add :term:`permission` declarations to the ``edit_page`` and ``add_page``
  views (``views.py``).

Then we will add the login and logout feature:

* Add routes for /login and /logout (``__init__.py``).
* Add ``login`` and ``logout`` views (``views.py``).
* Add a login template (``login.pt``).
* Make the existing views return a ``logged_in`` flag to the renderer (``views.py``).
* Add a "Logout" link to be shown when logged in and viewing or editing a page
  (``view.pt``, ``edit.pt``).

The source code for this tutorial stage can be browsed at
`http://github.com/Pylons/pyramid/tree/1.3-branch/docs/tutorials/wiki2/src/authorization/
<http://github.com/Pylons/pyramid/tree/1.3-branch/docs/tutorials/wiki2/src/authorization/>`_.

Access Control
--------------

Add users and groups
~~~~~~~~~~~~~~~~~~~~

Create a new ``tutorial/tutorial/security.py`` module with the
following content:

.. literalinclude:: src/authorization/tutorial/security.py
   :linenos:
   :language: python

The ``groupfinder`` function accepts a userid and a request and
returns one of these values:

- If the userid exists in the system, it will return a
  sequence of group identifiers (or an empty sequence if the user
  isn't a member of any groups).
- If the userid *does not* exist in the system, it will
  return ``None``.

For example, ``groupfinder('editor', request )`` returns ['group:editor'],
``groupfinder('viewer', request)`` returns [], and ``groupfinder('admin', request)``
returns ``None``.  We will use ``groupfinder()`` as an :term:`authentication policy`
"callback" that will provide the :term:`principal` or principals
for a user.

In a production system, user and group
data will most often come from a database, but here we use "dummy"
data to represent user and groups sources.

Add an ACL
~~~~~~~~~~

Open ``tutorial/tutorial/models.py`` and add the following import
statement at the head:

.. literalinclude:: src/authorization/tutorial/models.py
   :lines: 1-4
   :linenos:
   :language: python

Add the following class definition:

.. literalinclude:: src/authorization/tutorial/models.py
   :lines: 35-39
   :linenos:
   :language: python

We import :data:`~pyramid.security.Allow`, an action that
means that permission is allowed:, and
:data:`~pyramid.security.Everyone`, a special :term:`principal`
that is associated to all requests.  Both are used in the
:term:`ACE` entries that make up the ACL.

The ACL is a list that needs to be named `__acl__` and be an
attribute of a class.  We define an :term:`ACL` with two
:term:`ACE` entries: the first entry allows any user the `view`
permission.  The second entry allows the ``group:editors``
principal  the `edit` permission.

The ``RootFactory`` class that contains the ACL is a :term:`root factory`.
We need to associate it to our :app:`Pyramid` application, so the ACL is
provided to each view in the :term:`context` of the request, as
the ``context`` attribute.

Open ``tutorial/tutorial/__init__.py`` and add a ``root_factory``
parameter to our :term:`Configurator` constructor, that points to
the class we created above:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :lines: 23-24
   :linenos:
   :emphasize-lines: 2
   :language: python

(Only the highlighted line needs to be added.)

We are now providing the ACL to the application.  See
:ref:`assigning_acls` for more information about what an
:term:`ACL` represents.

.. note::

    Although we don't use the functionality here, the ``factory`` used
    to create route contexts may differ per-route as opposed to globally.  See
    the ``factory`` argument to
    :meth:`pyramid.config.Configurator.add_route` for more info.

Add Authentication and Authorization Policies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``tutorial/__init__.py`` and
add these import statements:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :lines: 2-3,7
   :linenos:
   :language: python

Now add those policies to the configuration:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :lines: 20-26
   :linenos:
   :emphasize-lines: 1-3,6-7
   :language: python

(Only the highlighted lines need to be added.)

We are enabling an ``AuthTktAuthenticationPolicy``, it is based in an auth
ticket that may be included in the request,  and an ``ACLAuthorizationPolicy``
that uses an ACL to determine the allow or deny outcome for a view.

Note that the
:class:`pyramid.authentication.AuthTktAuthenticationPolicy` constructor
accepts two arguments: ``secret`` and ``callback``.  ``secret`` is a string
representing an encryption key used by the "authentication ticket" machinery
represented by this policy: it is required.  The ``callback`` is the
``groupfinder()`` function that we created before.

Add permission declarations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add a ``permission='edit'`` parameter to the ``@view_config``
decorator for ``add_page()`` and ``edit_page()``, for example:

.. code-block:: python
   :linenos:
   :emphasize-lines: 2

   @view_config(route_name='add_page', renderer='templates/edit.pt',
                permission='edit')

(Only the highlighted line needs to be added.)

The result is that only users who possess the ``edit``
permission at the time of the request may invoke those two views.

Add a ``permission='view'`` parameter to the ``@view_config``
decorator for ``view_wiki()`` and ``view_page()``, like this:

.. code-block:: python
   :linenos:
   :emphasize-lines: 2

   @view_config(route_name='view_page', renderer='templates/view.pt',
                permission='view')

(Only the highlighted line needs to be added.)

This allows anyone to invoke these two views.

We are done with the changes needed to control access.  The
changes that follow will add the login and logout feature.

Login, Logout
-------------

Add routes for /login and /logout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Go back to ``tutorial/tutorial/__init__.py`` and add these two
routes:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :lines: 29-30
   :linenos:
   :language: python

Add Login and Logout Views
~~~~~~~~~~~~~~~~~~~~~~~~~~

We'll add a ``login`` view which renders a login form and processes
the post from the login form, checking credentials.

We'll also add a ``logout`` view callable to our application and
provide a link to it.  This view will clear the credentials of the
logged in user and redirect back to the front page.

Add the following import statements to the
head of ``tutorial/tutorial/views.py``:

.. literalinclude:: src/authorization/tutorial/views.py
   :lines: 9-16,18,24-25
   :linenos:
   :emphasize-lines: 3,6-9,11
   :language: python

(Only the highlighted lines need to be added.)

:meth:`~pyramid.view.forbidden_view_config` will be used
to customize the default 403 Forbidden page.
:meth:`~pyramid.security.remember` and
:meth:`~pyramid.security.forget` help to create and
expire an auth ticket cookie.

Now add the ``login`` and ``logout`` views:

.. literalinclude:: src/authorization/tutorial/views.py
   :lines: 91-123
   :linenos:
   :language: python

``login()`` is decorated with two decorators:

- a ``@view_config`` decorator which associates it with the
  ``login`` route and makes it visible when we visit ``/login``,
- a ``@forbidden_view_config`` decorator which turns it into
  an :term:`forbidden view`. ``login()`` will be invoked
  when a users tries to execute a view callable that
  they are not allowed to.  For example, if a user has not logged in
  and tries to add or edit a Wiki page, he will be shown the
  login form before being allowed to continue on.

The order of these two :term:`view configuration` decorators
is unimportant.

``logout()`` is decorated with a ``@view_config`` decorator
which associates it with the ``logout`` route.  It will be
invoked when we visit ``/logout``.

Add the ``login.pt`` Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create ``tutorial/tutorial/templates/login.pt`` with the following
content:

.. literalinclude:: src/authorization/tutorial/templates/login.pt
   :language: xml

The above template is referred to within the login view we just
added to ``views.py``.

Return a logged_in flag to the renderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add the following line to the import at the head of
``tutorial/tutorial/views.py``:

.. literalinclude:: src/authorization/tutorial/views.py
   :lines: 14-18
   :linenos:
   :emphasize-lines: 4
   :language: python

(Only the highlighted line needs to be added.)

Add a  ``logged_in`` parameter to the return value of
``view_page()``, ``edit_page()`` and  ``add_page()``,
like this:

.. code-block:: python
   :linenos:
   :emphasize-lines: 4

   return dict(page = page,
               content = content,
               edit_url = edit_url,
               logged_in = authenticated_userid(request))

(Only the highlighted line needs to be added.)

:meth:`~pyramid.security.authenticated_userid()` will return None
if the user is not authenticated, or some user id it the user
is authenticated.

Add a "Logout" link when logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``tutorial/tutorial/templates/edit.pt`` and
``tutorial/tutorial/templates/view.pt``  and add this within the
``<div id="right" class="app-welcome align-right">`` div:

.. code-block:: xml

   <span tal:condition="logged_in">
      <a href="${request.application_url}/logout">Logout</a>
   </span>

The attribute ``tal:condition="logged_in"`` will make the element be
included when ``logged_in`` is any user id. The link will invoke
the logout view.  The above element will not be included if ``logged_in``
is ``None``, such as when a user is not authenticated.

Seeing Our Changes
------------------

Our ``tutorial/tutorial/__init__.py`` will look something like this
when we're done:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :linenos:
   :emphasize-lines: 2-3,7,23-24,20-26,29-30
   :language: python

(Only the highlighted lines need to be added.)

Our ``tutorial/tutorial/models.py`` will look something like this
when we're done:

.. literalinclude:: src/authorization/tutorial/models.py
   :linenos:
   :emphasize-lines: 1-4,35-39
   :language: python

(Only the highlighted lines need to be added.)

Our ``tutorial/tutorial/views.py`` will look something like this
when we're done:

.. literalinclude:: src/authorization/tutorial/views.py
   :linenos:
   :emphasize-lines: 11,14-18,25,31,37,58,61,73,76,88,91-117,119-123
   :language: python

(Only the highlighted lines need to be added.)

Our ``tutorial/tutorial/templates/edit.pt`` template will look
something like this when we're done:

.. literalinclude:: src/authorization/tutorial/templates/edit.pt
   :linenos:
   :emphasize-lines: 41-43
   :language: xml

(Only the highlighted lines need to be added.)

Our ``tutorial/tutorial/templates/view.pt`` template will look
something like this when we're done:

.. literalinclude:: src/authorization/tutorial/templates/view.pt
   :linenos:
   :emphasize-lines: 41-43
   :language: xml

(Only the highlighted lines need to be added.)

Viewing the Application in a Browser
------------------------------------

We can finally examine our application in a browser (See
:ref:`wiki2-start-the-application`).  Launch a browser and visit
each of the following URLs, check that the result is as expected:

- ``http://localhost:6543/`` invokes the
  ``view_wiki`` view.  This always redirects to the ``view_page`` view
  of the FrontPage page object.  It is executable by any user.

- ``http://localhost:6543/FrontPage`` invokes
  the ``view_page`` view of the FrontPage page object.

- ``http://localhost:6543/FrontPage/edit_page``
  invokes the edit view for the FrontPage object.  It is executable by
  only the ``editor`` user.  If a different user (or the anonymous
  user) invokes it, a login form will be displayed.  Supplying the
  credentials with the username ``editor``, password ``editor`` will
  display the edit page form.

- ``http://localhost:6543/add_page/SomePageName``
  invokes the add view for a page.  It is executable by only
  the ``editor`` user.  If a different user (or the anonymous user)
  invokes it, a login form will be displayed.  Supplying the
  credentials with the username ``editor``, password ``editor`` will
  display the edit page form.

- After logging in (as a result of hitting an edit or add page
  and submitting the login form with the ``editor``
  credentials), we'll see a Logout link in the upper right hand
  corner.  When we click it, we're logged out, and redirected
  back to the front page.
