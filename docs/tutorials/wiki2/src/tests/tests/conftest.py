import alembic
import alembic.config
import alembic.command
import os
from pyramid.paster import get_appsettings
from pyramid.scripting import prepare
from pyramid.testing import DummyRequest
import pytest
import transaction
from webob.cookies import Cookie
import webtest

from tutorial import main
from tutorial import models
from tutorial.models.meta import Base


def pytest_addoption(parser):
    parser.addoption('--ini', action='store', metavar='INI_FILE')

@pytest.fixture(scope='session')
def ini_file(request):
    # potentially grab this path from a pytest option
    return os.path.abspath(request.config.option.ini or 'testing.ini')

@pytest.fixture(scope='session')
def app_settings(ini_file):
    return get_appsettings(ini_file)

@pytest.fixture(scope='session')
def dbengine(app_settings, ini_file):
    engine = models.get_engine(app_settings)

    alembic_cfg = alembic.config.Config(ini_file)
    Base.metadata.drop_all(bind=engine)
    alembic.command.stamp(alembic_cfg, None, purge=True)

    # run migrations to initialize the database
    # depending on how we want to initialize the database from scratch
    # we could alternatively call:
    # Base.metadata.create_all(bind=engine)
    # alembic.command.stamp(alembic_cfg, "head")
    alembic.command.upgrade(alembic_cfg, "head")

    yield engine

    Base.metadata.drop_all(bind=engine)
    alembic.command.stamp(alembic_cfg, None, purge=True)

@pytest.fixture(scope='session')
def app(app_settings, dbengine):
    return main({}, dbengine=dbengine, **app_settings)

@pytest.fixture
def tm():
    tm = transaction.TransactionManager(explicit=True)
    tm.begin()
    tm.doom()

    yield tm

    tm.abort()

@pytest.fixture
def dbsession(app, tm):
    session_factory = app.registry['dbsession_factory']
    return models.get_tm_session(session_factory, tm)

class TestApp(webtest.TestApp):
    def get_cookie(self, name, default=None):
        # webtest currently doesn't expose the unescaped cookie values
        # so we're using webob to parse them for us
        # see https://github.com/Pylons/webtest/issues/171
        cookie = Cookie(' '.join(
            '%s=%s' % (c.name, c.value)
            for c in self.cookiejar
            if c.name == name
        ))
        return next(
            (m.value.decode('latin-1') for m in cookie.values()),
            default,
        )

    def get_csrf_token(self):
        """
        Convenience method to get the current CSRF token.

        This value must be passed to POST/PUT/DELETE requests in either the
        "X-CSRF-Token" header or the "csrf_token" form value.

        testapp.post(..., headers={'X-CSRF-Token': testapp.get_csrf_token()})

        or

        testapp.post(..., {'csrf_token': testapp.get_csrf_token()})

        """
        return self.get_cookie('csrf_token')

    def login(self, params, status=303, **kw):
        """ Convenience method to login the client."""
        body = dict(csrf_token=self.get_csrf_token())
        body.update(params)
        return self.post('/login', body, **kw)

@pytest.fixture
def testapp(app, tm, dbsession):
    # override request.dbsession and request.tm with our own
    # externally-controlled values that are shared across requests but aborted
    # at the end
    testapp = TestApp(app, extra_environ={
        'HTTP_HOST': 'example.com',
        'tm.active': True,
        'tm.manager': tm,
        'app.dbsession': dbsession,
    })

    # initialize a csrf token instead of running an initial request to get one
    # from the actual app - this only works using the CookieCSRFStoragePolicy
    testapp.set_cookie('csrf_token', 'dummy_csrf_token')

    return testapp

@pytest.fixture
def app_request(app, tm, dbsession):
    """
    A real request.

    This request is almost identical to a real request but it has some
    drawbacks in tests as it's harder to mock data and is heavier.

    """
    env = prepare(registry=app.registry)
    request = env['request']
    request.host = 'example.com'

    # without this, request.dbsession will be joined to the same transaction
    # manager but it will be using a different sqlalchemy.orm.Session using
    # a separate database transaction
    request.dbsession = dbsession
    request.tm = tm

    yield request
    env['closer']()

@pytest.fixture
def dummy_request(app, tm, dbsession):
    """
    A lightweight dummy request.

    This request is ultra-lightweight and should be used only when the
    request itself is not a large focus in the call-stack.

    It is way easier to mock and control side-effects using this object.

    - It does not have request extensions applied.
    - Threadlocals are not properly pushed.

    """
    request = DummyRequest()
    request.registry = app.registry
    request.host = 'example.com'
    request.dbsession = dbsession
    request.tm = tm

    return request
