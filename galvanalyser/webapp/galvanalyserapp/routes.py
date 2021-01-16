import sys
from .protobuf import timeseries_data_pb2
import flask
from flask import request, abort
import flask_login

from pygalvanalyser.experiment.timeseries_data_row import (
    TimeseriesDataRow,
    RECORD_NO_COLUMN_ID,
)
from pygalvanalyser.experiment.access_row import AccessRow
import pygalvanalyser.experiment.timeseries_data_column as TimeseriesDataColumn
import math
import psycopg2

from flask import current_app as app

def log(text):
    with open("/tmp/log.txt", "a") as myfile:
        myfile.write(text + "\n")


@app.route("/data-server/data")
def serve_data():
    log("in serve_data")
    message = timeseries_data_pb2.DataRanges()
    message.dataset_id = 3
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

@app.route("/dataset/<int:dataset_id>/columns")
@flask_login.login_required
def dataset_columns(dataset_id):
    # return a list of available columns for this experiment
    return ["test_time", "volts", "amps"]

@app.route("/dataset/<int:dataset_id>/data")
@flask_login.login_required
def dataset_data(dataset_id):
    data_from = request.args.get("from", None)
    data_to = request.args.get("to", None)
    column_id = int(request.args.get("column_id", RECORD_NO_COLUMN_ID))
    # log(f"You asked for data for dataset {dataset_id} in range {data_from} - {data_to} and columns {columns}")
    conn = None
    try:
        conn = config["get_db_connection_for_current_user"]()
        if AccessRow.current_user_has_access_to_dataset(dataset_id, conn):
            # log("Getting results")
            if int(column_id) == RECORD_NO_COLUMN_ID:  # sample_no id
                results = TimeseriesDataColumn.select_timeseries_data_record_nos_in_range(
                    dataset_id, data_from, data_to, conn
                )
            else:
                results = TimeseriesDataColumn.select_timeseries_data_column_in_range(
                    dataset_id, column_id, data_from, data_to, conn
                )
            # log("got results")
            message = timeseries_data_pb2.DataRanges()
            # log("made message")
            message.dataset_id = dataset_id
            message.column_id = column_id
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
            # return (f"You asked for data for dataset {dataset_id} in range {data_from} - {data_to} and columns {columns}."
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

@app.route("/dataset/<int:id>/metadata")
@flask_login.login_required
def dataset_metadata(id):
    data_from = request.args.get("from", None)
    data_to = request.args.get("to", None)
    columns = request.args.get("columns", None)
    return f"You asked for metadata for dataset {id} in range {data_from} - {data_to} and columns {columns}"
