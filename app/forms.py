from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import InputRequired, Length

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(max=50)])
    email = StringField('Email', validators=[InputRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    role = StringField('Role', validators=[InputRequired(), Length(max=20)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    submit = SubmitField('Login')