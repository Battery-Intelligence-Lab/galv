init:
    pip install -r requirements.txt

test:
    py.test tests

protobuf: protobuf/placeholder.proto
    protoc -I=protobuf --python_out=galvanalyser/protobuf --js_out=import_style=commonjs,binary:webapp-static-content/js/protobuf protobuf/placeholder.proto

.PHONY: init test protobuf