init:
	pip install -r ./galvanalyser/harvester/requirements.txt && pip install -r ./galvanalyser/webapp/requirements.txt

test:
	py.test tests

protobuf: protobuf/placeholder.proto
	protoc -I=protobuf --python_out=galvanalyser/protobuf --js_out=import_style=commonjs,binary:webapp-static-content/js/protobuf protobuf/placeholder.proto

harvester-docker:
	docker build -t harvester -f harvester/Dockerfile .

.PHONY: init test protobuf harvester-docker