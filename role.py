import functools

from flask import session, redirect


def login_required(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        if session.get('userId') is None:
            session.clear()
            return redirect('/', code=302)
        else:
            return f(*args, **kwargs)
    return wrap