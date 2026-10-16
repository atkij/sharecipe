from typing import Self
from sqlite3 import Row

class Model:
    @classmethod
    def insert(cls) -> Self | None:
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError
    
    @classmethod
    def _from_row(cls, row: Row) -> Self:
        raise NotImplementedError

    def as_dict(self) -> dict:
        raise NotImplementedError

class ListItemModel(Model):
    @classmethod
    def insert(cls, parent_id: int, position: int, *args) -> Self | None:
        raise NotImplementedError

    @staticmethod
    def count(parent_id: int) -> int:
        raise NotImplementedError