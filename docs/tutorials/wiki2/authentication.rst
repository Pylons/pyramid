.. _wiki2_adding_authentication:

=====================
Adding authentication
=====================

:app:`Pyramid` provides facilities for :term:`authentication` and
:term:`authorization`. In this section we'll focus solely on the authentication
APIs to add login and logout functionality to our wiki.

We will implement authentication with the following steps:

* Add an :term:`authentication policy` and a ``request.user`` computed property
  (``security.py``).
* Add routes for ``/login`` and ``/logout`` (``routes.py``).
* Add login and logout views (``views/auth.py``).
* Add a login template (``login.jinja2``).
* Add "Login" and "Logout" links to every page based on the user's
  authenticated state (``layout.jinja2``).
* Make the existing views verify user state (``views/default.py``).
* Redirect to ``/login`` when a user is denied access to any of the views that
  require permission, instead of a default "403 Forbidden" page
  (``views/auth.py``).


Authenticating requests
-----------------------

The core of :app:`Pyramid` authentication is an :term:`authentication policy`
which is used to identify authentication information from a ``request``,
as well as handling the low-level login and logout operations required to
track users across requests (via cookies, headers, or whatever else you can
imagine).


Add the authentication policy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a new file ``tutorial/security.py`` with the following content:

.. literalinclude:: src/authentication/tutorial/security.py
   :linenos:
   :language: python

Here we've defined:

* A new authentication policy named ``MyAuthenticationPolicy``, which is
  subclassed from Pyramid's
  :class:`pyramid.authentication.AuthTktAuthenticationPolicy`, which tracks the
  :term:`userid` using a signed cookie (lines 7-11).
* A ``get_user`` function, which can convert the ``unauthenticated_userid``
  from the policy into a ``User`` object from our database (lines 13-17).
* The ``get_user`` is registered on the request as ``request.user`` to be used
  throughout our application as the authenticated ``User`` object for the
  logged-in user (line 27).

The logic in this file is a little bit interesting, so we'll go into detail
about what's happening here:

First, the default authentication policies all provide a method named
``unauthenticated_userid`` which is responsible for the low-level parsing
of the information in the request (cookies, headers, etc.). If a ``userid``
is found, then it is returned from this method. This is named
``unauthenticated_userid`` because, at the lowest level, it knows the value of
the userid in the cookie, but it doesn't know if it's actually a user in our
system (remember, anything the user sends to our app is untrusted).

Second, our application should only care about ``authenticated_userid`` and
``request.user``, which have gone through our application-specific process of
validating that the user is logged in.

In order to provide an ``authenticated_userid`` we need a verification step.
That can happen anywhere, so we've elected to do it inside of the cached
``request.user`` computed property. This is a convenience that makes
``request.user`` the source of truth in our system. It is either ``None`` or
a ``User`` object from our database. This is why the ``get_user`` function
uses the ``unauthenticated_userid`` to check the database.


Configure the app
~~~~~~~~~~~~~~~~~

Since we've added a new ``tutorial/security.py`` module, we need to include it.
Open the file ``tutorial/__init__.py`` and edit the following lines:

.. literalinclude:: src/authentication/tutorial/__init__.py
   :linenos:
   :emphasize-lines: 11
   :language: python

Our authentication policy is expecting a new setting, ``auth.secret``. Open
the file ``development.ini`` and add the highlighted line below:

.. literalinclude:: src/authentication/development.ini
   :lines: 19-21
   :emphasize-lines: 3
   :lineno-match:
   :language: ini

Finally, best practices tell us to use a different secret for production, so
open ``production.ini`` and add a different secret:

.. literalinclude:: src/authentication/production.ini
   :lines: 17-19
   :emphasize-lines: 3
   :lineno-match:
   :language: ini


Add permission checks
~~~~~~~~~~~~~~~~~~~~~

:app:`Pyramid` has full support for declarative authorization, which we'll
cover in the next chapter. However, many people looking to get their feet wet
are just interested in authentication with some basic form of home-grown
authorization. We'll show below how to accomplish the simple security goals of
our wiki, now that we can track the logged-in state of users.

Remember our goals:

* Allow only ``editor`` and ``basic`` logged-in users to create new pages.
* Only allow ``editor`` users and the page creator (possibly a ``basic`` user)
  to edit pages.

Open the file ``tutorial/views/default.py`` and fix the following imports:

.. literalinclude:: src/authentication/tutorial/views/default.py
   :lines: 5-13
   :lineno-match:
   :emphasize-lines: 2,9
   :language: python

Change the two highlighted lines.

In the same file, now edit the ``edit_page`` view function:

.. literalinclude:: src/authentication/tutorial/views/default.py
   :lines: 45-60
   :lineno-match:
   :emphasize-lines: 5-7
   :language: python

Only the highlighted lines need to be changed.

If the user either is not logged in or the user is not the page's creator
*and* not an ``editor``, then we raise ``HTTPForbidden``.

In the same file, now edit the ``add_page`` view function:

.. literalinclude:: src/authentication/tutorial/views/default.py
   :lines: 62-76
   :lineno-match:
   :emphasize-lines: 3-5,13
   :language: python

Only the highlighted lines need to be changed.

If the user either is not logged in or is not in the ``basic`` or ``editor``
roles, then we raise ``HTTPForbidden``, which will return a "403 Forbidden"
response to the user. However, we will hook this later to redirect to the login
page. Also, now that we have ``request.user``, we no longer have to hard-code
the creator as the ``editor`` user, so we can finally drop that hack.

