import sys
import flask
import numpy as np
from flask_cors import cross_origin
from flask import request, abort, jsonify, make_response
import os
from datetime import timezone
from datetime import datetime
from datetime import timedelta
import json

from celery.schedules import crontab

from galvanalyser.harvester import main as harvester_main

from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies
from flask_jwt_extended import get_jwt_identity

from .database.experiment.timeseries_data_row import (
    TimeseriesDataRow,
    RECORD_NO_COLUMN_ID,
)
from .database.experiment import (
    AccessRow, Dataset, ColumnRow, MetadataRow, Equipment,
)
from .database.cell_data import (
    Cell
)
from .database.harvester import (
    MonitoredPathRow, HarvesterRow, ObservedFileRow
)
from .database.experiment import select_timeseries_column
import math
import psycopg2

from flask import current_app as app
from celery import current_app as celery

from functools import wraps

from .database.user_data import UserRow

from galvanalyser import Session


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

    if user.validate_password(auth.password):
        access_token = create_access_token(
            identity=UserRow.to_json(user)
        )
        response = jsonify({
            "message": "login successful",
            "access_token": access_token,
        })
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
    return UserRow.to_json(users)


@app.route('/api/dataset', methods=['GET'])
@app.route('/api/dataset/<int:id_>', methods=['GET', 'PUT'])
@cross_origin()
@jwt_required()
def dataset(id_=None):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    with Session() as session:
        current_user = json.loads(get_jwt_identity())
        if (id_ is not None and
                not AccessRow.exists(id_, current_user['id'], conn)):
            return jsonify({
                'message': 'user {} does not have access to dataset {}'.format(
                    current_user['username'], id_
                )
            }), 404

        if request.method == 'GET':
            if id_ is None:
                return jsonify(session.query(Dataset).all())
            else:
                return jsonify(session.get(Dataset, id_))
        elif request.method == 'PUT':
            dataset = session.get(Dataset, id_)
            if dataset is None:
                return jsonify({
                    'message': 'cell not found'
                }), 404

            request_data = request.get_json()

            if 'name' in request_data:
                dataset.name = request_data['name']
            if 'cell_id' in request_data:
                dataset.cell_id = request_data['cell_id']
            if 'owner_id' in request_data:
                dataset.owner_id = request_data['owner_id']
            if 'equipment' in request_data:
                dataset.equipment =  [
                    session.get(Equipment, id_)
                    for id_ in request_data['equipment']
                ]
            if 'purpose' in request_data:
                dataset.purpose = request_data['purpose']

            session.commit()
            return jsonify(dataset)


@app.route('/api/equipment', methods=['GET', 'POST'])
@app.route('/api/equipment/<int:id_>', methods=['GET', 'PUT', 'DELETE'])
@cross_origin()
@jwt_required()
def equipment(id_=None):
    with Session() as session:
        if request.method == 'GET':
            if id_ is None:
                return jsonify(session.query(Equipment).all())
            else:
                equipment = session.get(Equipment, id_)
                if equipment is None:
                    return jsonify({
                        'message': 'equipment not found'
                    }), 404
                return jsonify(equipment)
        elif request.method == 'POST':
            request_data = request.get_json()
            equipment = Equipment(
                name=request_data.get('name', None),
                type=request_data.get('type', None),
            )
            session.add(equipment)
            session.commit()
            return jsonify(equipment)
        elif request.method == 'PUT':
            equipment = session.get(Equipment, id_)
            if equipment is None:
                return jsonify({
                    'message': 'equipment not found'
                }), 404

            request_data = request.get_json()

            if 'type' in request_data:
                equipment.type = request_data['type']
            if 'name' in request_data:
                equipment.name = request_data['name']

            session.commit()
            return jsonify(equipment)
        elif request.method == 'DELETE':
            equipment = session.get(Equipment, id_)
            if equipment is None:
                return jsonify({
                    'message': 'equipment not found'
                }), 404

            session.delete(equipment)
            session.commit()
            return jsonify({'success': True}), 200


