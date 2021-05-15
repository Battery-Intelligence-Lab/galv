import sys
import flask
from flask_cors import cross_origin
from flask import request, abort, session, jsonify, make_response
import jwt
import json
import datetime

from pygalvanalyser.experiment.timeseries_data_row import (
    TimeseriesDataRow,
    RECORD_NO_COLUMN_ID,
)
from pygalvanalyser.experiment import (
    AccessRow, DatasetRow
)
from pygalvanalyser.harvester import (
    MonitoredPathRow, HarvesterRow
)
import math
import psycopg2

from flask import current_app as app

from functools import wraps

from .database.user import User

def create_token(username, role):
    return jwt.encode(
        {
            'username': username,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        },
        app.config['SECRET_KEY'],
        algorithm='HS256',
    )

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'Authorization' in request.headers:
            if request.headers['Authorization'].startswith(
                    'Bearer '
            ):
                token = request.headers['Authorization'][7:]

        if not token:
            return jsonify({
                    'message': 'a valid token is missing'
            }), 401
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            current_user = User(data['username'], data['role'])
        except jwt.ExpiredSignatureError:
            return jsonify({
                    'message': 'Token has expired, please login again'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                    'message': 'Invalid token, please login again'
            }), 401

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
        token = create_token(user.username, user.role)
        return jsonify({'access_token': token})

    return make_response(
        'could not verify',  401,
        {'WWW.Authentication': 'Basic realm: "login required"'}
    )

@app.route('/api/refresh', methods=['POST'])
def refresh():
    print("refresh request")
    old_token = request.get_data()
    try:
        data = jwt.decode(
            old_token, app.config['SECRET_KEY'],
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

    new_token = create_token(data.username, data.role)
    return jsonify({'access_token': new_token})

def log(text):
    with open("/tmp/log.txt", "a") as myfile:
        myfile.write(text + "\n")

@app.route('/api/hello', methods=['GET'])
@cross_origin()
def hello():
    return 'Hello'

@app.route('/api/hello_user', methods=['GET'])
@token_required
@cross_origin()
def hello_user(user):
    return 'Hello {}'.format(user)

@app.route('/api/dataset', methods=['GET'])
@token_required
@cross_origin()
def dataset(user):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    id_ = request.args.get('id')
    if id_ is not None:
        datasets = DatasetRow.select_from_id(id_, conn)
    else:
        datasets = DatasetRow.all(conn)
    print('called dataset', datasets)
    return DatasetRow.to_json(datasets)

@app.route('/api/harvester', methods=['GET'])
@token_required
@cross_origin()
def harvester(user):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    id_ = request.args.get('id')
    if id_ is not None:
        harvesters = HarvesterRow.select_from_id(id_, conn)
    else:
        harvesters = HarvesterRow.all(conn)
    print('called harvesters', harvesters)
    return HarvesterRow.to_json(harvesters)

@app.route('/api/monitored_path',
           methods=['GET', 'PUT', 'POST', 'DELETE'])
@token_required
@cross_origin()
def monitored_path(user):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    print(request.method)
    if request.method == 'GET':
        id_ = request.args.get('id')
        if id_ is not None:
            paths = MonitoredPathRow.select_from_id(
                id_, conn
            )
        else:
            harvester_id = request.args['harvester_id']
            paths = MonitoredPathRow.select_from_harvester_id(
                harvester_id, conn
            )
        return MonitoredPathRow.to_json(paths)
    elif request.method == 'PUT':
        id_ = request.args['id']
        path = MonitoredPathRow.select_from_id(
            id_, conn
        )
        request_data = request.get_json()
        if 'path' in request_data:
            path.path = request_data['path']
        if 'monitored_for' in request_data:
            monitored_for = request_data['monitored_for']
            try:
                monitored_for = json.loads(monitored_for)
            except json.decoder.JSONDecodeError:
                return jsonify({
                    'message': 'monitored_for not json'
                }), 400

            if not isinstance(monitored_for, list):
                return jsonify({
                    'message': 'monitored_for not an array'
                }), 400

            all_strings = all(
                [isinstance(x, str) for x in monitored_for]
            )
            if all_strings:
                path.monitored_for = monitored_for
            else:
                return jsonify({
                    'message': 'monitored_for not an array of strings'
                }), 400
        if 'harvester_id' in request_data:
            path.harvester_id = request_data['harvester_id']
        path.update(conn)
        conn.commit()
        return MonitoredPathRow.to_json(path)
    elif request.method == 'POST':
        request_data = request.get_json()
        new_path = MonitoredPathRow(
            request_data['harvester_id'],
            request_data['monitored_for'],
            request_data['path'],
        )
        new_path.insert(conn)
        conn.commit()
        return MonitoredPathRow.to_json(new_path)
    elif request.method == 'DELETE':
        id_ = request.args['id']
        print('deleting', id_)
        path = MonitoredPathRow.select_from_id(
            id_, conn
        )
        path.delete(conn)
        conn.commit()
        return jsonify({'success': True}), 200


