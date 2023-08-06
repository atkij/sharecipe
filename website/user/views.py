from datetime import datetime
from flask import abort, g, redirect, render_template, url_for

from website.db import get_db
from website.util import login_required

from . import user_blueprint

@user_blueprint.route('/<int:user_id>')
def index(user_id):
    db = get_db()

    user = db.execute('SELECT user_id, username, last_login, created FROM user WHERE user_id = ?', (user_id,)).fetchone()

    if user is None:
        abort(404)

    follows = False
    if g.user:
        exists = db.execute('SELECT EXISTS(SELECT 1 FROM follower WHERE user_id = ? AND follower_id = ?)', (user_id, g.user['user_id'])).fetchone()
        if exists[0]:
            follows = True

    followers = db.execute('SELECT COUNT(*) FROM follower WHERE user_id = ?', (user_id,)).fetchone()
    following = db.execute('SELECT COUNT(*) FROM follower WHERE follower_id = ?', (user_id,)).fetchone()

    joined = datetime.fromisoformat(user['created']).strftime('%B %Y')
    active = abs(datetime.now() - datetime.fromisoformat(user['last_login'])).days

    return render_template('user/index.html', user=user, joined=joined, active=active, followers=followers[0], following=following[0], follows=follows)

@user_blueprint.route('/<int:user_id>/follow')
@login_required
def follow(user_id):
    db = get_db()

    try:
        db.execute(
            'INSERT INTO follower (user_id, follower_id) VALUES (?, ?)',
            (user_id, g.user['user_id'],)
            )
        db.commit()
    except db.IntegrityError:
        pass

    return redirect(url_for('user.index', user_id=user_id)) 

@user_blueprint.route('/<int:user_id>/unfollow')
@login_required
def unfollow(user_id):
    db = get_db()

    try:
        db.execute(
            'DELETE FROM follower WHERE user_id = ? AND follower_id = ?',
            (user_id, g.user['user_id'],)
            )
        db.commit()
    except db.IntegrityError:
        pass

    return redirect(url_for('user.index', user_id=user_id))
