.. index::
   single: Agendaless Consulting
   single: Pylons
   single: Django
   single: Zope
   single: frameworks vs. libraries
   single: framework

:app:`Pyramid` Introduction
===========================

:app:`Pyramid` is a Python web application *framework*. It is designed to make creating web applications easier. It is open source.

.. sidebar:: What Is a Framework?

   A *framework* provides capabilities that developers can enhance or extend. A web application framework provides many of the common needs of building web applications allowing developers to concentrate only on the parts that are specific to their application.

   Every framework makes choices about how a particular problem should be solved. When developers choose to use a framework, they cede control over the portions of their application that are provided by the framework. It is possible to write a complete web application without any framework, by using Python libraries. In practice, however, it is often more practical to use a framework, so long as your chosen framework fits the requirements of your application.

:app:`Pyramid` follows these design and engineering principles:

Simplicity
   :app:`Pyramid` is designed to be easy to use. You can get started even if you don't understand it all. And when you're ready to do more, :app:`Pyramid` will be there for you.

Minimalism
   Out of the box, :app:`Pyramid` provides only the core tools needed for nearly all web applications: mapping URLs to code, security, and serving static assets (files like JavaScript and CSS). Additional tools provide templating, database integration and more. But with :app:`Pyramid` you can *"pay only for what you eat"*.

Documentation
   :app:`Pyramid` is committed to comprehensive and up-to-date documentation.

Speed
  :app:`Pyramid` is designed to be noticeably fast.

Reliability
  :app:`Pyramid` is developed conservatively and tested exhaustively. Our motto is: "If it ain't tested, it's broke".

Openness
  As with Python, the :app:`Pyramid` software is distributed under a `permissive open source license <http://repoze.org/license.html>`_.

.. _why_pyramid:

Why Pyramid?
------------

In a world filled with web frameworks, why should you choose :app:`Pyramid`\ ?

Modern
~~~~~~

:app:`Pyramid` is fully compatible with Python 3. If you develop a :app:`Pyramid` application today, you can rest assured that you'll be able to use the most modern features of your favorite language. And in the years to come, you'll continue to bed working on a framework that is up-to-dateand forward-looking.

Tested
~~~~~~

Untested code is broken by design. The :app:`Pyramid` community has a strong testing culture and our framework reflects that. Every release of :app:`Pyramid` has 100% statement coverage (as measured by `coverage <https://coverage.readthedocs.io>`_) and 95% decision/condition coverage. (as measured by `instrumental <http://instrumental.readthedocs.io/en/latest/intro.html>`_) It is automatically tested using `Travis <https://travis-ci.org/Pylons/pyramid>`_ and `Jenkins <http://jenkins.pylonsproject.org/job/pyramid/>`_ on supported versions of Python after each commit to its GitHub repository. `Official Pyramid add-ons <https://trypyramid.com/resources-extending-pyramid.html>`_ are held to a similar testing standard.

We still find bugs in :app:`Pyramid`, but we've noticed we find a lot fewer of them while working on projects with a solid testing regime.

Documented
~~~~~~~~~~

The :app:`Pyramid` documentation is comprehensive. We strive to keep our narrative documentation both complete and friendly to newcomers. We also maintain the :ref:`Pyramid Community Cookbook <cookbook:pyramid-cookbook>` of  recipes demonstrating common scenarios you might face. Contributions in the form of improvements to our documentation are always appreciated. And we always welcome improvements to our `official tutorials <html_tutorials>`_ as well as new contributions to our `community maintained tutorials <tutorials:pyramid-tutorials>`_.

Supported
~~~~~~~~~

You can get help quickly with :app:`Pyramid`. It's our goal that no :app:`Pyramid` question go unanswered. Whether you ask a question on IRC, on the Pylons-discuss mailing list, or on StackOverflow, you're likely to get a reasonably prompt response.

:app:`Pyramid` is also a welcoming, friendly space for newcomers. We don't tolerate "support trolls" or those who enjoy berating fellow users in our support channels. We try to keep it well-lit and new-user-friendly.

.. seealso::

    See also our `#pyramid IRC channel <https://webchat.freenode.net/?channels=pyramid>`_, our `pylons-discuss mailing list <https://groups.google.com/forum/#!forum/pylons-discuss>`_, and :ref:`support-and-development`.

.. _what_makes_pyramid_unique:

What makes Pyramid unique
-------------------------

There are many tools available for web development. What would make someone want to use :app:`Pyramid` instead?  What makes :app:`Pyramid` unique?

