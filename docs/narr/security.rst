.. index::
   single: security

.. _security_chapter:

Security
========

:app:`Pyramid` provides an optional, declarative, security system. Security in
:app:`Pyramid` is separated into authentication and authorization. The two
systems communicate via :term:`principal` identifiers. Authentication is merely
the mechanism by which credentials provided in the :term:`request` are resolved
to one or more :term:`principal` identifiers. These identifiers represent the
users and groups that are in effect during the request. Authorization then
determines access based on the :term:`principal` identifiers, the requested
:term:`permission`, and a :term:`context`.

The :app:`Pyramid` authorization system can prevent a :term:`view` from being
invoked based on an :term:`authorization policy`. Before a view is invoked, the
authorization system can use the credentials in the :term:`request` along with
the :term:`context` resource to determine if access will be allowed.  Here's
how it works at a high level:

- A user may or may not have previously visited the application and supplied
  authentication credentials, including a :term:`userid`.  If so, the
  application may have called :func:`pyramid.security.remember` to remember
  these.

- A :term:`request` is generated when a user visits the application.

- Based on the request, a :term:`context` resource is located through
  :term:`resource location`.  A context is located differently depending on
  whether the application uses :term:`traversal` or :term:`URL dispatch`, but a
  context is ultimately found in either case.  See the
  :ref:`urldispatch_chapter` chapter for more information.

- A :term:`view callable` is located by :term:`view lookup` using the context
  as well as other attributes of the request.

- If an :term:`authentication policy` is in effect, it is passed the request.
  It will return some number of :term:`principal` identifiers. To do this, the
  policy would need to determine the authenticated :term:`userid` present in
  the request.

- If an :term:`authorization policy` is in effect and the :term:`view
  configuration` associated with the view callable that was found has a
  :term:`permission` associated with it, the authorization policy is passed the
  :term:`context`, some number of :term:`principal` identifiers returned by the
  authentication policy, and the :term:`permission` associated with the view;
  it will allow or deny access.

- If the authorization policy allows access, the view callable is invoked.

- If the authorization policy denies access, the view callable is not invoked.
  Instead the :term:`forbidden view` is invoked.

Authorization is enabled by modifying your application to include an
:term:`authentication policy` and :term:`authorization policy`. :app:`Pyramid`
comes with a variety of implementations of these policies.  To provide maximal
flexibility, :app:`Pyramid` also allows you to create custom authentication
policies and authorization policies.

.. index::
   single: authorization policy

.. _enabling_authorization_policy:

Enabling an Authorization Policy
--------------------------------

:app:`Pyramid` does not enable any authorization policy by default.  All views
are accessible by completely anonymous users.  In order to begin protecting
views from execution based on security settings, you need to enable an
authorization policy.

Enabling an Authorization Policy Imperatively
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the :meth:`~pyramid.config.Configurator.set_authorization_policy` method of
the :class:`~pyramid.config.Configurator` to enable an authorization policy.

You must also enable an :term:`authentication policy` in order to enable the
authorization policy.  This is because authorization, in general, depends upon
authentication.  Use the
:meth:`~pyramid.config.Configurator.set_authentication_policy` method during
application setup to specify the authentication policy.

For example:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator
   from pyramid.authentication import AuthTktAuthenticationPolicy
   from pyramid.authorization import ACLAuthorizationPolicy
   authn_policy = AuthTktAuthenticationPolicy('seekrit', hashalg='sha512')
   authz_policy = ACLAuthorizationPolicy()
   config = Configurator()
   config.set_authentication_policy(authn_policy)
   config.set_authorization_policy(authz_policy)

.. note:: The ``authentication_policy`` and ``authorization_policy`` arguments
   may also be passed to their respective methods mentioned above as
   :term:`dotted Python name` values, each representing the dotted name path to
   a suitable implementation global defined at Python module scope.

