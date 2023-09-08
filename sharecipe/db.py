import sqlite3

import click
from flask import current_app, g

# access the database
def get_db():
    if 'db' not in g:
        # connect to database if not already connected
        g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
                )
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = 1')

    return g.db

# close the database
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# initialise a new database
def init_db():
    db = get_db()

    # write tables
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))

@click.command('init-db')
def init_db_command():
    # clear existing data and create new tables
    init_db()
    click.echo('Initialised the databse.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
