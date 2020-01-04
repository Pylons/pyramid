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
-   Add an :term:`ACL` (``models.py``).
-   Add an :term:`authentication policy` and an :term:`authorization policy` (``__init__.py``).
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
    :linenos:
    :emphasize-lines: 23
    :language: python

Only the highlighted line needs to be added.

Do not forget to run ``pip install -e .`` just like in :ref:`wiki-running-pip-install`.

.. note::

    We are using the ``bcrypt`` package from PyPI to hash our passwords securely.
    There are other one-way hash algorithms for passwords if bcrypt is an issue on your system.
    Just make sure that it is an algorithm approved for storing passwords versus a generic one-way hash.


Add users and groups
~~~~~~~~~~~~~~~~~~~~

Create a new ``tutorial/security.py`` module with the following content:

.. literalinclude:: src/authorization/tutorial/security.py
    :linenos:
    :language: python

The ``groupfinder`` function accepts a ``userid`` and a ``request``
It returns one of these values:

-   If ``userid`` exists in the system, it will return either a sequence of group identifiers, or an empty sequence if the user is not a member of any groups.
-   If the userid *does not* exist in the system, it will return ``None``.

For example:

-   ``groupfinder('editor', request )`` returns ``['group:editor']``.
-   ``groupfinder('viewer', request)`` returns ``[]``.
-   ``groupfinder('admin', request)`` returns ``None``.

We will use ``groupfinder()`` as an :term:`authentication policy` "callback" that will provide the :term:`principal` or principals for a user.

There are two helper methods that will help us later to authenticate users.
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


Add an ACL
~~~~~~~~~~

Open ``tutorial/models/__init__.py`` and add the following import statement near the top:

.. literalinclude:: src/authorization/tutorial/models/__init__.py
    :lines: 4-8
    :lineno-match:
    :language: python

Add the following lines to the ``Wiki`` class:

.. literalinclude:: src/authorization/tutorial/models/__init__.py
    :lines: 9-13
    :lineno-match:
    :emphasize-lines: 4-5
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


Add authentication and authorization policies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``tutorial/__init__.py`` and add the highlighted import
statements:

.. literalinclude:: src/authorization/tutorial/__init__.py
    :lines: 1-8
    :linenos:
    :emphasize-lines: 3-6,8
    :language: python

Now add those policies to the configuration:

.. literalinclude:: src/authorization/tutorial/__init__.py
    :lines: 15-25
    :lineno-match:
    :emphasize-lines: 4-6,8-9
    :language: python

Only the highlighted lines need to be added.

We enabled an ``AuthTktAuthenticationPolicy`` which is based in an auth ticket that may be included in the request.
We also enabled an ``ACLAuthorizationPolicy`` which uses an ACL to determine the *allow* or *deny* outcome for a view.

Note that the :class:`pyramid.authentication.AuthTktAuthenticationPolicy` constructor accepts two arguments: ``secret`` and ``callback``.
``secret`` is a string representing an encryption key used by the "authentication ticket" machinery represented by this policy.
It is required.
The ``callback`` is the ``groupfinder()`` function that we created earlier.


Add permission declarations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``tutorial/views/default.py`` and add a ``permission='edit'`` parameter to the ``@view_config`` decorators for ``add_page()`` and ``edit_page()``:

.. literalinclude:: src/authorization/tutorial/views/default.py
    :lines: 49-51
    :emphasize-lines: 2-3
    :language: python

.. literalinclude:: src/authorization/tutorial/views/default.py
    :lines: 69-71
    :emphasize-lines: 2-3
    :language: python

Only the highlighted lines, along with their preceding commas, need to be edited and added.

The result is that only users who possess the ``edit`` permission at the time of the request may invoke those two views.

Add a ``permission='view'`` parameter to the ``@view_config`` decorator for
``view_wiki()`` and ``view_page()`` as follows:

.. literalinclude:: src/authorization/tutorial/views/default.py
    :lines: 21-22
    :emphasize-lines: 1-2
    :language: python

.. literalinclude:: src/authorization/tutorial/views/default.py
    :lines: 27-28
    :emphasize-lines: 1-2
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

Add the following import statements to the head of ``tutorial/views/default.py``:

.. literalinclude:: src/authorization/tutorial/views/default.py
    :lines: 4-15
    :emphasize-lines: 2-10,12
    :language: python

All the highlighted lines need to be added or edited.

:meth:`~pyramid.view.forbidden_view_config` will be used to customize the default 403 Forbidden page.
:meth:`~pyramid.security.remember` and :meth:`~pyramid.security.forget` help to create and expire an auth ticket cookie.

Now add the ``login`` and ``logout`` views at the end of the file:

.. literalinclude:: src/authorization/tutorial/views/default.py
    :lines: 78-
    :lineno-match:
    :language: python

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


Return a ``logged_in`` flag to the renderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``tutorial/views/default.py`` again.
Add a ``logged_in`` parameter to the return value of ``view_page()``, ``add_page()``, and ``edit_page()`` as follows:

.. literalinclude:: src/authorization/tutorial/views/default.py
    :lines: 45-46
    :emphasize-lines: 1-2
    :language: python

.. literalinclude:: src/authorization/tutorial/views/default.py
    :lines: 65-66
    :emphasize-lines: 1-2
    :language: python

.. literalinclude:: src/authorization/tutorial/views/default.py
    :lines: 77-79
    :emphasize-lines: 2-3
    :language: python

Only the highlighted lines need to be added or edited.

The :meth:`pyramid.request.Request.authenticated_userid` will be ``None`` if the user is not authenticated, or a ``userid`` if the user is authenticated.


Add a "Logout" link when logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``tutorial/templates/edit.pt`` and ``tutorial/templates/view.pt``.
Add the following code as indicated by the highlighted lines.

.. literalinclude:: src/authorization/tutorial/templates/edit.pt
    :lines: 4-8
    :emphasize-lines: 2-4
    :language: html

The attribute ``tal:condition="logged_in"`` will make the element be included when ``logged_in`` is any user id.
The link will invoke the logout view.
The above element will not be included if ``logged_in`` is ``None``, such as when
a user is not authenticated.


Reviewing our changes
---------------------

Our ``tutorial/__init__.py`` will look like this when we are done:

.. literalinclude:: src/authorization/tutorial/__init__.py
    :linenos:
    :emphasize-lines: 3-6,8,18-20,22-23
    :language: python

Only the highlighted lines need to be added or edited.

Our ``tutorial/models/__init__.py`` will look like this when we are done:

.. literalinclude:: src/authorization/tutorial/models/__init__.py
    :linenos:
    :emphasize-lines: 4-8,12-13
    :language: python

Only the highlighted lines need to be added or edited.

Our ``tutorial/views/default.py`` will look like this when we are done:

.. literalinclude:: src/authorization/tutorial/views/default.py
    :linenos:
    :emphasize-lines: 5-12,15,21-22,27-28,45-46,50-51,65-66,70-71,78-
    :language: python

Only the highlighted lines need to be added or edited.

Our ``tutorial/templates/edit.pt`` template will look like this when we are done:

.. literalinclude:: src/authorization/tutorial/templates/edit.pt
    :linenos:
    :emphasize-lines: 5-7
    :language: html

Only the highlighted lines need to be added or edited.

Our ``tutorial/templates/view.pt`` template will look like this when we are done:

.. literalinclude:: src/authorization/tutorial/templates/view.pt
    :linenos:
    :emphasize-lines: 5-7
    :language: html

Only the highlighted lines need to be added or edited.

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
