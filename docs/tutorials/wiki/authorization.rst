====================
Adding Authorization
====================

Our application currently allows anyone with access to the server to view,
edit, and add pages to our wiki.  For purposes of demonstration we'll change
our application to allow people who are members of a *group* named
``group:editors`` to add and edit wiki pages but we'll continue allowing
anyone with access to the server to view pages.  :app:`Pyramid` provides
facilities for :term:`authorization` and :term:`authentication`.  We'll make
use of both features to provide security to our application.

We will add an :term:`authentication policy` and an
:term:`authorization policy` to our :term:`application
registry`, add a ``security.py`` module and give our :term:`root`
resource an :term:`ACL`.

Then we will add ``login`` and ``logout`` views, and modify the
existing views to make them return a ``logged_in`` flag to the
renderer and add :term:`permission` declarations to their ``view_config``
decorators.

Finally, we will add a ``login.pt`` template and change the existing
``view.pt`` and ``edit.pt`` to show a "Logout" link when not logged in.

The source code for this tutorial stage can be browsed via
`http://github.com/Pylons/pyramid/tree/master/docs/tutorials/wiki/src/authorization/
<http://github.com/Pylons/pyramid/tree/master/docs/tutorials/wiki/src/authorization/>`_.

Add Authentication and Authorization Policies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We'll change our package's ``__init__.py`` file to enable an
``AuthTktAuthenticationPolicy`` and an ``ACLAuthorizationPolicy`` to enable
declarative security checking. We need to import the new policies:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :lines: 4-5,8
   :linenos:
   :language: python

Then, we'll add those policies to the configuration:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :lines: 17-22
   :linenos:
   :language: python

Note that the creation of an ``AuthTktAuthenticationPolicy`` requires two
arguments: ``secret`` and ``callback``.  ``secret`` is a string representing
an encryption key used by the "authentication ticket" machinery represented
by this policy: it is required.  The ``callback`` is a reference to a
``groupfinder`` function in the ``tutorial`` package's ``security.py`` file.
We haven't added that module yet, but we're about to.

When you're done, your ``__init__.py`` will
look like so:

.. literalinclude:: src/authorization/tutorial/__init__.py
   :linenos:
   :language: python

Add ``security.py``
~~~~~~~~~~~~~~~~~~~

Add a ``security.py`` module within your package (in the same
directory as ``__init__.py``, ``views.py``, etc.) with the following
content:

.. literalinclude:: src/authorization/tutorial/security.py
   :linenos:
   :language: python

