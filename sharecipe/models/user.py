from dataclasses import dataclass
from datetime import datetime
from sqlite3 import Row
from typing import List, Optional, Self

from . import Model
from ..database.database import get_db

class UserInsertError(Exception):
    pass

@dataclass
class UserModel(Model):
    id: int

    email: str
    password: str
    verified: bool

    created: datetime
    last_login: datetime

    @classmethod
    def _insert(cls, email: str, password: str) -> Self:
        db = get_db()

        query = 'INSERT INTO user (email, password) VALUES (?, ?)'

        res = db.execute(
            query,
            (email, password)
        )
        db.commit()

        if res is None:
            raise UserInsertError

        return cls.select_one(res.lastrowid)

    @classmethod
    def select_one(cls, id: int) -> Self | None:
        db = get_db()

        query = 'SELECT * FROM user WHERE id = ?'

        cur = db.execute(
            query,
            (id,),
        )
        res = cur.fetchone()

        if res is None:
            return None

        return cls._from_row(res)

    @classmethod
    def select_one_by_email(cls, email: str) -> Self | None:
        db = get_db()

        query = 'SELECT * FROM user WHERE email = ?'
        
        cur = db.execute(
            query,
            (email,),
        )
        res = cur.fetchone()

        if res is None:
            return None

        return cls._from_row(res)

    def _update(self):
        db = get_db()

        query = 'UPDATE user SET email = ?, password = ?, verified = ?, last_login = ? WHERE id = ?'

        res = db.execute(
            query,
            (self.email,
             self.password,
             self.verified,
             self.last_login.isoformat(),
             self.id),
        )

        db.commit()

    def _delete(self):
        db = get_db()

        query = 'DELETE FROM user WHERE id = ?'

        res = db.execute(
            query,
            (self.id,),
        )

        db.commit()

    @classmethod
    def _from_row(cls: Self, row: Row) -> Self:
        return cls(
            row['id'],
            row['email'],
            row['password'],
            bool(row['verified']),
            datetime.fromisoformat(row['created']),
            datetime.fromisoformat(row['last_login']),
        )

    def as_dict(self) -> dict:
        return {
            'id': self.id,
        }