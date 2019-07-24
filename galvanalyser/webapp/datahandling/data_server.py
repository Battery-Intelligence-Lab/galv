import galvanalyser.protobuf.experiment_data_pb2 as experiment_data_pb2
import flask

import math

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
        value.volts.extend([math.sin(x/10.0) for x in range(512)])
        value.test_time.extend([float(x)/60.0 for x in range(512)])
        #log(str(repr(message.data)))
        #log(repr(flask.request.headers))
        #message.data.extend([float(x) for x in range(512)])
        # log(str(repr(message.data)))
        # return flask.make_response("foo:") # + str(message)
        log(f"length {len(message.SerializeToString())}")
        response = flask.make_response(message.SerializeToString())
        response.headers.set("Content-Type", "application/octet-stream")
        # response.headers.set('Content-Disposition', 'attachment', filename='np-array.bin')
        return response

    # pass
