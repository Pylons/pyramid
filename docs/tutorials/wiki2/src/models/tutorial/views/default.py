from pyramid.view import view_config
from pyramid.response import Response
import sqlalchemy as sa

from .. import models


@view_config(route_name='home', renderer='tutorial:templates/mytemplate.jinja2')
def my_view(request):
    try:
        query = sa.select(models.MyModel).where(models.MyModel.name == 'one')
        one = request.dbsession.execute(query).scalar_one()
    except sa.exc.SQLAlchemyError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'one': one, 'project': 'myproj'}


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to initialize your database tables with `alembic`.
    Check your README.txt for descriptions and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
