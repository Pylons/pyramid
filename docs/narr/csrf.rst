.. _csrf_chapter:

Preventing Cross-Site Request Forgery Attacks
=============================================

`Cross-site request forgery
<http://en.wikipedia.org/wiki/Cross-site_request_forgery>`_ attacks are a
phenomenon whereby a user with an identity on your website might click on a
URL or button on another website which unwittingly redirects the user to your
application to perform some command that requires elevated privileges.

You can avoid most of these attacks by making sure that the correct *CSRF
token* has been set in an :app:`Pyramid` session object before performing any
actions in code which requires elevated privileges and is invoked via a form
post.  To use CSRF token support, you must enable a :term:`session factory`
as described in :ref:`using_the_default_session_factory` or
:ref:`using_alternate_session_factories`.

Using the ``session.new_csrf_token`` Method
-------------------------------------------

To add a CSRF token to the session, use the ``session.new_csrf_token`` method.

.. code-block:: python
   :linenos:

   token = request.session.new_csrf_token()

The ``.new_csrf_token`` method accepts no arguments.  It returns a *token*
string, which will be opaque and randomized.  This token will also be set
into the session, awaiting pickup by the ``session.get_csrf_token`` method.
You can subsequently use the returned token as the value of a hidden field in
a form that posts to a method that requires elevated privileges.  The handler
for the form post should use ``session.get_csrf_token`` (explained below) to
obtain the current CSRF token related to the user from the session, and
compare it to the value of the hidden form field.

Using the ``session.get_csrf_token`` Method
-------------------------------------------

To get the current CSRF token from the session, use the
``session.get_csrf_token`` method.

.. code-block:: python
   :linenos:

   token = request.session.get_csrf_token()

The ``get_csrf_token`` method accepts no arguments.  It returns the "current"
*token* string (as per the last call to ``session.new_csrf_token``).  You can
then use it to compare against the token provided within form post hidden
value data.  For example, if your form rendering included the CSRF token
obtained via ``session.new_csrf_token`` as a hidden input field named
``csrf_token``:

.. code-block:: python
   :linenos:

   token = request.session.get_csrf_token()
   if token != request.POST['csrf_token']:
       raise ValueError('CSRF token did not match')


