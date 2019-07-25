import galvanalyser.protobuf.experiment_data_pb2 as experiment_data_pb2
import flask
from flask import request, abort
import flask_login

from galvanalyser.database.experiment.data_row import DataRow
from galvanalyser.database.experiment.access_row import AccessRow
import galvanalyser.database.experiment.data_columns as DataColumns
import math
import psycopg2

def log(text):
    with open("/tmp/log.txt", "a") as myfile:
        myfile.write(text + "\n")


def register_handlers(app, config):
    @app.server.route("/data-server/data")
    def serve_data():
        log("in serve_data")
        message = experiment_data_pb2.DataRanges()
        message.experiment_id = 3
        value = message.ranges.add()
        value.start_sample_no = 50
        value.volts.extend([math.sin(x / 10.0) for x in range(512)])
        value.test_time.extend([float(x) / 60.0 for x in range(512)])
        # log(str(repr(message.data)))
        # log(repr(flask.request.headers))
        # message.data.extend([float(x) for x in range(512)])
        # log(str(repr(message.data)))
        # return flask.make_response("foo:") # + str(message)
        log(f"length {len(message.SerializeToString())}")
        response = flask.make_response(message.SerializeToString())
        response.headers.set("Content-Type", "application/octet-stream")
        # response.headers.set('Content-Disposition', 'attachment', filename='np-array.bin')
        return response

    @app.server.route("/experiment/<int:experiment_id>/data")
    @flask_login.login_required
    def experiment_data(experiment_id):
        data_from = request.args.get("from", None)
        data_to = request.args.get("to", None)
        columns = request.args.get("columns", None)
        conn = None
        try:
            conn = config["get_db_connection_for_current_user"]()
            if AccessRow.current_user_has_access_to_experiment(
                experiment_id, conn
            ):
                results = DataColumns.select_experiment_data_columns_in_range(
                    experiment_id, columns, data_from, data_to
                )
                pass
            else:
                abort(403)
        #except psycopg2.errors.InsufficientPrivilege:
        #    abort(403) # commented out for debugging
        finally:
            if conn:
                conn.close()
        return f"You asked for data for experiment {experiment_id} in range {data_from} - {data_to} and columns {columns}"

    @app.server.route("/experiment/<int:id>/metadata")
    @flask_login.login_required
    def experiment_metadata(id):
        data_from = request.args.get("from", None)
        data_to = request.args.get("to", None)
        columns = request.args.get("columns", None)
        return f"You asked for metadata for experiment {id} in range {data_from} - {data_to} and columns {columns}"

    # pass
