from dataclasses import asdict, dataclass
from typing import List, Optional

from .database import get_db

# def star(user_id, recipe_id):
#     db = get_db()

#     query = 'INSERT INTO star (user_id, recipe_id) VALUES (?, ?)'

#     db.execute(
#         query,
#         (user_id, recipe_id)
#     )

#     db.commit()

# def unstar(user_id: int, recipe_id: int):
#     db = get_db()

#     query = 'DELETE FROM star WHERE user_id = ? AND recipe_id = ?'

#     db.execute(
#         query,
#         (user_id, recipe_id)
#     )

#     db.commit()

# def photo(recipe_id: int, photo: str|None):
#     db = get_db()

#     query = 'UPDATE recipe SET photo = ? WHERE recipe_id = ?'

#     db.execute(
#         query,
#         (photo, recipe_id)
#     )

#     db.commit()