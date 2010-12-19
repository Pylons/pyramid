.. _declarative_chapter:

Declarative Configuration
=========================

The mode of configuration most comprehensively detailed by examples in
narrative chapters in this book is "imperative" configuration. This is the
configuration mode in which a developer cedes the least amount of control to
the framework; it's "imperative" because you express the configuration
directly in Python code, and you have the full power of Python at your
disposal as you issue configuration statements.  However, another mode of
configuration exists within :app:`Pyramid`, which often provides better
extensibility and configuration conflict detection.

A complete listing of ZCML directives is available within
:ref:`zcml_directives`.  This chapter provides an overview of how you might
get started with ZCML and highlights some common tasks performed when you use
ZCML.  You can get a better understanding of when it's appropriate to use
ZCML from :ref:`extending_chapter`.

.. index::
   single: declarative configuration

.. _declarative_configuration:

Declarative Configuration
-------------------------

A :app:`Pyramid` application can be configured "declaratively", if so
desired.  Declarative configuration relies on *declarations* made external to
the code in a configuration file format named :term:`ZCML` (Zope
Configuration Markup Language), an XML dialect.

A :app:`Pyramid` application configured declaratively requires not
one, but two files: a Python file and a :term:`ZCML` file.

In a file named ``helloworld.py``:

.. code-block:: python
   :linenos:

   from paste.httpserver import serve
   from pyramid.response import Response
   from pyramid.config import Configurator

   def hello_world(request):
       return Response('Hello world!')

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.load_zcml('configure.zcml')
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

In a file named ``configure.zcml`` in the same directory as the
previously created ``helloworld.py``:

.. code-block:: xml
   :linenos:

   <configure xmlns="http://pylonshq.com/pyramid">

     <include package="pyramid.includes" />

     <view
       view="helloworld.hello_world"
      />

   </configure>

This pair of files forms an application functionally equivalent to the
application we created earlier in :ref:`imperative_configuration`.
Let's examine the differences between that code listing and the code
above.

In :ref:`imperative_configuration`, we had the following lines within
the ``if __name__ == '__main__'`` section of ``helloworld.py``:

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.add_view(hello_world)
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

In our "declarative" code, we've removed the call to ``add_view`` and
replaced it with a call to the
:meth:`pyramid.config.Configurator.load_zcml` method so that
it now reads as:

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.load_zcml('configure.zcml')
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

Everything else is much the same.

The ``config.load_zcml('configure.zcml')`` line tells the configurator
to load configuration declarations from the file named
``configure.zcml`` which sits next to ``helloworld.py`` on the
filesystem.  Let's take a look at that ``configure.zcml`` file again:

.. code-block:: xml
   :linenos:

   <configure xmlns="http://pylonshq.com/pyramid">

      <include package="pyramid.includes" />

      <view
        view="helloworld.hello_world"
       />

   </configure>

Note that this file contains some XML, and that the XML contains a
``<view>`` :term:`configuration declaration` tag that references a
:term:`dotted Python name`.  This dotted name refers to the
``hello_world`` function that lives in our ``helloworld`` Python
module.

This ``<view>`` declaration tag performs the same function as the
``add_view`` method that was employed within
:ref:`imperative_configuration`.  In fact, the ``<view>`` tag is
effectively a "macro" which calls the
:meth:`pyramid.config.Configurator.add_view` method on your
behalf.

The ``<view>`` tag is an example of a :app:`Pyramid` declaration
tag.  Other such tags include ``<route>`` and ``<scan>``.  Each of
these tags is effectively a "macro" which calls methods of a
:class:`pyramid.config.Configurator` object on your behalf.

Essentially, using a :term:`ZCML` file and loading it from the
filesystem allows us to put our configuration statements within this
XML file rather as declarations, rather than representing them as
method calls to a :term:`Configurator` object.  Otherwise, declarative
and imperative configuration are functionally equivalent.

Using declarative configuration has a number of benefits, the primary
benefit being that applications configured declaratively can be
*overridden* and *extended* by third parties without requiring the
third party to change application code.  If you want to build a
framework or an extensible application, using declarative
configuration is a good idea.

Declarative configuration has an obvious downside: you can't use
plain-old-Python syntax you probably already know and understand to
configure your application; instead you need to use :term:`ZCML`.

.. index::
   single: ZCML conflict detection

ZCML Conflict Detection
~~~~~~~~~~~~~~~~~~~~~~~

