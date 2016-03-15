from functools import wraps

from flask import request, current_app, make_response, redirect, url_for, g

import jwt

def requires_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user:
            return redirect(url_for('users.login', next=request.url))

        return f(*args, **kwargs)
    return decorated_function

def requires_reserve_name_secret(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'key' not in request.args:
            return make_response('No "key".', 401)
        from hmac import compare_digest as constant_time_compare
        if not constant_time_compare(request.args.get('key'), current_app.config['RESERVE_NAME_SECRET']):
            return make_response('Bad "key".', 401)

        return f(*args, **kwargs)
    return decorated_function
