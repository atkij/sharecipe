from dataclasses import dataclass
from datetime import datetime
from sqlite3 import Row
from typing import Optional, Self

from .profile import Profile
from .comment import Comment

@dataclass
class RecipeDetails:
    id: int
    user: Profile

    title: str
    description: Optional[str]
    photo: Optional[str]

    time: Optional[int]
    difficulty: Optional[int]
    servings: Optional[int]
    vegetarian: bool

    @classmethod
    def from_query(cls: Self, query: Row) -> Self:
        return cls(
            id=query['recipe_id'],
            user=Profile.from_query(query),
            title=query['title'],
            description=query['description'],
            photo=query['photo'],
            time=query['time'],
            difficulty=query['difficulty'],
            servings=query['servings'],
            vegetarian=query['vegetarian'],
        )

@dataclass
class Recipe:
    id: int
    user: Profile

    title: str
    description: Optional[str]
    photo: Optional[str]

    time: Optional[int]
    difficulty: Optional[int]
    servings: Optional[int]
    vegetarian: bool

    ingredients: list[str]
    method: list[str]

    tags: list[str]

    rating: float
    ratings: int

    favourite: bool

    comments: list[Comment]
    
    created: datetime

    @classmethod
    def from_query(cls: Self, query: Row, comments: list[Comment]) -> Self:
        return cls(
            id=query['recipe_id'],
            user=Profile.from_query(query),
            title=query['title'],
            description=query['description'],
            photo=query['photo'],
            time=query['time'],
            difficulty=query['difficulty'],
            servings=query['servings'],
            vegetarian=bool(query['vegetarian']),
            ingredients=query['ingredients'].split('\n'),
            method=query['method'].split('\r\n\r\n'),
            tags=query['tags'].split(','),
            rating=query['rating'],
            ratings=query['ratings'],
            favourite=bool(query['favourite']),
            comments=comments,
            created=datetime.fromisoformat(query['created'])
        )