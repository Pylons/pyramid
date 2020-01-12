.. _wiki_adding_authorization:

=======================================
Adding authorization and authentication
=======================================

:app:`Pyramid` provides facilities for :term:`authentication` and :term:`authorization`.
We will make use of both features to provide security to our application.
Our application currently allows anyone with access to the server to view, edit, and add pages to our wiki.
We will change that to allow only people who are members of a *group* named ``group:editors`` to add and edit wiki pages.
We will continue to allow anyone with access to the server to view pages.

We will also add a login page and a logout link on all the pages.
The login page will be shown when a user is denied access to any of the views that
require permission, instead of a default "403 Forbidden" page.

We will implement the access control with the following steps:

-   Add password hashing dependencies.
-   Add users and groups (``security.py``, a new module).
-   Add a :term:`security policy` (``security.py``).
-   Add an :term:`ACL` (``models.py``).
-   Add :term:`permission` declarations to the ``edit_page`` and ``add_page`` views (``views.py``).

Then we will add the login and logout features:

-   Add ``login`` and ``logout`` views (``views.py``).
-   Add a login template (``login.pt``).
-   Make the existing views return a ``logged_in`` flag to the renderer (``views.py``).
-   Add a "Logout" link to be shown when logged in and viewing or editing a page (``view.pt``, ``edit.pt``).


Access control
--------------


Add dependencies
~~~~~~~~~~~~~~~~

Just like in :ref:`wiki_defining_views`, we need a new dependency.
We need to add the `bcrypt <https://pypi.org/project/bcrypt/>`_ package to our tutorial package's ``setup.py`` file by assigning this dependency to the ``requires`` parameter in the ``setup()`` function.

Open ``setup.py`` and edit it to look like the following:

.. literalinclude:: src/authorization/setup.py
    :lines: 11-30
    :lineno-match:
    :emphasize-lines: 2
    :language: python

Only the highlighted line needs to be added.

Do not forget to run ``pip install -e .`` just like in :ref:`wiki-running-pip-install`.

.. note::

    We are using the ``bcrypt`` package from PyPI to hash our passwords securely.
    There are other one-way hash algorithms for passwords if bcrypt is an issue on your system.
    Just make sure that it is an algorithm approved for storing passwords versus a generic one-way hash.


Add the security policy
~~~~~~~~~~~~~~~~~~~~~~~

Create a new ``tutorial/security.py`` module with the following content:

.. literalinclude:: src/authorization/tutorial/security.py
    :linenos:
    :language: python

Since we've added a new ``tutorial/security.py`` module, we need to include it.
Open the file ``tutorial/__init__.py`` and edit the following lines:

.. literalinclude:: src/authorization/tutorial/__init__.py
    :linenos:
    :emphasize-lines: 21
    :language: python

The security policy controls several aspects of authentication and authorization:

- Identifying the current user / :term:`identity` for a ``request``.

- Authorizating access to resources.

- Creating payloads for remembering and forgetting users.


Identifying logged-in users
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``MySecurityPolicy.authenticated_identity`` method inspects the ``request`` and determines if it came from an authenticated user.
It does this by utilizing the :class:`pyramid.authentication.AuthTktCookieHelper` class which stores the :term:`identity` in a cryptographically-signed cookie.
If a ``request`` does contain an identity then we perform a final check to determine if the user is valid in our current ``USERS`` store.


Authorizing access to resources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``MySecurityPolicy.permits`` method determines if the ``request`` is allowed a specific ``permission`` on the given ``context``.
This process is done in a few steps:

- Convert the ``request`` into a list of :term:`principals <principal>` via the ``MySecurityPolicy.effective_principals`` method.

- Compare the list of principals to the ``context`` using the :class:`pyramid.authorization.ACLHelper`.
  It will only allow access if it can find an :term:`ACE` that grants one of the principals the necessary permission.

For our application we've defined a list of a few principals:

- ``u:<userid>``
- ``group:editor``
- :attr:`pyramid.security.Authenticated`
- :attr:`pyramid.security.Everyone`

