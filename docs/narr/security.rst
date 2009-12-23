.. _security_chapter:

Security
========

:mod:`repoze.bfg` provides an optional declarative authorization
system that prevents a :term:`view` from being invoked when the user
represented by credentials in the :term:`request` does not have an
appropriate level of access with respect to a specific
:term:`context`.

Authorization is enabled by modifying your application to include a
:term:`authentication policy` and :term:`authorization policy`.

Enabling an Authorization Policy Imperatively
---------------------------------------------

By default, :mod:`repoze.bfg` enables no authorization policy.  All
views are accessible by completely anonymous users.

However, if you use the ``authorization_policy`` argument to the
constructor of the :class:`repoze.bfg.configuration.Configurator`
class, you can enable an authorization policy.

You must also enable an :term:`authentication policy` in order to
enable the an authorization policy (this is because authorization, in
general, depends upon authentication).  Use the
``authorization_policy`` argument to the
:class:`repoze.bfg.configuration.Configurator` class during
application setup to specify an authentication policy.

For example:

.. code-block:: python
   :linenos:

   from repoze.bfg.configuration import Configurator
   from repoze.bfg.authentication import AuthTktAutenticationPolicy
   from repoze.bfg.authorization import ACLAuthorizationPolicy
   authentication_policy = AuthTktAuthenticationPolicy('seekrit')
   authorization_policy = ACLAuthorizationPolicy()
   config = Configurator(authentication_policy=authentication_policy,
                         authorization_policy=authorization_policy)

The above configuration enables a policy which compares the value of
an "auth ticket" cookie passed in the request's environment which
contains a reference to a single :term:`principal` against the
principals present in any :term:`ACL` found in model data when
attempting to call some :term:`view`.

While it is possible to mix and match different authentication and
authorization policies, it is an error to pass an authentication
policy without the an authorization policy or vice versa to a
:term:`Configurator` constructor.

See also the :mod:`repoze.bfg.authorization` and
:mod:`repoze.bfg.authentication` modules for alternate implementations
of authorization and authentication policies.  

It is also possible to construct your own custom authentication policy
or authorization policy: see :ref:`creating_an_authentication_policy`
and :ref:`creating_an_authorization_policy`.

Enabling an Authorization Policy Via ZCML
-----------------------------------------

If you'd rather use :term:`ZCML` to specify an authorization policy
than imperative configuration, modify the ZCML file loaded by your
application (usually named ``configure.zcml``) to enable an
authorization one.

For example, to enable a policy which compares the value of an "auth
ticket" cookie passed in the request's environment which contains a
reference to a single :term:`principal` against the principals present
in any :term:`ACL` found in model data when attempting to call some
:term:`view`, modify your ``configure.zcml`` to look something like
this:

.. code-block:: xml
   :linenos:

   <configure xmlns="http://namespaces.repoze.org/bfg">

     <!-- views and other directives before this... -->

     <authtktauthenticationpolicy
          secret="iamsosecret"/>

     <aclauthorizationpolicy/>

    </configure>

"Under the hood", these statements cause an instance of the class
:class:`repoze.bfg.authentication.AuthTktAuthenticationPolicy` to be
injected as the :term:`authentication policy` used by this application
and an instance of the class
:class:`repoze.bfg.authorization.ACLAuthorizationPolicy` to be
injected as the :term:`authorization policy` used by this application.

:mod:`repoze.bfg` ships with a number of authorization and
authentication policy ZCML directives that should prove useful.  See
:ref:`authentication_policies_directives_section` and
:ref:`authorization_policies_directives_section` for more information.

Protecting Views with Permissions
---------------------------------

You declaratively protect a particular view using a :term:`permission`
name via the ``configure.zcml`` application registry.  For example,
the following declaration protects the view named ``add_entry.html``
when invoked against a ``Blog`` context with the ``add`` permission:

.. code-block:: xml
   :linenos:

   <view
       for=".models.Blog"
       view=".views.blog_entry_add_view"
       name="add_entry.html"
       permission="add"
       />

The equivalent view registration including the 'add' permission name
may be performed via the ``bfg_view`` decorator within the "views"
module of your project's package

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view
   from models import Blog

   @bfg_view(for_=Blog, name='add_entry.html', permission='add')
   def blog_entry_add_view(request):
       """ Add blog entry code goes here """
       pass

