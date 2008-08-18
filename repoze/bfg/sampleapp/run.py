from repoze.bfg import make_app
from repoze.bfg import sampleapp
from repoze.bfg.sampleapp.models import get_root

def main():
    app = make_app(get_root, sampleapp, options={'reload_templates':True})
    from paste import httpserver
    httpserver.serve(app, host='0.0.0.0', port='5432')

if __name__ == '__main__':
    main()
