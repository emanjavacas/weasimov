from flask_wtf import Form
from wtforms import StringField, TextAreaField, Field, PasswordField, BooleanField, RadioField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email
from .models import User


class LoginForm(Form):
    username = StringField('username', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

    def validate_fields(self):
        user = self.get_user()
        if user is None:
            self.username.errors = ('Opgegeven gebruikersnaam is onbekend.',)
            return False
        if not user.is_correct_password(self.password.data):
            self.password.errors = ('Opgegeven wachtwoord is onbekend.',)
            return False
        return True

    def get_user(self):
        return User.query.filter_by(username=self.username.data).first()


class RegisterForm(Form):
    username = StringField('username', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    cpassword = PasswordField('confirm password', validators=[DataRequired()])

    def validate_fields(self):
        if not self.available_username():
            self.username.errors = ('Deze naam is al in gebruik.',)
            return False
        if self.password.data != self.cpassword.data:
            self.cpassword.errors = ('Wachtwoorden zijn niet hetzelfde', )
            return False
        return True

    def available_username(self):
        return User.query.filter_by(username=self.username.data).first() is None
