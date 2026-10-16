from dataclasses import dataclass
from datetime import datetime
from sqlite3 import Row
from typing import Optional, Self

from . import Model, ListItemModel
from ..database.database import get_db

@dataclass
class RecipeModel(Model):
    id: int
    user_id: int

    title: str
    description: Optional[str]

    prepare: Optional[int]
    cook: Optional[int]
    serves: Optional[str]
    vegetarian: bool

    tags: str    
    created: datetime

    @classmethod
    def insert(cls, user_id: int, title: str, description: str | None = None, prepare: int | None = None, cook: int | None = None, serves: str | None = None, vegetarian: int | None = None, tags: str | None = None) -> Self:
        db = get_db()

        query = 'INSERT INTO recipe (user_id, title, description, prepare, cook, serves, vegetarian, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'

        res = db.execute(
            query,
            (user_id,
             title,
             description,
             prepare,
             cook,
             serves,
             vegetarian,
             tags)
        )
        db.commit()

        return cls.select_one(res.lastrowid) if res else None

    @classmethod
    def select_one(cls, id: int) -> Self | None:
        db = get_db()

        query = 'SELECT * FROM recipe WHERE id = ?'

        cur = db.execute(
            query,
            (id,)
        )
        res = cur.fetchone()

        return cls._from_row(res) if res else None

    @classmethod
    def select_all(cls) -> list[Self]:
        db = get_db()

        query = 'SELECT * FROM recipe'

        cur = db.execute(query)
        res = cur.fetchall()

        return list(map(cls._from_row, res))

    @classmethod
    def select_by_filter(cls, user_id=None, vegetarian=None, limit=10, offset=0) -> list[Self]:
        db = get_db()

        query = ('SELECT * FROM recipe')

        query, parameters = cls._apply_filters(query, user_id, vegetarian)
        print(query, parameters)

        query += ' LIMIT ? OFFSET ?'
        
        parameters.append(limit)
        parameters.append(offset)

        cur = db.execute(
            query,
            parameters
        )
        res = cur.fetchall()

        return list(map(cls._from_row, res))

    @staticmethod
    def count_all() -> int:
        db = get_db()

        query = 'SELECT COUNT(*) FROM recipe'

        cur = db.execute(query)
        res = cur.fetchone()

        return res[0]

    @classmethod
    def count_by_filter(
        cls,
        user_id: int | None = None,
        vegetarian: bool | None = None
    ) -> int:
        db = get_db()

        query = 'SELECT COUNT(*) FROM recipe'

        query, parameters = cls._apply_filters(query, user_id, vegetarian)

        cur = db.execute(
            query,
            parameters
        )
        res = cur.fetchone()

        return res[0]

    def update(self):
        db = get_db()

        query = 'UPDATE recipe SET title = ?, description = ?, prepare = ?, cook = ?, serves = ?, vegetarian = ?, tags = ? WHERE id = ?'

        res = db.execute(
            query,
            (self.title,
             self.description,
             self.prepare,
             self.cook,
             self.serves,
             self.vegetarian,
             self.tags,
             self.id)
        )

        db.commit()

    def delete(self):
        db = get_db()

        query = 'DELETE FROM recipe WHERE id = ?'

        res = db.execute(
            query,
            (self.id,)
        )

        db.commit()

    @staticmethod
    def _apply_filters(
        query: str,
        user_id: int | None = None,
        vegetarian: bool | None = None
    ) -> tuple[str, list]:

        filters = []
        parameters = []

        if user_id is not None:
            filters.append('user_id = ?')
            parameters.append(user_id)

        if vegetarian == True:
            filters.append('vegetarian = ?')
            parameters.append(vegetarian)

        if len(filters) > 0:
            where = ' '.join(filters)
            query += ' WHERE ' + where
     
        return (query, parameters)

    @classmethod
    def _from_row(cls: Self, row: Row) -> Self:
        return cls(
            row['id'],
            row['user_id'],
            row['title'],
            row['description'],
            row['prepare'],
            row['cook'],
            row['serves'],
            bool(row['vegetarian']),
            row['tags'],
            datetime.fromisoformat(row['created'])
        )

    def as_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'prepare': self.prepare,
            'cook': self.cook,
            'serves': self.serves,
            'vegetarian': self.vegetarian,
            'tags': self.tags,
        }

