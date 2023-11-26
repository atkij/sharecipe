from flask import abort, current_app, flash, g, redirect, render_template, request, url_for

import os
import uuid

from sharecipe.db import get_db
from sharecipe.forms import DeleteForm, MultiPhotoForm, PostForm
from sharecipe.util import login_required

from . import social_blueprint as bp

@bp.route('/')
def index():
    return render_template('social/index.html')

@bp.route('/<int:post_id>')
def view(post_id):
    db = get_db()

    post = db.execute(
            'SELECT post.*, user.* FROM post INNER JOIN user ON post.user_id = user.user_id WHERE post_id = ?',
            (post_id,)
            ).fetchone()
    photos = db.execute(
            'SELECT photo.* FROM photo WHERE post_id = ?',
            (post_id,)
            ).fetchall()

    if post is None:
        abort(404)
    elif not visible(post):
        abort(403)
    
    return render_template('social/view.html', post=post, photos=photos, photo_form=MultiPhotoForm(), delete_form=DeleteForm())

@bp.route('/post', methods=('GET', 'POST'))
@login_required
def post():
    form = PostForm(request.form)

    if request.method == 'POST' and form.validate():
        db = get_db()
        
        res = db.execute(
                'INSERT INTO post (user_id, title, body, sharing) VALUES (?, ?, ?, ?)',
                (g.user['user_id'], form.title.data, form.body.data, form.sharing.data)
                )
        """
        print(request.files.getlist('photos'))
        
        for photo in request.files.getlist('photos'):
            if not photo:
                continue

            ext = photo.filename.rsplit('.', 1)[1].lower()

            if ext not in ['jpeg', 'jpg', 'png', 'gif']:
                flash('Unsupported image format.', 'error')
                render_template('social/post.html', form=form)

            filename = str(uuid.uuid4()) + '.' + ext
            db.execute(
                    'INSERT INTO photo (post_id, photo) VALUES (?, ?)',
                    (res.lastrowid, filename)
                    )
            photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        """

        db.commit()
        return redirect(url_for('social.view', post_id=res.lastrowid))
    return render_template('social/post.html', form=form)

@bp.route('/<int:post_id>/update', methods=('GET', 'POST'))
@login_required
def update(post_id):
    db = get_db()

    post = db.execute(
            'SELECT * FROM post WHERE post_id = ?',
            (post_id,)
            ).fetchone()

    if post is None:
        abort(404)
    elif g.user['user_id'] != post['user_id']:
        abort(403)

    form = PostForm(request.form, data=post)

    if request.method == 'POST' and form.validate():
        db.execute(
                'UPDATE post SET title = ?, body = ?, sharing = ?, updated = datetime("now") WHERE post_id = ?',
                (form.title.data, form.body.data, form.sharing.data, post_id),
                )
        db.commit()

        return redirect(url_for('social.view', post_id=post_id))
    return render_template('social/update.html', form=form)

@bp.route('/<int:post_id>/delete', methods=('GET', 'POST'))
@login_required
def delete(post_id):
    form = DeleteForm()
    db = get_db()

    post = db.execute(
            'SELECT * FROM post WHERE post_id = ?',
            (post_id,)
            ).fetchone()

    if post is None:
        abort(404)
    elif g.user['user_id'] != post['user_id']:
        abort(403)

    if request.method == 'POST' and form.validate():
        photos = db.execute(
                'SELECT * FROM photo WHERE post_id = ?',
                (post_id,)
                ).fetchall()

        for photo in photos:
            photo_delete(photo)

        db.execute(
                'DELETE FROM post WHERE post_id = ?',
                (post_id,)
                )
        db.commit()

        flash('Post deleted successfully.', 'success')
        return redirect(url_for('social.index'))
    else:
        flash('Unable to delete post.', 'error')
        return redirect(url_for('social.view', post_id=post_id))
    
@bp.route('/<int:post_id>/photos/upload', methods=('GET', 'POST'))
@login_required
def upload_photos(post_id):
    form = MultiPhotoForm(request.form)
    db = get_db()

    post = db.execute(
            'SELECT * FROM post WHERE post_id = ?',
            (post_id,)
            ).fetchone()

    if post is None:
        abort(404)
    elif g.user['user_id'] != post['user_id']:
        abort(403)
    
    if request.method == 'POST' and form.validate():
        error = None
        for photo in request.files.getlist('photos'):
            if not photo:
                continue
            error = photo_upload(photo, post_id)

        if error is None:
            flash('Photos uploaded successfully.', 'success')
        else:
            flash(error, 'error')

    return redirect(url_for('social.view', post_id=post_id))

def photo_upload(photo, post_id):
    db = get_db()

    ext = photo.filename.rsplit('.', 1)[1].lower()

    if ext not in ['jpeg', 'jpg', 'png', 'gif']:
        return 'Unsupported image format.'

    filename = str(uuid.uuid4()) + '.' + ext
    db.execute(
             'INSERT INTO photo (post_id, photo) VALUES (?, ?)',
            (post_id, filename)
            )
    photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    db.commit()

    return None


@bp.route('/<int:post_id>/photos/<int:photo_id>/delete', methods=('GET', 'POST'))
@login_required
def delete_photo(post_id, photo_id):
    form = DeleteForm(request.form)
    db = get_db()

    post = db.execute(
            'SELECT * FROM post WHERE post_id = ?',
            (post_id,)
            ).fetchone()

    if post is None:
        abort(404)
    elif g.user['user_id'] != post['user_id']:
        abort(403)

    photo = db.execute(
            'SELECT * FROM photo WHERE post_id = ? AND photo_id = ?',
            (post_id,photo_id)
            ).fetchone()

    if photo is None:
        abort(403)

    if request.method == 'POST' and form.validate():
        photo_delete(photo)

        flash('Photos deleted successfully.', 'success')
    else:
        flash('Unable to delete photos.', 'error')

    return redirect(url_for('social.view', post_id=post_id))

def photo_delete(photo):
    db = get_db()

    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], photo['photo']))

    db.execute(
            'DELETE FROM photo WHERE photo_id = ?',
            (photo['photo_id'],)
            )
    db.commit()

def visible(post):
    db = get_db()

    if post['sharing'] == 0:
        if g.user and g.user['user_id'] == post['user_id']:
            return True
    elif post['sharing'] == 1:
        follows = db.execute(
                'SELECT EXISTS(SELECT 1 FROM follower WHERE user_id = ? AND follower_id = ?)',
                (post['user_id'], g.user['user_id'] if g.user['user_id'] else None)
                ).fetchone()
        if follows[0] or g.user['user_id'] == post['user_id']:
            return True
    elif post['sharing'] == 2:
        return True

    return False


