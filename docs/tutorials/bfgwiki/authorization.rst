====================
Adding Authorization
====================

Our application currently allows anyone with access to the server to
view, edit, and add pages to our wiki.  For purposes of demonstration
we'll change our application to allow people whom possess a specific
username (`editor`) to add and edit wiki pages but we'll continue
allowing anyone with access to the server to view pages.

:mod:`repoze.bfg` provides a facility for *authorization*, but it
relies on "upstream" software to provide *authentication* information.
We're going to use a package named ``repoze.who`` to our setup, and
we'll rely on it to give us authentication information.

Adding a Dependency on ``repoze.who`` to Our ``setup.py`` File
--------------------------------------------------------------

We need to change our ``setup.py`` file, adding a dependency on the
``repoze.who`` package.  The ``repoze.who`` package provides a
mechanism for providing *authentication* data via :term:`WSGI`
middleware.  We'll add the ``repoze.who`` package to our ``requires``
list.

The resulting setup.py file:

.. literalinclude:: src/authorization/setup.py
   :linenos:
   :language: python

Changing our ``tutorial.ini`` file to Include the ``repoze.who`` Middleware
---------------------------------------------------------------------------

In order to make use of the ``repoze.who`` middleware which provides
authentication services, we need to wire it into our ``tutorial.ini``
file.  We'll add a ``[filter:who]`` section to our ``tutorial.ini``
file and wire it into our pipeline.  Our resulting ``tutorial.ini``
file will look like so:

.. literalinclude:: src/authorization/tutorial.ini
   :linenos:
   :language: ini

Note that we added a ``who`` line to our pipeline.  This refers to the
``[filter:who]`` section above it.  The ``[filter:who]`` section has a
``use`` line that points at an egg entry point for configuring the
repoze.who middleware via a config file.  The ``config_file`` line
points at an .ini config file named ``who.ini``.  This file is assumed
to live in the same directory as the ``tutorial.ini`` file.  We'll
need to create this file in order to get authentication working.

Adding a ``who.ini`` File
-------------------------

We'll create a file in our package directory named ``who.ini``.  It
will have the following contents.

.. literalinclude:: src/authorization/who.ini
   :linenos:
   :language: ini

The ``[general]``, ``[identifiers]``, ``[authenticators]``, and
``[challengers]`` section of this file are the meat of the
configuration in this file.

The ``[general]`` Section
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``[general]`` section configures the default "request classifier"
and "challenge decider".  For the purposes of this tutorial, it is not
important that you understand these settings.