Later, various wiki pages will grant some of these principals access to edit, or add new pages.

Finally, there are two helper methods that will help us later to authenticate users.
The first is ``hash_password`` which takes a raw password and transforms it using
bcrypt into an irreversible representation, a process known as "hashing".
The second method, ``check_password``, will allow us to compare the hashed value of the submitted password against the hashed value of the password stored in the user's
record.
If the two hashed values match, then the submitted password is valid, and we can authenticate the user.

We hash passwords so that it is impossible to decrypt and use them to authenticate in the application.
If we stored passwords foolishly in clear text, then anyone with access to the database could retrieve any password to authenticate as any user.

In a production system, user and group data will most often be saved and come from a
database.
Here we use "dummy" data to represent user and groups sources.


Add new settings
~~~~~~~~~~~~~~~~

Our authentication policy is expecting a new setting, ``auth.secret``. Open
the file ``development.ini`` and add the highlighted line below:

.. literalinclude:: src/authorization/development.ini
   :lines: 19-21
   :emphasize-lines: 3
   :lineno-match:
   :language: ini

Finally, best practices tell us to use a different secret in each environment, so
open ``production.ini`` and add a different secret:

.. literalinclude:: src/authorization/production.ini
   :lines: 17-19
   :emphasize-lines: 3
   :lineno-match:
   :language: ini

And ``testing.ini``:

.. literalinclude:: src/authorization/testing.ini
   :lines: 17-19
   :emphasize-lines: 3
   :lineno-match:
   :language: ini


Add an ACL
~~~~~~~~~~

Open ``tutorial/models/__init__.py`` and add the following import statement near the top:

.. literalinclude:: src/authorization/tutorial/models/__init__.py
    :lines: 4-7
    :lineno-match:
    :language: python

Add the following lines to the ``Wiki`` class:

.. literalinclude:: src/authorization/tutorial/models/__init__.py
    :pyobject: Wiki
    :lineno-match:
    :emphasize-lines: 4-7
    :language: python

We import :data:`~pyramid.security.Allow`, an action which means that
permission is allowed.
We also import :data:`~pyramid.security.Everyone`, a special :term:`principal` that is associated to all requests.
Both are used in the :term:`ACE` entries that make up the ACL.

The ACL is a list that needs to be named ``__acl__`` and be an attribute of a class.
We define an :term:`ACL` with two :term:`ACE` entries.
The first entry allows any user the ``view`` permission.
The second entry allows the ``group:editors`` principal the ``edit`` permission.

The ``Wiki`` class that contains the ACL is the :term:`resource` constructor for the :term:`root` resource, which is a ``Wiki`` instance.
The ACL is provided to each view in the :term:`context` of the request as the ``context`` attribute.

It is only happenstance that we assigned this ACL at class scope.
An ACL can be attached to an object *instance* too.
This is how "row level security" can be achieved in :app:`Pyramid` applications.
We actually need only *one* ACL for the entire system, however, because our security requirements are simple, so this feature is not demonstrated.

.. seealso::

    See :ref:`assigning_acls` for more information about what an :term:`ACL` represents.


Add permission declarations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``tutorial/views/default.py`` and add a ``permission='edit'`` parameter to the ``@view_config`` decorators for ``add_page()`` and ``edit_page()``:

.. literalinclude:: src/authorization/tutorial/views/default.py
    :lines: 39-41
    :lineno-match:
    :emphasize-lines: 2-3
    :language: python

.. literalinclude:: src/authorization/tutorial/views/default.py
    :lines: 58-60
    :lineno-match:
    :emphasize-lines: 2-3
    :language: python

Only the highlighted lines, along with their preceding commas, need to be edited and added.

The result is that only users who possess the ``edit`` permission at the time of the request may invoke those two views.

Add a ``permission='view'`` parameter to the ``@view_config`` decorator for
``view_wiki()`` as follows:

.. literalinclude:: src/authorization/tutorial/views/default.py
    :lines: 12
    :lineno-match:
    :emphasize-lines: 1
    :language: python

