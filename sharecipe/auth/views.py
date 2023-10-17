from flask import flash, g, redirect, render_template, request, session, url_for

from sharecipe.db import get_db
from sharecipe.util import check_password_hash, generate_password_hash
from sharecipe.forms import LoginForm, RegisterForm

from . import auth_blueprint

@auth_blueprint.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        db = get_db()

        try:
            res = db.execute(
                    'INSERT INTO user (username, password, email, name, last_login) VALUES (?, ?, ?, ?, datetime("now"))',
                    (form.username.data, generate_password_hash(form.password.data), form.email.data, form.name.data)
                    )
            db.commit()
        except db.IntegrityError:
            flash(f'Account already exists.', 'error')
        else:
            session.clear()
            session['user_id'] = res.lastrowid
                    
            return redirect(url_for('index'))
    return render_template('auth/register.html', form=form)

@auth_blueprint.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        db = get_db()
        user = db.execute(
                'SELECT * FROM user WHERE username = ?', (form.username.data,)
                ).fetchone()

        if not user or not check_password_hash(user['password'], form.password.data):
            flash('Incorrect username or password.', 'error')
        else:
            session.clear()
            session['user_id'] = user['user_id']

            db.execute('UPDATE user SET last_login = datetime("now") WHERE user_id = ?', (user['user_id'],))
            db.commit()

            return redirect(url_for('index'))
    return render_template('auth/login.html', form=form)

@auth_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@auth_blueprint.before_app_request
def load_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
                'SELECT user.* FROM user WHERE user.user_id = ?', (user_id,)
                ).fetchone()

