from flask import Blueprint, render_template

from ..database import recipes

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    #db = get_db()
    #latest_recipes = None
    #top_chefs = None

    #latest_recipes = db.execute(
    #        'SELECT recipe.*, user.* FROM recipe INNER JOIN user ON recipe.user_id = user.user_id ORDER BY created DESC LIMIT 10'
    #        ).fetchall()

    #top_chefs = db.execute(
    #        'SELECT user.* FROM user INNER JOIN follower ON user.user_id = follower.user_id INNER JOIN recipe ON user.user_id = recipe.user_id GROUP BY user.user_id ORDER BY COUNT(follower.follower_id) * COUNT(recipe.recipe_id) DESC LIMIT 10'
    #        ).fetchall()

    latest_recipes = recipes.find()

    return render_template('main/index.html', latest_recipes=latest_recipes)

@bp.route('/about')
def about():
    return render_template('main/about.html')