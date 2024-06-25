from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import EmailField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import Email, EqualTo, InputRequired, Length, Optional, ValidationError

from flask import g

from sharecipe.auth.helpers import check_password_hash

# additional validator for checking when one field is not equal to another
class NotEqualTo(object):
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError as exc:
            raise ValidationError(
                    field.gettext('Invalid field name \'%s\'.') % self.fieldname
                    ) from exc

        if field.data != other.data:
            return

        d = {
                'other_label': hasattr(other , 'label')
                and other.label.text
                or self.fieldname,
                'other_name': self.fieldname,
                }

        message = self.message
        if message is None:
            message = field.gettext('Field must not be equal to %(other_name)s.')

        raise ValidationError(message % d)

# validator check if password is correct for already signed in user
class PasswordCheck(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if g.user is not None and check_password_hash(g.user['password'], field.data):
            return

        message = self.message
        if message is None:
            message = 'Password incorrect'

        raise ValidationError(message)


# form for updating profile
class UpdateProfileForm(FlaskForm):
    name = StringField('Name', [
        Optional(),
        Length(max=56, message='Your name cannot be more than 56 characters')
        ], description='This is how you\'ll be known')
    email = EmailField('Email', [
        InputRequired(message='Email address is required'),
        Email(message='Enter a valid email address'),
        Length(max=256, message='Email must not be more than 256 characters'),
        ], description='Enter your email address to help recover your account if lost')
    bio = TextAreaField('Bio', [
        Optional(),
        Length(max=400, message='Bio cannot exceed 400 characters')
        ], description='Tell us about yourself')

# form for uploading profile picture
class UploadPictureForm(FlaskForm):
    picture = FileField('Profile Picture', [
        FileRequired(message='No photo supplied.'),
        FileAllowed(['jpg', 'jpeg', 'png'], message='Profile picture must be a jpg or png file.'),
        ], render_kw={'accept': 'image/jpeg,image/png'}, description='Upload a picture for your account profile')

# form for deleting profile picture
class DeletePictureForm(FlaskForm):
    confirm = SubmitField('Delete Picture')

# form for updating password
class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', [
        InputRequired(message='Please enter your password'),
        PasswordCheck(message='Incorrect password'),
        ], description='Enter your current password')
    new_password = PasswordField('New Password', [
        InputRequired(message='Please choose a new password'),
        Length(min=8, max=256, message='Your new password must be between 8 and 256 characters.'),
        NotEqualTo('current_password', message='New password must be different.')
        ], description='Choose a strong password to protect your account')
    confirm_password = PasswordField('Confirm Password', [
        InputRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
        ], description='Confirm your password')

# form for deleting account
class DeleteAccountForm(FlaskForm):
    password = PasswordField('Password', [
        InputRequired(message='Please enter your password'),
        PasswordCheck(message='Incorrect password'),
        ], description='Enter your password to delete your account')
