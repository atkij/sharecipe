from datetime import datetime
from flask import abort, g, redirect, render_template, request, url_for
import re

from website.db import get_db
from website.util import login_required

from . import recipe_blueprint as bp

@bp.route('/')
def index():
    return render_template('recipe/index.html')

@bp.route('/<int:recipe_id>')
def view(recipe_id):
    if recipe_id is None:
        abort(404)

    db = get_db()

    recipe = db.execute(
            'SELECT recipe.*, username FROM recipe INNER JOIN user ON recipe.user_id = user.user_id WHERE recipe_id = ?',
            (recipe_id,)
            ).fetchone()

    if recipe is None:
        abort(404)

    ingredients = recipe['ingredients'].split('\n')
    method = [x.split('\n') for x in recipe['method'].split('\n\n')]
    tags = recipe['tags'].split(',')

    return render_template('recipe/view.html', recipe=recipe, ingredients=ingredients, method=method, tags=tags)

@bp.route('/create', methods=('GET', 'POST'))
@login_required()
def create():
    if request.method == 'POST':
        # collect form data
        title = str(request.form['title']).strip()
        ingredients = str(request.form['ingredients']).strip().replace('\r', '')
        method = str(request.form['method']).strip().replace('\r', '')
        time = str(request.form['time'])
        difficulty = str(request.form['difficulty'])
        servings = str(request.form['servings'])
        tags = str(request.form['tags']).strip().lower()
        
        # process form data
        tags = re.sub('[^a-z,]', '', tags)
        
        # open database
        db = get_db()
        error = None

        # validate data
        if not time.isnumeric() and int(time) > 0:
            error = 'Time must be a valid number.'
        elif not difficulty.isnumeric() and 0 < int(difficulty) < 6:
            error = 'Difficulty must be a valid number.'
        elif not servings.isnumeric() and int(servings) > 0:
            error = 'Servings must be a valid number.'

        if error is None:
            res = db.execute(
                    'INSERT INTO recipe (user_id, title, ingredients, method, time, difficulty, servings, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (g.user['user_id'], title, ingredients, method, time, difficulty, servings, tags,)
                    )
            db.commit()

            return redirect(url_for('recipe.view', recipe_id=res.lastrowid))

        flash(error)

    return render_template('recipe/create.html')