A minor additional feature of ZCML is *conflict detection*.  If you
define two declaration tags within the same ZCML file which logically
"collide", an exception will be raised, and the application will not
start.  For example, the following ZCML file has two conflicting
``<view>`` tags:

.. code-block:: xml
   :linenos:

    <configure xmlns="http://pylonshq.com/pyramid">

      <include package="pyramid.includes" />

      <view
        view="helloworld.hello_world"
       />

      <view
        view="helloworld.hello_world"
       />

    </configure>

If you try to use this ZCML file as the source of ZCML for an
application, an error will be raised when you attempt to start the
application.  This error will contain information about which tags
might have conflicted.

.. index::
   single: helloworld (declarative)

.. _helloworld_declarative:

Hello World, Goodbye World (Declarative)
----------------------------------------

Another almost entirely equivalent mode of application configuration
exists named *declarative* configuration.  :app:`Pyramid` can be
configured for the same "hello world" application "declaratively", if
so desired.

To do so, first, create a file named ``helloworld.py``:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator
   from pyramid.response import Response
   from paste.httpserver import serve

   def hello_world(request):
       return Response('Hello world!')

   def goodbye_world(request):
       return Response('Goodbye world!')

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.load_zcml('configure.zcml')
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

Then create a file named ``configure.zcml`` in the same directory as
the previously created ``helloworld.py``:

.. code-block:: xml
   :linenos:

   <configure xmlns="http://pylonshq.com/pyramid">

     <include package="pyramid.includes" />

     <view
       view="helloworld.hello_world"
      />

     <view
       name="goodbye"
       view="helloworld.goodbye_world"
      />

   </configure>

This pair of files forms an application functionally equivalent to the
application we created earlier in :ref:`helloworld_imperative`.  We can run
it the same way.

.. code-block:: text

   $ python helloworld.py
   serving on 0.0.0.0:8080 view at http://127.0.0.1:8080

Let's examine the differences between the code in that section and the code
above.  In :ref:`helloworld_imperative_appconfig`, we had the following lines
within the ``if __name__ == '__main__'`` section of ``helloworld.py``:

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.add_view(hello_world)
       config.add_view(goodbye_world, name='goodbye')
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

In our "declarative" code, we've added a call to the
:meth:`pyramid.config.Configurator.load_zcml` method with
the value ``configure.zcml``, and we've removed the lines which read
``config.add_view(hello_world)`` and ``config.add_view(goodbye_world,
name='goodbye')``, so that it now reads as:

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.load_zcml('configure.zcml')
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

Everything else is much the same.

The ``config.load_zcml('configure.zcml')`` line tells the configurator
to load configuration declarations from the ``configure.zcml`` file
which sits next to ``helloworld.py``.  Let's take a look at the
``configure.zcml`` file now:

.. code-block:: xml
   :linenos:

   <configure xmlns="http://pylonshq.com/pyramid">

      <include package="pyramid.includes" />

      <view
        view="helloworld.hello_world"
       />

      <view
        name="goodbye"
        view="helloworld.goodbye_world"
       />

   </configure>

We already understand what the view code does, because the application
is functionally equivalent to the application described in
:ref:`helloworld_imperative`, but use of :term:`ZCML` is new.  Let's
break that down tag-by-tag.

The ``<configure>`` Tag
~~~~~~~~~~~~~~~~~~~~~~~

The ``configure.zcml`` ZCML file contains this bit of XML:

.. code-block:: xml
   :linenos:

    <configure xmlns="http://pylonshq.com/pyramid">

       <!-- other directives -->

    </configure>

Because :term:`ZCML` is XML, and because XML requires a single root
tag for each document, every ZCML file used by :app:`Pyramid` must
contain a ``configure`` container directive, which acts as the root
XML tag.  It is a "container" directive because its only job is to
contain other directives.

See also :ref:`configure_directive` and :ref:`word_on_xml_namespaces`.

The ``<include>`` Tag
~~~~~~~~~~~~~~~~~~~~~

The ``configure.zcml`` ZCML file contains this bit of XML within the
``<configure>`` root tag:

.. code-block:: xml
   :linenos:

   <include package="pyramid.includes" />

