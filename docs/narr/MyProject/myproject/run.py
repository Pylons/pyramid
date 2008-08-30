from repoze.bfg.router import make_app
from repoze.bfg.registry import get_options

def app(global_config, **kw):
    # paster app config callback
    from myproject.models import get_root
    import myproject
    return make_app(get_root, myproject, options=get_options(kw))

if __name__ == '__main__':
    from paste import httpserver
    httpserver.serve(app(None), host='0.0.0.0', port='6543')
    
