.. _wiki_adding_authorization:

====================
Adding authorization
====================

:app:`Pyramid` provides facilities for :term:`authentication` and :term:`authorization`. We'll make use of both features to provide security to our application. Our application currently allows anyone with access to the server to view, edit, and add pages to our wiki. We'll change that to allow only people who are members of a *group* named ``group:editors`` to add and edit wiki pages, but we'll continue allowing anyone with access to the server to view pages.

We will also add a login page and a logout link on all the pages.  The login page will be shown when a user is denied access to any of the views that require permission, instead of a default "403 Forbidden" page.

We will implement the access control with the following steps:

* Add password hashing dependencies.
* Add users and groups (``security.py``, a new module).
* Add an :term:`ACL` (``models.py``).
* Add an :term:`authentication policy` and an :term:`authorization policy` (``__init__.py``).
* Add :term:`permission` declarations to the ``edit_page`` and ``add_page`` views (``views.py``).

Then we will add the login and logout features:

* Add ``login`` and ``logout`` views (``views.py``).
* Add a login template (``login.pt``).
* Make the existing views return a ``logged_in`` flag to the renderer (``views.py``).
* Add a "Logout" link to be shown when logged in and viewing or editing a page (``view.pt``, ``edit.pt``).


Access control
--------------


Add dependencies
^^^^^^^^^^^^^^^^

Just like in :ref:`wiki_defining_views`, we need a new dependency. We need to add the `bcrypt <https://pypi.python.org/pypi/bcrypt>`_ package, to our tutorial package's ``setup.py`` file by assigning this dependency to the ``requires`` parameter in the ``setup()`` function.

Open ``setup.py`` and edit it to look like the following:

.. literalinclude:: src/authorization/setup.py
    :linenos:
    :emphasize-lines: 21
    :language: python

Only the highlighted line needs to be added.

Do not forget to run ``pip install -e .`` just like in :ref:`wiki-running-pip-install`.

.. note::

   We are using the ``bcrypt`` package from PyPI to hash our passwords securely. There are other one-way hash algorithms for passwords if bcrypt is an issue on your system. Just make sure that it's an algorithm approved for storing passwords versus a generic one-way hash.


Add users and groups
^^^^^^^^^^^^^^^^^^^^

Create a new ``pyramidtut/security.py`` module with the following content:

.. literalinclude:: src/authorization/pyramidtut/security.py
    :linenos:
    :language: python

The ``groupfinder`` function accepts a userid and a request and returns one of these values:

