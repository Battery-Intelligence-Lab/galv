import sys
import flask
import numpy as np
from flask_cors import cross_origin
from flask import request, abort, session, jsonify, make_response
import os
from datetime import timezone
from datetime import datetime
from datetime import timedelta
import json

from harvester.__main__ import main as harvester_main

from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies
from flask_jwt_extended import get_jwt_identity


from harvester.__main__ import main as harvester_main

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
    MonitoredPathRow, HarvesterRow, ObservedFileRow
)
from pygalvanalyser.experiment import select_timeseries_column
import math
import psycopg2

from flask import current_app as app
from celery import current_app as celery

from functools import wraps

from pygalvanalyser.user_data import UserRow


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response

@app.route('/api/login', methods=['POST'])
def login():

    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response(
            'could not verify', 401,
            {'WWW.Authentication': 'Basic realm: "login required"'}
        )

    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    user = UserRow.select_from_username(auth.username, conn)
    print('got user', user)

    if user.validate_password(auth.password):
        response = jsonify({"message": "login successful"})
        access_token = create_access_token(
            identity=UserRow.to_json(user)
        )
        set_access_cookies(response, access_token)
        return response

    return make_response(
        'could not verify',  401,
        {'WWW.Authentication': 'Basic realm: "login required"'}
    )

