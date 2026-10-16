from dataclasses import asdict
from math import ceil
from random import randint

from flask import abort, Blueprint, flash, g, redirect, render_template, request, url_for

from ..controllers.recipe import RecipeController, RecipePartController, RecipeIngredientModel, RecipeInstructionController, RecipePhotoController
from ..controllers.profile import ProfileController

from ..core.auth import login_required
from ..core.media import UnsupportedMediaError
from ..forms.recipe import StarForm, RecipeForm, PhotoForm, DeleteForm

bp = Blueprint('recipe', __name__, url_prefix='/recipe')

@bp.route('/')
def index():
    latest_recipes = RecipeController.select_by_filter()
    
    user_recipes = None
    starred_recipes = None
    if g.user:
        user_recipes = RecipeController.select_by_filter(user_id=g.user.id)
        #starred_recipes = recipes.find(star_id=g.user.id)
        pass

    return render_template('recipe/index.html',
        latest_recipes=latest_recipes,
        user_recipes=user_recipes,
        starred_recipes=starred_recipes
    )

@bp.route('/<int:recipe_id>')
def view(recipe_id):
    recipe = RecipeController.select_one(recipe_id)

    if recipe is None:
        abort(404)

    profile = ProfileController.select_one(recipe.user_id)

    return render_template('recipe/view.html',
        recipe=recipe,
        profile=profile,
        # upload_photo_form=PhotoForm(),
        # delete_photo_form=DeleteForm(),
        star_form=StarForm(),
        delete_form=DeleteForm(),
    )

@bp.route('/<int:recipe_id>/star', methods=('GET', 'POST'))
@login_required
def star(recipe_id):
    form = StarForm(request.form)

    if request.method == 'POST' and form.validate():
        recipe = RecipeController.select_one(recipe_id)

        if not recipe.star:
            #recipes.star(g.user.id, recipe_id)
            flash('Recipe added to starred.', 'success')
    
    return redirect(url_for('recipe.view', recipe_id=recipe_id))

@bp.route('/<int:recipe_id>/unstar', methods=('GET', 'POST'))
@login_required
def unstar(recipe_id):
    form = StarForm(request.form)

    if request.method == 'POST' and form.validate():
        recipe = RecipeController.select_one(recipe_id)

        if recipe.star:
            #recipes.unstar(g.user.id, recipe_id)
            flash('Recipe removed from starred.', 'success')
    
    return redirect(url_for('recipe.view', recipe_id=recipe_id))


@bp.route('/search')
def search():
    abort(404)
    return
# @bp.route('/search')
# def search():
#     abort(404)
#     return
#     params = request.args.copy()
#     params.pop('page', None)
#     params.pop('q', None)

#     search = request.args.get('q', '').strip().lower()
#     vegetarian = request.args.get('vegetarian') == 'vegetarian' or 'veg' in search
#     user_id = request.args.get('user_id')

#     recipes = None
#     count = int()
#     page = int()
#     pages = int()
#     limit = 60
    
#     if len(search) > 100:
#         flash('Queries are restricted to 100 characters maximum.')

#     if search:
#         keywords = search[:100].split(' ')
#         keywords = list(map(lambda w: '%'+w+'%', keywords))

#         db = get_db()
        
#         search = ' + '.join(['(tags IS NOT NULL AND tags LIKE ?) + (title LIKE ?) + (description IS NOT NULL AND description LIKE ?)'] * len(keywords))
#         query = f'SELECT recipe.*, user.*, ({search}) AS best_match FROM recipe INNER JOIN user ON recipe.user_id = user.user_id WHERE best_match > 0 AND (vegetarian = ? OR vegetarian = ?) AND (recipe.user_id = ? OR ?) ORDER BY best_match DESC LIMIT ? OFFSET ?'

#         keywords = [i for i in keywords for _ in (0, 1, 2)]

#         recipes = db.execute(query, (*keywords, vegetarian, vegetarian + 1, user_id, not user_id, limit, ((page - 1) * limit))).fetchall()
        
#         count = int(db.execute(
#                 f'SELECT COUNT(*) FROM recipe WHERE ({search}) > 0 AND (recipe.user_id = ? OR ?)',
#                 (*keywords, user_id, not user_id)
#                 ).fetchone()[0])

#         page = int(request.args.get('page')) if request.args.get('page', '').isnumeric() else 1
#         pages = ceil(count / limit)

#     return render_template('recipe/search.html', params=params, recipes=recipes, page=page, pages=pages, limit=limit, count=count)