- If ``userid`` exists in the system, it will return a sequence of group identifiers (or an empty sequence if the user isn't a member of any groups).
- If ``userid`` *does not* exist in the system, it will return ``None``.

For example, ``groupfinder('editor', request )`` returns ``['group:editor']``, ``groupfinder('viewer', request)`` returns ``[]``, and ``groupfinder('admin', request)`` returns ``None``.  We will use ``groupfinder()`` as an :term:`authentication policy` "callback" that will provide the :term:`principal` or principals for a user.

There are two helper methods that will help us later to authenticate users. The first is ``hash_password`` which takes a raw password and transforms it using bcrypt into an irreversible representation, a process known as "hashing". The second method, ``check_password``, will allow us to compare the hashed value of the submitted password against the hashed value of the password stored in the user's record. If the two hashed values match, then the submitted password is valid, and we can authenticate the user.

We hash passwords so that it is impossible to decrypt and use them to authenticate in the application. If we stored passwords foolishly in clear text, then anyone with access to the database could retrieve any password to authenticate as any user.

In a production system, user and group data will most often be saved and come from a database, but here we use "dummy" data to represent user and groups sources.


Add an ACL
^^^^^^^^^^

Open ``pyramidtut/models.py`` and add the following import statement near the top:

.. literalinclude:: src/authorization/pyramidtut/models.py
    :lines: 4-8
    :lineno-match:
    :language: python

Add the following lines to the ``Wiki`` class:

.. literalinclude:: src/authorization/pyramidtut/models.py
    :lines: 9-13
    :lineno-match:
    :emphasize-lines: 4-5
    :language: python

We import :data:`~pyramid.security.Allow`, an action that means that permission is allowed, and :data:`~pyramid.security.Everyone`, a special :term:`principal` that is associated to all requests.  Both are used in the :term:`ACE` entries that make up the ACL.

The ACL is a list that needs to be named ``__acl__`` and be an attribute of a class.  We define an :term:`ACL` with two :term:`ACE` entries: the first entry allows any user the ``view`` permission.  The second entry allows the ``group:editors`` principal the ``edit`` permission.

The ``Wiki`` class that contains the ACL is the :term:`resource` constructor for the :term:`root` resource, which is a ``Wiki`` instance.  The ACL is provided to each view in the :term:`context` of the request as the ``context`` attribute.

It's only happenstance that we're assigning this ACL at class scope.  An ACL can be attached to an object *instance* too; this is how "row level security" can be achieved in :app:`Pyramid` applications.  We actually need only *one* ACL for the entire system, however, because our security requirements are simple, so this feature is not demonstrated.  See :ref:`assigning_acls` for more information about what an :term:`ACL` represents.


Add authentication and authorization policies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open ``pyramidtut/__init__.py`` and add the highlighted import statements:

.. literalinclude:: src/authorization/pyramidtut/__init__.py
    :lines: 1-8
    :linenos:
    :emphasize-lines: 3-6,8
    :language: python

Now add those policies to the configuration:

.. literalinclude:: src/authorization/pyramidtut/__init__.py
    :lines: 18-23
    :linenos:
    :lineno-match:
    :emphasize-lines: 1-3,5-6
    :language: python

Only the highlighted lines need to be added.

We are enabling an ``AuthTktAuthenticationPolicy``, which is based in an auth ticket that may be included in the request. We are also enabling an ``ACLAuthorizationPolicy``, which uses an ACL to determine the *allow* or *deny* outcome for a view.

Note that the :class:`pyramid.authentication.AuthTktAuthenticationPolicy` constructor accepts two arguments: ``secret`` and ``callback``.  ``secret`` is a string representing an encryption key used by the "authentication ticket" machinery represented by this policy: it is required.  The ``callback`` is the ``groupfinder()`` function that we created before.


Add permission declarations
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open ``pyramidtut/views.py`` and add a ``permission='edit'`` parameter to the ``@view_config`` decorators for ``add_page()`` and ``edit_page()``:

.. literalinclude:: src/authorization/pyramidtut/views.py
    :lines: 49-51
    :emphasize-lines: 2-3
    :language: python

.. literalinclude:: src/authorization/pyramidtut/views.py
    :lines: 68-70
    :emphasize-lines: 2-3
    :language: python

Only the highlighted lines, along with their preceding commas, need to be edited and added.

The result is that only users who possess the ``edit`` permission at the time of the request may invoke those two views.

Add a ``permission='view'`` parameter to the ``@view_config`` decorator for ``view_wiki()`` and ``view_page()`` as follows:

.. literalinclude:: src/authorization/pyramidtut/views.py
    :lines: 23-24
    :emphasize-lines: 1-2
    :language: python

.. literalinclude:: src/authorization/pyramidtut/views.py
    :lines: 28-29
    :emphasize-lines: 1-2
    :language: python

Only the highlighted lines, along with their preceding commas, need to be edited and added.

This allows anyone to invoke these two views.

We are done with the changes needed to control access.  The changes that follow will add the login and logout feature.


Login, logout
-------------


Add login and logout views
^^^^^^^^^^^^^^^^^^^^^^^^^^

We'll add a ``login`` view which renders a login form and processes the post from the login form, checking credentials.

We'll also add a ``logout`` view callable to our application and provide a link to it.  This view will clear the credentials of the logged in user and redirect back to the front page.

Remove the import statement ``from pyramid.view import view_config``, and add the following import statements to the head of ``pyramidtut/views.py``:

.. literalinclude:: src/authorization/pyramidtut/views.py
    :lines: 5-18
    :emphasize-lines: 1-14
    :language: python

All the highlighted lines need to be added or edited.

:meth:`~pyramid.view.forbidden_view_config` will be used to customize the default 403 Forbidden page. :meth:`~pyramid.security.remember` and :meth:`~pyramid.security.forget` help to create and expire an auth ticket cookie.

Now add the ``login`` and ``logout`` views at the end of the file:

.. literalinclude:: src/authorization/pyramidtut/views.py
    :lines: 80-
    :lineno-match:
    :language: python

``login()`` has two decorators:

- a ``@view_config`` decorator which associates it with the ``login`` route and makes it visible when we visit ``/login``,
- a ``@forbidden_view_config`` decorator which turns it into a :term:`forbidden view`. ``login()`` will be invoked when a user tries to execute a view callable for which they lack authorization.  For example, if a user has not logged in and tries to add or edit a Wiki page, they will be shown the login form before being allowed to continue.

The order of these two :term:`view configuration` decorators is unimportant.

``logout()`` is decorated with a ``@view_config`` decorator which associates it with the ``logout`` route.  It will be invoked when we visit ``/logout``.


Add the ``login.pt`` template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create ``pyramidtut/templates/login.pt`` with the following content:

.. literalinclude:: src/authorization/pyramidtut/templates/login.pt
    :language: html

The above template is referenced in the login view that we just added in ``views.py``.


Return a ``logged_in`` flag to the renderer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open ``pyramidtut/views.py`` again. Add a ``logged_in`` parameter to the return value of ``view_page()``, ``add_page()``, and ``edit_page()`` as follows:

.. literalinclude:: src/authorization/pyramidtut/views.py
    :lines: 46-47
    :emphasize-lines: 1-2
    :language: python

.. literalinclude:: src/authorization/pyramidtut/views.py
    :lines: 65-66
    :emphasize-lines: 1-2
    :language: python

.. literalinclude:: src/authorization/pyramidtut/views.py
    :lines: 76-78
    :emphasize-lines: 2-3
    :language: python

Only the highlighted lines need to be added or edited.

The :meth:`pyramid.request.Request.authenticated_userid` will be ``None`` if the user is not authenticated, or a userid if the user is authenticated.


Add a "Logout" link when logged in
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open ``pyramidtut/templates/edit.pt`` and ``pyramidtut/templates/view.pt`` and add the following code as indicated by the highlighted lines.

.. literalinclude:: src/authorization/pyramidtut/templates/edit.pt
    :lines: 35-39
    :emphasize-lines: 3-5
    :language: html

The attribute ``tal:condition="logged_in"`` will make the element be included when ``logged_in`` is any user id. The link will invoke the logout view.  The above element will not be included if ``logged_in`` is ``None``, such as when a user is not authenticated.


Reviewing our changes
---------------------

Our ``pyramidtut/__init__.py`` will look like this when we're done:

.. literalinclude:: src/authorization/pyramidtut/__init__.py
    :linenos:
    :emphasize-lines: 4-5,8,18-20,22-23
    :language: python

Only the highlighted lines need to be added or edited.

Our ``pyramidtut/models.py`` will look like this when we're done:

.. literalinclude:: src/authorization/pyramidtut/models.py
    :linenos:
    :emphasize-lines: 4-7,12-13
    :language: python

Only the highlighted lines need to be added or edited.

Our ``pyramidtut/views.py`` will look like this when we're done:

.. literalinclude:: src/authorization/pyramidtut/views.py
    :linenos:
    :emphasize-lines: 8,11-15,17,24,29,47,51,66,70,78,80-
    :language: python

Only the highlighted lines need to be added or edited.

Our ``pyramidtut/templates/edit.pt`` template will look like this when we're done:

.. literalinclude:: src/authorization/pyramidtut/templates/edit.pt
    :linenos:
    :emphasize-lines: 37-39
    :language: html

Only the highlighted lines need to be added or edited.

Our ``pyramidtut/templates/view.pt`` template will look like this when we're done:

.. literalinclude:: src/authorization/pyramidtut/templates/view.pt
    :linenos:
    :emphasize-lines: 37-39
    :language: html

Only the highlighted lines need to be added or edited.


Viewing the application in a browser
------------------------------------

We can finally examine our application in a browser (See :ref:`wiki-start-the-application`).  Launch a browser and visit each of the following URLs, checking that the result is as expected:

- http://localhost:6543/ invokes the ``view_wiki`` view.  This always redirects to the ``view_page`` view of the ``FrontPage`` Page resource.  It is executable by any user.
- http://localhost:6543/FrontPage invokes the ``view_page`` view of the ``FrontPage`` Page resource. This is because it's the :term:`default view` (a view without a ``name``) for ``Page`` resources.  It is executable by any user.
- http://localhost:6543/FrontPage/edit_page invokes the edit view for the FrontPage object.  It is executable by only the ``editor`` user.  If a different user (or the anonymous user) invokes it, a login form will be displayed.  Supplying the credentials with the username ``editor``, password ``editor`` will display the edit page form.
- http://localhost:6543/add_page/SomePageName invokes the add view for a page. It is executable by only the ``editor`` user.  If a different user (or the anonymous user) invokes it, a login form will be displayed. Supplying the credentials with the username ``editor``, password ``editor`` will display the edit page form.
- After logging in (as a result of hitting an edit or add page and submitting the login form with the ``editor`` credentials), we'll see a Logout link in the upper right hand corner.  When we click it, we're logged out, and redirected back to the front page.
