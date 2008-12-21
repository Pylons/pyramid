.. _security_chapter:

Security
========

:mod:`repoze.bfg` provides an optional declarative security system
that prevents views that are protected by a :term:`permission` from
being rendered when the user represented by the request does not have
the appropriate level of access in a context.

Security is enabled by adding configuration to your ``configure.zcml``
which specifies a :term:`security policy`.

Enabling a Security Policy
--------------------------

By default, :mod:`repoze.bfg` enables no security policy.  All views
are accessible by completely anonymous users.

However, if you add the following bit of code to your application's
``configure.zcml``, you will enable a security policy:

.. code-block:: xml
   :linenos:

   <utility
     provides="repoze.bfg.interfaces.ISecurityPolicy"
     factory="repoze.bfg.security.RemoteUserACLSecurityPolicy"
     />

The above inscrutable stanza enables the
``RemoteUserACLSecurityPolicy`` to be in effect for every request to
your application.  The ``RemoteUserACLSecurityPolicy`` is a policy
which compares the ``REMOTE_USER`` variable passed in the reqest's
environment (as the sole :term:`principal`) against any *ACL* found in
model data when attempting to call some :term:`view`.  The policy
either allows the view that the permission was declared for to be
called, or returns a ``401 Unathorized`` response code to the upstream
WSGI server.

Protecting Views with Permissions
---------------------------------

You declaratively protected a particular view with a
:term:`permission` via the ``configure.zcml`` application registry.
For example, the following declaration protects the view named
``add_entry.html`` when invoked against an ``IBlog`` context with the
``add`` permission:

.. code-block:: xml
   :linenos:

   <view
       for=".models.IBlog"
       view=".views.blog_entry_add_view"
       name="add_entry.html"
       permission="add"
       />

If a security policy is in place when this view is found during normal
application operations, the user will need to possess the ``add``
permission against the context to be able to invoke the
``blog_entry_add_view`` view.

Permission names are just strings.  They hold no special significance
to the system.  You can name permissions whatever you like.

Assigning ACLs to your Model Objects
------------------------------------

When :mod:`repoze.bfg` determines whether a user possesses a particular
permission in a :term:`context`, it examines the :term:`ACL`
associated with the context.  An ACL is associated with a context by
virtue of the ``__acl__`` attribute of the model object representing
the context.  This attribute can be defined on the model *instance*
(if you need instance-level security), or it can be defined on the
model *class* (if you just need type-level security).

For example, an ACL might be attached to model for a blog via its
class:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Everyone
   from repoze.bfg.security import Allow

   class IBlog(Interface):
       pass

   class Blog(dict):
       __acl__ = [
           (Allow, Everyone, 'view'),
           (Allow, 'group:editors', 'add'),
           (Allow, 'group:editors', 'edit'),
           ]
       implements(IBlog)

The above ACL indicates that the ``Everyone`` principal (a special
system-defined principal indicating, literally, everyone) is allowed
to view the blog, the ``group:editors`` principal is allowed to add to
and edit the blog.

.. note:: Each tuple within the above ``__acl__`` structure is known
          as a :term:`ACE`, which stands for "access control entry".

A principal is usually a user id, however it also may be a group id if
your authentication system provides group information and the security
policy is written to respect them.  The
``RemoteUserACLSecurityPolicy`` does not respect group information.

ACL Inheritance
---------------

While the security policy is in place, if a model object does not have
an ACL when it is the context, its *parent* is consulted for an ACL.
If that object does not have an ACL, *its* parent is consulted for an
ACL, ad infinitum, until we've reached the root and there are no more
parents left.

The *first* ACL found by the security policy will be used as the
effective ACL.  No combination of ACLs found during traversal or
backtracking is done.

Location-Awareness
------------------

In order to allow the security machinery to perform ACL inheritance,
model objects must provide *location-awareness*.  Providing
location-awareness means two things: the root object in the graph must
have a ``_name__`` and a ``__parent__`` attribute and the root object
must be declared to implement the ``repoze.bfg.interfaces.ILocation``
interface.  For example:

.. code-block:: python
   :linenos:

   from repoze.bfg.interfaces import ILocation
   from zope.interface import implements

   class Blog(object):
       implements(ILocation)
       __name__ = ''
       __parent__ = None

An object with a ``__parent__`` attribute and a ``__name__`` attribute
is said to be *location-aware*.  Location-aware objects define an
``__parent__`` attribute which points at their parent object.  The
root object's ``__parent__`` is ``None``.

If the root object in a :mod:`repoze.bfg` application declares that it
implements the ``repoze.bfg.interfaces.ILocation`` interface, it is
assumed that the objects in the rest of the model are location-aware.
If those objects are not explictly location-aware, if the root object
is marked as ``ILocation``, the bfg framework will wrap each object
during traversal in a *location proxy* that has both the ``__name__``
and ``__parent__`` attributes, but otherwise acts the same as your
model object.

You can of course supply ``__name__`` and ``__parent__`` attributes
explicitly on all of your model objects, and no location proxying will
be performed.

See :ref:`location_module` for documentations of functions which use
location-awareness.

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

The ``has_permission`` API (see :ref:`security_module`) is used to
check security within view functions imperatively.  It returns
instances of objects that are effectively booleans.  But these objects
are not raw ``True`` or ``False`` objects, and have information
attached to them about why the permission was allowed or denied.  The
object will be one of ``ACLAllowed``, ``ACLDenied``, ``Allowed``, and
``Denied``, documented in :ref:`security_module`.  At very minimum
these objects will have a ``msg`` attribute, which is a string
indicating why permission was denied or allowed.  Introspecting this
information in the debugger or via print statements when a
``has_permission`` fails is often useful.
