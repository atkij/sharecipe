import functools
from flask import abort, g, redirect

def login_required(permissions=0):
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(*args, **kwargs):
            if g.user is None:
                return redirect(url_for('auth.login'))
            elif g.user['permissions'] & permissions != permissions:
                abort(403)
            return view(*args, **kwargs)
        return wrapped_view
    return decorator
