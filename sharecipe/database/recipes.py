from dataclasses import asdict, dataclass
from typing import List, Optional

from ..models.recipe import Recipe, RecipeDetails

from .database import get_db

from . import comments

def find(user_id=None, favourite_id=None, vegetarian=None, limit=10, offset=0) -> List[RecipeDetails]:
    db = get_db()

    query = ('SELECT recipe.*, profile_view.* FROM recipe '
             'INNER JOIN profile_view ON recipe.user_id = profile_view.user_id '
             'LEFT JOIN favourite ON recipe.recipe_id = favourite.recipe_id')
    filters = []

    if user_id is not None:
        filters.append('recipe.user_id = :user_id')

    if favourite_id is not None:
        filters.append('favourite.user_id = :favourite_id')

    if vegetarian is not None:
        filters.append('recipe.vegetarian = :vegetarian')
    
    if len(filters) > 0:
        where = ' '.join(filters)
        query += ' WHERE ' + where
    
    query += ' ORDER BY recipe.created DESC LIMIT :limit OFFSET :offset'
    
    recipes = db.execute(
        query,
        {
            'user_id': user_id,
            'favourite_id': favourite_id,
            'vegetarian': vegetarian,
            'limit': limit,
            'offset': offset
        }
    ).fetchall()

    return list(map(RecipeDetails.from_query, recipes))

def find_details(recipe_id: int) -> RecipeDetails|None:
    db = get_db()

    query = ('SELECT recipe.*, profile_view.* FROM recipe '
             'INNER JOIN profile_view ON recipe.user_id = profile_view.user_id '
             'WHERE recipe.recipe_id = ?')
    
    recipe = db.execute(
        query,
        (recipe_id,)
    ).fetchone()

    if recipe is None:
        return None
    
    return RecipeDetails.from_query(recipe)

def find_one(recipe_id: int, user_id: int|None = None) -> Recipe|None:
    db = get_db()

    query = ('SELECT recipe.*, profile_view.*, '
             'AVG(rating.rating) AS rating, COUNT(rating.rating) AS ratings, '
             'EXISTS(SELECT 1 FROM favourite WHERE user_id = ? AND recipe_id = ?) AS favourite FROM recipe '
             'INNER JOIN profile_view ON recipe.user_id = profile_view.user_id '
             'LEFT JOIN rating ON recipe.recipe_id = rating.recipe_id '
             'WHERE recipe.recipe_id = ?')
    
    recipe = db.execute(
        query,
        (user_id, recipe_id, recipe_id,)
    ).fetchone()

    if recipe[0] is None:
        return None

    return Recipe.from_query(recipe, comments.find(recipe_id))

def count(user_id=None, favourite_id=None, vegetarian=None) -> int:
    db = get_db()

    query = ('SELECT COUNT(*) FROM recipe '
             'INNER JOIN profile_view ON recipe.user_id = profile_view.user_id '
             'LEFT JOIN favourite ON recipe.recipe_id = favourite.recipe_id')
    filters = []

    if user_id is not None:
        filters.append('recipe.user_id = :user_id')

    if favourite_id is not None:
        filters.append('favourite.user_id = :favourite_id')

    if vegetarian is not None:
        filters.append('recipe.vegetarian = :vegetarian')
    
    if len(filters) > 0:
        where = ' '.join(filters)
        query += ' WHERE ' + where
    
    count = db.execute(
        query,
        {
            'user_id': user_id,
            'favourite_id': favourite_id,
            'vegetarian': vegetarian,
        }
    ).fetchone()[0]

    return count

def rate(user_id: int, recipe_id: int, rating: int):
    db = get_db()

    query = ('INSERT INTO rating (user_id, recipe_id, rating) VALUES (?, ?, ?) '
             'ON CONFLICT (user_id, recipe_id) DO UPDATE SET rating=excluded.rating')

    db.execute(
        query,
        (user_id, recipe_id, rating)
    )
    
    db.commit()

def favourite(user_id, recipe_id):
    db = get_db()

    query = 'INSERT INTO favourite (user_id, recipe_id) VALUES (?, ?)'

    db.execute(
        query,
        (user_id, recipe_id)
    )

    db.commit()

def unfavourite(user_id: int, recipe_id: int):
    db = get_db()

    query = 'DELETE FROM favourite WHERE user_id = ? AND recipe_id = ?'

    db.execute(
        query,
        (user_id, recipe_id)
    )

    db.commit()

def photo(recipe_id: int, photo: str|None):
    db = get_db()

    query = 'UPDATE recipe SET photo = ? WHERE recipe_id = ?'

    db.execute(
        query,
        (photo, recipe_id)
    )

    db.commit()

def create(
        user_id: int,
        title: str,
        description: str,
        time: int,
        difficulty: int,
        servings: int,
        vegetarian: bool,
        ingredients: list[str],
        method: list[str],
        tags: list[str]
) -> int:
    db = get_db()
    
    query = ('INSERT INTO recipe '
             '(user_id, title, description, time, difficulty, servings, vegetarian, ingredients, method, tags) '
             'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)')
    
    res = db.execute(
        query,
        (user_id, title, description, time, difficulty, servings, vegetarian, '\r\n'.join(ingredients), '\r\n\r\n'.join(method), ','.join(tags))
    )

    db.commit()

    return res.lastrowid

def update(
        recipe_id: int,
        title: str,
        description: str,
        time: int,
        difficulty: int,
        servings: int,
        vegetarian: bool,
        ingredients: list[str],
        method: list[str],
        tags: list[str]
):
    db = get_db()

    query = ('UPDATE recipe SET '
             'title = ?, description = ?, time = ?, difficulty = ?, servings = ?, vegetarian = ?, ingredients = ?, method = ?, tags = ? '
             'WHERE recipe_id = ?')
    
    res = db.execute(
        query,
        (title, description, time, difficulty, servings, vegetarian, '\r\n'.join(ingredients), '\r\n\r\n'.join(method), ','.join(tags), recipe_id)
    )

    db.commit()

def delete(recipe_id):
    db = get_db()

    db.execute(
        'DELETE FROM recipe WHERE recipe_id = ?',
        (recipe_id,)
    )

    db.commit()