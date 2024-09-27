from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..models.user import User

from .database import get_db
from . import profiles

def find(user_id: int|None = None, email: str|None = None) -> User|None:
    db = get_db()

    query = 'SELECT * FROM user WHERE user_id = ? OR email = ?'

    user = db.execute(
        query,
        (user_id, email)
    ).fetchone()

    if user is None:
        return None

    return User.from_query(user)

def login(user_id: int):
    db = get_db()

    query = 'UPDATE user SET last_login = datetime("now") WHERE user_id = ?'

    db.execute(
        query,
        (user_id,)
    )

    db.commit()

def create(email: str, password: str, name: str) -> int:
    db = get_db()

    query = 'INSERT INTO user (email, password) VALUES (?, ?)'

    res = db.execute(
        query,
        (email, password)
    )

    user_id = res.lastrowid

    profiles.create(user_id, name)

    return user_id

def update(user_id: int, email: str, password: str, verified: bool):
    db = get_db()

    query = 'UPDATE user SET email = ?, password = ?, verified = ? WHERE user_id = ?'

    db.execute(
        query,
        (email, password, verified, user_id)
    )

    db.commit()

def delete(user_id: int):
    db = get_db()

    query = 'DELETE FROM user WHERE user_id = ?'

    db.execute(
        query,
        (user_id,)
    )

    db.commit()

def get_code(user_id: int) -> int|None:
    db = get_db()

    query = 'SELECT code FROM verify WHERE user_id = ? AND expires > CURRENT_TIMESTAMP'

    res = db.execute(
        query,
        (user_id,)
    ).fetchone()

    if res is None:
        return None
    
    return res[0]

def set_code(user_id: int, code: int, expires: datetime):
    db = get_db()

    query = 'REPLACE INTO verify (user_id, code, expires) VALUES (?, ?, ?)'

    db.execute(
        query,
        (user_id, code, expires.strftime("%Y-%m-%d %H:%M:%S"))
    )
    
    db.commit()

def delete_code(user_id: int):
    db = get_db()

    query = 'DELETE FROM verify WHERE user_id = ?'

    db.execute(
        query,
        (user_id,)
    )

    db.commit()