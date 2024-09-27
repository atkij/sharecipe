from sharecipe.database.models import UserBase, RecipeBase

def parse_recipe(recipe: dict) -> RecipeBase:
    return RecipeBase(
        id = recipe['recipe_id'],
        user = parse_user(recipe),
        title = recipe['title'],
        description = recipe['description'],
        time = recipe['time'],
        difficulty = recipe['difficulty'],
        servings = recipe['servings'],
        vegetarian = recipe['vegetarian']
    )

def parse_user(user: dict) -> UserBase:
    return UserBase(
        id = user['user_id'],
        username = user['username'],
        name = user['name'],
        picture = user['picture']
    )