If an authorization policy is in place when this view is found during
normal application operations, the user will need to possess the
``add`` permission against the context to be able to invoke the
``blog_entry_add_view`` view.

Permission names are usually just strings.  They hold no special
significance to the system.  You can name permissions whatever you
like.

.. _assigning_acls:

Assigning ACLs to your Model Objects
------------------------------------

When :mod:`repoze.bfg` determines whether a user possesses a
particular permission in a :term:`context`, it examines the
:term:`ACL` associated with the context.  An ACL is associated with a
context by virtue of the ``__acl__`` attribute of the model object
representing the context.  This attribute can be defined on the model
*instance* (if you need instance-level security), or it can be defined
on the model *class* (if you just need type-level security).

For example, an ACL might be attached to model for a blog via its
class:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Everyone
   from repoze.bfg.security import Allow

   class Blog(object):
       __acl__ = [
           (Allow, Everyone, 'view'),
           (Allow, 'group:editors', 'add'),
           (Allow, 'group:editors', 'edit'),
           ]

Or, if your models are persistent, an ACL might be specified via the
``__acl__`` attribute of an *instance* of a model:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Everyone
   from repoze.bfg.security import Allow

   class Blog(object):
       pass

   blog = Blog()

   blog.__acl__ = [
           (Allow, Everyone, 'view'),
           (Allow, 'group:editors', 'add'),
           (Allow, 'group:editors', 'edit'),
           ]

Whether an ACL is attached to a model's class or an instance of the
model itself, the effect is the same.  It is useful to decorate
individual model instances with an ACL (as opposed to just decorating
their class) in applications such as "CMS" systems where fine-grained
access is required on an object-by-object basis.

Elements of an ACL
------------------

Here's an example ACL:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Everyone
   from repoze.bfg.security import Allow

   __acl__ = [
           (Allow, Everyone, 'view'),
           (Allow, 'group:editors', 'add'),
           (Allow, 'group:editors', 'edit'),
           ]

The example ACL indicates that the ``Everyone`` principal (a special
system-defined principal indicating, literally, everyone) is allowed
to view the blog, the ``group:editors`` principal is allowed to add to
and edit the blog.

The third argument in an ACE can also be a sequence of permission
names instead of a single permission name.  So instead of creating
multiple ACEs representing a number of different permission grants to
a single ``group:editors`` group, we can collapse this into a single
ACE, as below.

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Everyone
   from repoze.bfg.security import Allow

   __acl__ = [
       (Allow, Everyone, 'view'),
       (Allow, 'group:editors', ('add', 'edit')),
       ]

A principal is usually a user id, however it also may be a group id if
your authentication system provides group information and the
effective :term:`authentication policy` policy is written to respect
group information.  For example, the
:class:`repoze.bfg.authentication.RepozeWho1AuthenicationPolicy`
enabled by the ``repozewho1authenticationpolicy`` ZCML directive
respects group information if you configure it with a ``callback``.
See :ref:`authentication_policies_directives_section` for more
information about the ``callback`` attribute.

Each tuple within an ACL structure is known as a :term:`ACE`, which
stands for "access control entry".  For example, in the above ACL,
``(Allow, Everyone, 'view')`` is an ACE.  Each ACE in an ACL is
processed by an authorization policy *in the order dictated by the
ACL*.  So if you have an ACL like this:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Everyone
   from repoze.bfg.security import Allow
   from repoze.bfg.security import Deny

   __acl__ = [
       (Allow, Everyone, 'view'),
       (Deny, Everyone, 'view'),
       ]

The authorization policy will *allow* everyone the view permission,
even though later in the ACL you have an ACE that denies everyone the
view permission.  On the other hand, if you have an ACL like this:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Everyone
   from repoze.bfg.security import Allow
   from repoze.bfg.security import Deny

   __acl__ = [
       (Deny, Everyone, 'view'),
       (Allow, Everyone, 'view'),
       ]

The authorization policy will deny Everyone the view permission, even
though later in the ACL is an ACE that allows everyone.

Special Principal Names
-----------------------

Special principal names exist in the :mod:`repoze.bfg.security`
module.  They can be imported for use in your own code to populate
ACLs, e.g. :data:`repoze.bfg.security.Everyone`.

:data:`repoze.bfg.security.Everyone`

  Literally, everyone, no matter what.  This object is actually a
  string "under the hood" (``system.Everyone``).  Every user "is" the
  principal named Everyone during every request, even if a security
  policy is not in use.

