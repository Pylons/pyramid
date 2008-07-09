from repoze.bfg import sampleapp
from repoze.bfg.sampleapp.models import Blog
from repoze.bfg.sampleapp.models import BlogEntry
from repoze.bfg.router import make_app

def main():
    blog = Blog('Sample blog')
    blog['sample'] = BlogEntry('sample', 'Sample Blog Entry',
                               '<p>This is a sample blog entry</p>',
                               'chrism')
    def get_root(environ):
        return blog
    app = make_app(get_root, sampleapp)
##     from repoze.profile.profiler import AccumulatingProfileMiddleware
##     profiler = AccumulatingProfileMiddleware(
##         app,
##         log_filename='profile.log',
##         )
    from paste import httpserver
    httpserver.serve(app, host='0.0.0.0', port='5432')

if __name__ == '__main__':
    main()
    
