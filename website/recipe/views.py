from datetime import datetime
from flask import abort, flash, g, redirect, render_template, request, url_for
from math import ceil
import re

from website.db import get_db
from website.util import login_required

from . import recipe_blueprint as bp

@bp.route('/')
def index():
    db = get_db()
    latest_recipes = None
    user_recipes = None

    latest_recipes = db.execute(
            'SELECT recipe.*, user.username FROM recipe INNER JOIN user ON recipe.user_id = user.user_id ORDER BY created DESC LIMIT 10'
            ).fetchall()

    if g.user:
        user_recipes = db.execute(
                'SELECT recipe.*, user.username FROM recipe INNER JOIN user ON recipe.user_id = user.user_id WHERE recipe.user_id = ? ORDER BY created DESC LIMIT 10',
                (g.user['user_id'],)
                ).fetchall()
    
    return render_template('recipe/index.html', latest_recipes=latest_recipes, user_recipes=user_recipes)

@bp.route('/<int:recipe_id>')
def view(recipe_id):
    db = get_db()

    recipe = db.execute(
            'SELECT recipe.*, username FROM recipe INNER JOIN user ON recipe.user_id = user.user_id WHERE recipe_id = ?',
            (recipe_id,)
            ).fetchone()

    if recipe is None:
        abort(404)

    ingredients = recipe['ingredients'].split('\n')
    method = [x.split('\n') for x in recipe['method'].split('\n\n')]
    tags = (recipe['tags'] or '').split(',')

    return render_template('recipe/view.html', recipe=recipe, ingredients=ingredients, method=method, tags=tags)

@bp.route('/search')
def search():
    params = request.args.copy()
    params.pop('page', None)
    params.pop('q', None)

    search = request.args.get('q', '').strip().lower()
    vegetarian = request.args.get('vegetarian') == 'vegetarian' or 'veg' in search
    user_id = request.args.get('user_id')

    recipes = None
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
        
        search = ' + '.join(['(tags LIKE ?) + (title LIKE ?) + (description LIKE ?)'] * len(keywords))
        query = f'SELECT recipe.*, user.username, ({search}) AS best_match FROM recipe INNER JOIN user ON recipe.user_id = user.user_id WHERE best_match > 0 AND (vegetarian = ? OR vegetarian = ?) AND (recipe.user_id = ? OR ?) ORDER BY best_match DESC LIMIT ? OFFSET ?'

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
    db = get_db()

    params = request.args.copy()
    params.pop('page', None)
    
    vegetarian = request.args.get('vegetarian') == 'vegetarian'
    user_id = request.args.get('user_id')
    username = None

    count = int(db.execute(
            'SELECT COUNT(*) FROM recipe WHERE recipe.user_id = ? OR ?',
            (user_id, not user_id)
            ).fetchone()[0])
    
    page = int(request.args.get('page')) if request.args.get('page', '').isnumeric() else 1
    limit = 60
    pages = ceil(count / limit)

    recipes = db.execute(
            'SELECT recipe.*, user.username FROM recipe INNER JOIN user ON recipe.user_id = user.user_id WHERE (vegetarian = ? OR vegetarian = ?) AND recipe.user_id = ? OR ? ORDER BY created DESC LIMIT ? OFFSET ?',
            (vegetarian, vegetarian + 1, user_id, not user_id, limit, ((page - 1) * limit))
            ).fetchall()

    if user_id:
        username = db.execute(
                'SELECT user.username FROM user WHERE user.user_id = ?',
                (user_id,)
                ).fetchone()[0]
    
    return render_template('recipe/latest.html', params=params, recipes=recipes, username=username, page=page, pages=pages, limit=limit, count=count)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    error = {}

    if request.method == 'POST':
        # open database
        db = get_db()
        
        data = process(request.form)
        error = validate(data, error)

        if not error:
            res = db.execute(
                    'INSERT INTO recipe (user_id, title, description, ingredients, method, time, difficulty, servings, vegetarian, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (g.user['user_id'], data['title'], data['description'], data['ingredients'], data['method'], data['time'], data['difficulty'], data['servings'], data['vegetarian'], data['tags'])
                    )
            db.commit()

            return redirect(url_for('recipe.view', recipe_id=res.lastrowid))
    return render_template('recipe/create.html', error=error)

