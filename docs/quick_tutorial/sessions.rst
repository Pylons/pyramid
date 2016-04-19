.. _qtut_sessions:

=================================
17: Transient Data Using Sessions
=================================

Store and retrieve non-permanent data in Pyramid sessions.


Background
==========

When people use your web application, they frequently perform a task that
requires semi-permanent data to be saved. For example, a shopping cart. This is
called a :term:`session`.

Pyramid has basic built-in support for sessions.  Third party packages such as
`pyramid_redis_sessions
<https://github.com/ericrasmussen/pyramid_redis_sessions>`_ provide richer
session support. Or you can create your own custom sessioning engine. Let's
take a look at the :doc:`built-in sessioning support <../narr/sessions>`.


Objectives
==========

- Make a session factory using a built-in, simple Pyramid sessioning system.

- Change our code to use a session.


Steps
=====

#. First we copy the results of the ``view_classes`` step:

   .. code-block:: bash

    $ cd ..; cp -r view_classes sessions; cd sessions
    $ $VENV/bin/pip install -e .

#. Our ``sessions/tutorial/__init__.py`` needs a choice of session factory to
   get registered with the :term:`configurator`:

   .. literalinclude:: sessions/tutorial/__init__.py
    :linenos:

#. Our views in ``sessions/tutorial/views.py`` can now use ``request.session``:

   .. literalinclude:: sessions/tutorial/views.py
    :linenos:

#. The template at ``sessions/tutorial/home.pt`` can display the value:

   .. literalinclude:: sessions/tutorial/home.pt
    :language: html
    :linenos:

#. Make sure the tests still pass:

   .. code-block:: bash

    $ $VENV/bin/py.test tutorial/tests.py -q
    ....
    4 passed in 0.42 seconds

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ and http://localhost:6543/howdy in your browser.
   As you reload and switch between those URLs, note that the counter increases
   and is *not* specific to the URL.

#. Restart the application and revisit the page. Note that counter still
   increases from where it left off.


Analysis
========

Pyramid's :term:`request` object now has a ``session`` attribute that we can
use in our view code. It acts like a dictionary.

Since all the views are using the same counter, we made the counter a Python
property at the view class level. With this, each reload will increase the
counter displayed in our template.

In web development, "flash messages" are notes for the user that need to appear
on a screen after a future web request. For example, when you add an item using
a form ``POST``, the site usually issues a second HTTP Redirect web request to
view the new item. You might want a message to appear after that second web
request saying "Your item was added." You can't just return it in the web
response for the POST, as it will be tossed out during the second web request.

Flash messages are a technique where messages can be stored between requests,
using sessions, then removed when they finally get displayed.

.. seealso::
   :ref:`sessions_chapter`,
   :ref:`flash_messages`, and
   :ref:`session_module`.