:data:`repoze.bfg.security.Authenticated`

  Any user with credentials as determined by the current security
  policy.  You might think of it as any user that is "logged in".
  This object is actually a string "under the hood"
  (``system.Authenticated``).

Special Permissions
-------------------

Special permission names exist in the :mod:`repoze.bfg.security`
module.  These can be imported for use in ACLs.

.. _all_permissions:

:data:`repoze.bfg.security.ALL_PERMISSIONS`

  An object representing, literally, *all* permissions.  Useful in an
  ACL like so: ``(Allow, 'fred', ALL_PERMISSIONS)``.  The
  ``ALL_PERMISSIONS`` object is actually a stand-in object that has a
  ``__contains__`` method that always returns True, which, for all
  known authorization policies, has the effect of indicating that a
  given principal "has" any permission asked for by the system.

Special ACEs
------------

A convenience :term:`ACE` is defined within the
:mod:`repoze.bfg.security` module named
:data:`repoze.bfg.security.DENY_ALL`.  It equals the following:

.. code-block:: python

   from repoze.bfg.security import ALL_PERMISSIONS
   (Deny, Everyone, ALL_PERMISSIONS)

This ACE is often used as the *last* ACE of an ACL to explicitly cause
inheriting authorization policies to "stop looking up the traversal
tree" (effectively breaking any inheritance).  For example, an ACL
which allows *only* ``fred`` the view permission in a particular
traversal context despite what inherited ACLs may say when the default
authorization policy is in effect might look like so:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Allow
   from repoze.bfg.security import DENY_ALL

   __acl__ = [ (Allow, 'fred', 'view'), DENY_ALL ]

ACL Inheritance
---------------

While the default :term:`authorization policy` is in place, if a model
object does not have an ACL when it is the context, its *parent* is
consulted for an ACL.  If that object does not have an ACL, *its*
parent is consulted for an ACL, ad infinitum, until we've reached the
root and there are no more parents left.

Location-Awareness
------------------

In order to allow the security machinery to perform ACL inheritance,
model objects must provide :term:`location` -awareness.  Providing
*location-awareness* means two things: the root object in the graph
must have a ``_name__`` attribute and a ``__parent__`` attribute.

.. code-block:: python
   :linenos:

   class Blog(object):
       __name__ = ''
       __parent__ = None

An object with a ``__parent__`` attribute and a ``__name__`` attribute
is said to be *location-aware*.  Location-aware objects define an
``__parent__`` attribute which points at their parent object.  The
root object's ``__parent__`` is ``None``.

See :ref:`location_module` for documentations of functions which use
location-awareness.  See also :ref:`location_aware`.

Changing the Forbidden View
---------------------------

When :mod:`repoze.bfg` denies a view invocation due to an
authorization denial, the special ``forbidden`` view is invoked.  "Out
of the box", this forbidden view is very plain.  See
:ref:`changing_the_forbidden_view` within :ref:`hooks_chapter` for
instructions on how to create a custom forbidden view and arrange for
it to be called when view authorization is denied.

.. _debug_authorization_section:

Debugging View Authorization Failures
-------------------------------------

If your application in your judgment is allowing or denying view
access inappropriately, start your application under a shell using the
``BFG_DEBUG_AUTHORIZATION`` environment variable set to ``1``.  For
example::

  $ BFG_DEBUG_AUTHORIZATION=1 bin/paster serve myproject.ini

When any authorization takes place during a top-level view rendering,
a message will be logged to the console (to stderr) about what ACE in
which ACL permitted or denied the authorization based on
authentication information.

This behavior can also be turned on in the application ``.ini`` file
by setting the ``debug_authorization`` key to ``true`` within the
application's configuration section, e.g.::

  [app:main]
  use = egg:MyProject#app
  debug_authorization = true

With this debug flag turned on, the response sent to the browser will
also contain security debugging information in its body.

Debugging Imperative Authorization Failures
-------------------------------------------

