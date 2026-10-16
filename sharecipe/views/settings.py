from dataclasses import asdict

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from ..controllers.user import UserUpdateError

from ..core.auth import login_required
from ..core.media import upload_media, delete_media, UnsupportedMediaError
from ..forms.account import UpdateProfileForm, UploadPictureForm, DeletePictureForm, UpdatePasswordForm, DeleteAccountForm

bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route('/')
@login_required
def index():
    return redirect(url_for('settings.profile'))

@bp.route('/profile', methods=('GET', 'POST'))
@login_required
def profile():
    form = UpdateProfileForm(request.form, data=asdict(g.profile) | asdict(g.user))

    if request.method == 'POST' and form.validate():
        g.profile.name = form.name.data
        g.profile.bio = form.bio.data

        g.profile.update()

        try:
            g.user.email = form.email.data
            g.user.update()
        except UserUpdateError:
            flash('Account with email address already exists', 'error')
        else:
            flash('Email address updated', 'success')
        
        flash('Profile updated', 'success')
        return redirect(url_for('settings.profile'))

    return render_template('settings/profile.html',
            form=form,
            upload_picture_form=UploadPictureForm(),
            delete_picture_form=DeletePictureForm(),
            )

@bp.route('/picture/upload', methods=('GET', 'POST'))
@login_required
def upload_picture():
    form = UploadPictureForm()

    if request.method == 'POST' and form.validate():
        try:
            filename = upload_media(form.picture.data, max_size=256)
            print(filename)
            g.profile.picture = filename
            g.profile.update()
            print(g.profile)
        except UnsupportedMediaError:
            flash('Unsupported image format', 'error')
        else:
            flash('Profile picture updated', 'success')
    else:
        for error in form.picture.errors:
            flash(error, 'error')
    
    return redirect(url_for('settings.profile'))

@bp.route('/picture/delete', methods=('GET', 'POST'))
@login_required 
def delete_picture():
    form = DeletePictureForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            delete_media(g.profile.picture)
            g.profile.picture = None
            g.profile.update()
        except:
            flash('An unexpected error occurred', 'error')
        else:
            flash('Profile picture deleted', 'success')

    return redirect(url_for('settings.profile'))

@bp.route('/password', methods=('GET', 'POST'))
@login_required
def password():
    form = UpdatePasswordForm(request.form)

    if request.method == 'POST' and form.validate():
        g.user.set_password(form.new_password.data)

        flash('Password updated', 'success')
        return redirect(url_for('settings.password'))

    return render_template('settings/password.html', form=form)

@bp.route('/delete', methods=('GET', 'POST'))
@login_required
def delete():
    form = DeleteAccountForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            c.delete_picture()
        except c.PictureNotFound:
            pass

        g.user.delete()
        session.clear()

        flash('Sharecipe account deleted', 'success')
        return redirect(url_for('main.index'))

    return render_template('settings/delete.html', form=form)
