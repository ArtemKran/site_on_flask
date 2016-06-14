# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..models import Role, User
from flask.ext.pagedown.fields import PageDownField


class NameForm(Form):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    """Форма редактирования профиля пользователя"""
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    """Форма редактирования профиля пользователя администратором"""
    email = SubmitField(
        'Email', validators=[DataRequired(), Length(1, 64), Email()]
    )
    username = SubmitField(
        'Username', validators=[DataRequired(), Length(1, 64), Regexp(
            '^[A-Za-z][A-Za-z0-9_.]*$, 0, Usernames must have only letters, numbers, dots or undercores'
        )]
    )
    confirmed = BooleanField('Confirm')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm).__init__(*args, **kwargs)
        self.role.choices = [
            (role.id, role.name) for role in Role.querty.order_by(Role.name).all()
        ]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(Form):
    """Форма написания поста"""
    body = PageDownField("What's your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(Form):
    """Форма комментариев"""

    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('Submit')

