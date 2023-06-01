import functools

import jwt
from flask import redirect, request, current_app


def login_required(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        print(request.cookies.get('jwt'))
        if request.cookies.get('jwt') is None:
            return redirect('/', code=302)
        else:
            try:
                print(current_app.config['SECRET_KEY'])
                jwt.decode(request.cookies.get('jwt'), current_app.config['SECRET_KEY'], 'HS256')

            except Exception as e:
                print(e)
                return redirect('/', code=302)
            return f(*args, **kwargs)
    return wrap