.. _glossary:

============================
 :mod:`repoze.bfg` Glossary
============================

.. glossary::

  request
    A ``WebOb`` request object.
  response
    An object that has three attributes: app_iter (representing an
    iterable body), headerlist (representing the http headers sent
    upstream), and status (representing the http status string).  This
    is the interface defined for ``WebOb`` response objects.
  setuptools
    `Setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_
    builds on Python's ``distutils`` to provide easier building,
    distribution, and installation of packages.
  view
    A "view" is a callable which returns a response object.  It should
    accept two values: context and request.
  view name
    The "URL name" of a view, e.g "index.html".  If a view is
    configured without a name, its name is considered to be the empty
    string (which implies the "default view").
  model
    An object representing data in the system.  A model is part of the
    object graph traversed by the system.  Models are traversed to
    determine a context.
  context
    A model in the system that is found during traversal; it becomes
    the subject of a view.
  application registry
    A registry which maps model types to views, as well as performing
    other application-specific component registrations.
  template
    A file that is capable of representing some text when rendered.
  interface
    An attribute of a model object that determines its type.
  security policy
    An object that provides a mechanism to check authorization using
    authentication data and a permission associated with a model.  It
    essentially returns "true" if the combination of the authorization
    information in the model (e.g. an ACL) and the authentication data
    in the request (e.g. the REMOTE_USER) allow the action implied by
    the permission associated with the view (e.g. "add").
  principal
    A user id or group id.
  permission
    A permission is a string token that is associated with a view name
    and a model type by the developer.  Models are decorated with
    security declarations (e.g. ACLs), which reference these tokens
    also.  A security policy attempts to match the view permission
    against the model's statements about which permissions are granted
    to which principal to answer the question "is this user allowed to
    do this".
  WSGI
    `Web Server Gateway Interface <http://wsgi.org/>`_.  This is a
    Python standard for connecting web applications to web servers,
    similar to the concept of Java Servlets.