@dataclass
class RecipePartModel(ListItemModel):
    id: int
    recipe_id: int

    position: int
    name: str

    @classmethod
    def insert(cls, recipe_id: int, position: int, name: str) -> Self | None:
        db = get_db()

        query = 'INSERT INTO recipe_part (recipe_id, position, name) VALUES (?, ?, ?)'

        res = db.execute(
            query,
            (recipe_id, position, name)
        )
        db.commit()

        return cls.select_one(res.lastrowid) if res else None

    @classmethod
    def select_one(cls, id: int) -> Self | None:
        db = get_db()

        query = 'SELECT * FROM recipe_part WHERE id = ?'

        cur = db.execute(
            query,
            (id,)
        )
        res = cur.fetchone()

        return cls._from_row(res) if res else None

    @classmethod
    def select_by_recipe_id(cls, recipe_id: int) -> list[Self]:
        db = get_db()

        query = 'SELECT * FROM recipe_part WHERE recipe_id = ?'

        cur = db.execute(
            query,
            (recipe_id,)
        )
        res = cur.fetchall()

        return list(map(cls._from_row, res))

    @staticmethod
    def count(parent_id: int) -> int:
        db = get_db()

        query = 'SELECT COUNT(*) FROM recipe_part WHERE recipe_id = ?'

        cur = db.execute(
            query,
            (parent_id,)
        )
        res = cur.fetchone()

        return res[0]

    def update(self):
        db = get_db()

        query = ('UPDATE recipe_part '
                 'SET position = ?, name = ? '
                 'WHERE id = ?')

        res = db.execute(
            query,
            (self.position, self.name, self.id)
        )
        db.commit()

    def delete(self):
        db = get_db()

        query = 'DELETE FROM recipe_part WHERE id = ?'

        res = db.execute(
            query,
            (self.id,)
        )
        db.commit()

    @classmethod
    def _from_row(cls, row: Row) -> Self:
        return cls(
            row['id'],
            row['recipe_id'],
            row['position'],
            row['name'],
        )

    def as_dict(self) -> dict:
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'position': self.position,
            'name': self.name,
        }

@dataclass
class RecipeIngredientModel(ListItemModel):
    id: int
    part_id: int

    position: int
    ingredient: str

    @classmethod
    def insert(cls, part_id: int, position: int, ingredient: str) -> Self | None:
        db = get_db()
    
        query = 'INSERT INTO recipe_ingredient (part_id, position, ingredient) VALUES (?, ?, ?)'
    
        res = db.execute(
            query,
            (part_id, position, ingredient)
        )
        db.commit()
    
        return cls.select_one(res.lastrowid) if res else None
    
    @classmethod
    def select_one(cls, id: int) -> Self | None:
        db = get_db()
    
        query = 'SELECT * FROM recipe_ingredient WHERE id = ?'
    
        cur = db.execute(
            query,
            (id,)
        )
        res = cur.fetchone()
    
        return cls._from_row(res) if res else None

    @classmethod
    def select_by_part_id(cls, part_id: int) -> list[Self]:
        db = get_db()

        query = 'SELECT * FROM recipe_ingredient WHERE part_id = ?'

        cur = db.execute(
            query,
            (part_id,)
        )
        res = cur.fetchall()

        return list(map(cls._from_row, res))

    @staticmethod
    def count(parent_id: int) -> int:
        db = get_db()

        query = 'SELECT COUNT(*) FROM recipe_ingredient WHERE part_id = ?'

        cur = db.execute(
            query,
            (parent_id,)
        )
        res = cur.fetchone()

        return res[0]
    
    def update(self):
        db = get_db()
    
        query = ('UPDATE recipe_ingredient '
                 'SET position = ?, ingredient = ? '
                 'WHERE id = ?')
    
        res = db.execute(
            query,
            (self.position, self.ingredient, self.id)
        )
        db.commit()
    
    def delete(self):
        db = get_db()
    
        query = 'DELETE FROM recipe_part WHERE id = ?'
    
        res = db.execute(
            query,
            (self.id,)
        )
        db.commit()

    @classmethod
    def _from_row(cls, row: Row) -> Self:
        return cls(
            row['id'],
            row['part_id'],
            row['position'],
            row['ingredient'],
        )
    
    def as_dict(self) -> dict:
        return {
            'id': self.id,
            'part_id': self.part_id,
            'position': self.position,
            'ingredient': self.ingredient,
        }

