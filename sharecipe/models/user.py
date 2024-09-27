from dataclasses import dataclass
from datetime import datetime
from sqlite3 import Row
from typing import List, Optional, Self

@dataclass
class User:
    id: int

    email: str
    password: str
    verified: bool

    joined: datetime
    active: datetime

    @classmethod
    def from_query(cls: Self, query: Row) -> Self:
        return cls(
            id=query['user_id'],
            email=query['email'],
            password=query['password'],
            verified=bool(query['verified']),
            joined=datetime.fromisoformat(query['created']),
            active=datetime.fromisoformat(query['last_login']),
        )