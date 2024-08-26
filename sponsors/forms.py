from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError, EmailField, SubmitField, DateField, IntegerField, SelectField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from werkzeug.security import check_password_hash
from flask_wtf.file import FileField
from flask import session

from sponsors.models import sponsor_login, Campaigns, Advertisements
from admin.models import flag_sponsor


class signupForm(FlaskForm):
    sponsor_name = StringField('User Name', validators=[InputRequired()])
    email1 = EmailField('Email-ID', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=80)])
    confirm_password = PasswordField('Repeat Password', validators=[EqualTo('password', message='Passwords must match')])
    company_name = StringField('Company Name', validators=[InputRequired()])
    Industry = StringField('Industry', validators=[InputRequired()])
    profile_pic = FileField('Profile Picture')

    def validate_sponsor_name(self, sponsor_name):
        sponsor = sponsor_login.query.filter_by(sponsor_name=sponsor_name.data).first()
        if sponsor is not None:
            raise ValidationError('Please use a different username.')

    def validate_email1(self, email1):
        email = sponsor_login.query.filter_by(email=email1.data).first()
        if email is not None:
            raise ValidationError('This email is already in use. Please choose a different one.')


class loginForm(FlaskForm):
    sponsor_name = StringField('Sponsor Name', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=80)])
    submit = SubmitField('Login')

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        sponsor_name_value = self.sponsor_name.data
        password_value = self.password.data

        try:
            user = sponsor_login.query.filter_by(sponsor_name=sponsor_name_value).first()

            if user:
                if not check_password_hash(user.password, password_value):
                    self.password.errors.append('Incorrect username or password.')
                    return False

                flagged = flag_sponsor.query.filter_by(sponsor_name=sponsor_name_value).count()
                if flagged:
                    self.password.errors.append('You are flagged by the admin! You cannot log in.')
                    return False

                return True
            else:
                self.password.errors.append('Incorrect username or password.')
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False


class CampaignsForm(FlaskForm):
    campaign_name = StringField('Campaign Name', validators=[InputRequired()])
    description = StringField('Description')
    start_date = DateField('Start Date', validators=[InputRequired()])
    end_date = DateField('End Date', validators=[InputRequired()])
    budget = IntegerField('Budget', validators=[InputRequired()])
    visibility = SelectField('Visibility', choices=[('public', 'Public'), ('private', 'Private')], validators=[InputRequired()])
    goals = StringField('Goals')

    def validate_campaign_name(self, campaign_name):
        campaign = Campaigns.query.filter_by(campaign_name=campaign_name.data).first()
        if campaign is not None:
            raise ValidationError('Please use a different campaign name')


class AdvertisementForm(FlaskForm):
    ad_name = StringField('Advertisement Name', validators=[InputRequired()])
    amount = IntegerField('Amount', validators=[InputRequired()])
    requirements = StringField('Requirements', validators=[InputRequired()])
    images = FileField('Images (if any)')

    def validate_amount(self, amount):
        campaign = Campaigns.query.filter_by(campaign_id=session.get('campaign_id')).first()
        if campaign:
            camp_amt = campaign.budget
            total_amount = sum(a.amount for a in Advertisements.query.filter_by(campaign_id=session.get('campaign_id')).all())
            if total_amount + amount.data > camp_amt:
                raise ValidationError('Budget exceeded, please enter a smaller amount')


class SearchForm(FlaskForm):
    searched = StringField("Search", validators=[InputRequired()])
    submit = SubmitField("Submit")
