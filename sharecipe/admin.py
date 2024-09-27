import click
from flask import current_app, g
from sqlite3 import IntegrityError

from sharecipe.database.database import get_db
from sharecipe.util import generate_password_hash

def register(name, help=None):
    def decorator(func):
        func.name = name
        func.help = help
        return func
    return decorator

class Command:
    def __init__(self):
        self.commands = {}
        for name in dir(self):
            func = getattr(self, name)
            if 'name' in dir(func):
                self.commands[func.name] = func

    def __call__(self, command=None, *args):
        if command is None:
            return self.help()

        if command not in self.commands:
            print(f'Command not found: {command}')
            return self.help()
        
        try:
            return self.commands[command](*args)
        except TypeError:
            print('Incorrect arguments supplied.')
            return 1
        except Exception as e:
            print(e)
            return 1

    @register('help')
    def help(self):
        print('Available commands:')
        for name in self.commands:
            print(f'  {name}')
            if self.commands[name].help:
                print(f'    {self.commands[name].help}')
        return 0

class Prompt:
    def __init__(self):
        self.commands = {'quit': lambda: 2, 'exit': lambda: 2, 'commit': self.commit}

    def run(self):
        while True:
            try:
                prompt = input('> ').strip().split(' ')
                command = prompt[0]
                args = prompt[1:]

                code = 0

                if command not in self.commands:
                    print(f'Command not found: {command}')
                    code = 1
                else:
                    code = self.commands[command](*args)

                if code == 2:
                    break
            except KeyboardInterrupt as e:
                print('')
                pass

        print('Exiting...')

    def commit(self):
        db = get_db()
        db.commit()
        print('Database changes committed.')
        return 0

    def register(self, name):
        def decorator(func):
            self.commands[name] = func()
            return func
        return decorator

prompt = Prompt()

@prompt.register('user')
class User(Command):
    @register('add', 'username, email, password')
    def add(self, username, email, password):
        db = get_db()
        
        res = db.execute(
                'INSERT INTO user (username, email, password, name, bio) VALUES (?, ?, ?)',
                (username, email, generate_password_hash(password))
                )

        print(f'Added user {res.lastrowid}')
        return 0

    @register('get', 'user id')
    def get(self, user_id):
        db = get_db()

        res = db.execute(
                'SELECT * FROM user WHERE user_id = ?',
                (user_id,)
                ).fetchone()

        for field in dict(res):
            print(f'{field}: {res[field]}')

        return 0

    @register('set', 'user id, field, value')
    def set(self, user_id, field, value):
        if field == 'password':
            value = generate_password_hash(value)

        db = get_db()

        res = db.execute(
                f'UPDATE user SET {field} = ? WHERE user_id = ?',
                (value, user_id)
                )

        print(f'Updated user {user_id}')
        return 0

    @register('delete', 'user id')
    def delete(self, user_id):
        db = get_db()

        res = db.execute(
                'DELETE FROM user WHERE user_id = ?',
                (user_id,)
                )

        print(f'Deleted user {user_id}')
        return 0

    @register('follow', 'user id, user to follow id')
    def follow(self, follower_id, user_id):
        db = get_db()
        
        res = db.execute(
                'INSERT INTO follower (user_id, follower_id) VALUES (?, ?)',
                (user_id, follower_id)
                )

        print(f'User {follower_id} now follows user {user_id}')
        return 0

    @register('unfollow', 'user id, user to unfollow id')
    def unfollow(self, follower_id, user_id):
        db = get_db()

        res = db.execute(
                'DELETE FROM follower WHERE user_id = ? AND follower_id = ?',
                (user_id, follower_id)
                )

        print(f'User {follower_id} no longer follows user {user_id}')
        return 0

@click.command('admin')
def admin_command():
    prompt.run()
    return

def init_app(app):
    app.cli.add_command(admin_command)
