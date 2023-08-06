from datetime import datetime
from flask import abort, flash, g, redirect, render_template, request, url_for
import re

from website.db import get_db
from website.util import login_required

from . import recipe_blueprint as bp

@bp.route('/')
def index():
    return render_template('recipe/index.html')

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
    search = request.args.get('q', '').strip()
    recipes = None

    if search:
        keywords = search[:100].split(' ')
        keywords = list(map(lambda w: '%'+w+'%', keywords))

        db = get_db()
        query = 'SELECT recipe.*, (' + ' + '.join(['(tags LIKE ?)']*len(keywords)) + ') AS best_match FROM recipe ORDER BY best_match DESC LIMIT 10'
        print(query)
        print(keywords)

        recipes = db.execute(query, keywords).fetchall()

    if len(search) > 100:
        flash('Queries are restricted to 100 characters maximum.')

    return render_template('recipe/search.html', recipes=recipes)

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
            tags = None if not data['tags'] else re.sub('[^a-z,]', '', data['tags'].lower())

            res = db.execute(
                    'INSERT INTO recipe (user_id, title, description, ingredients, method, time, difficulty, servings, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (g.user['user_id'], data['title'], data['description'], data['ingredients'], data['method'], data['time'], data['difficulty'], data['servings'], tags,)
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
            tags = None if not data['tags'] else re.sub('[^a-z,]', '', data['tags'].lower())

            db.execute(
                    'UPDATE recipe SET title = ?, description = ?, ingredients = ?, method = ?, time = ?, difficulty = ?, servings = ?, tags = ?, updated = datetime("now") WHERE recipe_id = ?',
                    (data['title'], data['description'], data['ingredients'], data['method'], data['time'], data['difficulty'], data['servings'], tags, recipe_id,)
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
def process(data):
    data = {key: value.strip().replace('\r', '') for key, value in data.items()}
    return data

# validate data
def validate(data, error):
    if not data['title']:
        error['title'] = 'Title is required.'
    elif len(data['title'].strip()) > 50:
        error['title'] = 'Title cannot be more than 50 characters.'
    
    if not data['description']:
        pass
    elif len(data['description'].strip()) > 200:
        error['description'] = 'Description cannot be more than 400 characters.'
    
    if not data['ingredients']:
        error['ingredients'] = 'Ingredients are required.'
    elif len(data['ingredients']) > 200:
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
    elif int(data['difficulty']) < 1 or int(data['difficulty']) > 5:
        error['difficulty'] = 'Difficulty must be between 1 and 5.'

    if not data['servings']:
        pass
    elif not data['servings'].isnumeric():
        error['servings'] = 'Servings must be a number.'
    elif int(data['servings']) <= 0:
        error['servings'] = 'Servings must be greater than 0.'

    if not data['tags']:
        pass
    elif len(data['tags'].strip()) > 100:
        error['tags'] = 'Tags cannot be more than 100 characters.'

    return error
