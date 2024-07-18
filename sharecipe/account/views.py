from flask import current_app, flash, g, redirect, render_template, request, session, url_for

from datetime import datetime
import os
import uuid

from sharecipe.db import get_db
from sharecipe.util import resize_image
from sharecipe.auth.helpers import check_password_hash, generate_password_hash, login_required

from . import account_blueprint as bp
from .forms import UpdateProfileForm, UploadPictureForm, DeletePictureForm, UpdatePasswordForm, DeleteAccountForm

@bp.route('/')
@login_required
def index():
    return redirect(url_for('account.profile'))

@bp.route('/profile', methods=('GET', 'POST'))
@login_required
def profile():
    form = UpdateProfileForm(request.form, data=g.user)

    if request.method == 'POST' and form.validate():
        db = get_db()
        db.execute(
                'UPDATE user SET name = ?, email = ?, bio = ? WHERE user_id = ?',
                (form.name.data, form.email.data, form.bio.data, g.user['user_id'])
                )
        db.commit()

        flash('Profile updated successfully.', 'success')

        return redirect(url_for('account.index'))

    return render_template('account/profile.html',
            form=form,
            upload_picture_form=UploadPictureForm(),
            delete_picture_form=DeletePictureForm(),
            )

def _delete_picture():
    if g.user['picture'] is None:
        return

    filename = os.path.join(current_app.config['UPLOAD_FOLDER'] , g.user['picture'])
    if os.path.exists(filename):
        os.remove(filename)

    db = get_db()
    db.execute(
            'UPDATE user SET picture = NULL WHERE user_id = ?',
            (g.user['user_id'],)
            )
    db.commit()

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
        
        db = get_db()
        db.execute(
                'UPDATE user SET picture = ? WHERE user_id = ?',
                (filename, g.user['user_id'])
                )
        db.commit()

        flash('Profile picture updated successfully.', 'success')
    else:
        for error in form.picture.errors:
            flash(error, 'error')
    
    return redirect(url_for('account.index'))

@bp.route('/picture/delete', methods=('GET', 'POST'))
@login_required 
def delete_picture():
    form = DeletePictureForm(request.form)

    if request.method == 'POST' and g.user['picture'] and form.validate():
        _delete_picture()

        flash('Profile picture deleted successfully.', 'success')

    return redirect(url_for('account.index'))

@bp.route('/password', methods=('GET', 'POST'))
@login_required
def password():
    form = UpdatePasswordForm(request.form)

    if request.method == 'POST' and form.validate():
        db = get_db()

        db.execute(
                'UPDATE user SET password = ? WHERE user_id = ?',
                (generate_password_hash(form.new_password.data), g.user['user_id'])
                )
        db.commit()

        flash('Password updated successfully.', 'success')

        return redirect(url_for('account.index'))

    return render_template('account/password.html', form=form)

@bp.route('/delete', methods=('GET', 'POST'))
@login_required
def delete():
    form = DeleteAccountForm(request.form)

    if request.method == 'POST' and form.validate():
        _delete_picture()

        db = get_db()
        db.execute('DELETE FROM user WHERE user_id = ?', (g.user['user_id'],))
        db.commit()

        session.clear()
        g.user = None

        flash('Account deleted successfully.', 'success')

        return redirect(url_for('main.index'))

    return render_template('account/delete.html', form=form)
