.. index::
   single: session

.. _sessions_chapter:

Sessions
========

A :term:`session` is a namespace which is valid for some period of continual
activity that can be used to represent a user's interaction with a web
application.

This chapter describes how to configure sessions, what session implementations
:app:`Pyramid` provides out of the box, how to store and retrieve data from
sessions, and two session-specific features: flash messages, and cross-site
request forgery attack prevention.

.. index::
   single: session factory (default)

.. _using_the_default_session_factory:

Using the Default Session Factory
---------------------------------

In order to use sessions, you must set up a :term:`session factory` during your
:app:`Pyramid` configuration.

A very basic, insecure sample session factory implementation is provided in the
:app:`Pyramid` core.  It uses a cookie to store session information.  This
implementation has the following limitations:

- The session information in the cookies used by this implementation is *not*
  encrypted, so it can be viewed by anyone with access to the cookie storage of
  the user's browser or anyone with access to the network along which the
  cookie travels.

- The maximum number of bytes that are storable in a serialized representation
  of the session is fewer than 4000.  This is suitable only for very small data
  sets.

It is digitally signed, however, and thus its data cannot easily be tampered
with.

You can configure this session factory in your :app:`Pyramid` application by
using the :meth:`pyramid.config.Configurator.set_session_factory` method.

.. code-block:: python
   :linenos:

   from pyramid.session import SignedCookieSessionFactory
   my_session_factory = SignedCookieSessionFactory('itsaseekreet')

   from pyramid.config import Configurator
   config = Configurator()
   config.set_session_factory(my_session_factory)

.. warning::

   By default the :func:`~pyramid.session.SignedCookieSessionFactory`
   implementation is *unencrypted*.  You should not use it when you keep
   sensitive information in the session object, as the information can be
   easily read by both users of your application and third parties who have
   access to your users' network traffic.  And, if you use this sessioning
   implementation, and you inadvertently create a cross-site scripting
   vulnerability in your application, because the session data is stored
   unencrypted in a cookie, it will also be easier for evildoers to obtain the
   current user's cross-site scripting token.  In short, use a different
   session factory implementation (preferably one which keeps session data on
   the server) for anything but the most basic of applications where "session
   security doesn't matter", and you are sure your application has no
   cross-site scripting vulnerabilities.

.. index::
   single: session object

Using a Session Object
----------------------

Once a session factory has been configured for your application, you can access
session objects provided by the session factory via the ``session`` attribute
of any :term:`request` object.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   def myview(request):
       session = request.session
       if 'abc' in session:
           session['fred'] = 'yes'
       session['abc'] = '123'
       if 'fred' in session:
           return Response('Fred was in the session')
       else:
           return Response('Fred was not in the session')

The first time this view is invoked produces ``Fred was not in the session``.
Subsequent invocations produce ``Fred was in the session``, assuming of course
that the client side maintains the session's identity across multiple requests.

You can use a session much like a Python dictionary.  It supports all
dictionary methods, along with some extra attributes and methods.

Extra attributes:

``created``
  An integer timestamp indicating the time that this session was created.

``new``
  A boolean.  If ``new`` is True, this session is new.  Otherwise, it has been
  constituted from data that was already serialized.

Extra methods:

``changed()``
  Call this when you mutate a mutable value in the session namespace. See the
  gotchas below for details on when and why you should call this.

``invalidate()``
  Call this when you want to invalidate the session (dump all data, and perhaps
  set a clearing cookie).

The formal definition of the methods and attributes supported by the session
object are in the :class:`pyramid.interfaces.ISession` documentation.

Some gotchas:

- Keys and values of session data must be *pickleable*.  This means, typically,
  that they are instances of basic types of objects, such as strings, lists,
  dictionaries, tuples, integers, etc.  If you place an object in a session
  data key or value that is not pickleable, an error will be raised when the
  session is serialized.

- If you place a mutable value (for example, a list or a dictionary) in a
  session object, and you subsequently mutate that value, you must call the
  ``changed()`` method of the session object. In this case, the session has no
  way to know that it was modified.  However, when you modify a session object
  directly, such as setting a value (i.e., ``__setitem__``), or removing a key
  (e.g., ``del`` or ``pop``), the session will automatically know that it needs
  to re-serialize its data, thus calling ``changed()`` is unnecessary. There is
  no harm in calling ``changed()`` in either case, so when in doubt, call it
  after you've changed sessioning data.

.. index::
   single: pyramid_redis_sessions
   single: session factory (alternates)

.. _using_alternate_session_factories:

Using Alternate Session Factories
---------------------------------

The following session factories exist at the time of this writing.

======================= ======= =============================
Session Factory         Backend   Description
======================= ======= =============================
pyramid_redis_sessions_ Redis_  Server-side session library
                                for Pyramid, using Redis for
                                storage.
pyramid_beaker_         Beaker_ Session factory for Pyramid
                                backed by the Beaker
                                sessioning system.
======================= ======= =============================

.. _pyramid_redis_sessions: https://pypi.python.org/pypi/pyramid_redis_sessions
.. _Redis: http://redis.io/

.. _pyramid_beaker: https://pypi.python.org/pypi/pyramid_beaker
.. _Beaker: http://beaker.readthedocs.org/en/latest/

.. index::
   single: session factory (custom)

Creating Your Own Session Factory
---------------------------------

If none of the default or otherwise available sessioning implementations for
:app:`Pyramid` suit you, you may create your own session object by implementing
a :term:`session factory`.  Your session factory should return a
:term:`session`.  The interfaces for both types are available in
:class:`pyramid.interfaces.ISessionFactory` and
:class:`pyramid.interfaces.ISession`. You might use the cookie implementation
in the :mod:`pyramid.session` module as inspiration.

