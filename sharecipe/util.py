import functools
import hashlib
from PIL import Image, UnidentifiedImageError
import os
import time
from urllib.parse import urlparse, urljoin

from flask import abort, current_app, g, redirect, session, url_for, request


def name_filter(user):
    return user['name'] if user['name'] else user['username']

def return_url_for_global(endpoint, *, _anchor=None, _method=None, _scheme=None, _external=None, **values):
    next = url_for(request.endpoint, **request.view_args, **request.args)
    return url_for(endpoint, _anchor=_anchor, _method=_method, _scheme=_scheme, _external=_external, next=next, **values)

def inject_login_form():
    from sharecipe.auth.forms import LoginForm
    login_form = None

    if g.user is None:
        login_form=LoginForm()

    return dict(login_form=login_form)

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

def is_safe_redirect_url(target):
    host_url = urlparse(request.host_url)
    print(host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    print(redirect_url)
    return (
            redirect_url.scheme in ('http', 'https')
            and host_url.netloc == redirect_url.netloc
            )

def get_safe_redirect(url):
    if url and is_safe_redirect_url(url):
        return url

    url = request.referrer
    if url and is_safe_redirect_url(url):
        return url

    return url_for('index')

def redirect_dest(fallback):
    dest_url = request.args.get('next')

    if not dest_url:
        dest_url = url_for(fallback)
    
    return redirect(dest_url)
