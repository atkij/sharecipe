from dataclasses import asdict
from datetime import datetime
from flask import abort, current_app, flash, g, redirect, render_template, request, url_for
from math import ceil
from random import randint
import os
import re
import uuid

from sharecipe.database.database import get_db
from sharecipe.util import resize_image
from sharecipe.auth.helpers import login_required

from ..database import profiles, recipes, comments

from . import recipe_blueprint as bp
from .forms import FavouriteForm, RecipeForm, RateForm, PhotoForm, DeleteForm, CommentForm
from . import controllers

@bp.route('/')
def index():
    latest_recipes = recipes.find()
    
    user_recipes = None
    favourite_recipes = None
    if g.user:
        user_recipes = recipes.find(user_id=g.user.id)
        favourite_recipes = recipes.find(favourite_id=g.user.id)

    return render_template('recipe/index.html',
        latest_recipes=latest_recipes,
        user_recipes=user_recipes,
        favourite_recipes=favourite_recipes
    )

@bp.route('/<int:recipe_id>')
def view(recipe_id):
    recipe = recipes.find_one(recipe_id, g.user.id if g.user else None)

    if recipe is None:
        abort(404)

    return render_template('recipe/view.html',
        recipe=recipe,
        upload_photo_form=PhotoForm(),
        delete_photo_form=DeleteForm(),
        favourite_form=FavouriteForm(),
        rate_form=RateForm(),
        delete_form=DeleteForm(),
        comment_form=CommentForm(),
    )

@bp.route('/<int:recipe_id>/rate', methods=('GET', 'POST'))
@login_required
def rate(recipe_id):
    form = RateForm(request.form)

    if request.method == 'POST' and form.validate():
        recipe = recipes.find_details(recipe_id)

        if g.user.id == recipe.user.id:
            flash('You cannot rate your own recipe.', 'error')
            return redirect(url_for('recipe.view', recipe_id=recipe_id))

        recipes.rate(g.user.id, recipe.id, form.rating.data)

    return redirect(url_for('recipe.view', recipe_id=recipe_id))

@bp.route('/<int:recipe_id>/favourite', methods=('GET', 'POST'))
@login_required
def favourite(recipe_id):
    form = FavouriteForm(request.form)

    if request.method == 'POST' and form.validate():
        recipe = recipes.find_one(recipe_id, g.user.id)

        if not recipe.favourite:
            recipes.favourite(g.user.id, recipe_id)
            flash('Recipe added to favourites.', 'success')
    
    return redirect(url_for('recipe.view', recipe_id=recipe_id))

@bp.route('/<int:recipe_id>/unfavourite', methods=('GET', 'POST'))
@login_required
def unfavourite(recipe_id):
    form = FavouriteForm(request.form)

    if request.method == 'POST' and form.validate():
        recipe = recipes.find_one(recipe_id, g.user.id)

        if recipe.favourite:
            recipes.unfavourite(g.user.id, recipe_id)
            flash('Recipe removed from favourites.', 'success')
    
    return redirect(url_for('recipe.view', recipe_id=recipe_id))

@bp.route('/<int:recipe_id>/comment', methods=('GET', 'POST'))
@login_required
def comment(recipe_id):
    form = CommentForm(request.form)

    if request.method == 'POST' and form.validate():
        comments.create(g.user.id, recipe_id, form.comment.data)
        flash('New comment added.', 'success')
    
    return redirect(url_for('recipe.view', recipe_id=recipe_id))

@bp.route('/<int:recipe_id>/comment/<int:comment_id>/delete', methods=('GET', 'POST'))
@login_required
def delete_comment(recipe_id, comment_id):
    form = DeleteForm(request.form)

    if request.method == 'POST' and form.validate():
        if controllers.delete_comment(recipe_id, comment_id):
            flash('Comment deleted.', 'success')

    return redirect(url_for('recipe.view', recipe_id=recipe_id))

@bp.route('/search')
def search():
    params = request.args.copy()
    params.pop('page', None)
    params.pop('q', None)

    search = request.args.get('q', '').strip().lower()
    vegetarian = request.args.get('vegetarian') == 'vegetarian' or 'veg' in search
    user_id = request.args.get('user_id')

    recipess = None
    count = int()
    page = int()
    pages = int()
    limit = 60
    
    if len(search) > 100:
        flash('Queries are restricted to 100 characters maximum.')

    if search:
        keywords = search[:100].split(' ')
        keywords = list(map(lambda w: '%'+w+'%', keywords))

        db = get_db()
        
        search = ' + '.join(['(tags IS NOT NULL AND tags LIKE ?) + (title LIKE ?) + (description IS NOT NULL AND description LIKE ?)'] * len(keywords))
        query = f'SELECT recipe.*, user.*, ({search}) AS best_match FROM recipe INNER JOIN user ON recipe.user_id = user.user_id WHERE best_match > 0 AND (vegetarian = ? OR vegetarian = ?) AND (recipe.user_id = ? OR ?) ORDER BY best_match DESC LIMIT ? OFFSET ?'

        keywords = [i for i in keywords for _ in (0, 1, 2)]

        recipes = db.execute(query, (*keywords, vegetarian, vegetarian + 1, user_id, not user_id, limit, ((page - 1) * limit))).fetchall()
        
        count = int(db.execute(
                f'SELECT COUNT(*) FROM recipe WHERE ({search}) > 0 AND (recipe.user_id = ? OR ?)',
                (*keywords, user_id, not user_id)
                ).fetchone()[0])

        page = int(request.args.get('page')) if request.args.get('page', '').isnumeric() else 1
        pages = ceil(count / limit)

    return render_template('recipe/search.html', params=params, recipes=recipes, page=page, pages=pages, limit=limit, count=count)

