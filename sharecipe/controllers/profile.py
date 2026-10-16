from typing import Self

from . import Controller
from ..models.profile import ProfileModel

class ProfileController(ProfileModel, Controller):
    @classmethod
    def create(cls, id: int, name: str) -> Self:
        return cls._insert(id, name)

    def update(self):
        return self._update()

    def delete(self):
        return self._delete()