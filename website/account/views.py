from datetime import datetime
from flask import abort, g, redirect, render_template, request, session, url_for

from website.db import get_db
from website.util import check_password_hash, generate_password_hash, login_required

from . import account_blueprint

@account_blueprint.route('/')
@login_required
def index():
    db = get_db()

    user = db.execute(
            'SELECT user_id, username, last_login, created FROM user WHERE user_id = ?', (g.user['user_id'],)
            ).fetchone()

    if user is None:
        abort(500)

    followers = db.execute(
            'SELECT COUNT(*) FROM follower WHERE user_id = ?', (g.user['user_id'],)
            ).fetchone()
    following = db.execute(
            'SELECT COUNT(*) FROM follower WHERE follower_id = ?', (g.user['user_id'],)
            ).fetchone()

    joined = datetime.fromisoformat(user['created']).strftime('%d/%m/%Y')
    last_login = datetime.fromisoformat(user['last_login']).strftime('%H:%M %d/%m/%Y')

    return render_template('account/index.html', user=user, followers=followers[0], following=following[0], joined=joined, last_login=last_login)

@account_blueprint.route('/password', methods=('GET', 'POST'))
@login_required
def password():
    error = {}

    if request.method == 'POST':
        current_password = request.form['current-password']
        new_password = request.form['new-password']
        new_password_verify = request.form['new-password-verify']

        db = get_db()
        
        user = db.execute(
                'SELECT * FROM user WHERE user_id = ?', (g.user['user_id'],)
                ).fetchone()

        if not current_password:
            error['current-password'] = 'Current password is required.'
        elif not check_password_hash(user['password'], current_password):
            error['current-password'] = 'Incorrect password.'

        if not new_password:
            error['new-password'] = 'New password is required.'
        elif new_password == current_password:
            error['new-password'] = 'New password must be different.'
        elif len(new_password) < 8 or len(new_password) > 256:
            error['new-password'] = 'New password must be between 8 and 256 characters.'

        if not new_password_verify:
            error['new-password-verify'] = 'New password verification is required.'
        elif new_password_verify != new_password:
            error['new-password-verify'] = 'Passwords must match.'

        if not error:
            db.execute(
                    'UPDATE user SET password = ? WHERE user_id = ?',
                    (generate_password_hash(new_password), g.user['user_id'])
                    )
            db.commit()

            return render_template('account/password.html', error=error, success=True)
    return render_template('account/password.html', error=error)

@account_blueprint.route('/delete', methods=('GET', 'POST'))
@login_required
def delete():
    error = {}

    if request.method == 'POST':
        password = request.form['password']

        db = get_db()

        user = db.execute(
                'SELECT * FROM user WHERE user_id = ?', (g.user['user_id'],)
                ).fetchone()

        if not check_password_hash(user['password'], password):
            error['password'] = 'Incorrect password.'

        if not error:
            db.execute('DELETE FROM user WHERE user_id = ?', (g.user['user_id'],))
            db.commit()

            session.clear()
            g.user = None

            return render_template('account/delete.html', error=error, success=True)
    return render_template('account/delete.html', error=error)
