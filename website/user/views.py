from datetime import datetime
from flask import abort, g, redirect, render_template, url_for

from website.db import get_db

from . import user_blueprint

@user_blueprint.route('/<int:id>')
def index(id):
    db = get_db()

    user = db.execute('SELECT id, username, last_login, created FROM user WHERE id = ?', (id,)).fetchone()

    if user is None:
        abort(404)

    follows = False
    if g.user:
        exists = db.execute('SELECT EXISTS(SELECT 1 FROM follower WHERE user_id = ? AND follower_id = ?)', (id, g.user['id'])).fetchone()
        if exists[0]:
            follows = True

    followers = db.execute('SELECT COUNT(*) FROM follower WHERE user_id = ?', (id,)).fetchone()
    following = db.execute('SELECT COUNT(*) FROM follower WHERE follower_id = ?', (id,)).fetchone()

    joined = datetime.fromisoformat(user['created']).strftime('%B %Y')
    active = abs(datetime.now() - datetime.fromisoformat(user['last_login'])).days

    return render_template('user/index.html', user=user, joined=joined, active=active, followers=followers[0], following=following[0], follows=follows)

@user_blueprint.route('/<int:id>/follow')
def follow(id):
    if g.user:
        db = get_db()

        try:
            db.execute(
                'INSERT INTO follower (user_id, follower_id) VALUES (?, ?)',
                (id, g.user['id'],)
                )
            db.commit()
        except db.IntegrityError:
            pass

    return redirect(url_for('user.index', id=id)) 

@user_blueprint.route('/<int:id>/unfollow')
def unfollow(id):
    if g.user:
        db = get_db()

        try:
            db.execute(
                'DELETE FROM follower WHERE user_id = ? AND follower_id = ?',
                (id, g.user['id'],)
                )
            db.commit()
        except db.IntegrityError:
            pass

    return redirect(url_for('user.index', id=id))
