def handle_new_request(event):
    assert(hasattr(event, 'request'))

def handle_new_response(event):
    assert(hasattr(event, 'response'))
    