The :func:`repoze.bfg.security.has_permission` API is used to check
security within view functions imperatively.  It returns instances of
objects that are effectively booleans.  But these objects are not raw
``True`` or ``False`` objects, and have information attached to them
about why the permission was allowed or denied.  The object will be
one of :data:`repoze.bfg.security.ACLAllowed`,
:data:`repoze.bfg.security.ACLDenied`,
:data:`repoze.bfg.security.Allowed`, or
:data:`repoze.bfg.security.Denied`, as documented in
:ref:`security_module`.  At very minimum these objects will have a
``msg`` attribute, which is a string indicating why permission was
denied or allowed.  Introspecting this information in the debugger or
via print statements when a call to
:func:`repoze.bfg.security.has_permission` fails is often useful.

.. _authentication_policies_directives_section:

Built-In Authentication Policy ZCML Directives
----------------------------------------------

Instead of configuring an authentication policy and authorization
policy imperatively, :mod:`repoze.bfg` ships with a few "pre-chewed"
authentication policy ZCML directives that you can make use of within
your application.

``authtktauthenticationpolicy``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When this directive is used, authentication information is obtained
from an "auth ticket" cookie value, assumed to be set by a custom
login form.

An example of its usage, with all attributes fully expanded:

.. code-block:: xml
   :linenos:

   <authtktauthenticationpolicy
    secret="goshiamsosecret"
    callback=".somemodule.somefunc"
    cookie_name="mycookiename"
    secure="false"
    include_ip="false"
    timeout="86400"
    reissue_time="600"
    max_age="31536000"
    />

The ``secret`` is a string that will be used to encrypt the data
stored by the cookie.  It is required and has no default.

The ``callback`` is a Python dotted name to a function passed the
string representing the userid stored in the cookie and the request as
positional arguments.  The callback is expected to return None if the
user represented by the string doesn't exist or a sequence of group
identifiers (possibly empty) if the user does exist.  If ``callback``
is None, the userid will be assumed to exist with no groups.  It
defaults to ``None``.

The ``cookie_name`` is the name used for the cookie that contains the
user information.  It defaults to ``repoze.bfg.auth_tkt``.

``secure`` is a boolean value.  If it's set to "true", the cookie will
only be sent back by the browser over a secure (HTTPS) connection.
It defaults to "false".

``include_ip`` is a boolean value.  If it's set to true, the
requesting IP address is made part of the authentication data in the
cookie; if the IP encoded in the cookie differs from the IP of the
requesting user agent, the cookie is considered invalid.  It defaults
to "false".

``timeout`` is an integer value.  It represents the maximum age in
seconds which the auth_tkt ticket will be considered valid.  If
``timeout`` is specified, and ``reissue_time`` is also specified,
``reissue_time`` must be a smaller value than ``timeout``.  It
defaults to ``None``, meaning that the ticket will be considered valid
forever.

``reissue_time`` is an integer value.  If ``reissue_time`` is
specified, when we encounter a cookie that is older than the reissue
time (in seconds), but younger that the ``timeout``, a new cookie will
be issued.  It defaults to ``None``, meaning that authentication
cookies are never reissued.  A value of ``0`` means reissue a cookie
in the response to every request that requires authentication.

``max_age`` is the maximum age of the auth_tkt *cookie*, in seconds.
This differs from ``timeout`` inasmuch as ``timeout`` represents the
lifetime of the ticket contained in the cookie, while this value
represents the lifetime of the cookie itself.  When this value is set,
the cookie's ``Max-Age`` and ``Expires`` settings will be set,
allowing the auth_tkt cookie to last between browser sessions.  It is
typically nonsensical to set this to a value that is lower than
``timeout`` or ``reissue_time``, although it is not explicitly
prevented.  It defaults to ``None``, meaning (on all major browser
platforms) that auth_tkt cookies will last for the lifetime of the
user's browser session.

``remoteuserauthenticationpolicy``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When this directive is used, authentication information is obtained
from a ``REMOTE_USER`` key in the WSGI environment, assumed to
be set by a WSGI server or an upstream middleware component.

An example of its usage, with all attributes fully expanded:

.. code-block:: xml
   :linenos:

   <remoteuserauthenticationpolicy
    environ_key="REMOTE_USER"
    callback=".somemodule.somefunc"
    />

The ``environ_key`` is the name that will be used to obtain the remote
user value from the WSGI environment.  It defaults to ``REMOTE_USER``.

The ``callback`` is a Python dotted name to a function passed the
string representing the remote user and the request as positional
arguments.  The callback is expected to return None if the user
represented by the string doesn't exist or a sequence of group
identifiers (possibly empty) if the user does exist.  If ``callback``
is None, the userid will be assumed to exist with no groups.  It
defaults to ``None``.

