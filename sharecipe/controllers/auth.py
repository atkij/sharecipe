import secrets
import smtplib
import string

from datetime import datetime, timedelta
from email.mime.text import MIMEText

from flask import g, session, current_app, render_template

from ..database import users
from ..core import email

from ..core.auth import check_password_hash, generate_password_hash

class AccountError(Exception):
    pass

class LoginError(Exception):
    pass

class VerifyError(Exception):
    pass

def register(name: str, email: str, password: str) -> int:
    user = users.find(email=email)

    if user is not None:
        raise AccountError('Account already exists')
    
    return users.create(email, generate_password_hash(password), name)

def login(email: str, password: str) -> int:
    user = users.find(email=email)

    if user is None or not check_password_hash(user.password, password):
        raise LoginError('Username or password incorrect')
    
    users.login(user.id)
    
    return user.id

def verify(user_id: int, code: str):
    user = users.find(user_id)
    check_code = users.get_code(user_id)

    if check_code is None:
        raise VerifyError('No code to verify')
    
    if code != check_code:
        raise VerifyError('Verification codes do not match')
    
    users.update(user.id, user.email, user.password, True)
    users.delete_code(user_id)

def x_verify(user_id: int) -> tuple[str, timedelta]:
    user = users.find(user_id)

    code = ''.join(secrets.choice(string.digits) for i in range(6))
    expires = timedelta(minutes=30)

    users.set_code(user_id, code, datetime.now() + expires)

    email.send_email(
        'Sharecipe Verification Code',
        user.email,
        current_app.config['SMTP_USERNAME'],
        render_template('email/verify.html', user=user, code=code, expires=expires)
    )

    return (code, expires)


def verify_email(check: str) -> bool:
    code = session.get('code')

    if code is None or len(code) == 0:
        return False
    
    if check == code:
        return True

    return False    

def generate_code():
    return ''.join(secrets.choice(string.digits) for i in range(6))

def send_code(code):
    subject = 'Sharecipe Verification Code'
    body = ('Hello {},\n\n'
            'Your Sharecipe verification code is: {}\n\n'
            'Sharecipe')
    
    msg = MIMEText(body.format(g.profile.name, code))
    msg['Subject'] = subject
    msg['From'] = current_app.config['GMAIL_USERNAME']
    msg['To'] = g.user.email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(current_app.config['GMAIL_USERNAME'], current_app.config['GMAIL_PASSWORD'])
        smtp_server.sendmail(current_app.config['GMAIL_USERNAME'], g.user.email, msg.as_string())