With :app:`Pyramid` you can write very small applications without needing to know a lot. And by learning a bit more, you can write very large applications too. :app:`Pyramid` will allow you to become productive quickly, and will grow with you. It won't hold you back when your application is small, and it won't get in your way when your application becomes large. Other application frameworks seem to fall into two non-overlapping categories: those that support "small apps" and those designed for "big apps".

We don't believe you should have to make this choice. You can't really know how large your application will become.  You certainly shouldn't have to rewrite a small application in another framework when it gets "too big". A well-designed framework should be able to be good at both. :app:`Pyramid` is that kind of framework.

:app:`Pyramid` provides a set of features that are unique among Python web frameworks. Others may provide some, but only :app:`Pyramid` provides them all, in one place, fully documented, and *à la carte* without needing to pay for the whole banquet.


Build single-file applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can write a :app:`Pyramid` application that lives entirely in one Python file. Such an application is easy to understand since everything is in one place. It is easy to deploy because you don't need to know much about Python packaging. :app:`Pyramid` allows you to do almost everything that so-called *microframeworks* can in very similar ways.

.. literalinclude:: helloworld.py

.. seealso::

    See also :ref:`firstapp_chapter`.

Configure applications with decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:app:`Pyramid` allows you to keep your configuration right next to your code. That way you don't have to switch files to see your configuration. For example:

.. code-block:: python

   from pyramid.view import view_config
   from pyramid.response import Response

   @view_config(route_name='fred')
   def fred_view(request):
       return Response('fred')

However, using :app:`Pyramid` configuration decorators does not change your code. It remains easy to extend, test, or reuse. You can test your code as if the decorators were not there. You can instruct the framework to ignore some decorators. You can even use an imperative style to write your configuration, skipping decorators entirely.

.. seealso::

    See also :ref:`mapping_views_using_a_decorator_section`.

Generate application URLs
~~~~~~~~~~~~~~~~~~~~~~~~~

Dynamic web applications produce URLs that can change depending on what you are viewing. :app:`Pyramid` provides flexible, consistent, easy to use tools for generating URLs. When you use these tools to write your application, you can change your configuration without fear of breaking links in your web pages.

.. seealso::

    See also :ref:`generating_route_urls`.

Serve static assets
~~~~~~~~~~~~~~~~~~~

Web applications often require JavaScript, CSS, images and other so-called *static assets*. :app:`Pyramid` provides flexible tools for serving these kinds of files. You can serve them directly from :app:`Pyramid`, or host them on an external server or CDN (content delivery network). Either way, :app:`Pyramid` can help you to generate URLs so you can change where your files come from without changing any code.

.. seealso::

    See also :ref:`static_assets_section`.

Develop interactively
~~~~~~~~~~~~~~~~~~~~~

:app:`Pyramid` can automatically detect changes you make to template files and code, so your changes are immediately available in your browser. You can debug using plain old ``print()`` calls, which will display to your console.

:app:`Pyramid` has a debug toolbar that allows you to see information about how your application is working right in your browser. See configuration, installed packages, SQL queries, logging statements and more.

When your application has an error, an interactive debugger allows you to poke around from your browser to find out what happened.

To use the :app:`Pyramid` debug toolbar, build your project with a :app:`Pyramid` :term:`cookiecutter`.

.. seealso::

    See also :ref:`debug_toolbar`.

Debug with power
~~~~~~~~~~~~~~~~

When things go wrong, :app:`Pyramid` gives you powerful ways to fix the problem.

You can configure :app:`Pyramid` to print helpful information to the console. The ``debug_notfound`` setting shows information about URLs that aren't matched. The ``debug_authorization`` setting provides helpful messages about why you aren't allowed to do what you just tried.

:app:`Pyramid` also has command line tools to help you verify your configuration. You can use ``proutes`` and ``pviews`` to inspect how URLs are connected to your application code.

.. seealso::

    See also :ref:`debug_authorization_section`, :ref:`command_line_chapter`,
    and :doc:`../pscripts/index`

Extend your application
~~~~~~~~~~~~~~~~~~~~~~~

:app:`Pyramid` add-ons extend the core of the framework with useful abilities. There are add-ons available for your favorite template language, SQL and NoSQL databases, authentication services and more.

Supported :app:`Pyramid` add-ons are held to the same demanding standards as the framework itself. You will find them to be fully tested and well documented.

.. seealso::

    See also https://trypyramid.com/resources-extending-pyramid.html

Write your views, *your* way
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A fundamental task for any framework is to map URLs to code. In :app:`Pyramid`, that code is called a :term:`view callable`. View callables can be functions, class methods or even callable class instances. You are free to choose the approach that best fits your use case. Regardless of your choice, :app:`Pyramid` treats them the same. You can change your mind at any time without any penalty. There are no artificial distinctions between the various approaches.

