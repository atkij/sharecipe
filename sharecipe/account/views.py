from dataclasses import asdict
import os
import uuid

from flask import current_app, flash, g, redirect, render_template, request, session, url_for

from ..auth.helpers import generate_password_hash, login_required
from ..database import profiles, users
from ..util import resize_image

from . import account_blueprint as bp
from .forms import UpdateProfileForm, UploadPictureForm, DeletePictureForm, UpdatePasswordForm, DeleteAccountForm

@bp.route('/')
@login_required
def index():
    return redirect(url_for('account.profile'))

@bp.route('/profile', methods=('GET', 'POST'))
@login_required
def profile():
    form = UpdateProfileForm(request.form, data=asdict(g.profile) | asdict(g.user))

    if request.method == 'POST' and form.validate():
        profiles.update(g.user.id, form.name.data, g.profile.picture, form.bio.data)

        if form.email.data != g.user.email:
            user = users.find(email=form.email.data)

            if user is None:
                users.update(g.user.id, form.email.data, g.user.password, False)
                flash('Profile updated successfully', 'success')
            else:
                flash('Account with email address already exists', 'error')
        else:
            flash('Profile updated successfully', 'success')

        return redirect(url_for('account.index'))

    return render_template('account/profile.html',
            form=form,
            upload_picture_form=UploadPictureForm(),
            delete_picture_form=DeletePictureForm(),
            )

def _delete_picture():
    if g.profile.picture is None:
        return

    filename = os.path.join(current_app.config['UPLOAD_FOLDER'] , g.user['picture'])
    if os.path.exists(filename):
        os.remove(filename)

    profiles.update(g.user.id, g.profile.name, None, g.profile.bio)

@bp.route('/picture/upload', methods=('GET', 'POST'))
@login_required
def upload_picture():
    form = UploadPictureForm()

    if request.method == 'POST' and form.validate():
        _delete_picture()

        picture = form.picture.data
        filename = str(uuid.uuid4()) + '.' + picture.filename.split('.')[-1]

        picture = resize_image(picture.stream, 256)
        if picture is None:
            flash('Unsupported image format.', 'error')
            return redirect(url_for('account.index'))

        picture.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        profiles.update(g.user.id, g.profile.name, filename, g.profile.bio)

        flash('Profile picture updated successfully.', 'success')
    else:
        for error in form.picture.errors:
            flash(error, 'error')
    
    return redirect(url_for('account.index'))

@bp.route('/picture/delete', methods=('GET', 'POST'))
@login_required 
def delete_picture():
    form = DeletePictureForm(request.form)

    if request.method == 'POST' and g.profile.picture and form.validate():
        _delete_picture()

        flash('Profile picture deleted successfully.', 'success')

    return redirect(url_for('account.index'))

@bp.route('/password', methods=('GET', 'POST'))
@login_required
def password():
    form = UpdatePasswordForm(request.form)

    if request.method == 'POST' and form.validate():
        users.update(g.user.id, g.user.email, generate_password_hash(form.new_password.data), g.user.verified)

        flash('Password updated successfully.', 'success')

        return redirect(url_for('account.index'))

    return render_template('account/password.html', form=form)

@bp.route('/delete', methods=('GET', 'POST'))
@login_required
def delete():
    form = DeleteAccountForm(request.form)

    if request.method == 'POST' and form.validate():
        _delete_picture()

        users.delete(g.user.id)

        session.clear()
        g.user = None
        g.profile = None

        flash('Account deleted successfully.', 'success')

        return redirect(url_for('main.index'))

    return render_template('account/delete.html', form=form)
