from repoze.bfg.template import render_transform_to_response

def my_view(context, request):
    return render_transform_to_response('templates/mymtemplate.pt',
                                        greeting = 'hello world')
