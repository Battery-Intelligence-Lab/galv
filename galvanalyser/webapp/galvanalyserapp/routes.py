import sys
import flask
from flask import request, abort, session
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

@app.route("/dataset/<int:dataset_id>/metadata")
@flask_login.login_required
def dataset_metadata(dataset_id):
    # return a list of available columns for this experiment
    return "im user {}".format(flask_login.current_user)

@app.route("/dataset/<int:dataset_id>/columns")
@flask_login.login_required
def dataset_columns(dataset_id):
    # return a list of available columns for this experiment
    return ["test_time", "volts", "amps"]

@app.route("/")
def hello():
    # return a list of available columns for this experiment
    print('ASDFASDFASDFSDFSD', session)
    session['test'] = 1
    if 'test' not in session:
        session['test'] = 1
    else:
        session['test'] += int(session['test']) + 1
    return "its alive!!! {}".format(str(session['test']))
