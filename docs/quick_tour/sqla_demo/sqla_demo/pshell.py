from . import models


def setup(env):
    request = env['request']

    # start a transaction
    request.tm.begin()

    # inject some vars into the shell builtins
    env['tm'] = request.tm
    env['dbsession'] = request.dbsession
    env['models'] = models
