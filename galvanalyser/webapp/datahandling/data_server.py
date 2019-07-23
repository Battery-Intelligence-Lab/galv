import galvanalyser.protobuf.placeholder_pb2 as placeholder_pb2

def register_handlers(app, config):
    @app.server.route("/data-server/data")
    def serve_data():
        message = placeholder_pb2.DataMessage()
        message.data = [1.0,2.0,3.0,4.0]
        return ""
    pass