``repozewho1authenticationpolicy``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When this directive is used, authentication information is obtained
from a ``repoze.who.identity`` key in the WSGI environment, assumed to
be set by :term:`repoze.who` middleware.

An example of its usage, with all attributes fully expanded:

.. code-block:: xml
   :linenos:

   <repozewho1authenticationpolicy
    identifier_name="auth_tkt"
    callback=".somemodule.somefunc"
    />

The ``identifier_name`` controls the name used to look up the
:term:`repoze.who` "identifier" plugin within
``request.environ['repoze.who.plugins']`` which is used by this policy to
"remember" and "forget" credentials.  It defaults to ``auth_tkt``.

The ``callback`` is a Python dotted name to a function passed the
repoze.who identity and the request as positional arguments.  The
callback is expected to return None if the user represented by the
identity doesn't exist or a sequence of group identifiers (possibly
empty) if the user does exist.  If ``callback`` is None, the userid
will be assumed to exist with no groups.   It defaults to ``None``.


.. _authorization_policies_directives_section:

Built-In Authorization Policy ZCML Directives
---------------------------------------------

``aclauthorizationpolicy``

When this directive is used, authorization information is obtained
from :term:`ACL` objects attached to model instances.

An example of its usage, with all attributes fully expanded:

.. code-block:: xml
   :linenos:

   <aclauthorizationpolicy/>

In other words, it has no configuration attributes; its existence in a
``configure.zcml`` file enables it.

.. _creating_an_authentication_policy:

Creating Your Own Authentication Policy
---------------------------------------

:mod:`repoze.bfg` ships with a number of useful out-of-the-box
security policies (see :mod:`repoze.bfg.authentication`).  However,
creating your own authentication policy is often necessary when you
want to control the "horizontal and vertical" of how your users
authenticate.  Doing so is matter of creating an instance of something
that implements the following interface:

.. code-block:: python

   class AuthenticationPolicy(object):
       """ An object representing a BFG authentication policy. """
       def authenticated_userid(self, request):
           """ Return the authenticated userid or ``None`` if no
           authenticated userid can be found. """

       def effective_principals(self, request):
           """ Return a sequence representing the effective principals
           including the userid and any groups belonged to by the current
           user, including 'system' groups such as Everyone and
           Authenticated. """

       def remember(self, request, principal, **kw):
           """ Return a set of headers suitable for 'remembering' the
           principal named ``principal`` when set in a response.  An
           individual authentication policy and its consumers can decide
           on the composition and meaning of **kw. """
       
       def forget(self, request):
           """ Return a set of headers suitable for 'forgetting' the
           current user on subsequent requests. """

After you do so, you can pass an instance of such a class into the
:class:`repoze.bfg.configuration.Configurator` class at configuration
time as ``authentication_policy`` to use it.

.. _creating_an_authorization_policy:

Creating Your Own Authorization Policy
--------------------------------------

An authentication policy the policy that allows or denies access after
a user has been authenticated.  By default, :mod:`repoze.bfg` will use
the :class:`repoze.bfg.authorization.ACLAuthorizationPolicy` if an
authentication policy is activated and an authorization policy isn't
otherwise specified.

In some cases, it's useful to be able to use a different
authentication policy than the
:class:`repoze.bfg.authorization.ACLAuthorizationPolicy`.  For
example, it might be desirable to construct an alternate authorization
policy which allows the application to use an authorization mechanism
that does not involve :term:`ACL` objects.

:mod:`repoze.bfg` ships with only its single default
:class:`repoze.bfg.authorization.ACLAuthorizationPolicy`, so you'll
need to create your own if you'd like to use a different one.
Creating and using your own authorization policy is a matter of
creating an instance of an object that implements the following
interface:

.. code-block:: python

    class IAuthorizationPolicy(object):
        """ An object representing a BFG authorization policy. """
        def permits(self, context, principals, permission):
            """ Return True if any of the principals is allowed the
            permission in the current context, else return False """
            
        def principals_allowed_by_permission(self, context, permission):
            """ Return a set of principal identifiers allowed by the 
                permission """

After you do so, you can pass an instance of such a class into the
:class:`repoze.bfg.configuration.Configurator` class at configuration
time as ``authorization_policy`` to use it.
