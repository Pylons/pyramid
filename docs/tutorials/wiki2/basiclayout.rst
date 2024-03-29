.. _wiki2_basic_layout:

============
Basic Layout
============

The starter files generated from choosing the ``sqlalchemy`` backend option in
the cookiecutter are very basic, but they provide a good orientation for the
high-level patterns common to most :term:`URL dispatch`-based :app:`Pyramid`
projects.


Application configuration with ``__init__.py``
----------------------------------------------

A directory on disk can be turned into a Python :term:`package` by containing
an ``__init__.py`` file.  Even if empty, this marks a directory as a Python
package.  We use ``__init__.py`` both as a marker, indicating the directory in
which it's contained is a package, and to contain application configuration
code.

Open ``tutorial/__init__.py``.  It should already contain the following:

.. literalinclude:: src/basiclayout/tutorial/__init__.py
    :linenos:
    :language: py

Let's go over this piece-by-piece. First we need some imports to support later
code:

.. literalinclude:: src/basiclayout/tutorial/__init__.py
    :end-before: main
    :lineno-match:
    :language: py

``__init__.py`` defines a function named ``main``.  Here is the entirety of
the ``main`` function we've defined in our ``__init__.py``:

.. literalinclude:: src/basiclayout/tutorial/__init__.py
    :pyobject: main
    :lineno-match:
    :language: py

When you invoke the ``pserve development.ini`` command, the ``main`` function
above is executed.  It accepts some settings and returns a :term:`WSGI`
application.  (See :ref:`startup_chapter` for more about ``pserve``.)

Next in ``main``, construct a :term:`Configurator` object using a context manager:

.. literalinclude:: src/basiclayout/tutorial/__init__.py
    :lines: 7
    :lineno-match:
    :language: py

``settings`` is passed to the ``Configurator`` as a keyword argument with the
dictionary values passed as the ``**settings`` argument. This will be a
dictionary of settings parsed from the ``.ini`` file, which contains
deployment-related values, such as ``pyramid.reload_templates``,
``sqlalchemy.url``, and so on.

Next include :term:`Jinja2` templating bindings so that we can use renderers
with the ``.jinja2`` extension within our project.

.. literalinclude:: src/basiclayout/tutorial/__init__.py
    :lines: 8
    :lineno-match:
    :language: py

Next include the ``routes`` module using a dotted Python path. This module will
be explained in the next section.

.. literalinclude:: src/basiclayout/tutorial/__init__.py
    :lines: 9
    :lineno-match:
    :language: py

Next include the package ``models`` using a dotted Python path. The exact
setup of the models will be covered later.

.. literalinclude:: src/basiclayout/tutorial/__init__.py
    :lines: 10
    :lineno-match:
    :language: py

.. note::

   Pyramid's :meth:`pyramid.config.Configurator.include` method is the primary
   mechanism for extending the configurator and breaking your code into
   feature-focused modules.

``main`` next calls the ``scan`` method of the configurator
(:meth:`pyramid.config.Configurator.scan`), which will recursively scan our
``tutorial`` package, looking for ``@view_config`` and other special
decorators. When it finds a ``@view_config`` decorator, a view configuration
will be registered, allowing one of our application URLs to be mapped to some
code.

.. literalinclude:: src/basiclayout/tutorial/__init__.py
    :lines: 11
    :lineno-match:
    :language: py

Finally ``main`` is finished configuring things, so it uses the
:meth:`pyramid.config.Configurator.make_wsgi_app` method to return a
:term:`WSGI` application:

.. literalinclude:: src/basiclayout/tutorial/__init__.py
    :lines: 12
    :lineno-match:
    :language: py


Route declarations
------------------

Open the ``tutorial/routes.py`` file. It should already contain the following:

.. literalinclude:: src/basiclayout/tutorial/routes.py
    :linenos:
    :language: py

On line 2, we call :meth:`pyramid.config.Configurator.add_static_view` with
three arguments: ``static`` (the name), ``static`` (the path), and
``cache_max_age`` (a keyword argument).