These simple checks should protect our views.


Login, logout
-------------

Now that we've got the ability to detect logged-in users, we need to add the
``/login`` and ``/logout`` views so that they can actually login and logout!


Add routes for ``/login`` and ``/logout``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Go back to ``tutorial/routes.py`` and add these two routes as highlighted:

.. literalinclude:: src/authentication/tutorial/routes.py
   :lines: 3-6
   :lineno-match:
   :emphasize-lines: 2-3
   :language: python

.. note:: The preceding lines must be added *before* the following
   ``view_page`` route definition:

   .. literalinclude:: src/authentication/tutorial/routes.py
      :lines: 6
      :lineno-match:
      :language: python

   This is because ``view_page``'s route definition uses a catch-all
   "replacement marker" ``/{pagename}`` (see :ref:`route_pattern_syntax`),
   which will catch any route that was not already caught by any route
   registered before it. Hence, for ``login`` and ``logout`` views to
   have the opportunity of being matched (or "caught"), they must be above
   ``/{pagename}``.


Add login, logout, and forbidden views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a new file ``tutorial/views/auth.py``, and add the following code to it:

.. literalinclude:: src/authentication/tutorial/views/auth.py
   :linenos:
   :language: python

This code adds three new views to the application:

- The ``login`` view renders a login form and processes the post from the
  login form, checking credentials against our ``users`` table in the database.

  The check is done by first finding a ``User`` record in the database, then
  using our ``user.check_password`` method to compare the hashed passwords.

  If the credentials are valid, then we use our authentication policy to store
  the user's id in the response using :meth:`pyramid.security.remember`.

  Finally, the user is redirected back to either the page which they were
  trying to access (``next``) or the front page as a fallback. This parameter
  is used by our forbidden view, as explained below, to finish the login
  workflow.

- The ``logout`` view handles requests to ``/logout`` by clearing the
  credentials using :meth:`pyramid.security.forget`, then redirecting them to
  the front page.

- The ``forbidden_view`` is registered using the
  :class:`pyramid.view.forbidden_view_config` decorator. This is a special
  :term:`exception view`, which is invoked when a
  :class:`pyramid.httpexceptions.HTTPForbidden` exception is raised.

  This view will handle a forbidden error by redirecting the user to
  ``/login``. As a convenience, it also sets the ``next=`` query string to the
  current URL (the one that is forbidding access). This way, if the user
  successfully logs in, they will be sent back to the page which they had been
  trying to access.


Add the ``login.jinja2`` template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create ``tutorial/templates/login.jinja2`` with the following content:

.. literalinclude:: src/authentication/tutorial/templates/login.jinja2
   :language: html

The above template is referenced in the login view that we just added in
``tutorial/views/auth.py``.


Add "Login" and "Logout" links
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``tutorial/templates/layout.jinja2`` and add the following code as
indicated by the highlighted lines.

.. literalinclude:: src/authentication/tutorial/templates/layout.jinja2
   :lines: 35-46
   :lineno-match:
   :emphasize-lines: 2-10
   :language: html

The ``request.user`` will be ``None`` if the user is not authenticated, or a
``tutorial.models.User`` object if the user is authenticated. This check will
make the logout link shown only when the user is logged in, and conversely the
login link is only shown when the user is logged out.


Viewing the application in a browser
------------------------------------

We can finally examine our application in a browser (See
:ref:`wiki2-start-the-application`).  Launch a browser and visit each of the
following URLs, checking that the result is as expected:

- http://localhost:6543/ invokes the ``view_wiki`` view.  This always
  redirects to the ``view_page`` view of the ``FrontPage`` page object.  It
  is executable by any user.

- http://localhost:6543/FrontPage invokes the ``view_page`` view of the
  ``FrontPage`` page object. There is a "Login" link in the upper right corner
  while the user is not authenticated, else it is a "Logout" link when the user
  is authenticated.

- http://localhost:6543/FrontPage/edit_page invokes the ``edit_page`` view for
  the ``FrontPage`` page object.  It is executable by only the ``editor`` user.
  If a different user (or the anonymous user) invokes it, then a login form
  will be displayed. Supplying the credentials with the username ``editor`` and
  password ``editor`` will display the edit page form.

- http://localhost:6543/add_page/SomePageName invokes the ``add_page`` view for
  a page. If the page already exists, then it redirects the user to the
  ``edit_page`` view for the page object. It is executable by either the
  ``editor`` or ``basic`` user.  If a different user (or the anonymous user)
  invokes it, then a login form will be displayed. Supplying the credentials
  with either the username ``editor`` and password ``editor``, or username
  ``basic`` and password ``basic``, will display the edit page form.

- http://localhost:6543/SomePageName/edit_page invokes the ``edit_page`` view
  for an existing page, or generates an error if the page does not exist. It is
  editable by the ``basic`` user if the page was created by that user in the
  previous step. If, instead, the page was created by the ``editor`` user, then
  the login page should be shown for the ``basic`` user.

- After logging in (as a result of hitting an edit or add page and submitting
  the login form with the ``editor`` credentials), we'll see a "Logout" link in
  the upper right hand corner.  When we click it, we're logged out, redirected
  back to the front page, and a "Login" link is shown in the upper right hand
  corner.
