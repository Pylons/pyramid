=======================
Pyramid Quick Reference
=======================

Preparation
-----------

Create a virtual environment::

    virtualenv -p python2.7 --no-site-packages env27

Install Pyramid, coverage and nosetests in the virtual enviroment::

    env27/bin/easy_install pyramid coverage nose

Projects
--------

Create a new project::

  ../bin/pcreate -s alchemy <name>

  ../bin/pcreate -s zodb <name>

  ../bin/pcreate -s pyramid_jinja2_starter <name>

Install the project in development mode::

  cd <name>
  ../bin/python setup.py develop

Run the tests::

  ../bin/python setup.py test -q

Show coverage information::

  ../bin/nosetests --cover-package=<name> --cover-erase --with-coverage

Initialize the database (Alchemy only)::

  initialize_<name>_db

Start the application::

  ../bin/pserve development.ini --reload

Distribute the application::

  ../bin/python setup.py sdist

Organization
------------
::

    project/
            project/
                    __init__.py
                    models.py
                    views.py
                    tests.py
                    [security.py]
                    templates/
                    static/
            setup.py
            setup.cfg
            development.ini
            production.ini

Configuration
-------------
project/project/__init__.py::

    def main(global_config, **settings):
        from pyramid.config import Configurator

        # ZODB-based only
        from pyramid_zodbconn import get_connection
        from .models import appmaker
        def root_factory(request):
            conn = get_connection(request)
            return appmaker(conn.root())
        config = Configurator(root_factory=root_factory, settings=settings)

        # SQL alchemy-based only
        from sqlalchemy import engine_from_config
        from .models import DBSession
        engine = engine_from_config(settings, 'sqlalchemy.')
        DBSession.configure(bind=engine)
        config = Configurator(settings=settings)

        # settings provided by pserver development.ini

        # route-based only
        config.add_static_view('static', 'static', cache_max_age=3600)
        config.add_route('home', '/')

        config.add_view('project.views.my_view', renderer='json')
        config.scan()

        # return a WSGI application
        return config.make_wsgi_app()


Models
------

SQL Alchemy
~~~~~~~~~~~
::

    # Begin establishing a session
    from sqlalchemy.ext.declarative import declarative_base

    from sqlalchemy.orm import (
        scoped_session,
        sessionmaker,
        )

    from zope.sqlalchemy import ZopeTransactionExtension

    DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
    Base = declarative_base()
    # End establishing a session

    # Project-specific details
    from sqlalchemy import (
        Column,
        Integer,
        Text,
        )

    class Page(Base):
        """ The SQLAlchemy declarative model class for a Page object. """
        __tablename__ = 'pages'
        id = Column(Integer, primary_key=True)
        name = Column(Text, unique=True)
        data = Column(Text)

        def __init__(self, name, data):
            self.name = name
            self.data = data

ZODB
~~~~
::

    from persistent import Persistent
    from persistent.mapping import PersistentMapping

    class Wiki(PersistentMapping):
        __name__ = None
        __parent__ = None

    class Page(Persistent):
        def __init__(self, data):
            self.data = data

    def appmaker(zodb_root):
        'Initializes ZODB once only, returns the application root'
        if not 'app_root' in zodb_root:
            app_root = Wiki()
            frontpage = Page('This is the front page')
            app_root['FrontPage'] = frontpage
            frontpage.__name__ = 'FrontPage'
            frontpage.__parent__ = app_root
            zodb_root['app_root'] = app_root
            import transaction
            transaction.commit()
        return zodb_root['app_root']

Views
-----

- routes_based_view( :term:`request` ) => :term:`response`

- traversal_based_view( :term:`context`, request ) => response

- view() => dictionary => :term:`renderer` => response

Redirect
~~~~~~~~
::

    @view_config(context='.models.Wiki')
    def view_wiki(context, request):
        return HTTPFound(location=request.resource_url(context, 'FrontPage'))

Also::

    @view_config(route_name='view_wiki')
    def view_wiki(request):
        return HTTPFound(location = request.route_url('view_page', pagename='FrontPage'))


Handle a form
~~~~~~~~~~~~~
1. Display the form (the return at the end is used)

2. Get the form values, redirect to another view (the if condition is true)

