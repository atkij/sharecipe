from flask import abort, flash, g, redirect, render_template, request, url_for

from website.db import get_db
from website.util import login_required

from . import social_blueprint as bp

@bp.route('/')
def index():
    return render_template('social/index.html')

@bp.route('/feed')
def feed():
    return render_template('social/feed.html')

@bp.route('/post', methods=('GET', 'POST'))
@login_required
def post():
    error = {}

    if request.method == 'POST':
        db = get_db()

        data = process(request.form)
        error = validate(data, error)

        if not error:
            res = db.execute(
                    'INSERT INTO post (user_id, title, body) VALUES (?, ?, ?)',
                    (g.user['user_id'], data['title'], data['body'])
                    )
            db.commit()

            return redirect(url_for('social.view', post_id=res.lastrowid))
    return render_template('social/post.html', error=error)

@bp.route('/post/<int:post_id>')
def view(post_id):
    db = get_db()

    post = db.execute(
            'SELECT post.*, user.username FROM post INNER JOIN user ON post.user_id = user.user_id WHERE post.post_id = ?',
            (post_id,)
            ).fetchone()

    if post is None:
        abort(404)

    return render_template('social/view.html', post=post)

@bp.route('/post/<int:post_id>/update', methods=('GET', 'POST'))
def update(post_id):
    db = get_db()
    error = {}

    post = db.execute(
            'SELECT * FROM post WHERE post_id = ?',
            (post_id,)
            ).fetchone()

    if post is None:
        abort(404)
    elif g.user['user_id'] != post['user_id']:
        abort(403)

    if request.method == 'POST':
        data = process(request.form)
        error = validate(data, error)

        if not error:
            db.execte(
                    'UPDATE post SET title = ?, body = ?, updated = datetime("now") WHERE post_id = ?',
                    (data['title'], data['body'], post_id)
                    )
            db.commit()

            return redirect(url_for('social.view', post_id=post_id))
    return render_template('social/update.html', error=error, post=post)

@bp.route('/post/<int:post_id>/delete')
def delete(post_id):
    db = get_db()

    post = db.execute(
            'SELECT * FROM post WHERE post_id = ?',
            (post_id,)
            ).fetchone()

    if post is None:
        abort(404)
    elif g.user['user_id'] != post['user_id']:
        abort(403)

    db.execute(
            'DELETE FROM post WHERE post_id = ?',
            (post_id,)
            )
    db.commit()

    return redirect(url_for('social.index'))

@bp.route('/post/<int:post_id>/like')
def like(post_id):
    return redirect(url_for('social.post', post_id=post_id))

def process(data):
    data = {key: value.strip().replace('\r', '') for key, value in data.items()}
    return data

def validate(data, error):
    if not data['title']:
        error['title'] = 'Title is required.'
    elif len(data['title']) > 100:
        error['title'] = 'Title cannot be more than 100 characters.'

    if not data['body']:
        error['body'] = 'Body text is required.'
    elif len(data['body']) > 4000:
        error['body'] = 'Body text cannot be more than 4000 characters.'

    return error
