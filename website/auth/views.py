from flask import flash, redirect, render_template, request, session, url_for

from website.db import get_db
from website.util import check_password_hash, generate_password_hash

from . import auth_blueprint

@auth_blueprint.route('/register', methods=('GET', 'POST'))
def register():
    error = {}

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        verify_password = request.form['verify-password'].strip()
        forename = request.form['forename'].strip()
        surname = request.form['surname'].strip()

        db = get_db()
        
        if not username:
            error['username'] = 'Username is required.'
        elif len(username) < 3 or len(username) > 36:
            error['username'] = 'Username must be between 3 and 36 characters.'

        if not password:
            error['password'] = 'Password is required.'
        elif len(password) < 8 or len(password) > 256:
            error['password'] = 'Password must be between 8 and 256 characters.'

        if not verify_password:
            error['verify-password'] = 'Enter your password again.'
        elif verify_password != password:
            error['verify-password'] = 'Passwords must match.'

        if len(forename) > 36:
            error['forename'] = 'Forename must not be greater than 36 characters.'

        if len(surname) > 36:
            error['surname'] = 'Surname must not be greater than 36 characters.'

        if not error:
            try:
                db.execute(
                        'INSERT INTO user (username, password, forename, surname, last_login) VALUES (?, ?, ?, ?, datetime("now"))',
                        (username, generate_password_hash(password), forename, surname)
                        )
                db.commit()
            except db.IntegrityError:
                flash(f'User {username} is already registered.', 'username')
            else:
                user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
                
                if user is None:
                    error['form'] = 'Unable to register user.  Please try again.'
                else:
                    session.clear()
                    session['user_id'] = user['user_id']
                    
                    return redirect(url_for('index'))
    return render_template('auth/register.html', error=error)

@auth_blueprint.route('/login', methods=('GET', 'POST'))
def login():
    error = {}

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()

        if not username:
            error['username'] = 'Username is required.'

        if not password:
            error['password'] = 'Password is required.'
        
        if not error:
            user = db.execute(
                    'SELECT * FROM user WHERE username = ?', (username,)
                    ).fetchone()

            if not user or not check_password_hash(user['password'], password):
                error['form'] = 'Incorrect username or password.'

        if not error:
            session.clear()
            session['user_id'] = user['user_id']

            db.execute('UPDATE user SET last_login = datetime("now") WHERE user_id = ?', (user['user_id'],))
            db.commit()

            return redirect(url_for('index'))
    return render_template('auth/login.html', error=error)

@auth_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


