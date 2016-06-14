# -*- coding: utf-8 -*-

from flask import g, jsonify
from flask.ext.httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    """
    Инициализация HTTPBasicAuth, проверка пароля и email.
    Проверка аутентификации с поддержкой маркеров.
    Поддерживается идентификация ананимного пользователя.
    """
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    # Для отличия способов аутентификации, с маркером и без
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    """Обработчик ошибок HTTPBasicAuth"""
    return unauthorized('Invalid credentials')


# @auth.login_required для защиты маршрутов
@api.before_request
@auth.login_required
def before_request():
    """Обработчик с аутентификацией для всех маршрутов в макете"""
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/token')
def get_token():
    """Генератор маркеров"""
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify(
        {'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600}
    )
