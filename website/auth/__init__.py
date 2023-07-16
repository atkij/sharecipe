import functools
from flask import abort, Blueprint, g, session

from website.db import get_db

auth_blueprint = Blueprint('auth', __name__, template_folder='templates')

@auth_blueprint.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
                'SELECT id, username, permissions, created, last_login FROM user WHERE id = ?', (user_id,)
                ).fetchone()

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

from . import views
