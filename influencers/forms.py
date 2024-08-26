from flask_wtf import FlaskForm
from wtforms import validators, StringField, PasswordField, ValidationError, EmailField, SubmitField
from werkzeug.security import check_password_hash
from flask_wtf.file import FileField

from influencers.models import influencer_login
from admin.models import flag_influencer

class signupForm(FlaskForm):
    influencer_name = StringField('User Name', [validators.input_required()])
    email = EmailField('Email-ID', [validators.input_required(), validators.email()])
    password = PasswordField('Password', [validators.InputRequired(), validators.Length(min=4, max=80)])
    confirm_password = PasswordField('Repeat password', [validators.EqualTo('password',
                                                                            message='Password must match')])
    category = StringField('Category', [validators.input_required()])
    Instagram = StringField('Instagram link')
    twitter = StringField('Twitter link')
    youtube = StringField('youtube link')
    profile_pic = FileField('Profile Picture')

    def validate_usename(self, influencer_name):
        influencer = influencer_login.query.filter_by(full_name=influencer_name.data).first()
        if influencer is not None:
            raise ValidationError('Please use a different username')

    def validate_email(self, email):
        email = influencer_login.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('This email is already in use.Please choose a different one')


class loginForm(FlaskForm):
    influencer_name = StringField('Influencer Name', [validators.InputRequired()])
    password = PasswordField('Password', [validators.InputRequired(), validators.Length(min=4, max=80)])
    submit = SubmitField('Login')
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        influencer_name_value = self.influencer_name.data
        password_value = self.password.data
        user = influencer_login.query.filter_by(influencer_name=influencer_name_value).first()
        if user:
            if not check_password_hash(user.password, password_value):
                self.password.errors.append('Incorrect email or password')
                return False
            flagged = flag_influencer.query.filter_by(influencer_name=influencer_name_value).count()
            if flagged:
                self.password.errors.append('You are flagged by the admin! You cannot log in')
                return False
            return True
        else:
            self.password.errors.append('Incorrect email or password')
            return False


class SearchForm(FlaskForm):
    searched = StringField("Searched", [validators.input_required()])
    submit = SubmitField("submit")