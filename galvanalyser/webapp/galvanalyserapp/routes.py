import sys
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


@app.route("/dataset/<int:dataset_id>/columns")
@flask_login.login_required
def dataset_columns(dataset_id):
    # return a list of available columns for this experiment
    return ["test_time", "volts", "amps"]

@app.route("/dataset/<int:id>/metadata")
@flask_login.login_required
def dataset_metadata(id):
    data_from = request.args.get("from", None)
    data_to = request.args.get("to", None)
    columns = request.args.get("columns", None)
    return f"You asked for metadata for dataset {id} in range {data_from} - {data_to} and columns {columns}"
