#!/bin/bash

source /workdir/venv/bin/activate

cd /workdir/project

make init

pushd libs/galvanalyser-dash-components
npm install
npm run build
python setup.py sdist
popd

make protobuf