@app.route("/api/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "logout successful"})
    unset_jwt_cookies(response)
    return response

@app.route('/api/refresh', methods=['POST'])
def refresh():
    print("refresh request")
    old_token = request.get_data()
    try:
        data = jwt.decode(
            old_token, app.config['SECRET_KEY'],
            algorithms=['HS256'],
            options={"verify_exp": False}
        )
    except jwt.ExpiredSignatureError:
        return jsonify({
            'message': 'Token has expired, please login again'
        }), 401
    except jwt.InvalidTokenError:
        return jsonify({
            'message': 'Invalid token, please login again'
        }), 401

    new_token = create_token(data['username'], data['role'])
    return jsonify({'access_token': new_token})

@app.route('/api/hello', methods=['GET'])
@cross_origin()
def hello():
    return 'Hello'

@app.route('/api/user', methods=['GET'])
@cross_origin()
@jwt_required()
def user():
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    users = UserRow.all(conn)
    print('called user', users)
    return UserRow.to_json(users)

@app.route('/api/dataset', methods=['GET'])
@app.route('/api/dataset/<int:id_>', methods=['GET', 'PUT'])
@cross_origin()
@jwt_required()
def dataset(id_=None):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    if request.method == 'GET':
        if id_ is None:
            datasets = DatasetRow.all(conn)
        else:
            datasets = DatasetRow.select_from_id(id_, conn)
        print('called dataset', datasets)
        return DatasetRow.to_json(datasets)
    elif request.method == 'PUT':
        dataset = DatasetRow.select_from_id(id_, conn)
        if dataset is None:
            return jsonify({
                'message': 'cell not found'
            }), 404

        request_data = request.get_json()

        if 'name' in request_data:
            dataset.name = request_data['name']
        if 'cell_id' in request_data:
            dataset.cell_id = request_data['cell_id']
        if 'owner' in request_data:
            dataset.owner = request_data['owner']
        if 'test_equipment' in request_data:
            dataset.test_equipment = request_data['test_equipment']
        if 'purpose' in request_data:
            dataset.purpose = request_data['purpose']

        dataset.update(conn)
        conn.commit()
        return DatasetRow.to_json(dataset)

@app.route('/api/cell', methods=['GET', 'POST'])
@app.route('/api/cell/<int:id_>', methods=['GET', 'PUT', 'DELETE'])
@cross_origin()
@jwt_required()
def cell(id_=None):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    if request.method == 'GET':
        if id_ is None:
            cell = CellRow.all(conn)
        else:
            cell = CellRow.select_from_id(id_, conn)
            if cell is None:
                return jsonify({
                    'message': 'cell not found'
                }), 404
        return CellRow.to_json(cell)
    elif request.method == 'POST':
        request_data = request.get_json()
        cell = CellRow(
            uid=request_data.get('uid', None),
            manufacturer=request_data.get('manufacturer', None),
            form_factor=request_data.get('form_factor', None),
            link_to_datasheet=request_data.get('link_to_datasheet', None),
            anode_chemistry=request_data.get('anode_chemistry', None),
            cathode_chemistry=request_data.get('cathode_chemistry', None),
            nominal_capacity=request_data.get('nominal_capacity', None),
            nominal_cell_weight=request_data.get('nominal_cell_weight', None),
        )
        cell.insert(conn)
        conn.commit()
        return CellRow.to_json(cell)
    elif request.method == 'PUT':
        cell = CellRow.select_from_id(id_, conn)
        if cell is None:
            return jsonify({
                'message': 'cell not found'
            }), 404

        request_data = request.get_json()

        if 'manufacturer' in request_data:
            cell.manufacturer = \
                request_data['manufacturer']
        if 'uid' in request_data:
            cell.uid = request_data['uid']
        if 'manufacturer' in request_data:
            cell.manufacturer = request_data['manufacturer']
        if 'form_factor' in request_data:
            cell.form_factor = request_data['form_factor']
        if 'link_to_datasheet' in request_data:
            cell.link_to_datasheet = \
                request_data['link_to_datasheet']
        if 'anode_chemistry' in request_data:
            cell.anode_chemistry = request_data['anode_chemistry']
        if 'cathode_chemistry' in request_data:
            cell.cathode_chemistry = request_data['cathode_chemistry']
        if 'nominal_capacity' in request_data:
            cell.nominal_capacity = request_data['nominal_capacity']
        if 'nominal_cell_weight' in request_data:
            cell.nominal_cell_weight = \
                request_data['nominal_cell_weight']

        cell.update(conn)
        conn.commit()
        return CellRow.to_json(cell)
    elif request.method == 'DELETE':
        print('deleting', id_)
        cell = CellRow.select_from_id(
            id_, conn
        )
        if cell is None:
            return jsonify({
                'message': 'cell not found'
            }), 404

        cell.delete(conn)
        conn.commit()
        return jsonify({'success': True}), 200


@app.route('/api/manufacturer', methods=['GET', 'POST'])
@app.route('/api/manufacturer/<int:id_>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@cross_origin()
def manufacturer(id_=None):
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
@jwt_required()
@cross_origin()
def metadata(dataset_id):
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
@jwt_required()
@cross_origin()
def dataset_by_id(dataset_id):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    datasets = DatasetRow.select_from_id(dataset_id, conn)
    return DatasetRow.to_json(datasets)

@app.route('/api/file', methods=['GET'])
@jwt_required()
@cross_origin()
def file():
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    path_id = request.args['path_id']
    files = ObservedFileRow.select_from_id_(path_id, conn)
    return ObservedFileRow.to_json(files)

@app.route('/api/column', methods=['GET'])
@jwt_required()
@cross_origin()
def column():
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
@jwt_required()
@cross_origin()
def timeseries_column(dataset_id, col_id):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()

    array = select_timeseries_column(dataset_id, col_id, conn)

    single_precision = request.args.get('single_precision', True)
    if single_precision:
        array = array.astype(np.float32)
    print('sending array of dtype', array.dtype)
    print('sending array of length', len(array))
    print(array)

    return serialise_numpy_array(array)


@celery.task()
def run_harvester_celery(machine_id):
    print('running harvester', machine_id)
    harvester_main(
        os.getenv('HARVESTER_USERNAME'),
        os.getenv('HARVESTER_PASSWORD'),
        machine_id,
        'galvanalyser_postgres', '5433',
        'galvanalyser', base_path='/usr/data'
    )

@celery.task()
def get_env_celery():
    env_var = 'GALVANALYSER_HARVESTER_BASE_PATH'
    return {env_var: os.getenv(env_var)}

@app.route('/api/harvester/<int:id_>/env', methods=['GET'])
@jwt_required()
@cross_origin()
def env_harvester(id_=None):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    harvester = HarvesterRow.select_from_id(
        id_, conn
    )
    result = get_env_celery.apply_async(
        queue=harvester.harvester_name
    )
    print('env success!')
    return jsonify(result.get()), 200

@app.route('/api/harvester/<int:id_>/run', methods=['PUT'])
@jwt_required()
@cross_origin()
def run_harvester(id_=None):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    harvester = HarvesterRow.select_from_id(
        id_, conn
    )
    run_harvester_celery.apply_async(
        args=[harvester.machine_id],
        queue=harvester.harvester_name
    )
    print('success!')
    return jsonify({'success': True}), 200


@app.route('/api/harvester', methods=['GET', 'POST'])
@app.route('/api/harvester/<int:id_>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@cross_origin()
def harvester(id_=None):
    user = UserRow.from_json(get_jwt_identity())
    print('USER', user)
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    if request.method == 'GET':
        if id_ is not None:
            harvesters = HarvesterRow.select_from_id(id_, conn)
        else:
            harvesters = HarvesterRow.all(conn)
        print('called harvesters', harvesters)
        return HarvesterRow.to_json(harvesters)
    elif request.method == 'PUT':
        harvester = HarvesterRow.select_from_id(
            id_, conn
        )
        request_data = request.get_json()
        if 'machine_id' in request_data:
            harvester.machine_id = request_data['machine_id']
        harvester.update(conn)
        conn.commit()
        return HarvesterRow.to_json(harvester)
    elif request.method == 'POST':
        request_data = request.get_json()
        new_harvester = HarvesterRow(
            request_data.get('machine_id', None),
            harvester_name=os.getenv('HARVESTER_USERNAME'),
        )
        new_harvester.insert(conn)
        conn.commit()
        return HarvesterRow.to_json(new_harvester)
    elif request.method == 'DELETE':
        print('deleting', id_)
        harvester = HarvesterRow.select_from_id(
            id_, conn
        )
        harvester.delete(conn)
        conn.commit()
        return jsonify({'success': True}), 200


@app.route('/api/monitored_path', methods=['GET', 'POST'])
@app.route('/api/monitored_path/<int:id_>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@cross_origin()
def monitored_path(id_=None):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    print(request.method)
    if request.method == 'GET':
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
        path = MonitoredPathRow.select_from_id(
            id_, conn
        )
        request_data = request.get_json()
        if 'path' in request_data:
            path.path = request_data['path']
        if 'monitored_for' in request_data:
            path.monitored_for = request_data['monitored_for']
        if 'harvester_id' in request_data:
            path.harvester_id = request_data['harvester_id']
        path.update(conn)
        conn.commit()
        return MonitoredPathRow.to_json(path)
    elif request.method == 'POST':
        request_data = request.get_json()
        new_path = MonitoredPathRow(
            request_data['harvester_id'],
            request_data.get('monitored_for', []),
            request_data.get('path', ''),
        )
        new_path.insert(conn)
        conn.commit()
        return MonitoredPathRow.to_json(new_path)
    elif request.method == 'DELETE':
        print('deleting', id_)
        path = MonitoredPathRow.select_from_id(
            id_, conn
        )
        path.delete(conn)
        conn.commit()
        return jsonify({'success': True}), 200


