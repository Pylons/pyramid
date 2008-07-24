from paste import httpserver

from repoze.bfg import make_app
from myapp.models import get_root
import myapp

app = make_app(get_root, myapp)
httpserver.serve(app, host='0.0.0.0', port='5432')