Here's a view callable defined as a function:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config(route_name='aview')
   def aview(request):
       return Response('one')

Here's a few views defined as methods of a class instead:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   class AView(object):
       def __init__(self, request):
           self.request = request

       @view_config(route_name='view_one')
       def view_one(self):
           return Response('one')

       @view_config(route_name='view_two')
       def view_two(self):
           return Response('two')

.. seealso::

    See also :ref:`view_config_placement`.

.. _intro_asset_specs:

Find *your* static assets
~~~~~~~~~~~~~~~~~~~~~~~~~

In many web frameworks, the static assets required by an application are kept in a globally shared location, "the *static* directory". Others use a lookup scheme, like an ordered set of template directories. Both of these approaches have problems when it comes to customization.

:app:`Pyramid` takes a different approach. Static assets are located using *asset specifications*, strings that contain reference both to a Python package name and a file or directory name, e.g. ``MyPackage:static/index.html``. These specifications are used for templates, JavaScript and CSS, translation files, and any other package-bound static resource. By using asset specifications, :app:`Pyramid` makes it easy to extend your application with other packages without worrying about conflicts.

What happens if another :app:`Pyramid` package you are using provides an asset you need to customize? Maybe that page template needs better HTML, or you want to update some CSS. With asset specifications you can override the assets from other packages using simple wrappers.

Examples: :ref:`asset_specifications` and :ref:`overriding_assets_section`.

Use *your* templates
~~~~~~~~~~~~~~~~~~~~

In :app:`Pyramid`, the job of creating a ``Response`` belongs to a :term:`renderer`. Any templating system—Mako, Chameleon, Jinja2—can be a renderer. In fact, packages exist for all of these systems. But if you'd rather use another, a structured API exists allowing you to create a renderer using your favorite templating system. You can use the templating system *you* understand, not one required by the framework.

What's more, :app:`Pyramid` does not make you use a single templating system exclusively.  You can use multiple templating systems, even in the same project.

Example: :ref:`templates_used_directly`.

Write testable views
~~~~~~~~~~~~~~~~~~~~

When you use a :term:`renderer` with your view callable, you are freed from needing to return a "webby" ``Response`` object. Instead your views can return a simple Python dictionary. :app:`Pyramid` will take care of rendering the information in that dictionary to a ``Response`` on your behalf. As a result, your views are more easily tested, since you don't need to parse HTML to evaluate the results. :app:`Pyramid` makes it a snap to write unit tests for your views, instead of requiring you to use functional tests.

.. index::
   pair: renderer; explicitly calling
   pair: view renderer; explictly calling

.. _example_render_to_response_call:

For example, a typical web framework might return a ``Response`` object from a ``render_to_response`` call:

.. code-block:: python
    :linenos:

    from pyramid.renderers import render_to_response

    def myview(request):
        return render_to_response('myapp:templates/mytemplate.pt', {'a':1},
                                  request=request)

While you *can* do this in :app:`Pyramid`, you can also return a Python dictionary:

.. code-block:: python
    :linenos:

    from pyramid.view import view_config

    @view_config(renderer='myapp:templates/mytemplate.pt')
    def myview(request):
        return {'a':1}

By configuring your view to use a renderer, you tell :app:`Pyramid` to use the ``{'a':1}`` dictionary and the specified template to render a response on your behalf.

The string passed as ``renderer=`` above is an :term:`asset specification`. Asset specifications are widely used in :app:`Pyramid`. They allow for more reliable customization. See :ref:`intro_asset_specs` for more information.

Example: :ref:`renderers_chapter`.

Use events to coordinate actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When writing web applications, it is often important to have your code run at a specific point in the lifecycle of a request. In :app:`Pyramid`, you can accomplish this using *subscribers* and *events*.

For example, you might have a job that needs to be done each time your application handles a new request. :app:`Pyramid` emits a ``NewRequest`` event at this point in the request handling lifecycle. You can register your code as a subscriber to this event using a clear, declarative style:

.. code-block:: python

    from pyramid.events import NewRequest
    from pyramid.events import subscriber

    @subscriber(NewRequest)
    def my_job(event):
        do_something(event.request)

:app:`Pyramid`\ 's event system can be extended as well. If you need, you can create events of your own and send them using :app:`Pyramid`\ 's event system. Then anyone working with your application can subscribe to your events and coordinate their code with yours.

Example: :ref:`events_chapter` and :ref:`event_types`.

Build international applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:app:`Pyramid` ships with internationalization-related features in its core: localization, pluralization, and creating message catalogs from source files and templates.  :app:`Pyramid` allows for a plurality of message catalogs via the use of translation domains.  You can create a system that has its own translations without conflict with other translations in other domains.

