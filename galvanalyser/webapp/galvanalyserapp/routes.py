import sys
import flask
import numpy as np
from flask_cors import cross_origin
from flask import request, abort, session, jsonify, make_response
from datetime import timezone
from datetime import datetime
from datetime import timedelta
import json

from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies
from flask_jwt_extended import get_jwt_identity

from pygalvanalyser.experiment.timeseries_data_row import (
    TimeseriesDataRow,
    RECORD_NO_COLUMN_ID,
)
from pygalvanalyser.experiment import (
    AccessRow, DatasetRow, ColumnRow, MetadataRow, InstitutionRow
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

    user = User.get(auth.username)

    if user.validate_password(auth.password):
        response = jsonify({"message": "login successful"})
        access_token = create_access_token(
            identity=user.to_json()
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

@app.route('/api/dataset', methods=['GET'])
@cross_origin()
@jwt_required()
def dataset():
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    datasets = DatasetRow.all(conn, with_metadata=True)
    print('called dataset', datasets)
    return DatasetRow.to_json(datasets)

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
            manufacturer_id=request_data.get('manufacturer_id', None),
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

        if 'manufacturer_id' in request_data:
            cell.manufacturer_id = \
                request_data['manufacturer_id']
        if 'uid' in request_data:
            cell.uid = request_data['uid']
        if 'manufacturer_id' in request_data:
            cell.manufacturer_id = request_data['manufacturer_id']
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


@app.route('/api/institution', methods=['GET', 'POST'])
@app.route('/api/institution/<int:id_>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@cross_origin()
def institution(id_=None):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    print('institution')
    if request.method == 'GET':
        if id_ is None:
            institution = InstitutionRow.all(conn)
        else:
            institution = InstitutionRow.select_from_id(id_, conn)
            if institution is None:
                return jsonify({
                    'message': 'institution not found'
                }), 404
        return InstitutionRow.to_json(institution)
    elif request.method == 'POST':
        request_data = request.get_json()
        print('institution post', request_data)
        institution = InstitutionRow(
            name=request_data.get('name', ''),
        )
        institution.insert(conn)
        conn.commit()
        return InstitutionRow.to_json(institution)
    elif request.method == 'PUT':
        print('PUT with id', id_)
        institution = InstitutionRow.select_from_id(id_, conn)
        if institution is None:
            return jsonify({
                'message': 'institution not found'
            }), 404

        request_data = request.get_json()

        if 'name' in request_data:
            institution.name = request_data['name']

        institution.update(conn)
        conn.commit()
        return InstitutionRow.to_json(institution)
    elif request.method == 'DELETE':
        print('deleting', id_)
        institution = InstitutionRow.select_from_id(
            id_, conn
        )
        if institution is None:
            return jsonify({
                'message': 'institution not found'
            }), 404

        institution.delete(conn)
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


@app.route('/api/harvester', methods=['GET', 'POST'])
@app.route('/api/harvester/<int:id_>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@cross_origin()
def harvester(id_=None):
    user = User.from_json(get_jwt_identity())
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
        return MonitoredPathRow.to_json(harvester)
    elif request.method == 'POST':
        request_data = request.get_json()
        new_harvester = HarvesterRow(
            request_data.get('machine_id', None),
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

@app.route('/api/monitored_path',
           methods=['GET', 'PUT', 'POST', 'DELETE'])
@jwt_required()
@cross_origin()
def monitored_path():
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


