from wtforms import (Form, BooleanField, StringField, SubmitField,
                     PasswordField, validators, SelectField, TextAreaField)

#
#   Form Classes (WTForms Module)
#


class LoginForm(Form):
    username = StringField("Username", [validators.Length(min=2, max=20)])
    passwd = PasswordField("Password", [validators.Length(min=8, max=30)])
    submit = SubmitField("Login")


class RegisterForm(Form):
    name = StringField("Name", [validators.Length(min=2, max=20)])
    surname = StringField("Surname", [validators.Length(min=2, max=20)])
    email = StringField("Email", [validators.email("Invalid Email")])
    username = StringField("Username", [validators.Length(min=2, max=20)])
    passwd = PasswordField('Password', [validators.input_required(),
                                        validators.Length(min=8, max=30),
                                        validators.EqualTo('confirm',
                                                           message=
                                                           'Passwords Do'
                                                           ' NOT match!')])
    confirm = PasswordField('Repeat')
    accept_rules = BooleanField('I Accept The Site Rules and Regulations',
                                [validators.InputRequired()])
    submit = SubmitField("Register")


class PostsForm(Form):
    title = StringField("Title", [validators.Length(min=1, max=40)])
    content = TextAreaField("Content", [validators.InputRequired()])
    accessLevel = SelectField("Availability", choices=[('pub', 'Public'),
                                                       ('prv', 'Private')])
    submit = SubmitField("Submit")
    cancel = SubmitField("Cancel")


class CommentForm(Form):
    comment = TextAreaField("Comment", [validators.InputRequired()])
    submit = SubmitField("Submit")
