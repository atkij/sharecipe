from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from website.db import get_db

from . import auth_blueprint

@auth_blueprint.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                        'INSERT INTO user (username, password, permissions) VALUES (?, ?, ?)',
                        (username, generate_password_hash(password), 0b11)
                        )
                db.commit()
            except db.IntegrityError:
                error = f'User {username} is already registered.'
            else:
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@auth_blueprint.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
                ).fetchone()

        if user is None or not check_password_hash(user['password'], password):
            error = 'Incorrect username or password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']

            db.execute('UPDATE user SET last_login = datetime("now") WHERE id = ?', (user['id'],))
            db.commit()

            return redirect(url_for('main.index'))

        flash(error)

    return render_template('auth/login.html')

@auth_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