The above configuration enables a policy which compares the value of an "auth
ticket" cookie passed in the request's environment which contains a reference
to a single :term:`userid`, and matches that userid's :term:`principals
<principal>` against the principals present in any :term:`ACL` found in the
resource tree when attempting to call some :term:`view`.

While it is possible to mix and match different authentication and
authorization policies, it is an error to configure a Pyramid application with
an authentication policy but without the authorization policy or vice versa. If
you do this, you'll receive an error at application startup time.

.. seealso::

    See also the :mod:`pyramid.authorization` and :mod:`pyramid.authentication`
    modules for alternative implementations of authorization and authentication
    policies.

.. index::
   single: permissions
   single: protecting views

.. _protecting_views:

Protecting Views with Permissions
---------------------------------

To protect a :term:`view callable` from invocation based on a user's security
settings when a particular type of resource becomes the :term:`context`, you
must pass a :term:`permission` to :term:`view configuration`.  Permissions are
usually just strings, and they have no required composition: you can name
permissions whatever you like.

For example, the following view declaration protects the view named
``add_entry.html`` when the context resource is of type ``Blog`` with the
``add`` permission using the :meth:`pyramid.config.Configurator.add_view` API:

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator

   config.add_view('mypackage.views.blog_entry_add_view',
                   name='add_entry.html', 
                   context='mypackage.resources.Blog',
                   permission='add')

The equivalent view registration including the ``add`` permission name may be
performed via the ``@view_config`` decorator:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from resources import Blog

   @view_config(context=Blog, name='add_entry.html', permission='add')
   def blog_entry_add_view(request):
       """ Add blog entry code goes here """
       pass

As a result of any of these various view configuration statements, if an
authorization policy is in place when the view callable is found during normal
application operations, the requesting user will need to possess the ``add``
permission against the :term:`context` resource in order to be able to invoke
the ``blog_entry_add_view`` view.  If they do not, the :term:`Forbidden view`
will be invoked.

.. index::
   pair: permission; default

.. _setting_a_default_permission:

Setting a Default Permission
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a permission is not supplied to a view configuration, the registered view
will always be executable by entirely anonymous users: any authorization policy
in effect is ignored.

In support of making it easier to configure applications which are "secure by
default", :app:`Pyramid` allows you to configure a *default* permission.  If
supplied, the default permission is used as the permission string to all view
registrations which don't otherwise name a ``permission`` argument.

The :meth:`pyramid.config.Configurator.set_default_permission` method supports
configuring a default permission for an application.

When a default permission is registered:

- If a view configuration names an explicit ``permission``, the default
  permission is ignored for that view registration, and the
  view-configuration-named permission is used.

- If a view configuration names the permission
  :data:`pyramid.security.NO_PERMISSION_REQUIRED`, the default permission is
  ignored, and the view is registered *without* a permission (making it
  available to all callers regardless of their credentials).

.. warning::

   When you register a default permission, *all* views (even :term:`exception
   view` views) are protected by a permission.  For all views which are truly
   meant to be anonymously accessible, you will need to associate the view's
   configuration with the :data:`pyramid.security.NO_PERMISSION_REQUIRED`
   permission.

.. index::
   single: ACL
   single: access control list
   pair: resource; ACL

.. _assigning_acls:

Assigning ACLs to Your Resource Objects
---------------------------------------

When the default :app:`Pyramid` :term:`authorization policy` determines whether
a user possesses a particular permission with respect to a resource, it
examines the :term:`ACL` associated with the resource.  An ACL is associated
with a resource by adding an ``__acl__`` attribute to the resource object.
This attribute can be defined on the resource *instance* if you need
instance-level security, or it can be defined on the resource *class* if you
just need type-level security.

For example, an ACL might be attached to the resource for a blog via its class:

.. code-block:: python
   :linenos:

   from pyramid.security import Allow
   from pyramid.security import Everyone

   class Blog(object):
       __acl__ = [
           (Allow, Everyone, 'view'),
           (Allow, 'group:editors', 'add'),
           (Allow, 'group:editors', 'edit'),
           ]

Or, if your resources are persistent, an ACL might be specified via the
``__acl__`` attribute of an *instance* of a resource:

.. code-block:: python
   :linenos:

   from pyramid.security import Allow
   from pyramid.security import Everyone

   class Blog(object):
       pass

   blog = Blog()

   blog.__acl__ = [
           (Allow, Everyone, 'view'),
           (Allow, 'group:editors', 'add'),
           (Allow, 'group:editors', 'edit'),
           ]

Whether an ACL is attached to a resource's class or an instance of the resource
itself, the effect is the same.  It is useful to decorate individual resource
instances with an ACL (as opposed to just decorating their class) in
applications such as content management systems where fine-grained access is
required on an object-by-object basis.

Dynamic ACLs are also possible by turning the ACL into a callable on the
resource. This may allow the ACL to dynamically generate rules based on
properties of the instance.

.. code-block:: python
   :linenos:

   from pyramid.security import Allow
   from pyramid.security import Everyone

   class Blog(object):
       def __acl__(self):
           return [
               (Allow, Everyone, 'view'),
               (Allow, self.owner, 'edit'),
               (Allow, 'group:editors', 'edit'),
           ]

       def __init__(self, owner):
           self.owner = owner

.. index::
   single: ACE
   single: access control entry

Elements of an ACL
------------------

Here's an example ACL:

.. code-block:: python
   :linenos:

   from pyramid.security import Allow
   from pyramid.security import Everyone

   __acl__ = [
           (Allow, Everyone, 'view'),
           (Allow, 'group:editors', 'add'),
           (Allow, 'group:editors', 'edit'),
           ]

The example ACL indicates that the :data:`pyramid.security.Everyone`
principal—a special system-defined principal indicating, literally, everyone—is
allowed to view the blog, and the ``group:editors`` principal is allowed to add
to and edit the blog.

Each element of an ACL is an :term:`ACE`, or access control entry. For example,
in the above code block, there are three ACEs: ``(Allow, Everyone, 'view')``,
``(Allow, 'group:editors', 'add')``, and ``(Allow, 'group:editors', 'edit')``.

The first element of any ACE is either :data:`pyramid.security.Allow`, or
:data:`pyramid.security.Deny`, representing the action to take when the ACE
matches.  The second element is a :term:`principal`.  The third argument is a
permission or sequence of permission names.

A principal is usually a user id, however it also may be a group id if your
authentication system provides group information and the effective
:term:`authentication policy` policy is written to respect group information.
See :ref:`extending_default_authentication_policies`.

Each ACE in an ACL is processed by an authorization policy *in the order
dictated by the ACL*.  So if you have an ACL like this:

.. code-block:: python
   :linenos:

   from pyramid.security import Allow
   from pyramid.security import Deny
   from pyramid.security import Everyone

   __acl__ = [
       (Allow, Everyone, 'view'),
       (Deny, Everyone, 'view'),
       ]

The default authorization policy will *allow* everyone the view permission,
even though later in the ACL you have an ACE that denies everyone the view
permission.  On the other hand, if you have an ACL like this:

.. code-block:: python
   :linenos:

   from pyramid.security import Everyone
   from pyramid.security import Allow
   from pyramid.security import Deny

   __acl__ = [
       (Deny, Everyone, 'view'),
       (Allow, Everyone, 'view'),
       ]

The authorization policy will deny everyone the view permission, even though
later in the ACL, there is an ACE that allows everyone.

The third argument in an ACE can also be a sequence of permission names instead
of a single permission name.  So instead of creating multiple ACEs representing
a number of different permission grants to a single ``group:editors`` group, we
can collapse this into a single ACE, as below.

.. code-block:: python
   :linenos:

   from pyramid.security import Allow
   from pyramid.security import Everyone

   __acl__ = [
       (Allow, Everyone, 'view'),
       (Allow, 'group:editors', ('add', 'edit')),
       ]


.. index::
   single: principal
   single: principal names

Special Principal Names
-----------------------

Special principal names exist in the :mod:`pyramid.security` module.  They can
be imported for use in your own code to populate ACLs, e.g.,
:data:`pyramid.security.Everyone`.

:data:`pyramid.security.Everyone`

  Literally, everyone, no matter what.  This object is actually a string under
  the hood (``system.Everyone``).  Every user *is* the principal named
  "Everyone" during every request, even if a security policy is not in use.

:data:`pyramid.security.Authenticated`

  Any user with credentials as determined by the current security policy.  You
  might think of it as any user that is "logged in".  This object is actually a
  string under the hood (``system.Authenticated``).

.. index::
   single: permission names
   single: special permission names

Special Permissions
-------------------

Special permission names exist in the :mod:`pyramid.security` module.  These
can be imported for use in ACLs.

.. _all_permissions:

:data:`pyramid.security.ALL_PERMISSIONS`

  An object representing, literally, *all* permissions.  Useful in an ACL like
  so: ``(Allow, 'fred', ALL_PERMISSIONS)``.  The ``ALL_PERMISSIONS`` object is
  actually a stand-in object that has a ``__contains__`` method that always
  returns ``True``, which, for all known authorization policies, has the effect
  of indicating that a given principal has any permission asked for by the
  system.

.. index::
   single: special ACE
   single: ACE (special)

Special ACEs
------------

A convenience :term:`ACE` is defined representing a deny to everyone of all
permissions in :data:`pyramid.security.DENY_ALL`.  This ACE is often used as
the *last* ACE of an ACL to explicitly cause inheriting authorization policies
to "stop looking up the traversal tree" (effectively breaking any inheritance).
For example, an ACL which allows *only* ``fred`` the view permission for a
particular resource, despite what inherited ACLs may say when the default
authorization policy is in effect, might look like so:

.. code-block:: python
   :linenos:

   from pyramid.security import Allow
   from pyramid.security import DENY_ALL

   __acl__ = [ (Allow, 'fred', 'view'), DENY_ALL ]

Under the hood, the :data:`pyramid.security.DENY_ALL` ACE equals the
following:

.. code-block:: python
   :linenos:

   from pyramid.security import ALL_PERMISSIONS
   __acl__ = [ (Deny, Everyone, ALL_PERMISSIONS) ]

.. index::
   single: ACL inheritance
   pair: location-aware; security

ACL Inheritance and Location-Awareness
--------------------------------------

While the default :term:`authorization policy` is in place, if a resource
object does not have an ACL when it is the context, its *parent* is consulted
for an ACL.  If that object does not have an ACL, *its* parent is consulted for
an ACL, ad infinitum, until we've reached the root and there are no more
parents left.

In order to allow the security machinery to perform ACL inheritance, resource
objects must provide *location-awareness*.  Providing *location-awareness*
means two things: the root object in the resource tree must have a ``__name__``
attribute and a ``__parent__`` attribute.

.. code-block:: python
   :linenos:

   class Blog(object):
       __name__ = ''
       __parent__ = None

An object with a ``__parent__`` attribute and a ``__name__`` attribute is said
to be *location-aware*.  Location-aware objects define a ``__parent__``
attribute which points at their parent object.  The root object's
``__parent__`` is ``None``.

.. seealso::

    See also :ref:`location_module` for documentations of functions which use
    location-awareness.

.. seealso::

    See also :ref:`location_aware`.

.. index::
   single: forbidden view

Changing the Forbidden View
---------------------------

When :app:`Pyramid` denies a view invocation due to an authorization denial,
the special ``forbidden`` view is invoked.  Out of the box, this forbidden view
is very plain.  See :ref:`changing_the_forbidden_view` within
:ref:`hooks_chapter` for instructions on how to create a custom forbidden view
and arrange for it to be called when view authorization is denied.

.. index::
   single: debugging authorization failures

.. _debug_authorization_section:

Debugging View Authorization Failures
-------------------------------------

If your application in your judgment is allowing or denying view access
inappropriately, start your application under a shell using the
``PYRAMID_DEBUG_AUTHORIZATION`` environment variable set to ``1``.  For
example:

.. code-block:: text

  $ PYRAMID_DEBUG_AUTHORIZATION=1 $VENV/bin/pserve myproject.ini

When any authorization takes place during a top-level view rendering, a message
will be logged to the console (to stderr) about what ACE in which ACL permitted
or denied the authorization based on authentication information.

This behavior can also be turned on in the application ``.ini`` file by setting
the ``pyramid.debug_authorization`` key to ``true`` within the application's
configuration section, e.g.:

.. code-block:: ini
  :linenos:

  [app:main]
  use = egg:MyProject
  pyramid.debug_authorization = true

With this debug flag turned on, the response sent to the browser will also
contain security debugging information in its body.

Debugging Imperative Authorization Failures
-------------------------------------------

The :meth:`pyramid.request.Request.has_permission` API is used to check
security within view functions imperatively.  It returns instances of objects
that are effectively booleans.  But these objects are not raw ``True`` or
``False`` objects, and have information attached to them about why the
permission was allowed or denied.  The object will be one of
:data:`pyramid.security.ACLAllowed`, :data:`pyramid.security.ACLDenied`,
:data:`pyramid.security.Allowed`, or :data:`pyramid.security.Denied`, as
documented in :ref:`security_module`.  At the very minimum, these objects will
have a ``msg`` attribute, which is a string indicating why the permission was
denied or allowed.  Introspecting this information in the debugger or via print
statements when a call to :meth:`~pyramid.request.Request.has_permission` fails
is often useful.

.. index::
   single: authentication policy (extending)

.. _extending_default_authentication_policies:

Extending Default Authentication Policies
-----------------------------------------

Pyramid ships with some built in authentication policies for use in your
applications. See :mod:`pyramid.authentication` for the available policies.
They differ on their mechanisms for tracking authentication credentials between
requests, however they all interface with your application in mostly the same
way.

Above you learned about :ref:`assigning_acls`. Each :term:`principal` used in
the :term:`ACL` is matched against the list returned from
:meth:`pyramid.interfaces.IAuthenticationPolicy.effective_principals`.
Similarly, :meth:`pyramid.request.Request.authenticated_userid` maps to
:meth:`pyramid.interfaces.IAuthenticationPolicy.authenticated_userid`.

You may control these values by subclassing the default authentication
policies. For example, below we subclass the
:class:`pyramid.authentication.AuthTktAuthenticationPolicy` and define extra
functionality to query our database before confirming that the :term:`userid`
is valid in order to avoid blindly trusting the value in the cookie (what if
the cookie is still valid, but the user has deleted their account?).  We then
use that :term:`userid` to augment the ``effective_principals`` with
information about groups and other state for that user.

.. code-block:: python
   :linenos:

   from pyramid.authentication import AuthTktAuthenticationPolicy

   class MyAuthenticationPolicy(AuthTktAuthenticationPolicy):
       def authenticated_userid(self, request):
           userid = self.unauthenticated_userid(request)
           if userid:
               if request.verify_userid_is_still_valid(userid):
                   return userid

       def effective_principals(self, request):
           principals = [Everyone]
           userid = self.authenticated_userid(request)
           if userid:
               principals += [Authenticated, str(userid)]
           return principals

In most instances ``authenticated_userid`` and ``effective_principals`` are
application-specific, whereas ``unauthenticated_userid``, ``remember``, and
``forget`` are generic and focused on transport and serialization of data
between consecutive requests.

.. index::
   single: authentication policy (creating)

.. _creating_an_authentication_policy:

Creating Your Own Authentication Policy
---------------------------------------

:app:`Pyramid` ships with a number of useful out-of-the-box security policies
(see :mod:`pyramid.authentication`).  However, creating your own authentication
policy is often necessary when you want to control the "horizontal and
vertical" of how your users authenticate.  Doing so is a matter of creating an
instance of something that implements the following interface:

.. code-block:: python
   :linenos:

   class IAuthenticationPolicy(object):
       """ An object representing a Pyramid authentication policy. """

       def authenticated_userid(self, request):
           """ Return the authenticated :term:`userid` or ``None`` if
           no authenticated userid can be found. This method of the
           policy should ensure that a record exists in whatever
           persistent store is used related to the user (the user
           should not have been deleted); if a record associated with
           the current id does not exist in a persistent store, it
           should return ``None``.

           """

       def unauthenticated_userid(self, request):
           """ Return the *unauthenticated* userid.  This method
           performs the same duty as ``authenticated_userid`` but is
           permitted to return the userid based only on data present
           in the request; it needn't (and shouldn't) check any
           persistent store to ensure that the user record related to
           the request userid exists.

           This method is intended primarily a helper to assist the
           ``authenticated_userid`` method in pulling credentials out
           of the request data, abstracting away the specific headers,
           query strings, etc that are used to authenticate the request.

           """

       def effective_principals(self, request):
           """ Return a sequence representing the effective principals
           typically including the :term:`userid` and any groups belonged
           to by the current user, always including 'system' groups such
           as ``pyramid.security.Everyone`` and
           ``pyramid.security.Authenticated``.

           """

       def remember(self, request, userid, **kw):
           """ Return a set of headers suitable for 'remembering' the
           :term:`userid` named ``userid`` when set in a response.  An
           individual authentication policy and its consumers can
           decide on the composition and meaning of **kw.

           """

       def forget(self, request):
           """ Return a set of headers suitable for 'forgetting' the
           current user on subsequent requests.

           """

After you do so, you can pass an instance of such a class into the
:class:`~pyramid.config.Configurator.set_authentication_policy` method at
configuration time to use it.

.. index::
   single: authorization policy (creating)

.. _creating_an_authorization_policy:

Creating Your Own Authorization Policy
--------------------------------------

An authorization policy is a policy that allows or denies access after a user
has been authenticated.  Most :app:`Pyramid` applications will use the default
:class:`pyramid.authorization.ACLAuthorizationPolicy`.

However, in some cases, it's useful to be able to use a different authorization
policy than the default :class:`~pyramid.authorization.ACLAuthorizationPolicy`.
For example, it might be desirable to construct an alternate authorization
policy which allows the application to use an authorization mechanism that does
not involve :term:`ACL` objects.

:app:`Pyramid` ships with only a single default authorization policy, so you'll
need to create your own if you'd like to use a different one.  Creating and
using your own authorization policy is a matter of creating an instance of an
object that implements the following interface:

.. code-block:: python
    :linenos:

    class IAuthorizationPolicy(object):
        """ An object representing a Pyramid authorization policy. """
        def permits(self, context, principals, permission):
            """ Return ``True`` if any of the ``principals`` is allowed the
            ``permission`` in the current ``context``, else return ``False``
            """
            
        def principals_allowed_by_permission(self, context, permission):
            """ Return a set of principal identifiers allowed by the
            ``permission`` in ``context``.  This behavior is optional; if you
            choose to not implement it you should define this method as
            something which raises a ``NotImplementedError``.  This method
            will only be called when the
            ``pyramid.security.principals_allowed_by_permission`` API is
            used."""

After you do so, you can pass an instance of such a class into the
:class:`~pyramid.config.Configurator.set_authorization_policy` method at
configuration time to use it.

.. _admonishment_against_secret_sharing:

Admonishment Against Secret-Sharing
-----------------------------------

A "secret" is required by various components of Pyramid.  For example, the
:term:`authentication policy` below uses a secret value ``seekrit``::

  authn_policy = AuthTktAuthenticationPolicy('seekrit', hashalg='sha512')

A :term:`session factory` also requires a secret::

  my_session_factory = SignedCookieSessionFactory('itsaseekreet')

It is tempting to use the same secret for multiple Pyramid subsystems.  For
example, you might be tempted to use the value ``seekrit`` as the secret for
both the authentication policy and the session factory defined above.  This is
a bad idea, because in both cases, these secrets are used to sign the payload
of the data.

If you use the same secret for two different parts of your application for
signing purposes, it may allow an attacker to get his chosen plaintext signed,
which would allow the attacker to control the content of the payload.  Re-using
a secret across two different subsystems might drop the security of signing to
zero. Keys should not be re-used across different contexts where an attacker
has the possibility of providing a chosen plaintext.
