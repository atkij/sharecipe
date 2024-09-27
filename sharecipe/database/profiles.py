from dataclasses import dataclass
from typing import Optional

from ..models.profile import Profile

from .database import get_db

def find(user_id: int) -> Profile|None:
    db = get_db()
    
    profile = db.execute(
        'SELECT * FROM profile_view WHERE user_id = ?',
        (user_id,)
    ).fetchone()

    if profile is None:
        return None

    return Profile.from_query(profile)

def find_following(user_id: int) -> list[Profile]:
    db = get_db()

    following = db.execute(
        'SELECT profile_view.* FROM follower INNER JOIN profile_view ON follower.user_id = profile_view.user_id WHERE follower.follower_id = ?',
        (user_id,)
    ).fetchall()

    return list(map(Profile.from_query, following))

def find_followers(user_id: int) -> list[Profile]:
    db = get_db()

    followers = db.execute(
        'SELECT profile_view.* FROM follower INNER JOIN profile_view ON follower.follower_id = profile_view.user_id WHERE follower.user_id = ?',
        (user_id,)
    ).fetchall()

    return list(map(Profile.from_query, followers))

def follows(user_id: int, follower_id: int) -> bool:
    db = get_db()

    query = 'SELECT EXISTS(SELECT 1 FROM follower WHERE user_id = ? AND follower_id = ?)'

    follows = db.execute(
        query,
        (user_id, follower_id)
    ).fetchone()[0]

    return follows

def follow(user_id: int, follower_id: int):
    db = get_db()

    query = 'INSERT INTO follower (user_id, follower_id) VALUES (?, ?)'

    db.execute(
        query,
        (user_id, follower_id)
    )

    db.commit()

def unfollow(user_id, follower_id):
    db = get_db()

    query = 'DELETE FROM follower WHERE user_id = ? AND follower_id = ?'

    db.execute(
        query,
        (user_id, follower_id)
    )

    db.commit()

def create(user_id: int, name: str):
    db = get_db()

    query = 'INSERT INTO profile (user_id, name) VALUES (?, ?)'

    db.execute(
        query,
        (user_id, name)
    )

    db.commit()

def update(user_id: int, name: str, picture: str|None, bio: str|None):
    db = get_db()

    query = 'UPDATE profile SET name = ?, picture = ?, bio = ? WHERE user_id = ?'

    db.execute(
        query,
        (name, picture, bio, user_id)
    )

    db.commit()