The ``groupfinder`` function defined here is an :term:`authentication policy`
"callback"; it is a callable that accepts a userid and a request.  If the
userid exists in the system, the callback will return a sequence of group
identifiers (or an empty sequence if the user isn't a member of any groups).
If the userid *does not* exist in the system, the callback will return
``None``.  In a production system, user and group data will most often come
from a database, but here we use "dummy" data to represent user and groups
sources. Note that the ``editor`` user is a member of the ``group:editors``
group in our dummy group data (the ``GROUPS`` data structure).

Give Our Root Resource an ACL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We need to give our root resource object an :term:`ACL`.  This ACL will be
sufficient to provide enough information to the :app:`Pyramid` security
machinery to challenge a user who doesn't have appropriate credentials when
he attempts to invoke the ``add_page`` or ``edit_page`` views.

We need to perform some imports at module scope in our ``models.py`` file:

.. code-block:: python
   :linenos:

   from pyramid.security import Allow
   from pyramid.security import Everyone

Our root resource object is a ``Wiki`` instance.  We'll add the following
line at class scope to our ``Wiki`` class:

.. code-block:: python
   :linenos:

   __acl__ = [ (Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit') ]

It's only happenstance that we're assigning this ACL at class scope.  An ACL
can be attached to an object *instance* too; this is how "row level security"
can be achieved in :app:`Pyramid` applications.  We actually only need *one*
ACL for the entire system, however, because our security requirements are
simple, so this feature is not demonstrated.

Our resulting ``models.py`` file will now look like so:

.. literalinclude:: src/authorization/tutorial/models.py
   :linenos:
   :language: python

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

Change Existing Views
~~~~~~~~~~~~~~~~~~~~~

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

Add ``permission`` Declarations to our ``view_config`` Decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To protect each of our views with a particular permission, we need to pass a
``permission`` argument to each of our :class:`pyramid.view.view_config`
decorators.  To do so, within ``views.py``:

- We add ``permission='view'`` to the decorator attached to the
  ``view_wiki`` and ``view_page`` view functions. This makes the
  assertion that only users who possess the ``view`` permission
  against the context resource at the time of the request may
  invoke these views.  We've granted
  :data:`pyramid.security.Everyone` the view permission at the
  root model via its ACL, so everyone will be able to invoke the
  ``view_wiki`` and ``view_page`` views.

- We add ``permission='edit'`` to the decorator attached to the
  ``add_page`` and ``edit_page`` view functions.  This makes the
  assertion that only users who possess the effective ``edit``
  permission against the context resource at the time of the
  request may invoke these views.  We've granted the
  ``group:editors`` principal the ``edit`` permission at the
  root model via its ACL, so only a user whom is a member of
  the group named ``group:editors`` will able to invoke the
  ``add_page`` or  ``edit_page`` views.  We've likewise given
  the ``editor`` user membership to this group via the
  ``security.py`` file by mapping him to the ``group:editors``
  group in the ``GROUPS`` data structure (``GROUPS
  = {'editor':['group:editors']}``); the ``groupfinder``
  function consults the ``GROUPS`` data structure.  This means
  that the ``editor`` user can add and edit pages.

Add the ``login.pt`` Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add a ``login.pt`` template to your templates directory.  It's
referred to within the login view we just added to ``views.py``.

.. literalinclude:: src/authorization/tutorial/templates/login.pt
   :language: xml

Change ``view.pt`` and ``edit.pt``
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

See Our Changes To ``views.py`` and our Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Our ``views.py`` module will look something like this when we're done:

.. literalinclude:: src/authorization/tutorial/views.py
   :linenos:
   :language: python

Our ``edit.pt`` template will look something like this when we're done:

.. literalinclude:: src/authorization/tutorial/templates/edit.pt
   :linenos:
   :language: xml

Our ``view.pt`` template will look something like this when we're done:

.. literalinclude:: src/authorization/tutorial/templates/view.pt
   :linenos:
   :language: xml

View the Application in a Browser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can finally examine our application in a browser.  The views we'll try are
as follows:

- Visiting ``http://localhost:6543/`` in a browser invokes the ``view_wiki``
  view.  This always redirects to the ``view_page`` view of the ``FrontPage``
  page resource.  It is executable by any user.

- Visiting ``http://localhost:6543/FrontPage/`` in a browser invokes the
  ``view_page`` view of the ``FrontPage`` Page resource.  This is because
  it's the :term:`default view` (a view without a ``name``) for ``Page``
  resources.  It is executable by any user.

- Visiting ``http://localhost:6543/FrontPage/edit_page`` in a browser invokes
  the edit view for the ``FrontPage`` Page resource.  It is executable by
  only the ``editor`` user.  If a different user (or the anonymous user)
  invokes it, a login form will be displayed.  Supplying the credentials with
  the username ``editor``, password ``editor`` will show the edit page form
  being displayed.

- Visiting ``http://localhost:6543/add_page/SomePageName`` in a
  browser invokes the add view for a page.  It is executable by only
  the ``editor`` user.  If a different user (or the anonymous user)
  invokes it, a login form will be displayed.  Supplying the
  credentials with the username ``editor``, password ``editor`` will
  show the edit page form being displayed.

- After logging in (as a result of hitting an edit or add page and
  submitting the login form with the ``editor`` credentials), we'll see
  a Logout link in the upper right hand corner.  When we click it,
  we're logged out, and redirected back to the front page.
