.. index::
   single: security

.. _security_chapter:

Security
========

:app:`Pyramid` provides an optional, declarative security system.  The system
determines the identity of the current user (authentication) and whether or not
the user has access to certain resources (authorization).

The :app:`Pyramid` security system can prevent a :term:`view` from being
invoked based on the :term:`security policy`. Before a view is invoked, the
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

- If a :term:`security policy` is in effect, it is passed the request and
  returns the :term:`identity` of the current user.

- If a :term:`security policy` is in effect and the :term:`view
  configuration` associated with the view callable that was found has a
  :term:`permission` associated with it, the policy is passed the
  :term:`context`, the current :term:`identity`, and the :term:`permission`
  associated with the view; it will allow or deny access.

- If the security policy allows access, the view callable is invoked.

- If the security policy denies access, the view callable is not invoked.
  Instead the :term:`forbidden view` is invoked.

The security system is enabled by modifying your application to include a
:term:`security policy`. :app:`Pyramid` comes with a variety of helpers to
assist in the creation of this policy.

.. index::
   single: security policy

.. _writing_security_policy:

Writing a Security Policy
-------------------------

:app:`Pyramid` does not enable any security policy by default.  All views are
accessible by completely anonymous users.  In order to begin protecting views
from execution based on security settings, you need to write a security policy.

Security policies are simple classes implementing a
:class:`pyramid.interfaces.ISecurityPolicy`, defined as follows:

.. autointerface:: pyramid.interfaces.ISecurityPolicy
  :members:

A simple security policy might look like the following:

.. code-block:: python
    :linenos:

    from pyramid.security import Allowed, Denied

    class SessionSecurityPolicy:
        def identify(self, request):
            """ Return the user ID stored in the session. """
            return request.session.get('userid')

        def permits(self, request, context, identity, permission):
            """ Allow access to everything if signed in. """
            if identity is not None:
                return Allowed('User is signed in.')
            else:
                return Denied('User is not signed in.')

        def remember(request, userid, **kw):
            request.session.get('userid')
            return []

        def forget(request):
            del request.session['userid']
            return []

Use the :meth:`~pyramid.config.Configurator.set_security_policy` method of
the :class:`~pyramid.config.Configurator` to enforce the security policy on
your application.

.. seealso::

    For more information on implementing the ``permits`` method, see
    :ref:`security_policy_permits`.

Writing a Security Policy Using Helpers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To assist in writing common security policies, Pyramid provides several
helpers.  The following authentication helpers assist with implementing
``identity``, ``remember``, and ``forget``.

+-------------------------------+-------------------------------------------------------------------+
| Use Case                      | Helper                                                            |
+===============================+===================================================================+
| Store the :term:`userid`      | :class:`pyramid.authentication.SessionAuthenticationHelper`       |
| in the :term:`session`.       |                                                                   |
+-------------------------------+-------------------------------------------------------------------+
| Store the :term:`userid`      | :class:`pyramid.authentication.AuthTktCookieHelper`               |
| with an "auth ticket" cookie. |                                                                   |
+-------------------------------+-------------------------------------------------------------------+
| Retrieve user credentials     | Use :func:`pyramid.authentication.extract_http_basic_credentials` |
| using HTTP Basic Auth.        | to retrieve credentials.                                          |
+-------------------------------+-------------------------------------------------------------------+
| Retrieve the :term:`userid`   | ``REMOTE_USER`` can be accessed with                              |
| from ``REMOTE_USER`` in the   | ``request.environ.get('REMOTE_USER')``.                           |
| WSGI environment.             |                                                                   |
+-------------------------------+-------------------------------------------------------------------+

For example, our above security policy can leverage these helpers like so:

.. code-block:: python
    :linenos:

    from pyramid.security import Allowed, Denied
    from pyramid.authentication import SessionAuthenticationHelper

    class SessionSecurityPolicy:
        def __init__(self):
            self.helper = SessionAuthenticationHelper()

        def identify(self, request):
            """ Return the user ID stored in the session. """
            return self.helper.identify(request)

        def permits(self, request, context, identity, permission):
            """ Allow access to everything if signed in. """
            if identity is not None:
                return Allowed('User is signed in.')
            else:
                return Denied('User is not signed in.')

        def remember(request, userid, **kw):
            return self.helper.remember(request, userid, **kw)

        def forget(request):
            return self.helper.forget(request)

