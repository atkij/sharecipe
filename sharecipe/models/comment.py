from dataclasses import dataclass
from datetime import datetime
from sqlite3 import Row
from typing import List, Self

from .profile import Profile


@dataclass
class Comment:
    id: int
    user: Profile
    recipe: int

    body: str

    created: datetime

    @classmethod
    def from_query(cls: Self, query: Row) -> Self:
        return cls(
            id=query['comment_id'],
            user=Profile.from_query(query),
            recipe=query['recipe_id'],
            body=query['body'],
            created=datetime.fromisoformat(query['created'])
        )