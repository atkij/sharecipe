from flask import abort, g, redirect, render_template, url_for

from ..auth.helpers import login_required
from ..database import profiles, recipes

from . import user_blueprint

@user_blueprint.route('/<int:user_id>')
def index(user_id):
    profile = profiles.find(user_id)

    if profile is None:
        abort(404)

    following = profiles.find_following(user_id)
    followers = profiles.find_followers(user_id)
    latest_recipes = recipes.find(user_id=user_id)
    favourite_recipes = recipes.find(favourite_id=user_id)

    follows = None
    if g.user is not None and g.user.id != user_id:
        follows = profiles.follows(user_id, g.user.id)

    return render_template('user/index.html',
        profile=profile,
        follows=follows,
        following=following,
        followers=followers,
        latest_recipes=latest_recipes,
        favourite_recipes=favourite_recipes
    )

@user_blueprint.route('/<int:user_id>/follow')
@login_required
def follow(user_id):
    if not (g.user is None or g.user.id == user_id or profiles.follows(user_id, g.user.id)):
        profiles.follow(user_id, g.user.id)

    return redirect(url_for('user.index', user_id=user_id)) 

@user_blueprint.route('/<int:user_id>/unfollow')
@login_required
def unfollow(user_id):
    if not (g.user is None or g.user.id == user_id or not profiles.follows(user_id, g.user.id)):
        profiles.unfollow(user_id, g.user.id)

    return redirect(url_for('user.index', user_id=user_id))
