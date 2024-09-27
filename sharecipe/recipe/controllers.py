from flask import g

from ..database import recipes, comments

def delete_comment(recipe_id, comment_id):
    comment = comments.find_one(comment_id)
    if comment is None:
        return False
    
    recipe = recipes.find_one(comment.recipe)
    if recipe is None:
        return False
    
    if recipe_id != recipe.id:
        return False
    
    if comment.user.id == g.user.id or recipe.user.id == g.user.id:
        comments.delete(comment_id)
        return True

    return False