::

    @view_config(route_name='edit', renderer='templates/form.jinja2')
    def edit_data(request):
        customer = request.matchdict['customer']

        if 'form.submitted' in request.params:
            # get the form data
            value1 = request.params.get('field1', None)
            return HTTPFound(location = route_url('view_data', request, value=value1))

        # display the form
        return dict(customer=customer)


Templates
---------

+--------------------+-------------------------------------------------------------------------+---------------+
|       Choice       |         How to use                                                      |   Tips        |
+====================+=========================================================================+===============+
|                    |\                                                                        |               |
|                    |                                                                         |               |
|:term:`Chameleon`   |::                                                                       |               |
|                    |                                                                         |               |
|                    |   @view_config(renderer='templates/mytemplate.pt')                      |               |
|                    |   def my_view(request):                                                 |               |
|                    |       return {'bar':1, 'project':'myproject'}                           |               |
|                    |                                                                         |               |
|                    |                                                                         |               |
|                    |\                                                                        |               |
+--------------------+-------------------------------------------------------------------------+---------------+
|                    |\                                                                        |               |
|                    |                                                                         |               |
|:term:`Mako`        |::                                                                       |               |
|                    |                                                                         |               |
|                    |   @view_config(renderer='foo.mak')                                      |               |
|                    |   def my_view(request):                                                 |               |
|                    |       return {'project':'my project'}                                   |               |
|                    |                                                                         |               |
|                    |                                                                         |               |
|                    |\                                                                        |               |
+--------------------+-------------------------------------------------------------------------+---------------+
|                    |\                                                                        |               |
|                    |                                                                         |               |
|:term:`Jinja2`      |::                                                                       |               |
|                    |                                                                         |               |
|                    |   @view_config(renderer='mytemplate.jinja2')                            |               |
|                    |   def myview(request):                                                  |               |
|                    |       return {'foo':1, 'bar':2}                                         |               |
|                    |                                                                         |               |
|                    |Install the `pyramid_jinja2`__ package::                                 |               |
|                    |                                                                         |               |
|                    |    ../bin/easy_install pyramid_jinja2                                   |               |
|                    |                                                                         |               |
|                    |Activate it::                                                            |               |
|                    |                                                                         |               |
|                    |    config.include('pyramid_jinja2')                                     |               |
|                    |    config.add_jinja2_search_path("yourapp:templates")                   |               |
|                    |                                                                         |               |
|                    |__ `http://docs.pylonsproject.org/projects/pyramid_jinja2/en/latest/`    |               |
|                    |                                                                         |               |
|                    |\                                                                        |               |
+--------------------+-------------------------------------------------------------------------+---------------+


Direct use
~~~~~~~~~~

+--------------+------------------------------------------------------------------+
| Choice       |         How to use                                               |
+==============+==================================================================+
|              |\                                                                 |
|              |                                                                  |
| Chameleon    |::                                                                |
|              |                                                                  |
|              |   from pyramid.renderers import render_to_response               |
|              |                                                                  |
|              |   def sample_view(request):                                      |
|              |       return render_to_response('templates/foo.pt',              |
|              |                                 {'foo':1, 'bar':2})              |
|              |                                                                  |
|              |                                                                  |
|              |\                                                                 |
+--------------+------------------------------------------------------------------+
|              |\                                                                 |
|              |                                                                  |
| Mako         |::                                                                |
|              |                                                                  |
|              |   from mako.template import Template                             |
|              |   from pyramid.response import Response                          |
|              |                                                                  |
|              |   def make_view(request):                                        |
|              |       template = Template(filename='/templates/template.mak')    |
|              |       result = template.render(name=request.params['name'])      |
|              |       response = Response(result)                                |
|              |       return response                                            |
|              |                                                                  |
|              |\                                                                 |
+--------------+------------------------------------------------------------------+
|              |\                                                                 |
|              |                                                                  |
| Jinja2       |::                                                                |
|              |                                                                  |
|              |   from pyramid.renderers import render_to_response               |
|              |   def sample_view(request):                                      |
|              |       return render_to_response('mytemplate.jinja2',             |
|              |                                 {'foo':1, 'bar':2})              |
|              |                                                                  |
|              |                                                                  |
|              |\                                                                 |
+--------------+------------------------------------------------------------------+


Form generation
---------------

- `deform`__, Chameleon templates ---> `online demo`__, `local demo`__

- `deform_mako`__, a Mako port of the Chameleon templates included
  in Deform

