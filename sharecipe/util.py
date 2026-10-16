from urllib.parse import urlparse, urljoin

from flask import g, redirect, url_for, request

def return_url_for(endpoint, *, _anchor=None, _method=None, _scheme=None, _external=None, **values):
    return_url = url_for(request.endpoint, **request.view_args, **request.args)
    return url_for(endpoint, _anchor=_anchor, _method=_method, _scheme=_scheme, _external=_external, return_url=return_url, **values)

def inject_login_form():
    from .forms.auth import LoginForm
    login_form = None

    if g.user is None:
        login_form=LoginForm()

    return dict(login_form=login_form)

def is_safe_redirect_url(target):
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))

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