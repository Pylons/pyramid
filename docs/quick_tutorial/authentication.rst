.. _qtut_authentication:

==============================
20: Logins with authentication
==============================

Login views that authenticate a username and password against a list of users.


Background
==========

Most web applications have URLs that allow people to add/edit/delete content
via a web browser. Time to add :ref:`security <security_chapter>` to the
application. In this first step we introduce authentication. That is, logging
in and logging out, using Pyramid's rich facilities for pluggable user storage.

In the next step we will introduce protection of resources with authorization
security statements.


Objectives
==========

- Introduce the Pyramid concepts of authentication.

- Create login and logout views.

Steps
=====

#. We are going to use the view classes step as our starting point:

   .. code-block:: bash

       cd ..; cp -r view_classes authentication; cd authentication

#. Add ``bcrypt`` as a dependency in ``authentication/setup.py``:

   .. literalinclude:: authentication/setup.py
    :language: python
    :emphasize-lines: 6
    :linenos:

#. We can now install our project in development mode:

   .. code-block:: bash

       $VENV/bin/pip install -e .

#. Put the security hash in the ``authentication/development.ini``
   configuration file as ``tutorial.secret`` instead of putting it in the code:

   .. literalinclude:: authentication/development.ini
    :language: ini
    :linenos:

#. Create an ``authentication/tutorial/security.py`` module that can find our
   user information by providing a :term:`security policy`:

   .. literalinclude:: authentication/tutorial/security.py
    :linenos:

#. Register the ``SecurityPolicy`` with the :term:`configurator` in ``authentication/tutorial/__init__.py``:

   .. literalinclude:: authentication/tutorial/__init__.py
    :linenos:

#. Update the views in ``authentication/tutorial/views.py``:

   .. literalinclude:: authentication/tutorial/views.py
    :linenos:

#. Add a login template at ``authentication/tutorial/login.pt``:

   .. literalinclude:: authentication/tutorial/login.pt
    :language: html
    :linenos:

#. Provide a login/logout box in ``authentication/tutorial/home.pt``:

   .. literalinclude:: authentication/tutorial/home.pt
    :language: html
    :linenos:

#. Run your Pyramid application with:

   .. code-block:: bash

       $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ in a browser.

#. Click the "Log In" link.

#. Submit the login form with the username ``editor`` and the password
   ``editor``.

#. Note that the "Log In" link has changed to "Logout".

#. Click the "Logout" link.

Analysis
========

Unlike many web frameworks, Pyramid includes a built-in but optional security
model for authentication and authorization. This security system is intended to
be flexible and support many needs. In this security model, authentication (who
are you) and authorization (what are you allowed to do) are pluggable.
To learn one step at a time, we provide a system that identifies
users and lets them log out.

In this example we chose to use the bundled :class:`pyramid.authentication.AuthTktCookieHelper` helper to store the user's logged-in state in a cookie.
We enabled it in our configuration and provided a ticket-signing secret in our INI file.

Our view class grew a login view. When you reached it via a ``GET`` request, it
returned a login form. When reached via ``POST``, it processed the submitted
username and password against the ``USERS`` data store.

The function ``hash_password`` uses a one-way hashing algorithm with a salt on
the user's password via ``bcrypt``, instead of storing the password in plain
text. This is considered to be a "best practice" for security.

.. note::
    There are alternative libraries to ``bcrypt`` if it is an issue on your
    system. Just make sure that the library uses an algorithm approved for
    storing passwords securely.

The function ``check_password`` will compare the two hashed values of the
submitted password and the user's password stored in the database. If the
hashed values are equivalent, then the user is authenticated, else
authentication fails.

Assuming the password was validated, we invoke :func:`pyramid.security.remember` to generate a cookie that is set in the response.
Subsequent requests return that cookie and identify the user.

In our template, we fetched the ``logged_in`` value from the view class. We use
this to calculate the logged-in user, if any. In the template we can then
choose to show a login link to anonymous visitors or a logout link to logged-in
users, including their login name.


Extra credit
============

#. Can I use a database instead of ``USERS`` to authenticate users?

#. Once I am logged in, does any user-centric information get jammed onto each
   request? Use ``import pdb; pdb.set_trace()`` to answer this.

.. seealso:: See also :ref:`security_chapter`, :class:`pyramid.authentication.AuthTktCookieHelper`, `bcrypt <https://pypi.org/project/bcrypt/>`_