- `deform_jinja2`__, a set of jinja2 templates for deform.
  Includes standard and uni-form templates ---> `example`__

- `colander`__, schema-based validation and deserializing

__ https://github.com/Pylons/deform
__ http://deformdemo.repoze.org/
__ https://github.com/Pylons/deformdemo
__ https://github.com/mcdonc/deform_mako
__ https://github.com/sontek/deform_jinja2
__ http://www.getkoru.com/register
__ https://github.com/Pylons/colander

Security
--------
For authentication routines, see `Velruse`__

__ `http://packages.python.org/velruse/index.html`

- Add a root factory with an ACL (models.py).
- Add an authentication policy and an authorization policy (__init__.py).
- Add an authentication policy callback (new security.py module).
- Add login and logout views (views.py).
- Add permission declarations to the edit_page and add_page views (views.py).
- Make the existing views return a logged_in flag to the renderer (views.py).
- Add a login template (new login.pt).
- Add a “Logout” link to be shown when logged in and viewing or editing a page (view.pt, edit.pt).

Root factory
~~~~~~~~~~~~
::

    from pyramid.security import (
        Allow,
        Everyone,
        )
    class RootFactory(object):
        __acl__ = [ (Allow, Everyone, 'view'),
                    (Allow, 'group:editors', 'edit') ]
        def __init__(self, request):
            pass

Authentication and authorization policies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    from pyramid.authentication import AuthTktAuthenticationPolicy
    from pyramid.authorization import ACLAuthorizationPolicy

    authn_policy = AuthTktAuthenticationPolicy('sosecret', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings, root_factory='project.models.RootFactory')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

Authentication policy callback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    USERS = {'editor':'editor',
            'viewer':'viewer'}
    GROUPS = {'editor':['group:editors']}

    def groupfinder(userid, request):
        if userid in USERS:
            return GROUPS.get(userid, [])

Logged in status
~~~~~~~~~~~~~~~~

In the view::

    from pyramid.security import authenticated_userid
    logged_in = authenticated_userid(request)

In the template (Chameleon)::

    <span tal:condition="logged_in">
    <a href="${request.application_url}/logout">Logout</a>
    </span>

Permission declarations
~~~~~~~~~~~~~~~~~~~~~~~
::

    @view_config(route_name='edit_page', renderer='templates/edit.pt',
             permission='edit')

Login view
~~~~~~~~~~
This is a form-handling view with three steps:

1. Display login

2. Get login values after submit, authenticate:

   2.1 If successful return to the referrer

   2.2 If failed display login with 'login failed' text

::

    from pyramid.view import forbidden_view_config

    @view_config(route_name='login', renderer='templates/login.pt')
    @forbidden_view_config(renderer='templates/login.pt')
    def login(request):
        login_url = request.route_url('login')
        referrer = request.url
        if referrer == login_url:
            referrer = '/' # never use the login form itself as came_from
        came_from = request.params.get('came_from', referrer)
        message = ''
        login = ''
        password = ''
        if 'form.submitted' in request.params:
            login = request.params['login']
            password = request.params['password']
            if USERS.get(login) == password:
                headers = remember(request, login)
                return HTTPFound(location = came_from,
                                headers = headers)
            message = 'Failed login'

        return dict(
            message = message,
            url = request.application_url + '/login',
            came_from = came_from,
            login = login,
            password = password,
            )

Single file applications
------------------------
::

    project/
            project.py
            templates/
            static/

project/project.py::

    if __name__ == '__main__':
        settings = {}
        settings['reload_all'] = True
        settings['debug_all'] = True
        settings['mako.directories'] = os.path.join(here, 'templates')
        settings['db'] = os.path.join(here, 'tasks.db')
        config.settings = settings

        config.add_route('note', '/blog/{year}/{month}/{title}')
        config.add_view(view_note, route_name='note')

        config = Configurator()
        config.add_route('hello', '/hello/{name}')
        config.add_view(hello_world, route_name='hello')
        app = config.make_wsgi_app()
        server = make_server('0.0.0.0', 8080, app)
        server.serve_forever()

Run with::

    cd project
    ../bin/python project.py

Examples: `Tasks Tutorial`__, `Hello world`__

__ `http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/single_file_tasks/single_file_tasks.html`
__ `http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/firstapp.html`