This self-closing tag instructs :app:`Pyramid` to load a ZCML file
from the Python package with the :term:`dotted Python name`
``pyramid.includes``, as specified by its ``package`` attribute.
This particular ``<include>`` declaration is required because it
actually allows subsequent declaration tags (such as ``<view>``, which
we'll see shortly) to be recognized.  The ``<include>`` tag
effectively just includes another ZCML file, causing its declarations
to be executed.  In this case, we want to load the declarations from
the file named ``configure.zcml`` within the
:mod:`pyramid.includes` Python package.  We know we want to load
the ``configure.zcml`` from this package because ``configure.zcml`` is
the default value for another attribute of the ``<include>`` tag named
``file``.  We could have spelled the include tag more verbosely, but
equivalently as:

.. code-block:: xml
   :linenos:

   <include package="pyramid.includes" 
            file="configure.zcml"/>

The ``<include>`` tag that includes the ZCML statements implied by the
``configure.zcml`` file from the Python package named
:mod:`pyramid.includes` is basically required to come before any
other named declaration in an application's ``configure.zcml``.  If it
is not included, subsequent declaration tags will fail to be
recognized, and the configuration system will generate an error at
startup.  However, the ``<include package="pyramid.includes"/>``
tag needs to exist only in a "top-level" ZCML file, it needn't also
exist in ZCML files *included by* a top-level ZCML file.

See also :ref:`include_directive`.

The ``<view>`` Tag
~~~~~~~~~~~~~~~~~~

The ``configure.zcml`` ZCML file contains these bits of XML *after* the
``<include>`` tag, but *within* the ``<configure>`` root tag:

.. code-block:: xml
   :linenos:

   <view
     view="helloworld.hello_world"
    />

   <view
     name="goodbye"
     view="helloworld.goodbye_world"
    />

These ``<view>`` declaration tags direct :app:`Pyramid` to create
two :term:`view configuration` registrations.  The first ``<view>``
tag has an attribute (the attribute is also named ``view``), which
points at a :term:`dotted Python name`, referencing the
``hello_world`` function defined within the ``helloworld`` package.
The second ``<view>`` tag has a ``view`` attribute which points at a
:term:`dotted Python name`, referencing the ``goodbye_world`` function
defined within the ``helloworld`` package.  The second ``<view>`` tag
also has an attribute called ``name`` with a value of ``goodbye``.

These effect of the ``<view>`` tag declarations we've put into our
``configure.zcml`` is functionally equivalent to the effect of lines
we've already seen in an imperatively-configured application.  We're
just spelling things differently, using XML instead of Python.

In our previously defined application, in which we added view
configurations imperatively, we saw this code:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.add_view(hello_world)
   config.add_view(goodbye_world, name='goodbye')

Each ``<view>`` declaration tag encountered in a ZCML file effectively
invokes the :meth:`pyramid.config.Configurator.add_view`
method on the behalf of the developer.  Various attributes can be
specified on the ``<view>`` tag which influence the :term:`view
configuration` it creates.

Since the relative ordering of calls to
:meth:`pyramid.config.Configurator.add_view` doesn't matter
(see the sidebar entitled *View Dispatch and Ordering* within
:ref:`adding_configuration`), the relative order of ``<view>`` tags in
ZCML doesn't matter either.  The following ZCML orderings are
completely equivalent:

.. topic:: Hello Before Goodbye

  .. code-block:: xml
     :linenos:

     <view
       view="helloworld.hello_world"
      />

     <view
       name="goodbye"
       view="helloworld.goodbye_world"
      />

.. topic:: Goodbye Before Hello

  .. code-block:: xml
     :linenos:

     <view
       name="goodbye"
       view="helloworld.goodbye_world"
      />

     <view
       view="helloworld.hello_world"
      />

We've now configured a :app:`Pyramid` helloworld application
declaratively.  More information about this mode of configuration is
available in :ref:`declarative_configuration` and within
:ref:`zcml_reference`.

.. _zcml_scanning:

Scanning via ZCML
-----------------

:term:`ZCML` can invoke a :term:`scan` via its ``<scan>`` directive.  If a
ZCML file is processed that contains a scan directive, the package the ZCML
file points to is scanned.

.. code-block:: python
   :linenos:

   # helloworld.py

   from paste.httpserver import serve
   from pyramid.response import Response
   from pyramid.view import view_config
  
   @view_config()
   def hello(request):
       return Response('Hello')

   if __name__ == '__main__':
       from pyramid.config import Configurator
       config = Configurator()
       config.begin()
       config.load_zcml('configure.zcml')
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

.. code-block:: xml
   :linenos:

   <configure xmlns="http://namespaces.repoze.org">

     <!-- configure.zcml -->

     <include package="pyramid.includes"/>
     <scan package="."/>

   </configure>

See also :ref:`scan_directive`.

Which Mode Should I Use?
------------------------

A combination of imperative configuration, declarative configuration
via ZCML and scanning can be used to configure any application.  They
are not mutually exclusive.

The :app:`Pyramid` authors often recommend using mostly declarative
configuration, because it's the more traditional form of configuration
used in :app:`Pyramid` applications, it can be overridden and
extended by third party deployers, and there are more examples for it
"in the wild".

However, imperative mode configuration can be simpler to understand,
and the framework is not "opinionated" about the choice.  This book
presents examples in both styles, mostly interchangeably.  You can
choose the mode that best fits your brain as necessary.

.. index::
   single: ZCML view configuration

.. _mapping_views_using_zcml_section:

View Configuration Via ZCML
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may associate a view with a URL by adding :ref:`view_directive`
declarations via :term:`ZCML` in a ``configure.zcml`` file.  An
example of a view declaration in ZCML is as follows:

.. code-block:: xml
   :linenos:

   <view
     context=".resources.Hello"
     view=".views.hello_world"
     name="hello.html"
    />

The above maps the ``.views.hello_world`` view callable function to
the following set of :term:`resource location` results:

- A :term:`context` object which is an instance (or subclass) of the
  Python class represented by ``.resources.Hello``

- A :term:`view name` equalling ``hello.html``.

.. note:: Values prefixed with a period (``.``) for the ``context``
   and ``view`` attributes of a ``view`` declaration (such as those
   above) mean "relative to the Python package directory in which this
   :term:`ZCML` file is stored".  So if the above ``view`` declaration
   was made inside a ``configure.zcml`` file that lived in the
   ``hello`` package, you could replace the relative ``.resources.Hello``
   with the absolute ``hello.resources.Hello``; likewise you could
   replace the relative ``.views.hello_world`` with the absolute
   ``hello.views.hello_world``.  Either the relative or absolute form
   is functionally equivalent.  It's often useful to use the relative
   form, in case your package's name changes.  It's also shorter to
   type.

You can also declare a *default view callable* for a :term:`resource` type:

.. code-block:: xml
   :linenos:

   <view
     context=".resources.Hello"
     view=".views.hello_world"
    />

A *default view callable* simply has no ``name`` attribute.  For the above
registration, when a :term:`context` is found that is of the type
``.resources.Hello`` and there is no :term:`view name` associated with the
result of :term:`resource location`, the *default view callable* will be
used.  In this case, it's the view at ``.views.hello_world``.

A default view callable can alternately be defined by using the empty
string as its ``name`` attribute:

.. code-block:: xml
   :linenos:

   <view
     context=".resources.Hello"
     view=".views.hello_world"
     name=""
    />

You may also declare that a view callable is good for any context type
by using the special ``*`` character as the value of the ``context``
attribute:

.. code-block:: xml
   :linenos:

   <view
     context="*"
     view=".views.hello_world"
     name="hello.html"
    />

This indicates that when :app:`Pyramid` identifies that the
:term:`view name` is ``hello.html`` and the context is of any type,
the ``.views.hello_world`` view callable will be invoked.

A ZCML ``view`` declaration's ``view`` attribute can also name a
class.  In this case, the rules described in :ref:`class_as_view`
apply for the class which is named.

See :ref:`view_directive` for complete ZCML directive documentation.

.. index::
   single: ZCML directive; route

.. _zcml_route_configuration:

Configuring a Route via ZCML
----------------------------

Instead of using the imperative :meth:`pyramid.config.Configurator.add_route`
method to add a new route, you can alternately use :term:`ZCML`.
:ref:`route_directive` statements in a :term:`ZCML` file. For example, the
following :term:`ZCML declaration` causes a route to be added to the
application.

.. code-block:: xml
   :linenos:

   <route
     name="myroute"
     pattern="/prefix/{one}/{two}"
     view=".views.myview"
    />

.. note::

   Values prefixed with a period (``.``) within the values of ZCML
   attributes such as the ``view`` attribute of a ``route`` mean
   "relative to the Python package directory in which this
   :term:`ZCML` file is stored".  So if the above ``route``
   declaration was made inside a ``configure.zcml`` file that lived in
   the ``hello`` package, you could replace the relative
   ``.views.myview`` with the absolute ``hello.views.myview`` Either
   the relative or absolute form is functionally equivalent.  It's
   often useful to use the relative form, in case your package's name
   changes.  It's also shorter to type.

The order that routes are evaluated when declarative configuration is used
is the order that they appear relative to each other in the ZCML file.

See :ref:`route_directive` for full ``route`` ZCML directive
documentation.

.. _zcml_handler_configuration:

Configuring a Handler via ZCML
------------------------------

Instead of using the imperative
:meth:`pyramid.config.Configurator.add_handler` method to add a new
route, you can alternately use :term:`ZCML`.  :ref:`handler_directive`
statements in a :term:`ZCML` file used by your application is a sign that
you're using :term:`URL dispatch`.  For example, the following :term:`ZCML
declaration` causes a route to be added to the application.

.. code-block:: xml
   :linenos:

   <handler
     route_name="myroute"
     pattern="/prefix/{action}"
     handler=".handlers.MyHandler"
    />

.. note::

   Values prefixed with a period (``.``) within the values of ZCML attributes
   such as the ``handler`` attribute of a ``handler`` directive mean
   "relative to the Python package directory in which this :term:`ZCML` file
   is stored".  So if the above ``handler`` declaration was made inside a
   ``configure.zcml`` file that lived in the ``hello`` package, you could
   replace the relative ``.views.MyHandler`` with the absolute
   ``hello.views.MyHandler`` Either the relative or absolute form is
   functionally equivalent.  It's often useful to use the relative form, in
   case your package's name changes.  It's also shorter to type.

The order that the routes attached to handlers are evaluated when declarative
configuration is used is the order that they appear relative to each other in
the ZCML file.

See :ref:`handler_directive` for full ``handler`` ZCML directive
documentation.

.. index::
   triple: view; zcml; static resource

.. _zcml_static_assets_section:

Serving Static Assets Using ZCML
--------------------------------

Use of the ``static`` ZCML directive makes static assets available at a name
relative to the application root URL, e.g. ``/static``.

Note that the ``path`` provided to the ``static`` ZCML directive may be a
fully qualified :term:`asset specification`, a package-relative path, or
an *absolute path*.  The ``path`` with the value ``a/b/c/static`` of a
``static`` directive in a ZCML file that resides in the "mypackage" package
will resolve to a package-qualified assets such as
``some_package:a/b/c/static``.

Here's an example of a ``static`` ZCML directive that will serve files
up under the ``/static`` URL from the ``/var/www/static`` directory of
the computer which runs the :app:`Pyramid` application using an
absolute path.

.. code-block:: xml
   :linenos:

   <static
     name="static"
     path="/var/www/static"
    />

Here's an example of a ``static`` directive that will serve files up
under the ``/static`` URL from the ``a/b/c/static`` directory of the
Python package named ``some_package`` using a fully qualified
:term:`asset specification`.

.. code-block:: xml
   :linenos:

   <static
     name="static"
     path="some_package:a/b/c/static"
    />

Here's an example of a ``static`` directive that will serve files up
under the ``/static`` URL from the ``static`` directory of the Python
package in which the ``configure.zcml`` file lives using a
package-relative path.

.. code-block:: xml
   :linenos:

   <static
     name="static"
     path="static"
    />

Whether you use for ``path`` a fully qualified asset specification,
an absolute path, or a package-relative path, When you place your
static files on the filesystem in the directory represented as the
``path`` of the directive, you will then be able to view the static
files in this directory via a browser at URLs prefixed with the
directive's ``name``.  For instance if the ``static`` directive's
``name`` is ``static`` and the static directive's ``path`` is
``/path/to/static``, ``http://localhost:6543/static/foo.js`` will
return the file ``/path/to/static/dir/foo.js``.  The static directory
may contain subdirectories recursively, and any subdirectories may
hold files; these will be resolved by the static view as you would
expect.

While the ``path`` argument can be a number of different things, the
``name`` argument of the ``static`` ZCML directive can also be one of
a number of things: a *view name* or a *URL*.  The above examples have
shown usage of the ``name`` argument as a view name.  When ``name`` is
a *URL* (or any string with a slash (``/``) in it), static assets
can be served from an external webserver.  In this mode, the ``name``
is used as the URL prefix when generating a URL using
:func:`pyramid.url.static_url`.

For example, the ``static`` ZCML directive may be fed a ``name``
argument which is ``http://example.com/images``:

.. code-block:: xml
   :linenos:

   <static
     name="http://example.com/images"
     path="mypackage:images"
    />

Because the ``static`` ZCML directive is provided with a ``name`` argument
that is the URL prefix ``http://example.com/images``, subsequent calls to
:func:`pyramid.url.static_url` with paths that start with the ``path``
argument passed to :meth:`pyramid.url.static_url` will generate a URL
something like ``http://example.com/logo.png``.  The external webserver
listening on ``example.com`` must be itself configured to respond properly to
such a request.  The :func:`pyramid.url.static_url` API is discussed in more
detail later in this chapter.

The :meth:`pyramid.config.Configurator.add_static_view` method offers
an imperative equivalent to the ``static`` ZCML directive.  Use of the
``add_static_view`` imperative configuration method is completely equivalent
to using ZCML for the same purpose.  See :ref:`static_assets_section` for
more information.

.. index::
   pair: ZCML directive; asset

.. _asset_zcml_directive:

The ``asset`` ZCML Directive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of using :meth:`pyramid.config.Configurator.override_asset` during
:term:`imperative configuration`, an equivalent ZCML directive can be used.
The ZCML ``asset`` tag is a frontend to using
:meth:`pyramid.config.Configurator.override_asset`.

An individual :app:`Pyramid` ``asset`` ZCML statement can override a
single asset.  For example:

.. code-block:: xml
   :linenos:

    <asset
      to_override="some.package:templates/mytemplate.pt"
      override_with="another.package:othertemplates/anothertemplate.pt"
     />

The string value passed to both ``to_override`` and ``override_with``
attached to an ``asset`` directive is called an "asset specification".  The
colon separator in a specification separates the *package name* from the
*asset name*.  The colon and the following asset name are optional.  If they
are not specified, the override attempts to resolve every lookup into a
package from the directory of another package.  For example:

.. code-block:: xml
   :linenos:

    <asset
      to_override="some.package"
      override_with="another.package"
     />

Individual subdirectories within a package can also be overridden:

.. code-block:: xml
   :linenos:

    <asset
      to_override="some.package:templates/"
      override_with="another.package:othertemplates/"
     />

If you wish to override an asset directory with another directory, you *must*
make sure to attach the slash to the end of both the ``to_override``
specification and the ``override_with`` specification.  If you fail to attach
a slash to the end of an asset specification that points to a directory, you
will get unexpected results.

The package name in an asset specification may start with a dot, meaning that
the package is relative to the package in which the ZCML file resides.  For
example:

.. code-block:: xml
   :linenos:

    <asset
      to_override=".subpackage:templates/"
      override_with="another.package:templates/"
     />

See also :ref:`asset_directive`.

.. _zcml_authorization_policy:

Enabling an Authorization Policy Via ZCML
-----------------------------------------

If you'd rather use :term:`ZCML` to specify an authorization policy
than imperative configuration, modify the ZCML file loaded by your
application (usually named ``configure.zcml``) to enable an
authorization policy.

For example, to enable a policy which compares the value of an "auth ticket"
cookie passed in the request's environment which contains a reference to a
single :term:`principal` against the principals present in any :term:`ACL`
found in the resource tree when attempting to call some :term:`view`, modify
your ``configure.zcml`` to look something like this:

.. code-block:: xml
   :linenos:

   <configure xmlns="http://pylonshq.com/pyramid">

     <!-- views and other directives before this... -->

     <authtktauthenticationpolicy
       secret="iamsosecret"/>

     <aclauthorizationpolicy/>

    </configure>

"Under the hood", these statements cause an instance of the class
:class:`pyramid.authentication.AuthTktAuthenticationPolicy` to be
injected as the :term:`authentication policy` used by this application
and an instance of the class
:class:`pyramid.authorization.ACLAuthorizationPolicy` to be
injected as the :term:`authorization policy` used by this application.

:app:`Pyramid` ships with a number of authorization and
authentication policy ZCML directives that should prove useful.  See
:ref:`authentication_policies_directives_section` and
:ref:`authorization_policies_directives_section` for more information.

.. index::
   pair: ZCML directive; authentication policy

.. _authentication_policies_directives_section:

Built-In Authentication Policy ZCML Directives
----------------------------------------------

Instead of configuring an authentication policy and authorization
policy imperatively, :app:`Pyramid` ships with a few "pre-chewed"
authentication policy ZCML directives that you can make use of within
your application.

``authtktauthenticationpolicy``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When this directive is used, authentication information is obtained
from an "auth ticket" cookie value, assumed to be set by a custom
login form.

An example of its usage, with all attributes fully expanded:

.. code-block:: xml
   :linenos:

   <authtktauthenticationpolicy
     secret="goshiamsosecret"
     callback=".somemodule.somefunc"
     cookie_name="mycookiename"
     secure="false"
     include_ip="false"
     timeout="86400"
     reissue_time="600"
     max_age="31536000"
     path="/"
     http_only="false"
    />

See :ref:`authtktauthenticationpolicy_directive` for details about
this directive.

``remoteuserauthenticationpolicy``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When this directive is used, authentication information is obtained
from a ``REMOTE_USER`` key in the WSGI environment, assumed to
be set by a WSGI server or an upstream middleware component.

An example of its usage, with all attributes fully expanded:

.. code-block:: xml
   :linenos:

   <remoteuserauthenticationpolicy
     environ_key="REMOTE_USER"
     callback=".somemodule.somefunc"
    />

See :ref:`remoteuserauthenticationpolicy_directive` for detailed
information.

``repozewho1authenticationpolicy``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When this directive is used, authentication information is obtained
from a ``repoze.who.identity`` key in the WSGI environment, assumed to
be set by :term:`repoze.who` middleware.

An example of its usage, with all attributes fully expanded:

.. code-block:: xml
   :linenos:

   <repozewho1authenticationpolicy
     identifier_name="auth_tkt"
     callback=".somemodule.somefunc"
    />

See :ref:`repozewho1authenticationpolicy_directive` for detailed
information.

.. index::
   pair: ZCML directive; authorization policy

.. _authorization_policies_directives_section:

Built-In Authorization Policy ZCML Directives
---------------------------------------------

``aclauthorizationpolicy``

When this directive is used, authorization information is obtained
from :term:`ACL` objects attached to resources.

An example of its usage, with all attributes fully expanded:

.. code-block:: xml
   :linenos:

   <aclauthorizationpolicy/>

In other words, it has no configuration attributes; its existence in a
``configure.zcml`` file enables it.

See :ref:`aclauthorizationpolicy_directive` for detailed information.

.. _zcml_adding_and_overriding_renderers:

Adding and Overriding Renderers via ZCML
----------------------------------------

New templating systems and serializers can be associated with :app:`Pyramid`
renderer names.  To this end, configuration declarations can be made which
override an existing :term:`renderer factory` and which add a new renderer
factory.

Adding or overriding a renderer via ZCML is accomplished via the
:ref:`renderer_directive` ZCML directive.

For example, to add a renderer which renders views which have a
``renderer`` attribute that is a path that ends in ``.jinja2``:

.. code-block:: xml
   :linenos:

   <renderer
     name=".jinja2"
     factory="my.package.MyJinja2Renderer"
    />

The ``factory`` attribute is a :term:`dotted Python name` that must
point to an implementation of a :term:`renderer factory`.

The ``name`` attribute is the renderer name.

Registering a Renderer Factory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See :ref:`adding_a_renderer` for more information for the definition of a
:term:`renderer factory`.  Here's an example of the registration of a simple
:term:`renderer factory` via ZCML:

.. code-block:: xml
   :linenos:

   <renderer
     name="amf"
     factory="my.package.MyAMFRenderer"
    />

Adding the above ZCML to your application will allow you to use the
``my.package.MyAMFRenderer`` renderer factory implementation in view
configurations by subseqently referring to it as ``amf`` in the ``renderer``
attribute of a :term:`view configuration`:

.. code-block:: xml
   :linenos:

   <view
     view="mypackage.views.my_view"
     renderer="amf"
    />

Here's an example of the registration of a more complicated renderer
factory, which expects to be passed a filesystem path:

.. code-block:: xml
   :linenos:

   <renderer
     name=".jinja2"
     factory="my.package.MyJinja2Renderer"
    />

Adding the above ZCML to your application will allow you to use the
``my.package.MyJinja2Renderer`` renderer factory implementation in
view configurations by referring to any ``renderer`` which *ends in*
``.jinja`` in the ``renderer`` attribute of a :term:`view
configuration`:

.. code-block:: xml
   :linenos:

   <view
     view="mypackage.views.my_view"
     renderer="templates/mytemplate.jinja2"
    />

When a :term:`view configuration` which has a ``name`` attribute that does
contain a dot, such as ``templates/mytemplate.jinja2`` above is encountered at
startup time, the value of the name attribute is split on its final dot.  The
second element of the split is typically the filename extension.  This
extension is used to look up a renderer factory for the configured view.  Then
the value of ``renderer`` is passed to the factory to create a renderer for the
view.  In this case, the view configuration will create an instance of a
``Jinja2Renderer`` for each view configuration which includes anything ending
with ``.jinja2`` as its ``renderer`` value.  The ``name`` passed to the
``Jinja2Renderer`` constructor will be whatever the user passed as
``renderer=`` to the view configuration.

See also :ref:`renderer_directive` and
:meth:`pyramid.config.Configurator.add_renderer`.

Overriding an Existing Renderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can associate more than one filename extension with the same
existing renderer implementation as necessary if you need to use a
different file extension for the same kinds of templates.  For
example, to associate the ``.zpt`` extension with the Chameleon ZPT
renderer factory, use:

.. code-block:: xml
   :linenos:

   <renderer
     name=".zpt"
     factory="pyramid.chameleon_zpt.renderer_factory"
    />

After you do this, :app:`Pyramid` will treat templates ending in
both the ``.pt`` and ``.zpt`` filename extensions as Chameleon ZPT
templates.

To override the default mapping in which files with a ``.pt``
extension are rendered via a Chameleon ZPT page template renderer, use
a variation on the following in your application's ZCML:

.. code-block:: xml
   :linenos:

   <renderer
     name=".pt"
     factory="my.package.pt_renderer"
    />

After you do this, the :term:`renderer factory` in
``my.package.pt_renderer`` will be used to render templates which end
in ``.pt``, replacing the default Chameleon ZPT renderer.

To override the default mapping in which files with a ``.txt``
extension are rendered via a Chameleon text template renderer, use a
variation on the following in your application's ZCML:

.. code-block:: xml
   :linenos:

   <renderer
     name=".txt"
     factory="my.package.text_renderer"
    />

After you do this, the :term:`renderer factory` in
``my.package.text_renderer`` will be used to render templates which
end in ``.txt``, replacing the default Chameleon text renderer.

To associate a *default* renderer with *all* view configurations (even
ones which do not possess a ``renderer`` attribute), use a variation
on the following (ie. omit the ``name`` attribute to the renderer
tag):

.. code-block:: xml
   :linenos:

   <renderer
     factory="pyramid.renderers.json_renderer_factory"
    />

See also :ref:`renderer_directive` and
:meth:`pyramid.config.Configurator.add_renderer`.

.. _zcml_adding_a_translation_directory:

Adding a Translation Directory via ZCML
---------------------------------------

You can add a translation directory via ZCML by using the
:ref:`translationdir_directive` ZCML directive:

.. code-block:: xml
   :linenos:

   <translationdir dir="my.application:locale/"/>

A message catalog in a translation directory added via
:ref:`translationdir_directive` will be merged into translations from
a message catalog added earlier if both translation directories
contain translations for the same locale and :term:`translation
domain`.

See also :ref:`translationdir_directive` and
:ref:`adding_a_translation_directory`.

.. _zcml_adding_a_locale_negotiator:

Adding a Custom Locale Negotiator via ZCML
------------------------------------------

You can add a custom locale negotiator via ZCML by using the
:ref:`localenegotiator_directive` ZCML directive:

.. code-block:: xml
   :linenos:

    <localenegotiator 
      negotiator="my_application.my_module.my_locale_negotiator"
     />

See also :ref:`custom_locale_negotiator` and
:ref:`localenegotiator_directive`.

.. index::
   pair: subscriber; ZCML directive

.. _zcml_event_listener:

Configuring an Event Listener via ZCML
--------------------------------------

You can configure an :term:`subscriber` by modifying your application's
``configure.zcml``.  Here's an example of a bit of XML you can add to the
``configure.zcml`` file which registers the above ``mysubscriber`` function,
which we assume lives in a ``subscribers.py`` module within your application:

.. code-block:: xml
   :linenos:

   <subscriber
     for="pyramid.events.NewRequest"
     handler=".subscribers.mysubscriber"
    />

See also :ref:`subscriber_directive` and :ref:`events_chapter`.


.. Todo
.. ----

.. - hooks chapter still has topics for ZCML

