init:
	pip install -r ./galvanalyser/harvester/requirements.txt && pip install -r ./galvanalyser/webapp/requirements.txt

test:
	py.test tests

protobuf: protobuf/placeholder.proto
	mkdir -p galvanalyser/protobuf && mkdir -p galvanalyser/webapp/assets/protobuf && \
	protoc -I=protobuf --python_out=galvanalyser/protobuf --js_out=import_style=commonjs,binary:galvanalyser/webapp/assets/protobuf protobuf/placeholder.proto

format:
	black --line-length 79 ./

harvester-docker-build:
	docker build -t harvester -f harvester/Dockerfile .

harvester-docker-run:
	docker run --rm -it -v /Users/luke/code/battery-project/battery-project/galvanalyser:/usr/src/app/galvanalyser -v /Users/luke/code/battery-project/harvester-test:/usr/src/app/config --net host harvester

.PHONY: init test protobuf format harvester-docker-build harvester-docker-run