@bp.route('/latest')
def latest():   
    user_id = request.args.get('user_id')
    favourite_id = request.args.get('favourite_id')
    vegetarian = request.args.get('vegetarian')

    count = recipes.count(user_id, favourite_id, vegetarian)
    page = request.args.get('page', 1, type=int)
    limit = 60
    offset = (page - 1) * limit
    pages = ceil(count / limit)

    latest_recipes = recipes.find(user_id, favourite_id, vegetarian, limit, offset)
    profile = profiles.find(user_id)

    return render_template('recipe/latest.html',
        latest_recipes=latest_recipes,
        profile=profile,
        filters={
            'user_id': user_id,
            'favourite_id': favourite_id,
            'vegetarian': vegetarian
        },
        pagination={
            'page': page,
            'pages': pages,
            'count': count,
            'limit': limit,
            'offset': offset
        }
    )

@bp.route('/random')
def random():
    count = recipes.count()

    return redirect(url_for('recipe.view', recipe_id=randint(1, count)))

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    form = RecipeForm(request.form)

    if request.method == 'POST' and form.validate():
        recipe_id = recipes.create(
            g.user.id,
            form.title.data,
            form.description.data,
            form.time.data,
            form.difficulty.data,
            form.servings.data,
            form.vegetarian.data,
            form.ingredients.data.split('\r\n'),
            form.method.data.split('\r\n\r\n'),
            form.tags.data.split(',')
        )

        return redirect(url_for('recipe.view', recipe_id=recipe_id))
    return render_template('recipe/create.html', form=form)

@bp.route('/<int:recipe_id>/update', methods=('GET', 'POST'))
@login_required
def update(recipe_id):
    recipe = recipes.find_one(recipe_id)

    if recipe is None:
        abort(404)
    elif g.user.id != recipe.user.id:
        abort(403)
    
    data = asdict(recipe)
    data['ingredients'] = '\r\n'.join(data['ingredients'])
    data['method'] = '\r\n\r\n'.join(data['method'])
    data['tags'] = ','.join(data['tags'])

    form = RecipeForm(request.form, data=data)
    form.vegetarian.data = recipe.vegetarian

    if request.method == 'POST' and form.validate():
        recipes.update(
            recipe_id,
            form.title.data,
            form.description.data,
            form.time.data,
            form.difficulty.data,
            form.servings.data,
            form.vegetarian.data,
            form.ingredients.data.split('\r\n'),
            form.method.data.split('\r\n\r\n'),
            form.tags.data.split(',')
        )

        return redirect(url_for('recipe.view', recipe_id=recipe_id))
    return render_template('recipe/update.html', form=form)

@bp.route('/<int:recipe_id>/delete', methods=('GET', 'POST'))
@login_required
def delete(recipe_id):
    form = DeleteForm()
    
    recipe = recipes.find_details(recipe_id)

    if recipe is None:
        abort(404)
    elif g.user.id != recipe.user.id:
        abort(403)

    if request.method == 'POST' and form.validate():
        if recipe.photo is not None:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], recipe.photo))

        recipes.delete(recipe_id)

        flash('Recipe deleted successfully.', 'success')
        return redirect(url_for('recipe.index'))
    else:
        flash('Unable to delete recipe.', 'error')
        return redirect(url_for('recipe.view', recipe_id=recipe_id))

@bp.route('/<int:recipe_id>/photo/upload', methods=('GET','POST'))
@login_required
def upload_photo(recipe_id):
    form = PhotoForm()
    recipe = recipes.find_details(recipe_id)
    
    if recipe is None:
        abort(404)
    elif g.user.id != recipe.user.id:
        abort(403)

    if request.method == 'POST' and form.validate():
        if recipe.photo is not None:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], recipe.photo))

        photo = form.photo.data
        filename = str(uuid.uuid4()) + '.' + photo.filename.split('.')[-1]

        photo = resize_image(photo.stream, 1024)
        if photo is None:
            flash('Unsupported image format.', 'error')
            return redirect(url_for('recipe.view', recipe_id=recipe_id))
        
        photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        recipes.photo(recipe_id, filename)

        flash('Photo uploaded successfully.', 'success')
    else:
        for error in form.photo.errors:
            flash(error, 'error')

    return redirect(url_for('recipe.view', recipe_id=recipe_id))

@bp.route('/<int:recipe_id>/photo/delete', methods=('GET', 'POST'))
@login_required
def delete_photo(recipe_id):
    form = DeleteForm(request.form)
    recipe = recipes.find_details(recipe_id)

    if recipe is None:
        abort(404)
    elif g.user.id != recipe.user.id:
        abort(403)

    if request.method == 'POST' and form.validate():
        if recipe.photo is not None:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], recipe.photo))

            recipes.photo(recipe_id, None)

            flash('Photo deleted successfully.', 'success')
        else:
            flash('No photo to delete.', 'error')
    else:
        flash('Unable to delete photo.', 'error')

    return redirect(url_for('recipe.view', recipe_id=recipe_id))