@bp.route('/<int:recipe_id>/update', methods=('GET', 'POST'))
@login_required
def update(recipe_id):
    db = get_db()
    error = {}

    recipe = db.execute(
            'SELECT * FROM recipe WHERE recipe_id = ?',
            (recipe_id,)
            ).fetchone()

    if recipe is None:
        abort(404)
    elif g.user['user_id'] != recipe['user_id']:
        abort(403)

    if request.method == 'POST':
        data = process(request.form)
        error = validate(data, error)

        if not error:
            db.execute(
                    'UPDATE recipe SET title = ?, description = ?, ingredients = ?, method = ?, time = ?, difficulty = ?, servings = ?, vegetarian = ?, tags = ?, updated = datetime("now") WHERE recipe_id = ?',
                    (data['title'], data['description'], data['ingredients'], data['method'], data['time'], data['difficulty'], data['servings'], data['vegetarian'], data['tags'], recipe_id)
                    )
            db.commit()

            return redirect(url_for('recipe.view', recipe_id=recipe_id))
    return render_template('recipe/update.html', recipe=recipe, error=error)

@bp.route('/<int:recipe_id>/delete')
@login_required
def delete(recipe_id):
    db = get_db()

    recipe = db.execute(
            'SELECT * FROM recipe WHERE recipe_id = ?',
            (recipe_id,)
            ).fetchone()

    if recipe is None:
        abort(404)
    elif g.user['user_id'] != recipe['user_id']:
        abort(403)

    db.execute(
            'DELETE FROM recipe WHERE recipe_id = ?',
            (recipe_id,)
            )
    db.commit()

    return redirect(url_for('recipe.index'))

# change empty fields to None and remove return codes
def process(original):
    data = dict.fromkeys(('title', 'description', 'ingredients', 'method', 'time', 'difficulty', 'servings', 'vegetarian', 'tags', 'method', 'ingredients'), '')
    data.update({key: value.strip().replace('\r', '') for key, value in original.items()})

    data['tags'] = None if not data['tags'] else re.sub('[^a-z,]', '', data['tags'].lower())
    data['vegetarian'] = True if data['vegetarian'] else False

    return data

# validate data
def validate(data, error):
    if not data['title']:
        error['title'] = 'Title is required.'
    elif len(data['title']) > 100:
        error['title'] = 'Title cannot be more than 100 characters.'
    
    if not data['description']:
        pass
    elif len(data['description']) > 200:
        error['description'] = 'Description cannot be more than 400 characters.'
    
    if not data['ingredients']:
        error['ingredients'] = 'Ingredients are required.'
    elif len(data['ingredients']) > 1000:
        error['ingredients'] = 'Ingredients cannot be more than 1000 characters.'

    if not data['method']:
        error['method'] = 'Method is required.'
    elif len(data['method']) > 4000:
        error['method'] = 'Method cannot be more than 4000 characters.'
    
    if not data['time']:
        pass
    elif not data['time'].isnumeric():
        error['time'] = 'Time must be a number.'
    elif int(data['time']) <= 0:
        error['time'] = 'Time must be greater than 0.'

    if not data['difficulty']:
        pass
    elif not data['difficulty'].isnumeric():
        error['difficulty'] = 'Difficulty must be a number.'
    elif int(data['difficulty']) < 1 or int(data['difficulty']) > 3:
        error['difficulty'] = 'Difficulty must be between 1 and 3.'

    if not data['servings']:
        pass
    elif not data['servings'].isnumeric():
        error['servings'] = 'Servings must be a number.'
    elif int(data['servings']) <= 0:
        error['servings'] = 'Servings must be greater than 0.'
    
    if not data['tags']:
        pass
    elif len(data['tags']) > 100:
        error['tags'] = 'Tags cannot be more than 100 characters.'

    return error
