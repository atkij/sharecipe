from datetime import datetime
from flask import abort, current_app, flash, g, redirect, render_template, request, session, url_for
from PIL import Image
import os

from sharecipe.db import get_db
from sharecipe.util import check_password_hash, generate_filename, generate_password_hash, login_required, validate_image

from . import account_blueprint as bp

@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    error = {}

    if request.method == 'POST':
        if request.form['action'] == 'profile':
            if update_profile(error):
                flash('Profile updated successfully.', 'success')
        elif request.form['action'] == 'update-picture':
            if update_profile_pic():
                flash('Profile picture updated successfully.', 'success')
            else:
                flash('Unable to update profile picture.', 'error')
        elif request.form['action'] == 'delete-picture':
            if delete_profile_pic():
                flash('Profile picture deleted successfully.', 'success')
            else:
                flash('No profile picture to delete.', 'info')
        elif request.form['action'] == 'password':
            if update_password(error):
                flash('Password updated successfully.', 'success')
        elif request.form['action'] == 'transfer':
            pass
        elif request.form['action'] == 'delete':
            if delete_account(error):
                flash('Account deleted successfully.', 'success')
                return redirect(url_for('index'))

    return render_template('account/index.html', error=error)

def update_profile(error):
    forename = request.form.get('forename', '').strip()
    surname = request.form.get('surname', '').strip()
    bio = request.form.get('bio', '').strip()

    if not forename:
        pass
    elif len(forename) > 36:
        error['forename'] = 'Forename must not be more than 36 characters.'

    if not surname:
        pass
    elif len(surname) > 36:
        error['surname'] = 'Surname must not be more than 36 characters.'

    if not bio:
        pass
    elif len(bio) > 400:
        error['bio'] = 'Bio must not be more than 400 characters.'

    if not error:
        db = get_db()

        db.execute(
                'UPDATE user SET forename = ?, surname = ?, bio = ? WHERE user_id = ?',
                (forename, surname, bio, g.user['user_id'])
                )
        db.commit()

        return True

    return False

def delete_profile_pic():
    filename = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profile', str(g.user['user_id']) + '.jpg')
    if os.path.exists(filename):
        os.remove(filename)
        return True
    return False

def update_profile_pic():
    picture = request.files['profile-pic']

    if picture.filename and validate_image(picture.stream):
        pic = process_profile_pic(picture.stream)
        pic.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'profile', str(g.user['user_id']) + '.jpg'), 'JPEG')
        return True

    return False

def process_profile_pic(stream):
    img = Image.open(stream).convert('RGBA')
    w, h = img.size
    new_img = Image.new('RGBA', img.size, 'WHITE')
    new_img.paste(img, (0, 0), img)
    img_crop = new_img.crop((0, 0, h if w > h else w, w if h > w else h))
    img_resize = img_crop.resize((1024, 1024))
    return img_resize.convert('RGB')

def update_password(error):
    current_password = request.form.get('current-password', '')
    new_password = request.form.get('new-password', '')
    new_password_verify = request.form.get('new-password-verify', '')

    if not current_password:
        error['current-password'] = 'Current password is required.'
    elif not check_password_hash(g.user['password'], current_password):
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
        db = get_db()

        db.execute(
                'UPDATE user SET password = ? WHERE user_id = ?',
                (generate_password_hash(new_password), g.user['user_id'])
                )
        db.commit()
        return True

    return False

def delete_account(error):
    password = request.form.get('password')

    if not check_password_hash(g.user['password'], password):
        error['password'] = 'Incorrect password.'

    if not error:
        db = get_db()
        db.execute('DELETE FROM user WHERE user_id = ?', (g.user['user_id'],))
        db.commit()

        session.clear()
        g.user = None
        
        return True

    return False

