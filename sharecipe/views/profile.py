from flask import abort, Blueprint, g, redirect, render_template, url_for

from ..controllers.profile import ProfileController


bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/<int:id>')
def index(id):
    profile = ProfileController.select_one(id)

    if profile is None:
        abort(404)

    latest_recipes = []#recipes.find(user_id=id)
    starred_recipes = []#recipes.find(star_id=id)

    return render_template('profile/index.html',
        profile=profile,
        latest_recipes=latest_recipes,
        starred_recipes=starred_recipes
    )
