.. _configuration_narr:

Creating Your First :mod:`repoze.bfg` Application
=================================================

The majority of the logic in any web application is completely
application-specific.  For example, the body of a web page served by
one web application might be a representation of the contents of an
accounting ledger, while the content of of a web page served by
another might be a listing of songs.  These applications obviously
might not service the same set of customers.  However, both the
ledger-serving and song-serving applications can be written using
:mod:`repoze.bfg`, because :mod:`repoze.bfg` is a very general
*framework* which can be used to create most sorts of web
applications.  As a framework, the primary job of :mod:`repoze.bfg` is
to make it easier for a developer to create an arbitrary web
application.

.. sidebar:: Frameworks vs. Libraries

   A framework differs from a *library*: library code is always
   *called* by code that you write, while a framework always *calls*
   code that you write.  Using the average library is typically easier
   than using the average framework.  During typical library usage,
   the developer can more granularly avoid ceding any control to code
   he does not himself author.  During typical framework usage,
   however, the developer must cede a greater portion of control to
   the framework.  In practice, using a framework to create a web
   application is often more practical than using a set of libraries
   if the framework provides a set of facilities and assumptions that
   fit a large portion of your application requirements.
   :mod:`repoze.bfg` is a framework that fits a large set of
   assumptions in the domain of web application creation.

Because :mod:`repoze.bfg` is a framework, from the perspective of the
people who have written :mod:`repoze.bfg` itself, each deployment of
an application written using :mod:`repoze.bfg` implies a specific
*configuration* of the framework iself.  For example, a song-serving
application might plug code into the framework that manages songs,
while the ledger-serving application might code into the framework
that manages accounting information.  :mod:`repoze.bfg` refers to the
way which code is plugged in to it as "configuration".

It can be a bit strange to think of code you write which
:mod:`repoze.bfg` interacts with as "configuration".  Many people
think of "configuration" as entirely declarative knobs that control
operation of a specific application deployment; for instance, it's
easy to think of the values implied by a ``.ini.`` configuration file
that is read at application startup time as configuration.  However,
because :mod:`repoze.bfg` is itself a framework, from the perspective
of the authors of :mod:`repoze.bfg`, when you plug code into it, you
**are** "configuring" the :mod:`repoze.bfg` framework *itself* for the
purpose of creating an application.  :mod:`repoze.bfg` refers to this
act as "configuration".

There are a number of different mechanisms you may use to configure
:mod:`repoze.bfg` to create an application: *imperative* configuration
and *declarative* configuration.

Hello World, Configured Imperatively
------------------------------------

The mechanism simplest for existing Python programmers is "imperative"
configuration.  This is the configuration mode in which developers
cede the least amount of control to the framework itself.  Because
application qdevelopers cede the least amount of control to the
framework, it is also the easiest configuration mode to understand.

Here's the simplest :mod:`repoze.bfg` application, configured
imperatively:

.. code-block:: python
   :linenos:

   from webob import Response
   from wsgiref import simple_server
   from repoze.bfg.configuration import Configurator

   def hello_world(request):
       return Response('Hello world!')

   if __name__ == '__main__':
       config = Configurator()
       config.view(hello_world)
       app = config.make_wsgi_app()
       simple_server.make_server('', 8080, app).serve_forever()

When inserted into a Python script and executed, this code starts an
HTTP server on port 8080.  When visited by a user agent on any
applicable URL, the server simply serves serves up the words "Hello
world!" with the HTTP response values ``200 OK`` as a response code
and a ``Content-Type`` header value of ``text/plain``.

