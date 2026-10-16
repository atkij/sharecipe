from dataclasses import dataclass
from sqlite3 import Row
from typing import Optional, Self

from . import Model
from ..database.database import get_db

class ProfileInsertError(Exception):
    pass

@dataclass
class ProfileModel(Model):
    id: int

    name: str
    bio: Optional[str]
    picture: Optional[str]

    @classmethod
    def _insert(cls, id: int, name: str) -> Self:
        db = get_db()

        query = 'INSERT INTO profile (id, name) VALUES (?, ?)'

        res = db.execute(
            query,
            (id, name)
        )
        db.commit()

        if res is None:
            raise ProfileInsertError

        return cls.select_one(id)

    @classmethod
    def select_one(cls, id: int) -> Self | None:
        db = get_db()

        query = 'SELECT * FROM profile WHERE id = ?'

        cur = db.execute(
            query,
            (id,)
        )
        res = cur.fetchone()

        return cls._from_row(res) if res else None

    def _update(self):
        db = get_db()

        query = 'UPDATE profile SET name = ?, bio = ?, picture = ? WHERE id = ?'

        res = db.execute(
            query,
            (self.name,
             self.bio,
             self.picture,
             self.id)
        )

        db.commit()

    def _delete(self):
        db = get_db()

        query = 'DELETE FROM profile WHERE id = ?'

        res = db.execute(
            query,
            (self.id,)
        )

        db.commit()

    @classmethod
    def _from_row(cls: Self, row: Row):
        return cls(
            row['id'],
            row['name'],
            row['bio'],
            row['picture'],
        )

    def as_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'bio': self.bio,
            'picture': self.picture,
        }