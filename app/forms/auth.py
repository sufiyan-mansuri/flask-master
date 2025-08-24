from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=6, max=20)])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(), EqualTo('password')])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
        
class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

class PasswordResetRequestForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])

class PasswordResetForm(FlaskForm):
    password = PasswordField('password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(), EqualTo('password')])