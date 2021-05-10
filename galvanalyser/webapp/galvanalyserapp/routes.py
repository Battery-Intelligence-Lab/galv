import sys
import flask
from flask import request, abort, session, jsonify, make_response
import jwt
import datetime

from pygalvanalyser.experiment.timeseries_data_row import (
    TimeseriesDataRow,
    RECORD_NO_COLUMN_ID,
)
from pygalvanalyser.experiment.access_row import AccessRow
import pygalvanalyser.experiment.timeseries_data_column as TimeseriesDataColumn
import math
import psycopg2

from flask import current_app as app

from functools import wraps

from .database.user import User


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            current_user = User(data['username'], data['role'])
        except jwt.ExpiredSignatureError:
            return jsonify({
                'message': 'Token has expired, please login again'
            })
        except jwt.InvalidTokenError:
            return jsonify({
                'message': 'Invalid token, please login again'
            })

        return f(current_user, *args, **kwargs)
    return decorator

@app.route('/api/login', methods=['GET', 'POST'])
def login_user():

    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response(
            'could not verify', 401,
            {'WWW.Authentication': 'Basic realm: "login required"'}
        )

    user = User.get(auth.username)

    if user.validate_password(auth.password):
        token = jwt.encode(
            {
                'username': user.username,
                'role': user.role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            },
            app.config['SECRET_KEY'],
            algorithm='HS256',
        )
        return jsonify({'access_token': token})

    return make_response(
        'could not verify',  401,
        {'WWW.Authentication': 'Basic realm: "login required"'}
    )

def log(text):
    with open("/tmp/log.txt", "a") as myfile:
        myfile.write(text + "\n")

@app.route('/api/hello', methods=['GET'])
def hello():
    return 'Hello'

@app.route('/api/hello_user', methods=['GET'])
@token_required
def hello_user(user):
    return 'Hello {}'.format(user)



