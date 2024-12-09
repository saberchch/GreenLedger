from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    profession = SelectField('Profession', choices=[
        ('civil_engineer', 'Civil Engineer'),
        ('mechanical_engineer', 'Mechanical Engineer'),
        ('electronics_engineer', 'Electronics Engineer')
    ], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    secret_phrase = PasswordField('Secret Phrase', validators=[DataRequired()])
    submit = SubmitField('Login') 