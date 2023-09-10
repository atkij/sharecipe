from datetime import datetime
from flask import abort, g, redirect, render_template, request, url_for
from math import ceil

from sharecipe.db import get_db
from sharecipe.util import login_required

from . import user_blueprint

@user_blueprint.route('/<int:user_id>')
def index(user_id):
    db = get_db()

    user = db.execute('SELECT user.* FROM user WHERE user_id = ?', (user_id,)).fetchone()

    if user is None:
        abort(404)
    
    recipes = db.execute(
                'SELECT recipe.*, user.* FROM recipe INNER JOIN user ON recipe.user_id = user.user_id WHERE recipe.user_id = ? ORDER BY created DESC LIMIT 10',
                (user_id,)
                ).fetchall()
    
    follows = False
    if g.user:
        exists = db.execute('SELECT EXISTS(SELECT 1 FROM follower WHERE user_id = ? AND follower_id = ?)', (user_id, g.user['user_id'])).fetchone()
        if exists[0]:
            follows = True

    followers = db.execute(
            'SELECT user.* FROM follower INNER JOIN user ON follower.follower_id = user.user_id WHERE follower.user_id = ?',
            (user_id,)
            ).fetchall()

    following = db.execute(
            'SELECT user.* FROM follower INNER JOIN user ON follower.user_id = user.user_id WHERE follower.follower_id = ?',
            (user_id,)
            ).fetchall()

    joined = datetime.fromisoformat(user['created']).strftime('%B %Y')
    active = abs(datetime.now() - datetime.fromisoformat(user['last_login'])).days

    return render_template('user/index.html', user=user, recipes=recipes, joined=joined, active=active, followers=followers, following=following, follows=follows)

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
