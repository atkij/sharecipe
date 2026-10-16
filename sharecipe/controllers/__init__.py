from typing import Self

from ..models import ListItemModel

class Controller:
    pass

class ListItemController(ListItemModel, Controller):
    @classmethod
    def append(cls, parent_id: int, *args) -> Self | None:
        position = cls.count(parent_id)
        return cls.insert(parent_id, position, *args)