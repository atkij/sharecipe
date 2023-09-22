import functools
import hashlib
from PIL import Image, UnidentifiedImageError
import os
import time

from flask import abort, current_app, g, redirect, session, url_for

def _hash_internal(password, salt, n=16384, r=8, p=1):
    maxmem = 132 * n * r * p
    password = password.encode('utf-8')

    h = hashlib.scrypt(password, salt=salt, n=n, r=r, p=p, maxmem=maxmem).hex()

    return (h, f'scrypt:{n}:{r}:{p}')

def generate_password_hash(password):
    salt = os.urandom(16)
    hashval, method = _hash_internal(password, salt)
    return f'{method}${salt.hex()}${hashval}'

def check_password_hash(password_hash, password):
    method, salt, hashval = password_hash.split('$', 2)
    _, n, r, p = method.split(':', 3)

    salt = bytes.fromhex(salt)
    n, r, p = map(int, (n, r, p))

    return hashval == _hash_internal(password, salt, n=n, r=r, p=p)[0]

def name_filter(user):
    return user['name'] if user['name'] else user['username']

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped_view

def resize_image(stream, size):
    try:
        img = Image.open(stream)

        if img.size[0] <= size and img.size[1] <= size:
            return img

        if img.size[0] > img.size[1]:
            return img.resize((size, int((size / img.size[0]) * img.size[1])))
        else:
            return img.resize((int((size / img.size[1]) * img.size[0]), size))
    except UnidentifiedImageError:
        return None
