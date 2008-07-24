================================================
Step 01: Non-XML Hello World for ``repoze.bfg``
================================================

Before we work on implementing an XML graph, we need a simple starting
point for a basic ``repoze.bfg`` application.  In this step we'll do
the least amount possible to run a ``repoze.bfg`` sample application.

.. note::

  All steps in this writeup presume that you have a virtualenv setup
  as shown in the Installation step.  More specifically: *make sure
  you are using that virtualenv's Python* !!

Directory Layout
====================

Each step in this writeup has a subdirectory for the working
application described in that step.  Thus, starting at this docs
directory, we have::

  docs/
    step01/
      myapp/
        __init__.py
      	configure.zcml
      	models.py
      	views.py
      run.py
    step02/
    step03/

Below we discuss each file in the ``step01``, then show how to run and
use the demo application.


Directory ``myapp``
---------------------

This directory contains the *package* to be published.  That's right,
I said *package*.  ``repoze.bfg``, as we will see in a moment, uses
Python packages as the unit of publishing.


Module ``myapp/__init__.py``
------------------------------

This is (usually-empty) file that makes a directory into a Python
"package."  For ``repoze.bfg`` this is particularly important


Module ``myapp/configure.zcml``
--------------------------------

Unlike other frameworks, ``repoze.bfg`` doesn't try to hide
configuration.  Instead, configuration using ZCML is the central
wiring point.  At the same time, ZCML is used in a very basic way, to
avoid confusion it can cause.

.. literalinclude:: step01/myapp/configure.zcml
   :linenos:
   :language: xml

#. Lines 1-3 provide the root node and namespaces for the
   configuration language.  ``bfg`` is the namespace for
   ``repoze.bfg``-specific configuration directives.

#. Line 5 initializes those ``repoze.bfg``-specific configuration
   directives.

#. Lines 8-11 register a single view for model objects that support
   the IMyModel interface.  In this case we made a default view, which
   means going to ``/a`` triggers the default view of instance ``a``.
   Finally, the ``view`` attribute points at a Python function that
   does all the work for this view.


Module ``myapp/models.py``
-----------------------------

In our sample app, the ``models.py`` module provides the model data.
We create an interface ``IMyModel`` that gives us the "type system"
for our data.  We then write a class ``MyModel`` that provides the
behavior for instances of the ``IMyModel`` type.

.. literalinclude:: step01/myapp/models.py
   :linenos:

#. Lines 5-6 define the interface.

#. Lines 8-11 provide a class for that interface.

#. Lines 13-15 make a small tree of sample data (``/a`` and ``/b`` for
   URLs.)

#. Line 17 is a function that will be grabbed by the server when it
   wants to find the top of the model.


Module ``myapp/views.py``
---------------------------

Much of the heavy liftin in a ``repoze.bfg`` application comes in the
views.  These are the bridge between the content in the model, and the
HTML given back to the browser.  Since ``repoze.bfg`` is very
type-centric, URLs grab information of a certain type.  Once we have
the information and its type, we can grab a view that is registered
for that type.

.. note::

  This "Step 01" doesn't use a template.  The "view" we define is done
  in Python, which generates the HTML.  Most applications will use
  templates to generate markup.

.. literalinclude:: step01/myapp/models.py
   :linenos:

#. Lines 3 provide the ``my_hello_view`` that was registered as the
   view.  ``configure.zcml``, on Line 10, said that the default URL
   for IMyModel content should run this ``my_hello_view`` function.

   The function is handed two pieces of information: the ``context``
   and the ``request``.  The ``context`` is the data at the current
   hop in the URL.  (That data comes from the model.)  The request is
   an instance of a WebOb request.

#. Lines 4-7 generate a WebOb Response object and return it.


Module ``run.py``
---------------------

We need a small Python module that sets everything, fires up a web
server, and handles incoming requests.  Later we'll see how to use a
Paste configuration file to do this work for us.

.. literalinclude:: step01/run.py
   :linenos:

#. Line 1 uses the web server from the Paste project.

#. Line 3 imports the big gun from ``repoze.bfg``.

#. Line 4 grabs the function that hands back the top of the
   application's model data.

#. Line 5 imports the package that we want to "publish".

#. Line 7 loads the big gun with the data and the package.

#. And finally, line 8 starts the web server on port 5432.


Running and Browsing the Application
---------------------------------------

We have our minimal application now in place.  We can run the
application as follows::

  cd docs/step01
  python run.py

.. note::

  Just to say it AGAIN: make sure the Python you are using is the
  Python from your virtual environment.  One way to ensure you always
  get the right scripts is to do ``source bin/activate`` from the top
  of your virtualenv.  This will modify your PATH to look first in the
  virtual env.

You should then see::

  $ python ./run.py 
  serving on 0.0.0.0:5432 view at http://127.0.0.1:5432

If you connect in a web browser to ``http://localhost:5432/a`` you
will see::

  Hello from a @ /a

This also works for ``http://localhost:5432/b``.  However, if you
connect to ``http://localhost:5432/c`` you will get::

  404 Not Found
  The resource could not be found.

  http://localhost:5432/c