Helpers are intended to be used with application-specific code, so perhaps your
authentication also queries to database to ensure the identity is valid.

.. code-block:: python
    :linenos:

        def identify(self, request):
            """ Return the user ID stored in the session. """
            user_id = self.helper.identify(request)
            if validate_user_id(user_id):
                return user_id
            else:
                return None

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
security policy is in place when the view callable is found during normal
application operations, the security policy will be queried to see if the
requesting user is allowed the ``add`` permission within the current
:term:`context`.  If the policy allows access, ``blog_entry_add_view`` will be
invoked.  If not, the :term:`Forbidden view` will be invoked.

.. _security_policy_permits:

Allowing and Denying Access With a Security Policy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To determine whether access is allowed to a view with an attached permission,
Pyramid calls the ``permits`` method of the security policy.  ``permits``
should return an instance of :class:`pyramid.security.Allowed` or
:class:`pyramid.security.Denied`.  Both classes accept a string as an argument,
which should detail why access was allowed or denied.

A simple ``permits`` implementation that grants access based on a user role
might look like so:

.. code-block:: python
    :linenos:

    from pyramid.security import Allowed, Denied

    class SecurityPolicy:
        def permits(self, request, context, identity, permission):
            if identity is None:
                return Denied('User is not signed in.')
            if identity.role == 'admin':
                allowed = ['read', 'write', 'delete']
            elif identity.role == 'editor':
                allowed = ['read', 'write']
            else:
                allowed = ['read']
            if permission in allowed:
                return Allowed(
                    'Access granted for user %s with role %s.',
                    identity,
                    identity.role,
                )
            else:
                return Denied(
                    'Access denied for user %s with role %s.',
                    identity,
                    identity.role,
                )

.. index::
   pair: permission; default

.. _setting_a_default_permission:

Setting a Default Permission
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a permission is not supplied to a view configuration, the registered view
will always be executable by entirely anonymous users: any security policy
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

Implementing ACL Authorization
------------------------------

A common way to implement authorization is using an :term:`ACL`.  An ACL is a
:term:`context`-specific list of access control entries, which allow or deny
access to permissions based on a user's principals.

Pyramid provides :class:`pyramid.authorization.ACLHelper` to assist with an
ACL-based implementation of ``permits``.  Application-specific code should
construct a list of principals for the user and call
:meth:`pyramid.authorization.ACLHelper.permits`, which will return an
:class:`pyramid.security.ACLAllowed` or :class:`pyramid.security.ACLDenied`
object.  An implementation might look like this:

.. code-block:: python
    :linenos:

    from pyramid.security import Everyone, Authenticated
    from pyramid.authorization import ACLHelper

    class SecurityPolicy:
        def permits(self, request, context, identity, permission):
            principals = [Everyone]
            if identity is not None:
                principals.append(Authenticated)
                principals.append('user:' + identity.id)
                principals.append('group:' + identity.group)
            return ACLHelper().permits(context, principals, permission)

To associate an ACL with a resource, add an ``__acl__`` attribute to the
resource object.  This attribute can be defined on the resource *instance* if
you need instance-level security, or it can be defined on the resource *class*
if you just need type-level security.

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

.. warning::

   Writing ``__acl__`` as properties is discouraged because an
   ``AttributeError`` occurring in ``fget`` or ``fset`` will be silently
   dismissed (this is consistent with Python ``getattr`` and ``hasattr``
   behaviors). For dynamic ACLs, simply use callables, as documented above.


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
authentication system provides group information.

Each ACE in an ACL is processed by the ACL helper *in the order
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

The ACL helper will *allow* everyone the view permission, even though later in
the ACL you have an ACE that denies everyone the view permission.  On the other
hand, if you have an ACL like this:

.. code-block:: python
    :linenos:

    from pyramid.security import Everyone
    from pyramid.security import Allow
    from pyramid.security import Deny

    __acl__ = [
        (Deny, Everyone, 'view'),
        (Allow, Everyone, 'view'),
        ]

The ACL helper will deny everyone the view permission, even though
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