@app.route('/api/cell', methods=['GET', 'POST'])
@app.route('/api/cell/<int:id_>', methods=['GET', 'PUT', 'DELETE'])
@cross_origin()
@jwt_required()
def cell(id_=None):
    with Session() as session:
        if request.method == 'GET':
            if id_ is None:
                return jsonify(session.query(Cell).all())
            else:
                cell = session.get(Cell, id_)
                if cell is None:
                    return jsonify({
                        'message': 'cell not found'
                    }), 404
                return jsonify(cell)

        elif request.method == 'POST':
            request_data = request.get_json()
            cell = Cell(
                name=request_data.get('name', None),
                manufacturer=request_data.get('manufacturer', None),
                form_factor=request_data.get('form_factor', None),
                link_to_datasheet=request_data.get('link_to_datasheet', None),
                anode_chemistry=request_data.get('anode_chemistry', None),
                cathode_chemistry=request_data.get('cathode_chemistry', None),
                nominal_capacity=request_data.get('nominal_capacity', None),
                nominal_cell_weight=request_data.get('nominal_cell_weight', None),
            )
            session.add(cell)
            session.commit()
            return jsonify(cell)
        elif request.method == 'PUT':
            cell = session.get(Cell, id_)
            if cell is None:
                return jsonify({
                    'message': 'cell not found'
                }), 404

            request_data = request.get_json()

            if 'manufacturer' in request_data:
                cell.manufacturer = \
                    request_data['manufacturer']
            if 'name' in request_data:
                cell.name = request_data['name']
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

            session.commit()
            return jsonify(cell)
        elif request.method == 'DELETE':
            cell = session.get(Cell, id_)
            if cell is None:
                return jsonify({
                    'message': 'cell not found'
                }), 404

            session.delete(cell)
            session.commit()
            return jsonify({'success': True}), 200


@app.route('/api/manufacturer', methods=['GET', 'POST'])
@app.route('/api/manufacturer/<int:id_>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@cross_origin()
def manufacturer(id_=None):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
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
        manufacturer = ManufacturerRow(
            name=request_data.get('name', ''),
        )
        manufacturer.insert(conn)
        conn.commit()
        return ManufacturerRow.to_json(manufacturer)
    elif request.method == 'PUT':
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

    return serialise_numpy_array(array)


@celery.task()
def run_harvester_celery(machine_id):
    harvester_main(
        os.getenv('HARVESTER_USERNAME'),
        os.getenv('HARVESTER_PASSWORD'),
        machine_id,
        'galvanalyser_postgres', '5433',
        'galvanalyser', base_path='/usr/data'
    )


def run_harvester_periodic(harvester, sender=celery):
    if harvester.periodic_hour is None:
        del_harvester_periodic(harvester, sender=sender)
    else:
        sender.add_periodic_task(
            crontab(hour=harvester.periodic_hour, minute=0),
            run_harvester_celery
            .s(harvester.machine_id)
            .set(queue=harvester.harvester_name),
            name=harvester.machine_id + 'periodic'
        )


def del_harvester_periodic(harvester, sender=celery):
    del celery.conf.beat_schedule[harvester.machine_id + 'periodic']


@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    conn = sender.conf["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    for harvester in HarvesterRow.all(conn):
        run_harvester_periodic(harvester, sender=sender)


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
    return jsonify({'success': True}), 200


@app.route('/api/harvester', methods=['GET', 'POST'])
@app.route('/api/harvester/<int:id_>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@cross_origin()
def harvester(id_=None):
    user = UserRow.from_json(get_jwt_identity())
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
    if request.method == 'GET':
        if id_ is not None:
            harvesters = HarvesterRow.select_from_id(id_, conn)
        else:
            harvesters = HarvesterRow.all(conn)
        return HarvesterRow.to_json(harvesters)
    elif request.method == 'PUT':
        harvester = HarvesterRow.select_from_id(
            id_, conn
        )
        request_data = request.get_json()
        if 'machine_id' in request_data:
            harvester.machine_id = request_data['machine_id']
        if 'periodic_hour' in request_data:
            harvester.periodic_hour = request_data['periodic_hour']
        harvester.update(conn)
        conn.commit()

        # add periodic task
        run_harvester_periodic(harvester)

        return HarvesterRow.to_json(harvester)
    elif request.method == 'POST':
        request_data = request.get_json()
        new_harvester = HarvesterRow(
            request_data.get('machine_id', None),
            harvester_name=os.getenv('HARVESTER_USERNAME'),
        )
        new_harvester.insert(conn)
        conn.commit()

        # add periodic task
        run_harvester_periodic(harvester)

        return HarvesterRow.to_json(new_harvester)
    elif request.method == 'DELETE':
        harvester = HarvesterRow.select_from_id(
            id_, conn
        )
        harvester.delete(conn)
        conn.commit()

        # delete periodic task
        del_harvester_periodic(harvester)
        return jsonify({'success': True}), 200


@app.route('/api/monitored_path', methods=['GET', 'POST'])
@app.route('/api/monitored_path/<int:id_>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@cross_origin()
def monitored_path(id_=None):
    conn = app.config["GET_DATABASE_CONN_FOR_SUPERUSER"]()
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
        path = MonitoredPathRow.select_from_id(
            id_, conn
        )
        path.delete(conn)
        conn.commit()
        return jsonify({'success': True}), 200
