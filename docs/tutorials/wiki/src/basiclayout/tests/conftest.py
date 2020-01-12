import os
from pyramid.paster import get_appsettings
from pyramid.scripting import prepare
from pyramid.testing import DummyRequest
import pytest
import transaction
import webtest

from tutorial import main


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
def app(app_settings):
    return main({}, **app_settings)

@pytest.fixture
def tm():
    tm = transaction.manager
    tm.begin()
    tm.doom()

    yield tm

    tm.abort()

@pytest.fixture
def testapp(app, tm):
    testapp = webtest.TestApp(app, extra_environ={
        'HTTP_HOST': 'example.com',
        'tm.active': True,
        'tm.manager': tm,
    })

    return testapp

@pytest.fixture
def app_request(app, tm):
    """
    A real request.

    This request is almost identical to a real request but it has some
    drawbacks in tests as it's harder to mock data and is heavier.

    """
    env = prepare(registry=app.registry)
    request = env['request']
    request.host = 'example.com'
    request.tm = tm

    yield request
    env['closer']()

@pytest.fixture
def dummy_request(app, tm):
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
    request.tm = tm

    return request
