.. _qtut_logging:

============================================
16: Collecting Application Info With Logging
============================================

Capture debugging and error output from your web applications using standard
Python logging.


Background
==========

It's important to know what is going on inside our web application. In
development we might need to collect some output. In production, we might need
to detect problems when other people use the site. We need *logging*.

Fortunately Pyramid uses the normal Python approach to logging. The scaffold
generated in your ``development.ini`` has a number of lines that configure the
logging for you to some reasonable defaults. You then see messages sent by
Pyramid, for example, when a new request comes in.


Objectives
==========

- Inspect the configuration setup used for logging.

- Add logging statements to your view code.


Steps
=====

#. First we copy the results of the ``view_classes`` step:

   .. code-block:: bash

    $ cd ..; cp -r view_classes logging; cd logging
    $ $VENV/bin/pip install -e .

#. Extend ``logging/tutorial/views.py`` to log a message:

   .. literalinclude:: logging/tutorial/views.py
    :linenos:

#. Finally let's edit ``development.ini`` configuration file to enable logging
   for our Pyramid application:

   .. literalinclude:: logging/development.ini
       :language: ini

#. Make sure the tests still pass:

   .. code-block:: bash

    $ $VENV/bin/py.test tutorial/tests.py -q
    ....
    4 passed in 0.41 seconds

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ and http://localhost:6543/howdy in your browser.
   Note, both in the console and in the debug toolbar, the message that you
   logged.


Analysis
========

In our configuration file ``development.ini``, our ``tutorial`` Python package
is set up as a logger and configured to log messages at a ``DEBUG`` or higher
level. When you visit http://localhost:6543, your console will now show:

.. code-block:: text

    2013-08-09 10:42:42,968 DEBUG [tutorial.views][MainThread] In home view

Also, if you have configured your Pyramid application to use the
``pyramid_debugtoolbar``, logging statements appear in one of its menus.

.. seealso:: See also :ref:`logging_chapter`.