The ``[identifiers]`` Section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``[identifiers]`` section configures the identifier plugins that
will be used for this application.  In our case, our identifiers are
both the ``form`` plugin (configured above the ``[identifiers]``
section within ``[plugin:form]``) and the ``auth_tkt`` plugin
(configured above the ``[identifiers]`` section within
``[plugin:auth_tkt]``.  The ``form`` identifier will only be used when
the request is a "browser request" (for example, it *won't* be used
when the request is an XML-RPC request).

The ``[authenticators]`` Section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``[authenticators]`` section configures the "authenticator"
plugins that will be used in our setup.  An authenticator plugin is
one which checks a username and password provided by a user against a
database of valid username/password combinations.  We'll use an
htpasswd file as this database.  Since the ``htpasswd`` plugin
requires a file, we'll need to add a ``wiki.passwd`` file to our
``tutorial`` package with these contents:

.. literalinclude:: src/authorization/wiki.passwd
   :linenos:
   :language: ini

The ``[challengers]`` Section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``[challengers]`` section configures a "challenger" which is a
``repoze.who`` plugin which displays a login form.  We'll use the
standard ``repoze.who.plugins.form`` plugin for this, configured
within the ``[plugin:form]`` section of the file.

The ``[plugin:*]`` Sections
---------------------------

The ``[plugin:*]`` sections of the configuration file configure
individual plugins used by the more general configuration sections
(``[identifiers]``, ``[authenticators]``, ``[challengers]``).  The
``auth_tkt`` plugin is an identifier plugin which obtains credentials
from a cookie, the ``form`` plugin is an identifier and challenger
plugin which obtains credentials from a form post, the ``htpasswd``
plugin is an authenticator plugin which checks credentials against
valid usernames and files specified in an htpasswd file.

Configuring a ``repoze.bfg`` Authentication Policy
--------------------------------------------------

For any :mod:`repoze.bfg` application to perform authorization, we
need to change our ``run.py`` module to add an :term:`authentication
policy`.  Adding an authentication policy causes the system to use
authorization.

Change your run.py to import the ``RepozeWho1AuthenticationPolicy``
from ``repoze.who.authentication``, construct an instance of the
policy, and pass it as the ``authentication_policy`` argument to the
``make_app`` function.  When you're done, your application's
``run.py`` will look like this.

.. literalinclude:: src/authorization/tutorial/run.py
   :linenos:
   :language: python

Giving Our Root Model Object an ACL
-----------------------------------

We need to give our root model object an ACL.  This ACL will be
sufficient to provide enough information to the BFG security machinery
to challenge a user who doesn't have appropriate credentials when he
attempts to invoke the ``add_page`` or ``edit_page`` views.

We need to perform some imports at module scope in our ``models.py``
file:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Allow
   from repoze.bfg.security import Everyone

Our root model is a ``Wiki`` object.  We'll add the following line at
class scope to our ``Wiki`` class:

.. code-block:: python
   :linenos:

   __acl__ = [ (Allow, Everyone, 'view'), (Allow, 'editor', 'edit') ]

It's only happenstance that we're assigning this ACL at class scope.
An ACL can be attached to an object *instance* too; this is how "row
level security" can be achieved in :mod:`repoze.bfg` applications.  We
actually only need *one* ACL for the entire system, however, because
our security requirements are simple, so this feature is not
demonstrated.

Our resulting ``models.py`` file will now look like so:

.. literalinclude:: src/authorization/tutorial/models.py
   :linenos:
   :language: python

Adding ``permission`` Declarations to our ``bfg_view`` Decorators
-----------------------------------------------------------------

To protect each of our views with a particular permission, we need to
pass a ``permission`` argument to each of our ``bfg_view`` decorators.
To do so, within ``views.py``:

- We add ``permission='view'`` to the ``bfg_view`` decorator attached
  to the ``static_view`` view function.  This makes the assertion that
  only users who possess the effective ``view`` permission at the time
  of the request may invoke this view.  We've granted ``Everyone`` the
  view permission at the root model via its ACL, so everyone will be
  able to invoke the ``static_view`` view.

- We add ``permission='view'`` to the ``bfg_view`` decorator attached
  to the ``view_wiki`` view function. This makes the assertion that
  only users who possess the effective ``view`` permission at the time
  of the request may invoke this view.  We've granted ``Everyone`` the
  view permission at the root model via its ACL, so everyone will be
  able to invoke the ``view_wiki`` view.

- We add ``permission='view'`` to the ``bfg_view`` decorator attached
  to the ``view_page`` view function.  This makes the assertion that
  only users who possess the effective ``view`` permission at the time
  of the request may invoke this view.  We've granted ``Everyone`` the
  view permission at the root model via its ACL, so everyone will be
  able to invoke the ``view_page`` view.

- We add ``permission='edit'`` to the ``bfg_view`` decorator attached
  to the ``add_page`` view function.  This makes the assertion that
  only users who possess the effective ``view`` permission at the time
  of the request may invoke this view.  We've granted ``editor`` the
  view permission at the root model via its ACL, so only the user
  named ``editor`` will able to invoke the ``add_page`` view.

- We add ``permission='edit'`` to the ``bfg_view`` decorator attached
  to the ``edit_page`` view function.  This makes the assertion that
  only users who possess the effective ``view`` permission at the time
  of the request may invoke this view.  We've granted ``editor`` the
  view permission at the root model via its ACL, so only the user
  named ``editor`` will able to invoke the ``edit_page`` view.

Viewing the Application in a Browser
------------------------------------

Once we've set up the WSGI pipeline properly, we can finally examine
our application in a browser.  The views we'll try are as follows:

- Visiting `http://localhost:6543/ <http://localhost:6543/>`_ in a
  browser invokes the ``view_wiki`` view.  This always redirects to
  the ``view_page`` view of the FrontPage page object.  It is
  executable by any user.

- Visiting `http://localhost:6543/FrontPage/
  <http://localhost:6543/FrontPage/>`_ in a browser invokes the
  ``view_page`` view of the front page page object.  This is because
  it's the *default view* (a view without a ``name``) for Page
  objects.  It is executable by any user.

- Visiting `http://localhost:6543/FrontPage/edit_page
  <http://localhost:6543/FrontPage/edit_page>`_ in a browser invokes
  the edit view for the front page object.  It is executable by only
  the ``editor`` user.  If a different user (or the anonymous user)
  invokes it, a login form will be displayed.  Supplying the
  credentials with the username ``editor``, password ``editor`` will
  show the edit page form being displayed.

- Visiting `http://localhost:6543/add_page/SomePageName
  <http://localhost:6543/add_page/SomePageName>`_ in a browser invokes
  the add view for a page.  It is executable by only the ``editor``
  user.  If a different user (or the anonymous user) invokes it, a
  login form will be displayed.  Supplying the credentials with the
  username ``editor``, password ``editor`` will show the edit page
  form being displayed.

Add A Logout View
-------------------

We'll add a ``logout`` view to our application and provide a link to
it.  This view will clear the credentials of the logged in user and
redirect back to the front page.  The logout view will look someting
like this:

.. code-block:: python
   :linenos:

   @bfg_view(for_=Wiki, name='logout')
   def logout(context, request):
       identity = request.environ.get('repoze.who.identity')
       headers = []
       if identity is not None:
           auth_tkt = request.environ['repoze.who.plugins']['auth_tkt']
           headers = auth_tkt.forget(request.environ, identity)
       return HTTPFound(location = model_url(context, request),
                        headers = headers)


We'll also change our ``edit.pt`` template to display a "Logout" link
if someone is logged in.  This link will invoke the logout view.

To do so we'll add this to both templates within the ``<div
class="main_content">`` div:

.. code-block:: xml
   :linenos:

   <span tal:condition="logged_in"><a href="${request.application_url}/logout">Logout</a></span>

Then we need to change each opf our ``view_page``, ``edit_page`` and
``add_page`` views to pass a "logged in" parameter into its template.
We'll add something like this to each view body:

.. code-block:: python
   :linenos:

   logged_in = 'repoze.who.identity' in request.environ

We'll then change the return value of ``render_template_to_response``
to pass the `resulting `logged_in`` value to the template, e.g.:

.. code-block:: python
   :linenos:

   return render_template_to_response('templates/view.pt',
                                      request = request,
                                      page = context,
                                      content = content,
                                      logged_in = logged_in,
                                      edit_url = edit_url)

Seeing Our Changes To ``views.py`` and our Templates
----------------------------------------------------

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

Revisiting the Application
---------------------------

When we revisit the application in a browser, and log in (as a result
of hitting an edit or add page and submitting the login form with the
``editor`` credentials), we'll see a Logout link in the upper right
hand corner.  When we click it, we're logged out, and redirected back
to the front page.



