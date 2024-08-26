from flask_wtf import FlaskForm
from wtforms import validators, PasswordField


class admin_login_form(FlaskForm):
    admin_key = PasswordField('Admin key', [validators.input_required()])

    def validate(self):
        rv =FlaskForm.validate(self)
        if not rv:
            return False
        var = self.admin_key.data
        key = 'THIS IS THE KEY'
        if (var == key):
            return True
        else:
            self.admin_key.errors.append('Invalid admin key')
            return False