cancel_requested = False

def request_cancel():
    global cancel_requested
    cancel_requested = True

    
def reset_cancel():
    global cancel_requested
    cancel_requested = False