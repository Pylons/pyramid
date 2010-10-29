.. index::
   single: session

.. _sessions_chapter:

Session Objects
===============

A :term:`session` is a namespace which is valid for some period of
continual activity that can be used to represent a user's interaction
with a web application.

Using The Default Session Factory
---------------------------------

In order to use sessions, you must set up a :term:`session factory`
during your :mod:`pyramid` configuration.

A very basic, insecure sample session factory implementation is
provided in the :mod:`pyramid` core.  It uses a cookie to store
session information.  This implementation has the following
limitation:

- The session information in the cookies used by this implementation
  is *not* encrypted, so it can be viewed by anyone with access to the
  cookie storage of the user's browser or anyone with access to the
  network along which the cookie travels.

- The maximum number of bytes that are storable in a serialized
  representation of the session is fewer than 4000.  Only very small
  data sets can be kept in this

It is, however, digitally signed, and thus its data cannot easily be
tampered with.

You can configure this session factory in your :mod:`pyramid`
application by using the ``session_factory`` argument to the
:class:`pyramid.configuration.Configurator` class:

.. code-block:: python
   :linenos:

   from pyramid.session import InsecureCookieSessionFactoryConfig
   my_session_factory = InsecureCookieSessionFactoryConfig('itsaseekreet')
   
   from pyramid.configuration import Configurator
   config = Configurator(session_factory = my_session_factory)

.. warning:: 

   Note the very long, very explicit name for
   ``InsecureCookieSessionFactoryConfig``.  It's trying to tell you
   that this implementation is, by default, *insecure*.  You should
   not use it when you keep sensitive information in the session
   object, as the information can be easily read by both users of your
   application and third parties who have access to your users'
   network traffic.  Use a different session factory implementation
   (preferably one which keeps session data on the server) for
   anything but the most basic of applications where "session security
   doesn't matter".

Using a Session Object
----------------------

Once a session factory has been configured for your application, you
can access session objects provided by the session factory by asking
for the ``session`` attribute of any :term:`request` object.  For
example:

.. code-block:: python
   :linenos:

   from webob import Response

   def myview(request):
       session = request.session
       if 'abc' in session:
           session['fred'] = 'yes'
       session['abc'] = '123'
       if 'fred' in session:
           return Response('Fred was in the session')
       else:
           return Response('Fred was not in the session')

You can use a session much like a Python dictionary.  It supports all
methods of a Python dictionary, and it has three extra attributes, and
two extra methods.

Extra attributes:

``created``
  An integer timestamp indicating the time that this session was created.

``new``
  A boolean.  If ``new`` is True, this session is new.  Otherwise, it has 
  been constituted from data that was already serialized.

Extra methods:

``changed()``
  Call this when you mutate a mutable value in the session namespace.

``invalidate()``
  Call this when you want to invalidate the session (dump all data,
  and -- perhaps -- set a clearing cookie).

The formal definition of the methods and attributes supported by the
session object are in the :class:`pyramid.interfaces.ISession`
documentation.

Some gotchas:

- Keys and values of session data must be *pickleable*.  This means,
  typically, that they must be instances of basic types of objects,
  such as strings, lists, dictionaries, tuples, integers, etc.  If you
  place an object in a session data key or value that is not
  pickleable, an error will be raised when the session is serialized.

- If you place a mutable value (for example, a list or a dictionary)
  in a session object, and you subsequently mutate that value, you
  must call the ``changed()`` method of the session object.  This is
  because, although the session object can detect when you call its
  data-modifying methods such as ``__setitem__``, ``pop`` and other
  (and thus the session knows it needs to reserialize the session
  data), when you change a mutable object stored in the session
  itself, the session has no way to know that you changed that value.
  When in doubt, call ``changed()`` after you've changed sessioning
  data.

.. index::
   single: pyramid_beaker
   single: Beaker

Using Alternate Session Factories
---------------------------------

At the time of this writing, exactly one alternate session factory
implementation exists, named ``pyramid_beaker``. This is a session
factory that uses the `Beaker <http://beaker.groovie.org/>`_ library
as a backend.  Beaker has support for file-based sessions, database
based sessions, and encrypted cookie-based sessions.  See
`http://github.com/Pylons/pyramid_beaker
<http://github.com/Pylons/pyramid_beaker>`_ for more information about
``pyramid_beaker``.

.. index::
   single: session factory

Creating Your Own Session Factory
---------------------------------

If none of the default or otherwise available sessioning
implementations for :mod:`pyramid` suit you, you may create your own
session object by implementing a :term:`session factory`.  Your
session factory should return a :term:`session`.  The interfaces for
both types are available in
:class:`pyramid.interfaces.ISessionFactory` and
:class:`pyramid.interfaces.ISession`.  You might use the cookie
implementation in the :mod:`pyramid.session` module as inspiration.

