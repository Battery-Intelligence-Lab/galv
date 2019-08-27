#!/bin/bash

source /workdir/venv/bin/activate

cd /workdir/project

make init

pushd libs/galvanalyser-dash-components
npm install
popd

make custom-dash-components

make protobuf