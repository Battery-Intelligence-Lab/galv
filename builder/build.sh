#!/bin/bash
echo "
Running docker-builder build.sh
"
source /workdir/venv/bin/activate

cd /workdir/project

echo "
make init:
"
make init

echo "
npm install:
"
pushd libs/galvanalyser-dash-components
npm install
popd

echo "
make custom-dash-components:
"
make custom-dash-components

echo "
make protobuf:
"

make protobuf