This registers a static resource view which will match any URL that starts
with the prefix ``/static`` (by virtue of the first argument to
``add_static_view``). This will serve up static resources for us from within
the ``static`` directory of our ``tutorial`` package, in this case via
``http://localhost:6543/static/`` and below (by virtue of the second argument
to ``add_static_view``).  With this declaration, we're saying that any URL that
starts with ``/static`` should go to the static view; any remainder of its
path (e.g., the ``/foo`` in ``/static/foo``) will be used to compose a path to
a static file resource, such as a CSS file.

On line 3, the module registers a :term:`route configuration` via the
:meth:`pyramid.config.Configurator.add_route` method that will be used when the
URL is ``/``. Since this route has a ``pattern`` equaling ``/``, it is the
route that will be matched when the URL ``/`` is visited, e.g.,
``http://localhost:6543/``.


View declarations via the ``views`` package
-------------------------------------------

The main function of a web framework is mapping each URL pattern to code (a
:term:`view callable`) that is executed when the requested URL matches the
corresponding :term:`route`. Our application uses the
:meth:`pyramid.view.view_config` decorator to perform this mapping.

Open ``tutorial/views/default.py`` in the ``views`` package.  It should already
contain the following:

.. literalinclude:: src/basiclayout/tutorial/views/default.py
    :linenos:
    :language: py

The important part here is that the ``@view_config`` decorator associates the
function it decorates (``my_view``) with a :term:`view configuration`,
consisting of:

   * a ``route_name`` (``home``)
   * a ``renderer``, which is a template from the ``templates`` subdirectory of
     the package.

When the pattern associated with the ``home`` view is matched during a request,
``my_view()`` will be executed.  ``my_view()`` returns a dictionary; the
renderer will use the ``templates/mytemplate.jinja2`` template to create a
response based on the values in the dictionary.

Note that ``my_view()`` accepts a single argument named ``request``.  This is
the standard call signature for a Pyramid :term:`view callable`.

Remember in our ``__init__.py`` when we executed the
:meth:`pyramid.config.Configurator.scan` method ``config.scan()``? The purpose
of calling the scan method was to find and process this ``@view_config``
decorator in order to create a view configuration within our application.
Without being processed by ``scan``, the decorator effectively does nothing.
``@view_config`` is inert without being detected via a :term:`scan`.

The sample ``my_view()`` created by the cookiecutter uses a ``try:`` and
``except:`` clause to detect if there is a problem accessing the project
database and provide an alternate error response.  That response will include
the text shown at the end of the file, which will be displayed in the browser
to inform the user about possible actions to take to solve the problem.

Open ``tutorial/views/notfound.py`` in the ``views`` package to look at the second view.

.. literalinclude:: src/basiclayout/tutorial/views/notfound.py
    :linenos:
    :language: python

Without repeating ourselves, we will point out the differences between this view and the previous.

#.  *Line 4*.
    The ``notfound_view`` function is decorated with ``@notfound_view_config``.
    This decorator registers a :term:`Not Found View` using :meth:`pyramid.config.Configurator.add_notfound_view`.

    The ``renderer`` argument names an :term:`asset specification` of ``tutorial:templates/404.jinja2``.

#.  *Lines 5-7*.
    A :term:`view callable` named ``notfound_view`` is defined, which is decorated in the step above.
    It sets the HTTP response status code to ``404``.
    The function returns an empty dictionary to the template ``404.jinja2``, which accepts no parameters anyway.


Content models with the ``models`` package
------------------------------------------

In a SQLAlchemy-based application, a *model* object is an object composed by
querying the SQL database. The ``models`` package is where the ``alchemy``
cookiecutter put the classes that implement our models.

First, open ``tutorial/models/meta.py``, which should already contain the
following:

.. literalinclude:: src/basiclayout/tutorial/models/meta.py
    :linenos:
    :language: py

``meta.py`` contains imports and support code for defining the models.

The core goal of ``meta.py`` is to define a declarative base class (``Base``) that links all of our models together into a shared :class:`sqlalchemy.schema.MetaData`.

We create the :class:`sqlalchemy.schema.MetaData` with a ``naming_convention`` to support properly naming objects when generating migrations with ``alembic``.

Any object inheriting from the new ``Base`` will be attached to ``metadata`` and
are able to reference eachother in relationships by name.

Next open ``tutorial/models/mymodel.py``, which should already contain the
following:

.. literalinclude:: src/basiclayout/tutorial/models/mymodel.py
    :linenos:
    :language: py

Notice we've defined the ``models`` as a package to make it straightforward for
defining models in separate modules. To give a simple example of a model class,
we have defined one named ``MyModel`` in ``mymodel.py``:

.. literalinclude:: src/basiclayout/tutorial/models/mymodel.py
    :pyobject: MyModel
    :lineno-match:
    :language: py

Our example model does not require an ``__init__`` method because SQLAlchemy
supplies for us a default constructor, if one is not already present, which
accepts keyword arguments of the same name as that of the mapped attributes.

.. note:: Example usage of MyModel:

    .. code-block:: python

        johnny = MyModel(name="John Doe", value=10)

The ``MyModel`` class has a ``__tablename__`` attribute.  This informs
SQLAlchemy which table to use to store the data representing instances of this
class.

Finally, open ``tutorial/models/__init__.py``, which should already
contain the following:

.. literalinclude:: src/basiclayout/tutorial/models/__init__.py
    :linenos:
    :language: py

Our ``models/__init__.py`` module defines the primary API we will use for
configuring the database connections within our application, and it contains
several functions we will cover below.

As we mentioned above, the purpose of the ``models.meta.metadata`` object is to
describe the schema of the database. This is done by defining models that
inherit from the ``Base`` object attached to that ``metadata`` object. In
Python, code is only executed if it is imported, and so to attach the
``models`` table defined in ``mymodel.py`` to the ``metadata``, we must import
it. If we skip this step, then later, when we run
:meth:`sqlalchemy.schema.MetaData.create_all`, the table will not be created
because the ``metadata`` object does not know about it!

Another important reason to import all of the models is that, when defining
relationships between models, they must all exist in order for SQLAlchemy to
find and build those internal mappings. This is why, after importing all the
models, we explicitly execute the function
:func:`sqlalchemy.orm.configure_mappers`, once we are sure all the models have
been defined and before we start creating connections.

Next we define several functions for connecting to our database. The first and
lowest level is the ``get_engine`` function. This creates an :term:`SQLAlchemy`
database engine using :func:`sqlalchemy.engine_from_config` from the
``sqlalchemy.``-prefixed settings in the ``development.ini`` file's
``[app:main]`` section. This setting is a URI (something like ``sqlite://``).

.. literalinclude:: src/basiclayout/tutorial/models/__init__.py
    :pyobject: get_engine
    :lineno-match:
    :language: py

The function ``get_session_factory`` accepts an :term:`SQLAlchemy` database
engine, and creates a ``session_factory`` from the :term:`SQLAlchemy` class
:class:`sqlalchemy.orm.session.sessionmaker`. This ``session_factory`` is then
used for creating sessions bound to the database engine.

.. literalinclude:: src/basiclayout/tutorial/models/__init__.py
    :pyobject: get_session_factory
    :lineno-match:
    :language: py

The function ``get_tm_session`` registers a database session with a transaction
manager, and returns a ``dbsession`` object. With the transaction manager, our
application will automatically issue a transaction commit after every request,
unless an exception is raised, in which case the transaction will be aborted.

.. literalinclude:: src/basiclayout/tutorial/models/__init__.py
    :pyobject: get_tm_session
    :lineno-match:
    :language: py

Finally, we define an ``includeme`` function, which is a hook for use with
:meth:`pyramid.config.Configurator.include` to activate code in a Pyramid
application add-on. It is the code that is executed above when we ran
``config.include('.models')`` in our application's ``main`` function. This
function will take the settings from the application, create an engine, and
define a ``request.dbsession`` property, which we can use to do work on behalf
of an incoming request to our application.

.. literalinclude:: src/basiclayout/tutorial/models/__init__.py
    :pyobject: includeme
    :lineno-match:
    :language: py

That's about all there is to it regarding models, views, and initialization
code in our stock application.

The ``Index`` import and the ``Index`` object creation in ``mymodel.py`` is
not required for this tutorial, and will be removed in the next step.

Tests
-----

The project contains a basic structure for a test suite using ``pytest``.
The structure is covered later in :ref:`wiki2_adding_tests`.