@dataclass
class RecipeInstructionModel(ListItemModel):
    id: int
    recipe_id: int

    position: int
    instruction: str

    @classmethod
    def insert(cls, recipe_id: int, position: int, instruction: str) -> Self | None:
        db = get_db()
    
        query = 'INSERT INTO recipe_instruction (recipe_id, position, instruction) VALUES (?, ?, ?)'
    
        res = db.execute(
            query,
            (recipe_id, position, instruction)
        )
        db.commit()
    
        return cls.select_one(res.lastrowid) if res else None
    
    @classmethod
    def select_one(cls, id: int) -> Self | None:
        db = get_db()
    
        query = 'SELECT * FROM recipe_instruction WHERE id = ?'
    
        cur = db.execute(
            query,
            (id,)
        )
        res = cur.fetchone()
    
        return cls._from_row(res) if res else None

    @staticmethod
    def count(parent_id: int) -> int:
        db = get_db()

        query = 'SELECT COUNT(*) FROM recipe_instruction WHERE recipe_id = ?'

        cur = db.execute(
            query,
            (parent_id,)
        )
        res = cur.fetchone()

        return res[0]

    def update(self):
        db = get_db()
    
        query = ('UPDATE recipe_instruction '
                 'SET position = ?, instruction = ? '
                 'WHERE id = ?')
    
        res = db.execute(
            query,
            (self.position, self.instruction, self.id)
        )
        db.commit()

    @classmethod
    def select_by_recipe_id(cls, recipe_id: int) -> list[Self]:
        db = get_db()

        query = ('SELECT * FROM recipe_instruction '
                 'WHERE recipe_id = ? '
                 'ORDER BY position ASC')

        cur = db.execute(
            query,
            (recipe_id,)
        )
        res = cur.fetchall()

        return list(map(cls._from_row, res))
    
    def delete(self):
        db = get_db()
    
        query = 'DELETE FROM recipe_part WHERE id = ?'
    
        res = db.execute(
            query,
            (self.id,)
        )
        db.commit()

    @classmethod
    def _from_row(cls, row: Row) -> Self:
        return cls(
            row['id'],
            row['recipe_id'],
            row['position'],
            row['instruction'],
        )
    
    def as_dict(self) -> dict:
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'position': self.position,
            'instruction': self.instruction,
        }

class RecipePhotoModel(Model):
    id: int
    recipe_id: int

    position: int
    photo_uri: str

    @classmethod
    def insert(cls, recipe_id: int, position: int, photo_uri: str) -> Self | None:
        db = get_db()
    
        query = 'INSERT INTO recipe_photo (recipe_id, position, photo_uri) VALUES (?, ?, ?)'
    
        res = db.execute(
            query,
            (recipe_id, position, photo_uri)
        )
        db.commit()
    
        return cls.select_one(res.lastrowid) if res else None
    
    @classmethod
    def select_one(cls, id: int) -> Self | None:
        db = get_db()
    
        query = 'SELECT * FROM recipe_photo WHERE id = ?'
    
        cur = db.execute(
            query,
            (id,)
        )
        res = cur.fetchone()
    
        return cls._from_row(res) if res else None
    
    def update(self):
        db = get_db()
    
        query = ('UPDATE recipe_photo '
                 'SET position = ?, photo_uri = ? '
                 'WHERE id = ?')
    
        res = db.execute(
            query,
            (self.position, self.photo_uri, self.id)
        )
        db.commit()

    @classmethod
    def select_by_recipe_id(cls, recipe_id: int) -> list[Self]:
        db = get_db()

        query = 'SELECT * FROM recipe_photo WHERE recipe_id = ?'

        cur = db.execute(
            query,
            (recipe_id,)
        )
        res = cur.fetchall()

        return list(map(cls._from_row, res))

    @staticmethod
    def count(parent_id: int) -> int:
        db = get_db()

        query = 'SELECT COUNT(*) FROM recipe_photo WHERE recipe_id = ?'

        cur = db.execute(
            query,
            (parent_id,)
        )
        res = cur.fetchone()

        return res[0]
    
    def delete(self):
        db = get_db()
    
        query = 'DELETE FROM recipe_part WHERE id = ?'
    
        res = db.execute(
            query,
            (self.id,)
        )
        db.commit()

    @classmethod
    def _from_row(cls, row: Row) -> Self:
        return cls(
            row['id'],
            row['recipe_id'],
            row['position'],
            row['photo_uri'],
        )
    
    def as_dict(self) -> dict:
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'position': self.position,
            'photo_uri': self.photo_uri,
        }