Example: :ref:`i18n_chapter`.

Build efficient applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:app:`Pyramid` provides an easy way to *cache* the results of slow or expensive views. You can indicate in view configuration that you want a view to be cached:

.. code-block:: python

    @view_config(http_cache=3600) # 60 minutes
    def myview(request):
        # ...

:app:`Pyramid` will automatically add the appropriate ``Cache-Control`` and ``Expires`` headers to the response it creates.

See the :meth:`~pyramid.config.Configurator.add_view` method's ``http_cache`` documentation for more information.

Build fast applications
~~~~~~~~~~~~~~~~~~~~~~~

The :app:`Pyramid` core is fast. It has been engineered from the ground up for speed. It only does as much work as absolutely necessary when you ask it to get a job done. If you need speed from your application, :app:`Pyramid` is the right choice for you.

Example: http://blog.curiasolutions.com/pages/the-great-web-framework-shootout.html

Store session data
~~~~~~~~~~~~~~~~~~

:app:`Pyramid` has built-in support for HTTP sessions, so you can associate data with specific users between requests. Lots of other frameworks also support sessions. But :app:`Pyramid` allows you to plug in your own custom sessioning system. So long as your system conforms to a documented interface, you can drop it in in place of the provided system.

Currently there is a binding package for the third-party Redis sessioning system that does exactly this. But if you have a specialized need (perhaps you want to store your session data in MongoDB), you can.  You can even switch between implementations without changing your application code.

Example: :ref:`sessions_chapter`.

Handle problems with grace
~~~~~~~~~~~~~~~~~~~~~~~~~~

Mistakes happen. Problems crop up. No one writes bug-free code. :app:`Pyramid`provides a way to handle the exceptions your code encounters. An :term:`exception view` is a special kind of view which is automatically called when a particular exception type arises without being handled by your application.

For example, you might register an exception view for the :exc:`Exception` exception type, which will catch *all* exceptions, and present a pretty "well, this is embarrassing" page.  Or you might choose to register an exception view for only certain application-specific exceptions. You can make one for when a file is not found, or when the user doesn't have permission to do something. In the former case, you can show a pretty "Not Found" page; in the latter case you might show a login form.

Example: :ref:`exception_views`.

And much, much more...
~~~~~~~~~~~~~~~~~~~~~~

:app:`Pyramid` has been built with a number of other sophisticated design features that make it adaptable. Read more about them below.

.. toctree::
   :maxdepth: 2

   advanced-features





.. index::
   single: Pylons Project

What Is The Pylons Project?
---------------------------

:app:`Pyramid` is a member of the collection of software published under the Pylons Project.  Pylons software is written by a loose-knit community of contributors.  The `Pylons Project website <https://pylonsproject.org>`_ includes details about how :app:`Pyramid` relates to the Pylons Project.

.. index::
   single: pyramid and other frameworks
   single: Zope
   single: Pylons
   single: Django
   single: MVC

:app:`Pyramid` and Other Web Frameworks
---------------------------------------

The first release of :app:`Pyramid`\ 's predecessor (named :mod:`repoze.bfg`) was made in July of 2008.  At the end of 2010, we changed the name of :mod:`repoze.bfg` to :app:`Pyramid`.  It was merged into the Pylons project as :app:`Pyramid` in November of that year.

:app:`Pyramid` was inspired by :term:`Zope`, :term:`Pylons` (version 1.0), and :term:`Django`.  As a result, :app:`Pyramid` borrows several concepts and features from each, combining them into a unique web framework.

Similar to :term:`Zope`, :app:`Pyramid` applications may easily be extended. If you work within the constraints of the framework, you can produce applications that can be reused, modified, or extended without needing to modify the original application code. :app:`Pyramid` also inherits the concepts of :term:`traversal` and declarative security from Zope.

Similar to :term:`Pylons` version 1.0, :app:`Pyramid` is largely free of policy. It makes no assertions about which database or template system you should use. You are free to use whatever third-party components fit the needs of your specific application. :app:`Pyramid` also inherits its approach to :term:`URL dispatch` from Pylons.

Similar to :term:`Django`, :app:`Pyramid` values extensive documentation. In addition, the concept of a :term:`view` is used by :app:`Pyramid` much as it would be by Django.

Other Python web frameworks advertise themselves as members of a class of web frameworks named `model-view-controller <https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller>`_ frameworks. The authors of :app:`Pyramid` do not believe that the MVC pattern fits the web particularly well. However, if this abstraction works for you, :app:`Pyramid` also generally fits into this class.
