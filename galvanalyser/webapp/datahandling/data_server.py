import galvanalyser.protobuf.placeholder_pb2 as placeholder_pb2
import flask

def log(text):
    with open("/tmp/log.txt", "a") as myfile:
        myfile.write(text + "\n")

def register_handlers(app, config):
    @app.server.route("/data-server/data")
    def serve_data():
        log("in serve_data")
        message = placeholder_pb2.DataMessage()
        log(str(repr(message.data)))
        message.data.extend([1.0,2.0,3.0,4.0])
        log(str(repr(message.data)))
        #return flask.make_response("foo:") # + str(message)
        log(f"length {len(message.SerializeToString())}")
        response = flask.make_response(message.SerializeToString())
        response.headers.set('Content-Type', 'application/octet-stream')
        # response.headers.set('Content-Disposition', 'attachment', filename='np-array.bin')
        return response
    #pass