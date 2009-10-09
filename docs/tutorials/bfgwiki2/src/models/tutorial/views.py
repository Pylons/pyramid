from repoze.bfg.chameleon_zpt import render_template_to_response

from tutorial.models import DBSession
from tutorial.models import Model

def my_view(request):
    dbsession = DBSession()
    root = dbsession.query(Model).filter(Model.name==u'root').first()
    return render_template_to_response('templates/mytemplate.pt',
                                       root = root,
                                       request = request,
                                       project = 'tutorial')
