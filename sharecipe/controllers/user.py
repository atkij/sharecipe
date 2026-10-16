from datetime import datetime, timedelta
import secrets
import string
from typing import Self

from flask import current_app, session

from . import Controller
from ..models.user import UserModel

from ..core.auth import check_password_hash, generate_password_hash
from ..core import email

class UserRegisterError(Exception):
    pass

class UserLoginError(Exception):
    pass

class UserVerifyError(Exception):
    pass

class UserUpdateError(Exception):
    pass

class UserController(UserModel, Controller):
    @classmethod
    def register(cls, email: str, password: str) -> Self:
        user = cls.select_one_by_email(email)

        if user is not None:
            raise UserRegisterError('Account already exists')
        
        return cls._insert(email, generate_password_hash(password))

    @classmethod
    def login(cls, email: str, password: str) -> Self:
        user = cls.select_one_by_email(email)

        if user is None or not check_password_hash(user.password, password):
            raise UserLoginError('Username or password incorrect')

        user.last_login = datetime.now()
        user._update()

        return user

    def verify(self, code: str):
        if not self._check_code(code):
            raise UserVerifyError('Incorrect verification code')

        self.verified = True
        self._update()

    def verify_email(self):
        code, expires = self._set_code()

        email.send_email(
                'Sharecipe Verification Code',
                self.email,
                current_app.config['SMTP_USERNAME'],
                email.render_email('email/verify.html', user=self, code=code, expires=expires)
            )

    def set_password(self, password: str):
        self.password = generate_password_hash(password)
        self._update()

    @classmethod
    def _set_code(cls) -> tuple[int, timedelta]:
        code = cls._generate_code()
        expires = timedelta(minutes=30)
    
        session['verify_code'] = code
        session['verify_expires'] = datetime.now() + expires
    
        return code, expires

    @staticmethod
    def _check_code(code: str) -> bool:
        if session['verify_code'] is None or session['verify_code'] != code:
            return False
        
        return True

    @staticmethod
    def _generate_code():
        return ''.join(secrets.choice(string.digits) for i in range(6))

    def update(self):
        user = self.select_one(self.id)

        if user.email != self.email:
            self.verified = False

            if self.select_one_by_email(self.email) is not None:
                raise UserUpdateError('Account with that email address already exists')
        
        return self._update()

    def delete(self):
        return self._delete()

# def reset(user_id: int, code: str):
#     user = users.find(user_id)
#     check_code = users.get_code(user_id)

#     if check_code is None:
#         raise VerifyError('No code to verify')
    
#     if code != check_code:
#         raise VerifyError('Verification codes do not match')
