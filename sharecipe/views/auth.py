from flask import abort, Blueprint, flash, g, redirect, render_template, request, session, url_for

from ..util import get_safe_redirect
from ..forms.auth import LoginForm, RegisterForm, VerifyForm

from ..controllers.profile import ProfileController
from ..controllers.user import UserController, UserLoginError, UserRegisterError, UserVerifyError

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm(request.form)

    if g.user:
        abort(404)

    if request.method == 'POST' and form.validate():
        try:
            session.clear()

            user = UserController.register(form.email.data, form.password.data)
            profile = ProfileController.create(user.id, form.name.data)

            session['user_id'] = user.id
            session['flow'] = 'auth.verify'

            return redirect(url_for('auth.verify', return_url=request.args.get('return_url')))
        except UserRegisterError as e:
            flash(e, 'error')
    
    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm(request.form)

    if g.user:
        abort(404)

    if request.method == 'POST' and form.validate():
        try:
            session.clear()

            user = UserController.login(form.email.data, form.password.data)

            session['user_id'] = user.id

            if not user.verified:
                session['flow'] = 'auth.verify'

                return redirect(url_for('auth.verify', return_url=request.args.get('return_url')))
            
            return redirect(get_safe_redirect(request.args.get('return_url')))
        except UserLoginError as e:
            flash(e, 'error')

    return render_template('auth/login.html', form=form)

@bp.route('/verify', methods=('GET', 'POST'))
def verify():
    form = VerifyForm(request.form)

    if session.get('user_id') is None:
        return redirect(url_for('auth.login', return_url=request.args.get('return_url')))

    user = UserController.select_one(session.get('user_id'))

    if user.verified:
        abort(404)

    if request.method == 'POST' and form.validate():
        try:
            user.verify(form.code.data)
            session['flow'] = None
            flash('Email verification complete', 'success')

            return redirect(get_safe_redirect(request.args.get('return_url')))
        except UserVerifyError as e:
            flash(e, 'error')
    else:
        user.verify_email()

    return render_template('auth/verify.html', form=form)

@bp.route('/reset', methods=('GET', 'POST'))
def reset():
    email = EmailForm(request.form)
    verify = VerifyForm(request.form)
    password = PasswordForm(request.form)

    if request.method != 'POST':
        return render_template('auth/reset.html', form=email)
    
    if email.validate():
        c.reset_email(email.email.data)
        
        return render_template('auth/reset.html', form=verify)
    
    if verify.validate():
        try:
            c.verify(session.get('user_id'), verify.code.data)
        except c.VerifyError as e:
            flash(e, 'error')
    else:
        c.reset_email(session.get('user_id'))

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
        g.user = UserController.select_one(user_id)
        g.profile = ProfileController.select_one(user_id)
    
    flow = session.get('flow')

    if (flow is not None and request.endpoint != flow) and (request.endpoint != 'static'):
        return redirect(url_for(flow, return_url=request.args.get('return_url', request.path)))