.. index::
   single: flash messages

.. _flash_messages:

Flash Messages
--------------

"Flash messages" are simply a queue of message strings stored in the
:term:`session`.  To use flash messaging, you must enable a :term:`session
factory` as described in :ref:`using_the_default_session_factory` or
:ref:`using_alternate_session_factories`.

Flash messaging has two main uses: to display a status message only once to the
user after performing an internal redirect, and to allow generic code to log
messages for single-time display without having direct access to an HTML
template. The user interface consists of a number of methods of the
:term:`session` object.

.. index::
   single: session.flash

Using the ``session.flash`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add a message to a flash message queue, use a session object's ``flash()``
method:

.. code-block:: python

   request.session.flash('mymessage')

The ``flash()`` method appends a message to a flash queue, creating the queue
if necessary.

``flash()`` accepts three arguments:

.. method:: flash(message, queue='', allow_duplicate=True)

The ``message`` argument is required.  It represents a message you wish to
later display to a user.  It is usually a string but the ``message`` you
provide is not modified in any way.

The ``queue`` argument allows you to choose a queue to which to append the
message you provide.  This can be used to push different kinds of messages into
flash storage for later display in different places on a page.  You can pass
any name for your queue, but it must be a string. Each queue is independent,
and can be popped by ``pop_flash()`` or examined via ``peek_flash()``
separately.  ``queue`` defaults to the empty string.  The empty string
represents the default flash message queue.

.. code-block:: python

   request.session.flash(msg, 'myappsqueue')

The ``allow_duplicate`` argument defaults to ``True``.  If this is ``False``,
and you attempt to add a message value which is already present in the queue,
it will not be added.

.. index::
   single: session.pop_flash

Using the ``session.pop_flash`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once one or more messages have been added to a flash queue by the
``session.flash()`` API, the ``session.pop_flash()`` API can be used to pop an
entire queue and return it for use.

To pop a particular queue of messages from the flash object, use the session
object's ``pop_flash()`` method. This returns a list of the messages that were
added to the flash queue, and empties the queue.

.. method:: pop_flash(queue='')

.. testsetup::

   from pyramid import testing
   request = testing.DummyRequest()

.. doctest::

   >>> request.session.flash('info message')
   >>> request.session.pop_flash()
   ['info message']

Calling ``session.pop_flash()`` again like above without a corresponding call
to ``session.flash()`` will return an empty list, because the queue has already
been popped.

.. doctest::

   >>> request.session.flash('info message')
   >>> request.session.pop_flash()
   ['info message']
   >>> request.session.pop_flash()
   []

.. index::
   single: session.peek_flash

Using the ``session.peek_flash`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once one or more messages have been added to a flash queue by the
``session.flash()`` API, the ``session.peek_flash()`` API can be used to "peek"
at that queue.  Unlike ``session.pop_flash()``, the queue is not popped from
flash storage.

.. method:: peek_flash(queue='')

.. doctest::

   >>> request.session.flash('info message')
   >>> request.session.peek_flash()
   ['info message']
   >>> request.session.peek_flash()
   ['info message']
   >>> request.session.pop_flash()
   ['info message']
   >>> request.session.peek_flash()
   []

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
:app:`Pyramid` sessions provide facilities to create and check CSRF tokens.

To use CSRF tokens, you must first enable a :term:`session factory` as
described in :ref:`using_the_default_session_factory` or
:ref:`using_alternate_session_factories`.

.. index::
   single: session.get_csrf_token

Using the ``session.get_csrf_token`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get the current CSRF token from the session, use the
``session.get_csrf_token()`` method.

.. code-block:: python

   token = request.session.get_csrf_token()

The ``session.get_csrf_token()`` method accepts no arguments.  It returns a
CSRF *token* string. If ``session.get_csrf_token()`` or
``session.new_csrf_token()`` was invoked previously for this session, then the
existing token will be returned.  If no CSRF token previously existed for this
session, then a new token will be set into the session and returned.  The newly
created token will be opaque and randomized.

You can use the returned token as the value of a hidden field in a form that
posts to a method that requires elevated privileges, or supply it as a request
header in AJAX requests.

For example, include the CSRF token as a hidden field:

.. code-block:: html

    <form method="post" action="/myview">
      <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
      <input type="submit" value="Delete Everything">
    </form>

Or include it as a header in a jQuery AJAX request:

.. code-block:: javascript

    var csrfToken = ${request.session.get_csrf_token()};
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
   single: session.new_csrf_token

Using the ``session.new_csrf_token`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To explicitly create a new CSRF token, use the ``session.new_csrf_token()``
method.  This differs only from ``session.get_csrf_token()`` inasmuch as it
clears any existing CSRF token, creates a new CSRF token, sets the token into
the session, and returns the token.

.. code-block:: python

   token = request.session.new_csrf_token()

Checking CSRF Tokens Manually
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In request handling code, you can check the presence and validity of a CSRF
token with :func:`pyramid.session.check_csrf_token`. If the token is valid, it
will return ``True``, otherwise it will raise ``HTTPBadRequest``. Optionally,
you can specify ``raises=False`` to have the check return ``False`` instead of
raising an exception.

By default, it checks for a POST parameter named ``csrf_token`` or a header
named ``X-CSRF-Token``.

.. code-block:: python

   from pyramid.session import check_csrf_token

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
are non standard). If a host in the list of domains starts with a ``.`` then
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
        ...

.. note::
   A mismatch of a CSRF token is treated like any other predicate miss, and the
   predicate system, when it doesn't find a view, raises ``HTTPNotFound``
   instead of ``HTTPBadRequest``, so ``check_csrf=True`` behavior is different
   from calling :func:`pyramid.session.check_csrf_token`.