And ``view_page()`` as follows:

.. literalinclude:: src/authorization/tutorial/views/default.py
    :lines: 17-19
    :lineno-match:
    :emphasize-lines: 2-3
    :language: python

Only the highlighted lines, along with their preceding commas, need to be edited and added.

This allows anyone to invoke these two views.

We are done with the changes needed to control access.
The changes that follow will add the login and logout feature.


Login, logout
-------------


Add login and logout views
~~~~~~~~~~~~~~~~~~~~~~~~~~

We will add a ``login`` view which renders a login form and processes the post from the login form, checking credentials.

We will also add a ``logout`` view callable to our application and provide a link to it.
This view will clear the credentials of the logged in user and redirect back to the front page.

Add a new file ``tutorial/views/auth.py`` with the following contents:

.. literalinclude:: src/authorization/tutorial/views/auth.py
    :lineno-match:
    :language: python

:meth:`~pyramid.view.forbidden_view_config` will be used to customize the default 403 Forbidden page.
:meth:`~pyramid.security.remember` and :meth:`~pyramid.security.forget` help to create and expire an auth ticket cookie.

``login()`` has two decorators:

-   A ``@view_config`` decorator which associates it with the ``login`` route and makes it visible when we visit ``/login``.
-   A ``@forbidden_view_config`` decorator which turns it into a :term:`forbidden view`.
    ``login()`` will be invoked when a user tries to execute a view callable for which they lack authorization.
    For example, if a user has not logged in and tries to add or edit a Wiki page, then they will be shown the login form before being allowed to continue.

The order of these two :term:`view configuration` decorators is unimportant.

``logout()`` is decorated with a ``@view_config`` decorator which associates it with the ``logout`` route.
It will be invoked when we visit ``/logout``.


Add the ``login.pt`` Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create ``tutorial/templates/login.pt`` with the following content:

.. literalinclude:: src/authorization/tutorial/templates/login.pt
    :language: html

The above template is referenced in the login view that we just added in ``views.py``.


Add a "Login" and "Logout" links
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``tutorial/templates/layout.pt`` and add the following code as indicated by the highlighted lines.

.. literalinclude:: src/authorization/tutorial/templates/layout.pt
    :lines: 34-43
    :lineno-match:
    :emphasize-lines: 2-9
    :language: html

The attribute ``tal:condition="logged_in"`` will make the element be included when ``logged_in`` is any user id.
The link will invoke the logout view.
The above element will not be included if ``logged_in`` is ``None``, such as when
a user is not authenticated.


Viewing the application in a browser
------------------------------------

We can finally examine our application in a browser (See :ref:`wiki-start-the-application`).
Launch a browser and visit each of the following URLs, checking that the result is as expected:

-   http://localhost:6543/ invokes the ``view_wiki`` view.
    This always redirects to the ``view_page`` view of the ``FrontPage`` Page resource.
    It is executable by any user.

-   http://localhost:6543/FrontPage invokes the ``view_page`` view of the ``FrontPage`` Page resource.
    This is because it is the :term:`default view` (a view without a ``name``) for ``Page`` resources.
    It is executable by any user.

-   http://localhost:6543/FrontPage/edit_page invokes the edit view for the FrontPage object.
    It is executable by only the ``editor`` user.
    If a different user (or the anonymous user) invokes it, then a login form will be displayed.
    Supplying the credentials with the username ``editor`` and password ``editor`` will display the edit page form.

-   http://localhost:6543/add_page/SomePageName invokes the add view for a page.
    It is executable by only the ``editor`` user.
    If a different user (or the anonymous user) invokes it, a login form will be displayed.
    Supplying the credentials with the username ``editor``, password ``editor`` will display the edit page form.

-   After logging in (as a result of hitting an edit or add page and submitting the login form with the ``editor`` credentials), we will see a Logout link in the upper right hand corner.
    When we click it, we are logged out, and redirected back to the front page.

-   To generate a not found error, visit http://localhost:6543/wakawaka which will invoke the ``notfound_view`` view provided by the cookiecutter.
