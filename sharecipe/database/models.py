from datetime import datetime
from typing import List, Optional, Self
#from pydantic import BaseModel
from sqlite3 import Row
from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str

    name: str
    bio: Optional[str]
    picture: Optional[str]

    joined: datetime
    active: datetime

    @classmethod
    def parse(cls: Self, query: Row) -> Self:
        return cls(
            id = query['user_id'],
            username = query['username'],
            name = query['name'],
            bio = query['bio'],
            picture = query['picture'],
            joined = datetime.fromisoformat(query['created']),
            active = datetime.fromisoformat(query['last_login'])
        )

@dataclass
class RecipeDetails:
    id: int
    user: User

    title: str
    description: Optional[str]
    photo: Optional[str]

    time: Optional[int]
    difficulty: Optional[int]
    servings: Optional[int]
    vegetarian: bool

    @classmethod
    def parse(cls: Self, query: Row) -> Self:
        return cls(
            id = query['recipe_id'],
            user = User.parse(query),
            title = query['title'],
            description = query['description'],
            photo = query['photo'],
            time = query['time'],
            difficulty = query['difficulty'],
            servings = query['servings'],
            vegetarian = query['vegetarian']
        )

@dataclass
class Comment:
    id: int
    user: User

    body: str
    #replies = List['Comment']

    created: datetime
    
    @classmethod
    def parse(cls: Self, query: Row) -> Self:
        return cls(
            id = query['comment_id'],
            user = User.parse(query),
            body = query['body'],
            #replies = ...,
            created = datetime.fromisoformat(query['created'])
        )

@dataclass
class Recipe(RecipeDetails):
    ingredients: List[str]
    method: List[str]

    tags: List[str]

    #comments: List[Comment]

    created: datetime

    @classmethod
    def parse(cls: Self, query: Row) -> Self:
        return cls(
            id = query['recipe_id'],
            user = User.parse(query),
            title = query['title'],
            description = query['description'],
            photo = query['photo'],
            time = query['time'],
            difficulty = query['difficulty'],
            servings = query['servings'],
            vegetarian = query['vegetarian'],
            ingredients = query['ingredients'].split('\n'),
            method = [x.split('\r\n') for x in query['method'].split('\r\n\r\n')],
            tags = query['tags'].split(','),
            #comments = ...,
            created = datetime.fromisoformat(query['created'])
        )