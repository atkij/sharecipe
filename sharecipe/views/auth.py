from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from ..database import users, profiles
from ..util import get_safe_redirect
from ..forms.auth import LoginForm, RegisterForm, VerifyForm
from ..controllers import auth as c

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            session.clear()
            session['user_id'] = c.register(form.name.data, form.email.data, form.password.data)
            return redirect(url_for('auth.verify', return_url=request.args.get('return_url')))
        except c.AccountError as e:
            flash(e, 'error')
    
    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            session.clear()
            session['user_id'] = c.login(form.email.data, form.password.data)
            return redirect(get_safe_redirect(request.args.get('return_url')))
        except c.LoginError as e:
            flash(e, 'error')

    return render_template('auth/login.html', form=form)

@bp.route('/verify', methods=('GET', 'POST'))
def verify():
    form = VerifyForm(request.form)

    if session.get('user_id') is None:
        return redirect(url_for('auth.login', return_url=request.args.get('return_url')))

    if request.method == 'POST' and form.validate():
        try:
            c.verify(session.get('user_id'), form.code.data)
            flash('Email verification complete', 'success')
            return redirect(get_safe_redirect(request.args.get('return_url')))
        except c.VerifyError as e:
            flash(e, 'error')
    else:
        code, expires = c.x_verify(session.get('user_id'))

    return render_template('auth/verify.html', form=form)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(get_safe_redirect(request.args.get('return_url')))

@bp.before_app_request
def load_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
        g.profile = None
    else:
        g.user = users.find(user_id)

        if not g.user.verified:
            g.user = None
        else:
            g.profile = profiles.find(user_id)