@bp.route('/latest')
def latest():   
    user_id = request.args.get('user_id')
    vegetarian = request.args.get('vegetarian')

    if user_id is not None:
        try:
            user_id = int(user_id)
        except ValueError:
            abort(400)
    if vegetarian is not None:
        try:
            vegetarian = bool(vegetarian)
        except ValueError:
            abort(400)

    count = RecipeController.count_by_filter(user_id, vegetarian)
    page = request.args.get('page', 1, type=int)
    limit = 60
    offset = (page - 1) * limit
    pages = ceil(count / limit)

    recipes = RecipeController.select_by_filter(user_id, vegetarian, limit, offset)
    profile = ProfileController.select_one(user_id)

    return render_template('recipe/latest.html',
        recipes=recipes,
        profile=profile,
        filters={
            'user_id': user_id,
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
    count = RecipeController.count_all()

    return redirect(url_for('recipe.view', recipe_id=randint(1, count)))

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    form = RecipeForm(request.form)

    if request.method == 'POST' and form.validate():
        recipe = RecipeController.insert(
            g.user.id,
            form.title.data,
            form.description.data,
            form.prepare.data,
            form.cook.data,
            form.serves.data,
            form.vegetarian.data,
            form.tags.data,
        )

        for part in form.parts:
            recipe_part = RecipePartController.append(recipe.id, part.name.data)
            for instruction in part:
                recipe_instruction = RecipeInstructionController.append(recipe_part.id, instruction.instruction.data)

        for instruction in form.method:
            recipe_instruction = RecipeInstructionController.append(recipe.id, instruction.instruction.data)

        return redirect(url_for('recipe.view', recipe_id=recipe.id))
    return render_template('recipe/create.html', form=form)

@bp.route('/<int:recipe_id>/update', methods=('GET', 'POST'))
@login_required
def update(recipe_id):
    recipe = RecipeController.select_one(recipe_id)

    if recipe is None:
        abort(404)
    if g.user.id != recipe.user_id:
        abort(403)

    data = recipe.as_dict()

    data['parts'] = []

    for part in recipe.parts:
        part_d = part.as_dict()
        part_d['ingredients'] = list(map(lambda x: x.as_dict(), part.ingredients))
        data['parts'].append(part_d)
    
    data['method'] = list(map(lambda x: x.as_dict(), recipe.method))

    form = RecipeForm(request.form, data=data)
    form.vegetarian.data = data['vegetarian']

    if request.method == 'POST' and form.validate():
        recipe.title = form.title.data
        recipe.description = form.description.data
        recipe.prepare = form.prepare.data
        recipe.cook = form.cook.data
        recipe.serves = form.serves.data
        recipe.vegetarian = form.vegetarian.data
        recipe.tags = form.tags.data

        recipe.update()

        return redirect(url_for('recipe.view', recipe_id=recipe_id))
    return render_template('recipe/update.html', form=form)

@bp.route('/<int:recipe_id>/delete', methods=('GET', 'POST'))
@login_required
def delete(recipe_id):
    form = DeleteForm()

    if request.method == 'POST' and form.validate():
        recipe = RecipeController.select_one(recipe_id)

        if recipe is None:
            abort(404)

        if recipe.user_id != g.user.id:
            abort(403)

        recipe.delete()
        
        flash('Recipe deleted', 'success')
        return redirect(url_for('recipe.index'))
        
    return redirect(url_for('recipe.view', recipe_id=recipe_id))

@bp.route('/<int:recipe_id>/photo/upload', methods=('GET','POST'))
@login_required
def upload_photo(recipe_id):
    abort(404)
    return
    form = PhotoForm()

    if request.method == 'POST' and form.validate():
        recipe = RecipeController.select_one(recipe_id)

        if recipe is None:
            abort(404)

        if recipe.user_id != g.user.id:
            abort(403)

        try:
            RecipePhotoController.insert(recipe_id, form.photo.data)
        except UnsupportedMediaError:
            flash('Unsupported image format', 'error')
        else:
            flash('Recipe photo updated', 'success')
    else:
        for error in form.photo.errors:
            flash(error, 'error')

    return redirect(url_for('recipe.view', recipe_id=recipe_id))

@bp.route('/<int:recipe_id>/photo/delete', methods=('GET', 'POST'))
@login_required
def delete_photo(recipe_id):
    abort(404)
    return
    form = DeleteForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            controllers.delete_photo(recipe_id)
        except controllers.RecipeNotFound:
            abort(404)
        except controllers.PermissionError:
            flash('Not your photo to delete', 'error')
        except controllers.PhotoNotFound:
            flash('No photo to delete', 'error')
        else:
            flash('Recipe photo deleted', 'success')
    
    return redirect(url_for('recipe.view', recipe_id=recipe_id))
