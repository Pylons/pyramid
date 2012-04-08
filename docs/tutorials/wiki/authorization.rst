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
* Add an :term:`ACL` (``models.py``).
* Add an :term:`authentication policy` and an :term:`authorization policy`
  (``__init__.py``).
* Add :term:`permission` declarations to the ``edit_page`` and ``add_page``
  views (``views.py``).

Then we will add the login and logout feature:

* Add ``login`` and ``logout`` views (``views.py``).
* Add a login template (``login.pt``).
* Make the existing views return a ``logged_in`` flag to the renderer (``views.py``).
* Add a "Logout" link to be shown when logged in and viewing or editing a page
  (``view.pt``, ``edit.pt``).

The source code for this tutorial stage can be browsed via
`http://github.com/Pylons/pyramid/tree/1.3-branch/docs/tutorials/wiki/src/authorization/
<http://github.com/Pylons/pyramid/tree/1.3-branch/docs/tutorials/wiki/src/authorization/>`_.

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
statements at the head:

.. literalinclude:: src/authorization/tutorial/models.py
   :lines: 4-5
   :linenos:
   :language: python

Add the following lines at class scope to the ``Wiki`` class:

.. literalinclude:: src/authorization/tutorial/models.py
   :lines: 7-11
   :linenos:
   :emphasize-lines: 4-5
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

The ``Wiki`` class that contains the ACL is the :term:`resource`
constructor for the :term:`root` resource, which is
a ``Wiki`` instance.  The ACL is
provided to each view in the :term:`context` of the request, as
the ``context`` attribute.

It's only happenstance that we're assigning this ACL at class scope.  An ACL
can be attached to an object *instance* too; this is how "row level security"
can be achieved in :app:`Pyramid` applications.  We actually only need *one*
ACL for the entire system, however, because our security requirements are
simple, so this feature is not demonstrated.  See
:ref:`assigning_acls` for more information about what an
:term:`ACL` represents.

Add Authentication and Authorization Policies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``tutorial/__init__.py`` and
add these import statements:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :lines: 4-5,8
   :linenos:
   :language: python

Now add those policies to the configuration:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :lines: 17-22
   :linenos:
   :emphasize-lines: 1-3,5-6
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

Add Login and Logout Views
~~~~~~~~~~~~~~~~~~~~~~~~~~

We'll add a ``login`` view which renders a login form and processes
the post from the login form, checking credentials.

We'll also add a ``logout`` view to our application and provide a link
to it.  This view will clear the credentials of the logged in user and
redirect back to the front page.

We'll add these views to the existing ``views.py`` file we have in our
project.  Here's what the ``login`` view callable will look like:

.. literalinclude:: src/authorization/tutorial/views.py
   :lines: 86-113
   :linenos:
   :language: python

Here's what the ``logout`` view callable will look like:

.. literalinclude:: src/authorization/tutorial/views.py
   :lines: 115-119
   :linenos:
   :language: python

Note that the ``login`` view callable has *two* view configuration
decorators.  The order of these decorators is unimportant.  Each just adds a
different :term:`view configuration` for the ``login`` view callable.

The first view configuration decorator configures the ``login`` view callable
so it will be invoked when someone visits ``/login`` (when the context is a
Wiki and the view name is ``login``).  The second decorator, named
``forbidden_view_config`` specifies a :term:`forbidden view`.  This
configures our login view to be presented to the user when :app:`Pyramid`
detects that a view invocation can not be authorized.  Because we've
configured a forbidden view, the ``login`` view callable will be invoked
whenever one of our users tries to execute a view callable that they are not
allowed to invoke as determined by the :term:`authorization policy` in use.
In our application, for example, this means that if a user has not logged in,
and he tries to add or edit a Wiki page, he will be shown the login form.
Before being allowed to continue on to the add or edit form, he will have to
provide credentials that give him permission to add or edit via this login
form.

Note that we're relying on some additional imports within the bodies of these
views (e.g. ``remember`` and ``forget``).  We'll see a rendering of the
entire views.py file a little later here to show you where those come from.

Add the ``login.pt`` Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add a ``login.pt`` template to your templates directory.  It's
referred to within the login view we just added to ``views.py``.

.. literalinclude:: src/authorization/tutorial/templates/login.pt
   :language: xml

Return a logged_in flag to the renderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to indicate whether the current user is logged in, we need to change
each of our ``view_page``, ``edit_page`` and ``add_page`` views in
``views.py`` to pass a "logged in" parameter into its template.  We'll add
something like this to each view body:

.. code-block:: python
   :linenos:

   from pyramid.security import authenticated_userid
   logged_in = authenticated_userid(request)

We'll then change the return value of each view that has an associated
``renderer`` to pass the resulting ``logged_in`` value to the
template.  For example:

.. code-block:: python
   :linenos:

   return dict(page = context,
               content = content,
               logged_in = logged_in,
               edit_url = edit_url)

Add a "Logout" link when logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We'll also need to change our ``edit.pt`` and ``view.pt`` templates to
display a "Logout" link if someone is logged in.  This link will
invoke the logout view.

To do so we'll add this to both templates within the ``<div id="right"
class="app-welcome align-right">`` div:

.. code-block:: xml

   <span tal:condition="logged_in">
      <a href="${request.application_url}/logout">Logout</a>
   </span>

Seeing Our Changes
------------------

When you're done, your ``__init__.py`` will
look like so:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :linenos:
   :emphasize-lines: 4-5,8,17-19,21-22
   :language: python

Our ``models.py`` file will look like this:

.. literalinclude:: src/authorization/tutorial/models.py
   :linenos:
   :emphasize-lines: 4-5,10-11
   :language: python

Our ``views.py`` module will look something like this when we're done:

.. literalinclude:: src/authorization/tutorial/views.py
   :linenos:
   :emphasize-lines: 8,11-15,24,29,50,54,71,75,85,87-120
   :language: python

Our ``edit.pt`` template will look something like this when we're done:

.. literalinclude:: src/authorization/tutorial/templates/edit.pt
   :linenos:
   :emphasize-lines: 41-43
   :language: xml

Our ``view.pt`` template will look something like this when we're done:

.. literalinclude:: src/authorization/tutorial/templates/view.pt
   :linenos:
   :emphasize-lines: 41-43
   :language: xml


Viewing the Application in a Browser
------------------------------------

We can finally examine our application in a browser (See
:ref:`wiki-start-the-application`).  Launch a browser and visit
each of the following URLs, check that the result is as expected:

- ``http://localhost:6543/`` invokes the
  ``view_wiki`` view.  This always redirects to the ``view_page`` view
  of the ``FrontPage`` Page resource.  It is executable by any user.

- ``http://localhost:6543/FrontPage`` invokes
  the ``view_page`` view of the ``FrontPage`` Page resource. This is because
  it's the :term:`default view` (a view without a ``name``) for ``Page``
  resources.  It is executable by any user.

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
