import sys
import flask
import numpy as np
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
    AccessRow, DatasetRow, ColumnRow, MetadataRow
)
from pygalvanalyser.cell_data import (
    CellRow, ManufacturerRow
)
from pygalvanalyser.harvester import (
    MonitoredPathRow, HarvesterRow
)
from pygalvanalyser.experiment import select_timeseries_column
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
    datasets = DatasetRow.all(conn)
    print('called dataset', datasets)
    return DatasetRow.to_json(datasets)

@app.route('/api/cell/<int:uid>', methods=['GET', 'PUT', 'POST'])
@token_required
@cross_origin()
def cell(user, uid):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    if request.method == 'GET':
        if uid is None:
            cell = CellRow.all(conn)
        else:
            cell = CellRow.select_from_uid(uid, conn)
            if cell is None:
                return jsonify({
                    'message': 'cell not found'
                }), 404
        return CellRow.to_json(cell)
    elif request.method == 'POST':
        request_data = request.get_json()
        cell = CellRow(
            manufacturer_id=request_data['manufacturer_id'],
            cell_uid=request_data['cell_uid'],
            owner=request_data['owner'],
            purpose=request_data['purpose'],
            test_equipment=request_data['test_equipment'],
            json_data=request_data['json_data'],
        )
        cell.insert(conn)
        conn.commit()
        return CellRow.to_json(cell)
    elif request.method == 'PUT':
        cell = CellRow.select_from_uid(uid, conn)
        if cell is None:
            return jsonify({
                'message': 'cell not found'
            }), 404

        request_data = request.get_json()

        if 'manufacturer_id' in request_data:
            metadata.manufacturer_id = \
                request_data['manufacturer_id']
        if 'cell_uid' in request_data:
            metadata.cell_uid = request_data['cell_uid']
        if 'owner' in request_data:
            metadata.owner = request_data['owner']
        if 'purpose' in request_data:
            metadata.purpose = request_data['purpose']
        if 'test_equipment' in request_data:
            metadata.test_equipment = request_data['test_equipment']
        if 'json_data' in request_data:
            json_data = request_data['json_data']
            try:
                metadata.json_data = json.loads(json_data)
            except json.decoder.JSONDecodeError:
                return jsonify({
                    'message': 'json_data not json'
                }), 400
        metadata.update(conn)
        conn.commit()
        return MetadataRow.to_json(metadata)

@app.route('/api/manufacturer', methods=['GET', 'POST'])
@app.route('/api/manufacturer/<int:id_>', methods=['GET', 'PUT', 'DELETE'])
@token_required
@cross_origin()
def manufacturer(user, id_=None):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    print('manufacturer')
    if request.method == 'GET':
        if id_ is None:
            manufacturer = ManufacturerRow.all(conn)
        else:
            manufacturer = ManufacturerRow.select_from_id(id_, conn)
            if manufacturer is None:
                return jsonify({
                    'message': 'manufacturer not found'
                }), 404
        return ManufacturerRow.to_json(manufacturer)
    elif request.method == 'POST':
        request_data = request.get_json()
        print('manufacturer post', request_data)
        manufacturer = ManufacturerRow(
            name=request_data.get('name', ''),
        )
        manufacturer.insert(conn)
        conn.commit()
        return ManufacturerRow.to_json(manufacturer)
    elif request.method == 'PUT':
        print('PUT with id', id_)
        manufacturer = ManufacturerRow.select_from_id(id_, conn)
        if manufacturer is None:
            return jsonify({
                'message': 'manufacturer not found'
            }), 404

        request_data = request.get_json()

        if 'name' in request_data:
            manufacturer.name = request_data['name']

        manufacturer.update(conn)
        conn.commit()
        return ManufacturerRow.to_json(manufacturer)
    elif request.method == 'DELETE':
        id_ = request.args['id']
        print('deleting', id_)
        manufacturer = ManufacturerRow.select_from_id(
            id_, conn
        )
        if manufacturer is None:
            return jsonify({
                'message': 'manufacturer not found'
            }), 404

        manufacturer.delete(conn)
        conn.commit()
        return jsonify({'success': True}), 200



@app.route('/api/metadata/<int:dataset_id>', methods=['GET', 'PUT', 'POST'])
@token_required
@cross_origin()
def metadata(user, dataset_id):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    if request.method == 'GET':
        metadata = MetadataRow.select_from_dataset_id(dataset_id, conn)
        if metadata is None:
            return jsonify({
                'message': 'metadata not found'
            }), 404

        return MetadataRow.to_json(metadata)
    elif request.method == 'POST':
        metadata = MetadataRow(
            dataset_id=dataset_id,
        )
        metadata.insert(conn)
        conn.commit()

        return MetadataRow.to_json(metadata)
    elif request.method == 'PUT':
        metadata = MetadataRow.select_from_dataset_id(dataset_id, conn)
        if metadata is None:
            return jsonify({
                'message': 'metadata not found'
            }), 404

        request_data = request.get_json()

        if 'cell_uid' in request_data:
            metadata.path = request_data['cell_uid']
        if 'owner' in request_data:
            metadata.owner = request_data['owner']
        if 'purpose' in request_data:
            metadata.purpose = request_data['purpose']
        if 'test_equipment' in request_data:
            metadata.test_equipment = request_data['test_equipment']
        if 'json_data' in request_data:
            json_data = request_data['json_data']
            try:
                json_data = json.loads(json_data)
            except json.decoder.JSONDecodeError:
                return jsonify({
                    'message': 'json_data not json'
                }), 400
        metadata.update(conn)
        conn.commit()
        return MetadataRow.to_json(metadata)


@app.route('/api/dataset/<int:dataset_id>', methods=['GET'])
@token_required
@cross_origin()
def dataset_by_id(user, dataset_id):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    datasets = DatasetRow.select_from_id(dataset_id, conn)
    return DatasetRow.to_json(datasets)

@app.route('/api/column', methods=['GET'])
@token_required
@cross_origin()
def column(user):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    dataset_id = request.args['dataset_id']

    column_ids = \
        TimeseriesDataRow.select_column_ids_in_dataset(
            dataset_id, conn
        )

    columns = [ColumnRow.select_from_id(cid, conn)
               for cid in column_ids]

    return ColumnRow.to_json(columns)

def serialise_numpy_array(np_array):
    response = flask.make_response(np_array.tobytes())
    response.headers.set('Content-Type', 'application/octet-stream')
    return response

@app.route('/api/dataset/<int:dataset_id>/<int:col_id>', methods=['GET'])
@token_required
@cross_origin()
def timeseries_column(user, dataset_id, col_id):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()

    array = select_timeseries_column(dataset_id, col_id, conn)

    single_precision = request.args.get('single_precision', True)
    if single_precision:
        array = array.astype(np.float32)
    print('sending array of dtype', array.dtype)
    print('sending array of length', len(array))
    print(array)

    return serialise_numpy_array(array)

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


