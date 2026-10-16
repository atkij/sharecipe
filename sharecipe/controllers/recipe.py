from typing import Self, Type

from flask import current_app, g
from werkzeug.datastructures import FileStorage

from ..database import recipes
from ..core.media import upload_media, delete_media

from . import Controller, ListItemController
from .profile import ProfileController
from ..models.recipe import RecipeModel, RecipePartModel, RecipeIngredientModel, RecipeInstructionModel, RecipePhotoModel

class RecipeIngredientController(RecipeIngredientModel, ListItemController):
    pass

class RecipePartController(RecipePartModel, ListItemController):
    @property
    def ingredients(self) -> list[RecipeIngredientController]:
        return RecipeIngredientController.select_by_part_id(self.id)

class RecipeInstructionController(RecipeInstructionModel, ListItemController):
    pass

class RecipePhotoController(RecipePhotoModel, Controller):
    @classmethod
    def insert(cls, recipe_id: int, position: int, photo: FileStorage) -> Self | None:
        recipe = RecipeController.select_one(recipe_id)
        
        if recipe is None:
            return None

        filename = upload_media(photo.stream)

        # photos = cls.select_by_recipe_id(recipe_id)
        # position = len(photos)

        return super().insert(recipe_id, position, filename)    

    def delete(self):
        delete_media(self.photo_uri)
        return self._delete()

class RecipeController(RecipeModel, Controller):
    @property
    def parts(self) -> list[RecipePartController]:
        return RecipePartController.select_by_recipe_id(self.id)

    @property
    def method(self) -> list[RecipeInstructionController]:
        return RecipeInstructionController.select_by_recipe_id(self.id)

    @property
    def photos(self) -> list[RecipePhotoController]:
        return RecipePhotoController.select_by_recipe_id(self.id)

    @property
    def profile(self) -> ProfileController:
        return ProfileController.select_one(self.user_id)
    
    def delete(self):
        photos = RecipePhotoController.select_by_recipe_id(self.id)

        for photo in photos:
            photo.delete()
        
        return super().delete()  

