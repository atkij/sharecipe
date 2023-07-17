from datetime import datetime
from flask import abort, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from website.db import get_db
from website.util import login_required

from . import account_blueprint

@account_blueprint.route('/')
@login_required()
def index():
    db = get_db()

    user = db.execute(
            'SELECT id, username, last_login, created FROM user WHERE id = ?', (g.user['id'],)
            ).fetchone()

    if user is None:
        abort(500)

    followers = db.execute(
            'SELECT COUNT(*) FROM follower WHERE user_id = ?', (g.user['id'],)
            ).fetchone()
    following = db.execute(
            'SELECT COUNT(*) FROM follower WHERE follower_id = ?', (g.user['id'],)
            ).fetchone()

    joined = datetime.fromisoformat(user['created']).strftime('%d/%m/%Y')
    last_login = datetime.fromisoformat(user['last_login']).strftime('%M:%H %d/%m/%Y')

    return render_template('account/index.html', user=user, followers=followers[0], following=following[0], joined=joined, last_login=last_login)

@account_blueprint.route('/password', methods=('GET', 'POST'))
@login_required()
def password():
    if request.method == 'POST':
        current_password = request.form['current-password']
        new_password = request.form['new-password']
        new_password_verify = request.form['new-password-verify']

        db = get_db()
        error = None

        user = db.execute(
                'SELECT * FROM user WHERE id = ?', (g.user['id'],)
                ).fetchone()

        if user is None:
            abort(500)
        elif new_password != new_password_verify:
            error = 'Passwords do not match.'
        elif not check_password_hash(user['password'], current_password):
            error = 'Incorrect password.'

        if error is None:
            db.execute(
                    'UPDATE user SET password = ? WHERE id = ?',
                    (generate_password_hash(new_password), g.user['id'])
                    )
            db.commit()

            return render_template('account/password.html', success=True)

        flash(error)

    return render_template('account/password.html')

@account_blueprint.route('/delete', methods=('GET', 'POST'))
@login_required()
def delete():
    if request.method == 'POST':
        password = request.form['password']

        db = get_db()
        error = None

        user = db.execute(
                'SELECT * FROM user WHERE id = ?', (g.user['id'],)
                ).fetchone()

        if user is None:
            abort(500)
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            db.execute('DELETE FROM user WHERE id = ?', (g.user['id'],))
            db.commit()

            session.clear()
            g.user = None

            return render_template('account/delete.html', success=True)

        flash(error)

    return render_template('account/delete.html')
