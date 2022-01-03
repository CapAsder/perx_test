from flask import request
from app import USERNAME, PASSWORD, TOKEN


def error(desc, **kwargs):
    return {'status': 'error', 'error': desc, **kwargs}


def ok(response=None):
    if response is None:
        response = {}
    return {"status": "ok", **response}


def result(**kwargs):
    return {"status": "ok", **kwargs}


def auth_only():
    def wrapper(func):
        def call(*args, **kwargs):
            if is_auth():
                return func(*args, **kwargs)
            else:
                return error('auth_only'), 401

        return call

    return wrapper


def is_auth():
    if request.authorization is None:
        return False
    username = None
    password = None
    token = None
    if 'username' in request.authorization:
        username = request.authorization.username
    if 'password' in request.authorization:
        password = request.authorization.password
    if request.view_args is not None and 'token' in request.view_args:
        token = request.view_args['token']
    if request.json is not None and 'token' in request.json:
        token = request.json['token']

    if username is not None and password is not None:
        if USERNAME == username and PASSWORD == password:
            return True
    if token is not None:
        if TOKEN == token:
            return True
    return False
