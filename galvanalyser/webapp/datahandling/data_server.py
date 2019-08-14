import sys
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


    @app.server.route("/experiment/<int:experiment_id>/columns")
    @flask_login.login_required
    def experiment_columns(experiment_id):
        # return a list of available columns for this experiment
        return ["test_time", "volts", "amps"]

    @app.server.route("/experiment/<int:experiment_id>/data")
    @flask_login.login_required
    def experiment_data(experiment_id):
        data_from = request.args.get("from", None)
        data_to = request.args.get("to", None)
        column = request.args.get("column", None)
        # log(f"You asked for data for experiment {experiment_id} in range {data_from} - {data_to} and columns {columns}")
        conn = None
        try:
            conn = config["get_db_connection_for_current_user"]()
            if AccessRow.current_user_has_access_to_experiment(
                experiment_id, conn
            ):
                # log("Getting results")
                select_columns = (
                    ["sample_no"]
                    if "sample_no" == column
                    else ["sample_no", column]
                )
                results = DataColumns.select_experiment_data_columns_in_range(
                    experiment_id, select_columns, data_from, data_to, conn
                )
                # log("got results")
                message = experiment_data_pb2.DataRanges()
                # log("made message")
                message.experiment_id = experiment_id
                message.column = column
                iters = [iter(col) for col in results]
                sample_no_iter = iters[0]
                data_iter = iters[1]
                # log("made iters")
                try:
                    # What we actually want is to loop over all samples
                    # make contigious blocks for each channel
                    # split all blocks on discontinuities of sample numbers
                    # and split individual blocks on null values
                    first_sample_no = next(sample_no_iter)
                    while True:
                        current_sample_no = first_sample_no
                        # log(f"First block sample no is {first_sample_no}")
                        # loop for each block of contiguous data
                        range_msg = message.ranges.add()
                        # log("range msg added")
                        range_msg.start_sample_no = first_sample_no
                        # log("start_sample_no set")
                        while True:
                            # loop over contiguous data
                            # add data
                                # log(f"appending to {col_name}")
                            range_msg.values.append(next(data_iter))
                            new_sample_no = next(sample_no_iter)
                            if new_sample_no == (current_sample_no + 1):
                                current_sample_no = new_sample_no
                            else:
                                # a new bock of data
                                first_sample_no = new_sample_no
                                break
                except StopIteration:
                    pass
                # return (f"You asked for data for experiment {experiment_id} in range {data_from} - {data_to} and columns {columns}."
                #    f"\nThere were {str([x for x in map(len, results)])} results"
                # )
                log("Serializing response")
                response = flask.make_response(message.SerializeToString())
                response.headers.set(
                    "Content-Type", "application/octet-stream"
                )
                log("returning response")
                return response
            else:
                abort(403)
        except:
            log(f"Exception:\n{repr(sys.exc_info())}")
        # except psycopg2.errors.InsufficientPrivilege:
        #    abort(403) # commented out for debugging
        finally:
            if conn:
                conn.close()

    @app.server.route("/experiment/<int:id>/metadata")
    @flask_login.login_required
    def experiment_metadata(id):
        data_from = request.args.get("from", None)
        data_to = request.args.get("to", None)
        columns = request.args.get("columns", None)
        return f"You asked for metadata for experiment {id} in range {data_from} - {data_to} and columns {columns}"

    # pass
