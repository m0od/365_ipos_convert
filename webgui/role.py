import functools

import jwt
from flask import redirect, request, current_app


def login_required(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        if request.cookies.get('jwt') is None:
            return redirect('/', code=302)
        else:
            try:
                jwt.decode(request.cookies.get('jwt'), current_app.config['SECRET_KEY'], 'HS256')
            except:
                return redirect('/', code=302)
            return f(*args, **kwargs)
    return wrap