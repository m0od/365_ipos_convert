import functools

from flask import session, redirect


def login_required(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        if 'accessCode' in session:
            if session['accessCode'] != 'IT@P0s365kms':
                session.clear()
                return redirect('/', code=302)
            else:
                return f(*args, **kwargs)
        else:
            return redirect('/', code=302)

    return wrap