.. _special_principals:

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
particular resource, despite what inherited ACLs may say, might look like so:

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

While the ACL helper is in place, if a resource object does not have an ACL
when it is the context, its *parent* is consulted for an ACL.  If that object
does not have an ACL, *its* parent is consulted for an ACL, ad infinitum, until
we've reached the root and there are no more parents left.

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

    PYRAMID_DEBUG_AUTHORIZATION=1 $VENV/bin/pserve myproject.ini

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

.. _admonishment_against_secret_sharing:

Admonishment Against Secret-Sharing
-----------------------------------

A "secret" is required by various components of Pyramid.  For example, the
helper below might be used for a security policy and uses a secret value
``seekrit``::

  helper = AuthTktCookieHelper('seekrit', hashalg='sha512')

A :term:`session factory` also requires a secret::

  my_session_factory = SignedCookieSessionFactory('itsaseekreet')

It is tempting to use the same secret for multiple Pyramid subsystems.  For
example, you might be tempted to use the value ``seekrit`` as the secret for
both the helper and the session factory defined above.  This is a bad idea,
because in both cases, these secrets are used to sign the payload of the data.

If you use the same secret for two different parts of your application for
signing purposes, it may allow an attacker to get his chosen plaintext signed,
which would allow the attacker to control the content of the payload.  Re-using
a secret across two different subsystems might drop the security of signing to
zero. Keys should not be re-used across different contexts where an attacker
has the possibility of providing a chosen plaintext.

.. index::
   single: preventing cross-site request forgery attacks
   single: cross-site request forgery attacks, prevention

Preventing Cross-Site Request Forgery Attacks
---------------------------------------------

`Cross-site request forgery
<https://en.wikipedia.org/wiki/Cross-site_request_forgery>`_ attacks are a
phenomenon whereby a user who is logged in to your website might inadvertantly
load a URL because it is linked from, or embedded in, an attacker's website.
If the URL is one that may modify or delete data, the consequences can be dire.

You can avoid most of these attacks by issuing a unique token to the browser
and then requiring that it be present in all potentially unsafe requests.
:app:`Pyramid` provides facilities to create and check CSRF tokens.

By default :app:`Pyramid` comes with a session-based CSRF implementation
:class:`pyramid.csrf.SessionCSRFStoragePolicy`. To use it, you must first enable
a :term:`session factory` as described in
:ref:`using_the_default_session_factory` or
:ref:`using_alternate_session_factories`. Alternatively, you can use
a cookie-based implementation :class:`pyramid.csrf.CookieCSRFStoragePolicy` which gives
some additional flexibility as it does not require a session for each user.
You can also define your own implementation of
:class:`pyramid.interfaces.ICSRFStoragePolicy` and register it with the
:meth:`pyramid.config.Configurator.set_csrf_storage_policy` directive.

For example:

.. code-block:: python

    from pyramid.config import Configurator

    config = Configurator()
    config.set_csrf_storage_policy(MyCustomCSRFPolicy())

.. index::
   single: csrf.get_csrf_token

Using the ``csrf.get_csrf_token`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get the current CSRF token, use the
:data:`pyramid.csrf.get_csrf_token` method.

.. code-block:: python

    from pyramid.csrf import get_csrf_token
    token = get_csrf_token(request)

The ``get_csrf_token()`` method accepts a single argument: the request. It
returns a CSRF *token* string. If ``get_csrf_token()`` or ``new_csrf_token()``
was invoked previously for this user, then the existing token will be returned.
If no CSRF token previously existed for this user, then a new token will be set
into the session and returned. The newly created token will be opaque and
randomized.

.. _get_csrf_token_in_templates:

Using the ``get_csrf_token`` global in templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Templates have a ``get_csrf_token()`` method inserted into their globals, which
allows you to get the current token without modifying the view code. This
method takes no arguments and returns a CSRF token string. You can use the
returned token as the value of a hidden field in a form that posts to a method
that requires elevated privileges, or supply it as a request header in AJAX
requests.

For example, include the CSRF token as a hidden field:

.. code-block:: html

    <form method="post" action="/myview">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <input type="submit" value="Delete Everything">
    </form>

Or include it as a header in a jQuery AJAX request:

.. code-block:: javascript

    var csrfToken = "${get_csrf_token()}";
    $.ajax({
      type: "POST",
      url: "/myview",
      headers: { 'X-CSRF-Token': csrfToken }
    }).done(function() {
      alert("Deleted");
    });

The handler for the URL that receives the request should then require that the
correct CSRF token is supplied.

.. index::
   single: csrf.new_csrf_token

Using the ``csrf.new_csrf_token`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To explicitly create a new CSRF token, use the ``csrf.new_csrf_token()``
method.  This differs only from ``csrf.get_csrf_token()`` inasmuch as it
clears any existing CSRF token, creates a new CSRF token, sets the token into
the user, and returns the token.

