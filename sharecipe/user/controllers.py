from datetime import datetime
from typing import List

from sharecipe.database.database import get_db
from sharecipe.database.models import User, RecipeDetails

def get_user(id: int) -> User:
    db = get_db()

    user = db.execute(
        'SELECT * FROM user WHERE user_id = ?',
        (id,)
    ).fetchone()

    return User.parse(user)

def get_followers(id: int) -> List[User]:
    db = get_db()

    followers = db.execute(
        'SELECT * FROM follower INNER JOIN user ON follower.follower_id = user.user_id WHERE follower.user_id = ?',
        (id,)
    ).fetchall()

    return list(map(User.parse, followers))

def get_following(id: int) -> List[User]:
    db = get_db()

    following = db.execute(
        'SELECT * FROM follower INNER JOIN user ON follower.user_id = user.user_id WHERE follower.follower_id = ?',
        (id,)
    ).fetchall()

    return list(map(User.parse, following))
    