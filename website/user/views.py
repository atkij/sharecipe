from flask import render_template

from website.db import get_db

from . import user_blueprint

@user_blueprint.route('/<int:id>')
def show(id):
    if g.user
    db = get_db()
    user = db.execute('SELECT username, last_login, created FROM user WHERE id = ?', (id,)).fetchone()
    return render_template('user/profile.html', user=user)

@user_blueprint.route('/<int:id>/follow')
def follow(id):
    if g.user:
        db = get_db()
        db.execute(
            'INSERT INTO follower (user_id, follower_id) VALUES (?, ?)'
            (id, g.user['id'])
            )
        db.commit()