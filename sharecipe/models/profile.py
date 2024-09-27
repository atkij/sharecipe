from dataclasses import dataclass
from datetime import datetime
from sqlite3 import Row
from typing import Optional, Self

@dataclass
class Profile:
    id: int

    name: str
    bio: Optional[str]
    picture: Optional[str]

    joined: datetime
    active: datetime

    @classmethod
    def from_query(cls: Self, query: Row):
        return cls(
            id=query['user_id'],
            name=query['name'],
            bio=query['bio'],
            picture=query['picture'],
            joined=datetime.fromisoformat(query['joined']),
            active=datetime.fromisoformat(query['active']),
        )