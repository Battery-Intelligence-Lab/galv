init:
	pip install -r ./galvanalyser/harvester/requirements.txt && pip install -r ./galvanalyser/webapp/requirements.txt

test:
	py.test tests

protobuf: protobuf/experiment-data.proto
	mkdir -p galvanalyser/protobuf && mkdir -p libs/galvanalyser-js-protobufs && \
	protoc -I=protobuf --python_out=galvanalyser/protobuf --js_out=binary:libs/galvanalyser-js-protobufs protobuf/experiment-data.proto && \
	libs/closure-library/closure/bin/build/closurebuilder.py \
  --root=libs/closure-library \
  --root=libs/protobuf/js \
  --root=libs/galvanalyser-js-protobufs \
  --root=webapp-static-content/js \
  --input=libs/galvanalyser-js-protobufs/dataranges.js \
  --input=webapp-static-content/js/data-range.js \
  --output_mode=script \
  --output_file=webapp-static-content/libs/galvanalyser-protobuf.js && \
  sed -i -e "s/^goog\.global\.CLOSURE_NO_DEPS;/goog\.global\.CLOSURE_NO_DEPS = true;/" "webapp-static-content/libs/galvanalyser-protobuf.js" && \
  rm -f webapp-static-content/libs/galvanalyser-protobuf.js-e

custom-dash-components:
	pushd "libs/galvanalyser-dash-components" && \
	npm run build && \
	python setup.py sdist

builder-docker-build:
	docker build -t builder -f builder/Dockerfile .

builder-docker-run:
	docker run --rm -it -v ${CURDIR}:/workdir/project:rw builder


format:
	black --line-length 79 --exclude "libs|.venv|_pb2\.py" ./ && \
  find . \( -type f -name "*.js" ! -path "*/libs/*" ! -path "./.venv/*" \) -exec js-beautify -r {} \;

harvester-docker-build:
	docker build -t harvester -f harvester/Dockerfile .

harvester-docker-run:
	docker run --rm -it -v ${CURDIR}/galvanalyser:/usr/src/app/galvanalyser -v ${CURDIR}/harvester-test:/usr/src/app/config --net host harvester

.PHONY: init test protobuf custom-dash-components builder-docker-build builder-docker-run format harvester-docker-build harvester-docker-run