.. code-block:: python

    from pyramid.csrf import new_csrf_token
    token = new_csrf_token(request)

.. note::

    It is not possible to force a new CSRF token from a template. If you
    want to regenerate your CSRF token then do it in the view code and return
    the new token as part of the context.

Checking CSRF Tokens Manually
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In request handling code, you can check the presence and validity of a CSRF
token with :func:`pyramid.csrf.check_csrf_token`. If the token is valid, it
will return ``True``, otherwise it will raise ``HTTPBadRequest``. Optionally,
you can specify ``raises=False`` to have the check return ``False`` instead of
raising an exception.

By default, it checks for a POST parameter named ``csrf_token`` or a header
named ``X-CSRF-Token``.

.. code-block:: python

    from pyramid.csrf import check_csrf_token

    def myview(request):
        # Require CSRF Token
        check_csrf_token(request)

        # ...

.. _auto_csrf_checking:

Checking CSRF Tokens Automatically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 1.7

:app:`Pyramid` supports automatically checking CSRF tokens on requests with an
unsafe method as defined by RFC2616. Any other request may be checked manually.
This feature can be turned on globally for an application using the
:meth:`pyramid.config.Configurator.set_default_csrf_options` directive.
For example:

.. code-block:: python

    from pyramid.config import Configurator

    config = Configurator()
    config.set_default_csrf_options(require_csrf=True)

CSRF checking may be explicitly enabled or disabled on a per-view basis using
the ``require_csrf`` view option. A value of ``True`` or ``False`` will
override the default set by ``set_default_csrf_options``. For example:

.. code-block:: python

    @view_config(route_name='hello', require_csrf=False)
    def myview(request):
        # ...

When CSRF checking is active, the token and header used to find the
supplied CSRF token will be ``csrf_token`` and ``X-CSRF-Token``, respectively,
unless otherwise overridden by ``set_default_csrf_options``. The token is
checked against the value in ``request.POST`` which is the submitted form body.
If this value is not present, then the header will be checked.

In addition to token based CSRF checks, if the request is using HTTPS then the
automatic CSRF checking will also check the referrer of the request to ensure
that it matches one of the trusted origins. By default the only trusted origin
is the current host, however additional origins may be configured by setting
``pyramid.csrf_trusted_origins`` to a list of domain names (and ports if they
are non-standard). If a host in the list of domains starts with a ``.`` then
that will allow all subdomains as well as the domain without the ``.``.

If CSRF checks fail then a :class:`pyramid.exceptions.BadCSRFToken` or
:class:`pyramid.exceptions.BadCSRFOrigin` exception will be raised. This
exception may be caught and handled by an :term:`exception view` but, by
default, will result in a ``400 Bad Request`` response being sent to the
client.

Checking CSRF Tokens with a View Predicate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. deprecated:: 1.7
   Use the ``require_csrf`` option or read :ref:`auto_csrf_checking` instead
   to have :class:`pyramid.exceptions.BadCSRFToken` exceptions raised.

A convenient way to require a valid CSRF token for a particular view is to
include ``check_csrf=True`` as a view predicate. See
:meth:`pyramid.config.Configurator.add_view`.

.. code-block:: python

     @view_config(request_method='POST', check_csrf=True, ...)
     def myview(request):
         # ...

.. note::
   A mismatch of a CSRF token is treated like any other predicate miss, and the
   predicate system, when it doesn't find a view, raises ``HTTPNotFound``
   instead of ``HTTPBadRequest``, so ``check_csrf=True`` behavior is different
   from calling :func:`pyramid.csrf.check_csrf_token`.
