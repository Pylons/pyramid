``repoze.bfg`` Introduction
===========================

``repoze.bfg`` is a web application framework based on graph
traversal.  It is inspired by Zope's publisher, and uses Zope
libraries to do much of its work.  However, it is less ambitious and
less featureful than any released version of Zope's publisher.

``repoze.bfg`` uses the WSGI protocol to handle requests and
responses, and integrates Zope, Paste, and WebOb libraries to form the
basis for a simple web object publishing framework.

Similarities with Other Frameworks
----------------------------------

``repoze.bfg`` was inspired by Zope, Django, and Pylons.

``repoze.bfg``'s traversal is inspired by Zope.  ``repoze.bfg`` uses
the Zope Component Architecture ("CA") internally like Zope 2, Zope3,
and Grok.  Developers don't interact with the CA very much during
typical development, however; it's mostly used by the framework
developer rather than the application developer.

Like Pylons, ``repoze.bfg`` is mostly policy-free.  It makes no
assertions about which database you should use, and its built-in
templating facilities are only for convenience.  It is essentially
only supplies a mechanism to map URLs to view code and convention for
calling those views.  You are free to use third-party components in
your application that fit your needs.  Also like Pylons,
``repoze.bfg`` is heavily dependent on WSGI.

The Django docs state that Django is an "MTV" framework in their `FAQ
<http://www.djangoproject.com/documentation/faq/>`_.  This also
happens to be true for ``repoze.bfg``::

  Django appears to be a MVC framework, but you call the Controller
  the "view", and the View the "template". How come you don't use the
  standard names?

  Well, the standard names are debatable.

  In our interpretation of MVC, the "view" describes the data that
  gets presented to the user. It's not necessarily how the data looks,
  but which data is presented. The view describes which data you see,
  not how you see it. It's a subtle distinction.

  So, in our case, a "view" is the Python callback function for a
  particular URL, because that callback function describes which data
  is presented.

  Furthermore, it's sensible to separate content from presentation -
  which is where templates come in. In Django, a "view" describes
  which data is presented, but a view normally delegates to a
  template, which describes how the data is presented.

  Where does the "controller" fit in, then? In Django's case, it's
  probably the framework itself: the machinery that sends a request to
  the appropriate view, according to the Django URL configuration.

  If you're hungry for acronyms, you might say that Django is a "MTV"
  framework - that is, "model", "template", and "view." That breakdown
  makes much more sense.

Jargon
------

The following jargon is used casually in descriptions of
``repoze.bfg`` operations.

request

  A ``WebOb`` request object.

response

  An object that has three attributes: app_iter (representing an
  iterable body), headerlist (representing the http headers sent
  upstream), and status (representing the http status string).  This
  is the interface defined for ``WebOb`` response objects.

view

  A "view" is a callable which returns a response object.  It should
  accept two values: context and request.

view name

  The "URL name" of a view, e.g "index.html".  If a view is configured
  without a name, its name is considered to be the empty string (which
  implies the "default view").

model

  An object representing data in the system.  A model is part of the
  object graph traversed by the system.  Models are traversed to
  determine a context.

context

  A model in the system that is found during traversal; it becomes the
  subject of a view.

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

